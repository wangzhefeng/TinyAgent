"""In-process personal runtime with durable execution and recovery."""

from __future__ import annotations

import contextvars
import json
import threading
from typing import Any

from ..agent.context import ContextBuilder
from ..agent.types import RunRecord
from ..core.llm import parse_tool_arguments
from ..core.protocols import ChatModel
from ..core.tools import ToolRegistry
from ..memory import MemoryManager
from ..skills import SkillManager
from .approvals import CLIApprover
from .store import SQLiteStore

_DEFAULT_SYSTEM = (
    "You are a careful personal agent. Use tools to inspect the workspace, "
    "cite concrete evidence, and do not claim changes you did not make. "
    "Write files or run commands only when necessary, and report exact checks."
)
_SAFE_TOOL_NAMES = {"list_dir", "read_file", "search_text", "remember", "search_sessions", "load_skill", "update_plan"}
_PLAN_SAFE_TOOLS = {
    "list_dir", "read_file", "search_text", "search_sessions",
    "load_skill", "list_tasks", "update_plan", "submit_plan",
    "delegate", "delegate_parallel",
}

_CURRENT_SESSION: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_session", default=None
)


class RunCancelled(RuntimeError):
    """Raised when a run is cancelled at an execution boundary."""


class PersonalRuntime:
    """Run native tool-calling agents with SQLite-backed sessions."""

    def __init__(
        self,
        store: SQLiteStore,
        model: ChatModel,
        registry: ToolRegistry,
        approver: CLIApprover | None = None,
        context: ContextBuilder | None = None,
        system: str = _DEFAULT_SYSTEM,
        max_steps: int = 6,
        execution_name: str = "local",
        memory: MemoryManager | None = None,
        skills: SkillManager | None = None,
    ) -> None:
        self.store = store
        self.model = model
        self.registry = registry
        self.memory = memory
        self.skills = skills
        self.approver = approver or CLIApprover(_SAFE_TOOL_NAMES)
        self.context = context or ContextBuilder()
        self.system = system
        self.max_steps = max_steps
        self.execution_name = execution_name
        self._plan_sessions: set[str] = set()
        self._session_locks: dict[str, threading.Lock] = {}
        self._session_locks_guard = threading.Lock()

    def create_run(
        self,
        question: str,
        session_id: str = "default",
        idempotency_key: str | None = None,
        kind: str = "interactive",
    ) -> RunRecord:
        """Create an interactive run without executing it."""
        return self.store.create_run(session_id, question, idempotency_key, kind=kind)

    def run(
        self,
        question: str,
        session_id: str = "default",
        idempotency_key: str | None = None,
        kind: str = "interactive",
        tools: set[str] | None = None,
    ) -> str:
        """Create and execute one run, optionally restricted to a tool subset."""
        with self._session_lock(session_id):
            run = self.create_run(question, session_id, idempotency_key, kind=kind)
            if run.status == "completed":
                return run.output
            self.store.update_run_status(run.id, "running")
            return self._execute(run.id, append_input=True, allowed_tools=tools)

    def resume_run(self, run_id: str) -> str:
        """Resume a persisted run without duplicating its user input."""
        run = self.store.get_run(run_id)
        with self._session_lock(run.session_id):
            if run.status == "completed":
                return run.output
            self._check_recovery_events(run_id)
            self.store.update_run_status(run_id, "running")
            return self._execute(run_id, append_input=False)

    def cancel_run(self, run_id: str) -> RunRecord:
        """Request cooperative cancellation of a run."""
        run = self.store.get_run(run_id)
        if run.status != "completed":
            self.store.update_run_status(run_id, "cancelled")
            self.store.append_event(run_id, "run_end", {"final": False, "cancelled": True})
        return self.store.get_run(run_id)

    def enter_plan_mode(self, session_id: str = "default") -> None:
        """Restrict one session to read-only investigation until a plan is approved."""
        self._plan_sessions.add(session_id)

    def in_plan_mode(self, session_id: str = "default") -> bool:
        """Return whether one session is currently in plan mode."""
        return session_id in self._plan_sessions

    def _session_lock(self, session_id: str) -> threading.Lock:
        with self._session_locks_guard:
            return self._session_locks.setdefault(session_id, threading.Lock())

    def _execute(
        self, run_id: str, append_input: bool, allowed_tools: set[str] | None = None
    ) -> str:
        """Execute one persisted run, optionally restricted to a tool subset."""
        run = self.store.get_run(run_id)
        session_token = _CURRENT_SESSION.set(run.session_id)
        try:
            if append_input:
                self.store.append_event(run_id, "user_input", {"text": run.input})
            prompt_state = self._prompt_state(run.session_id)
            specs = (
                [spec for spec in self.registry.specs if spec.name in allowed_tools]
                if allowed_tools is not None
                else self.registry.specs
            )
            api_calls = 0
            tool_calls = 0
            token_totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
            has_real_usage = False
            last_usage: dict[str, Any] = {}
            try:
                for _step in range(1, self.max_steps + 1):
                    self._raise_if_cancelled(run_id)
                    view = self._view(run.session_id, last_usage, prompt_state)
                    if view.needs_compaction:
                        compaction_usage, view = self._compact_if_needed(run_id, view, prompt_state)
                        api_calls += compaction_usage["api_calls"]
                        for key in token_totals:
                            token_totals[key] += compaction_usage[key]
                        has_real_usage = has_real_usage or compaction_usage["has_real_usage"]
                    reply = self.model.chat(view.messages, tools=specs)
                    api_calls += 1
                    last_usage = reply.usage
                    if reply.usage:
                        has_real_usage = True
                        for key in token_totals:
                            token_totals[key] += self._reply_tokens(reply, key)
                    self.store.append_event(
                        run_id,
                        "assistant_reply",
                        {
                            "text": reply.text,
                            "tool_calls": [call.to_dict() for call in reply.tool_calls],
                            "usage": reply.usage,
                        },
                    )
                    if not reply.tool_calls:
                        usage = self._usage(api_calls, tool_calls, token_totals, has_real_usage)
                        self.store.update_run_status(run_id, "completed", output=reply.text, usage=usage)
                        self.store.append_event(run_id, "run_end", {"final": True})
                        return reply.text
                    for call in reply.tool_calls:
                        self._raise_if_cancelled(run_id)
                        tool_calls += 1
                        arguments = parse_tool_arguments(call.arguments)
                        self.store.append_event(
                            run_id,
                            "tool_call",
                            {"call_id": call.id, "name": call.name, "arguments": arguments},
                        )
                        if allowed_tools is not None and call.name not in allowed_tools:
                            result = f"Error: 当前运行不能使用工具 {call.name}"
                        else:
                            result = self._call_tool(run_id, call.id, call.name, arguments)
                        self.store.append_event(
                            run_id,
                            "tool_result",
                            {"call_id": call.id, "content": result},
                        )
                raise RuntimeError(f"maximum steps reached: {self.max_steps}")
            except RunCancelled:
                raise
            except Exception as error:
                usage = self._usage(api_calls, tool_calls, token_totals, has_real_usage)
                self.store.update_run_status(run_id, "failed", error=str(error), usage=usage)
                self.store.append_event(run_id, "run_end", {"final": False, "error": str(error)})
                raise
        finally:
            _CURRENT_SESSION.reset(session_token)

    def _prompt_state(self, session_id: str) -> dict[str, Any]:
        state = self.store.get_session_state(session_id)
        if "prompt_snapshot" not in state:
            state["prompt_snapshot"] = {
                "memory": self.memory.snapshot() if self.memory else {"user": "", "memory": ""},
                "skills": self.skills.catalog() if self.skills else "",
            }
            self.store.save_session_state(session_id, state)
        return state["prompt_snapshot"]

    def _view(self, session_id: str, usage: dict[str, Any], prompt_state: dict[str, Any]):
        return self.context.build(
            self.store.session_events(session_id),
            self.system,
            usage=usage,
            memory_snapshot=prompt_state["memory"],
            skills_catalog=prompt_state["skills"],
            compaction=self.store.latest_context_artifact(session_id, "compaction"),
        )

    def _compact_if_needed(self, run_id: str, view: Any, prompt_state: dict[str, Any]):
        usage = self._empty_usage()
        run = self.store.get_run(run_id)
        events = self.store.session_events(run.session_id)
        cut = self._compaction_cut(events)
        if cut is None:
            return usage, view
        if self.memory is not None:
            self._preserve_memory(run, usage)
        summary_reply = self.model.chat([
            {"role": "system", "content": (
                "Summarize the agent history. Preserve goals, completed steps, current plan, "
                "important paths and parameters, evidence references, and unresolved issues. "
                "Do not add facts."
            )},
            {"role": "user", "content": self._render_events(events[:cut])},
        ])
        self._accumulate_usage(usage, summary_reply)
        self.store.create_context_artifact(
            run.session_id, "compaction", summary_reply.text, 0, cut
        )
        self.store.append_event(
            run_id,
            "compaction",
            {"summary": summary_reply.text, "source_end": cut, "usage": summary_reply.usage},
        )
        return usage, self._view(run.session_id, {}, prompt_state)

    def _preserve_memory(self, run: RunRecord, usage: dict[str, Any]) -> None:
        spec = next((spec for spec in self.registry.specs if spec.name == "remember"), None)
        if spec is None:
            return
        events = self.store.session_events(run.session_id)
        reply = self.model.chat([
            {"role": "system", "content": (
                "Review the history and save only stable user preferences, environment "
                "conventions, and repeated lessons with the remember tool. Do not save "
                "one-time task progress. If nothing is worth saving, respond without tools."
            )},
            {"role": "user", "content": self._render_events(events)},
        ], tools=[spec])
        self._accumulate_usage(usage, reply)
        self.store.append_event(
            run.id,
            "assistant_reply",
            {"text": reply.text, "tool_calls": [call.to_dict() for call in reply.tool_calls],
             "usage": reply.usage, "purpose": "memory_nudge"},
        )
        for call in reply.tool_calls:
            arguments = parse_tool_arguments(call.arguments)
            self.store.append_event(
                run.id, "tool_call",
                {"call_id": call.id, "name": call.name, "arguments": arguments},
            )
            result = self._call_tool(run.id, call.id, call.name, arguments)
            self.store.append_event(
                run.id, "tool_result", {"call_id": call.id, "content": result}
            )

    @staticmethod
    def _compaction_cut(events: list[Any]) -> int | None:
        user_indexes = [index for index, event in enumerate(events) if event.type == "user_input"]
        if len(user_indexes) < 2:
            return None
        cut = user_indexes[-2]
        return cut if cut > 0 else None

    @staticmethod
    def _render_events(events: list[Any]) -> str:
        lines = []
        for event in events:
            if event.type in {"user_input", "assistant_reply", "tool_result"}:
                lines.append(f"[{event.type}] {event.data.get('text') or event.data.get('content', '')}")
        return "\n".join(lines)

    @staticmethod
    def _empty_usage() -> dict[str, Any]:
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "api_calls": 0,
            "has_real_usage": False,
        }

    def _accumulate_usage(self, usage: dict[str, Any], reply: Any) -> None:
        usage["api_calls"] += 1
        if not reply.usage:
            return
        usage["has_real_usage"] = True
        for key in ("input_tokens", "output_tokens", "total_tokens"):
            usage[key] += self._reply_tokens(reply, key)

    def _call_tool(
        self,
        run_id: str,
        call_id: str,
        name: str,
        arguments: dict[str, Any],
    ) -> str:
        run = self.store.get_run(run_id)
        if (
            run.kind != "scheduled"
            and run.session_id in self._plan_sessions
            and name not in _PLAN_SAFE_TOOLS
        ):
            return (
                "Permission denied: 计划模式下只能读和调查（可用 update_plan 记录计划）；"
                "想好后调用 submit_plan 提交完整计划，经批准后才能动手。"
            )
        if run.kind == "scheduled":
            task = self.store.scheduled_task_by_run(run_id)
            allowed = set(json.loads(task["allow_json"])) if task else set()
            read_only = {"list_dir", "read_file", "search_text", "search_sessions", "load_skill"}
            forbidden = {"run_shell", "remember", "create_skill_draft", "schedule_task", "cancel_task", "list_tasks", "update_plan", "submit_plan", "delegate", "delegate_parallel"}
            if name in forbidden or (name not in read_only and name not in allowed):
                return f"Permission denied: {name} is not preauthorized for unattended runs"
            try:
                return str(self.registry.call(name, **arguments))
            except Exception as error:  # noqa: BLE001
                return f"tool error: {type(error).__name__}: {error}"
        if name not in self.approver.safe_tools:
            approval_id = self.store.create_approval(
                run_id, call_id, {"name": name, "arguments": arguments}
            )
            self.store.append_event(
                run_id, "approval_requested", {"approval_id": approval_id, "name": name}
            )
        else:
            approval_id = None
        allowed, reason = self.approver.check(name, arguments)
        if approval_id is not None:
            self.store.resolve_approval(approval_id, allowed, reason)
            self.store.append_event(
                run_id,
                "approval_resolved",
                {"approval_id": approval_id, "allowed": allowed, "reason": reason},
            )
        if not allowed:
            return f"Permission denied: {reason}"
        run = self.store.get_run(run_id)
        if name == "remember" and run.kind != "interactive":
            return "Permission denied: only interactive runs may write long-term memory"
        try:
            result = str(self.registry.call(name, **arguments))
        except Exception as error:  # noqa: BLE001
            return f"tool error: {type(error).__name__}: {error}"
        if name == "submit_plan" and not result.startswith("Error"):
            self._plan_sessions.discard(run.session_id)
        if name == "remember" and not result.startswith("Error"):
            self.store.append_event(
                run_id,
                "memory_write",
                {"call_id": call_id, "arguments": arguments, "result": result},
            )
        return result

    def _raise_if_cancelled(self, run_id: str) -> None:
        if self.store.get_run(run_id).status == "cancelled":
            raise RunCancelled(run_id)

    def _check_recovery_events(self, run_id: str) -> None:
        declared: set[str] = set()
        answered: set[str] = set()
        for event in self.store.list_events(run_id):
            if event.type == "assistant_reply":
                declared.update(call["id"] for call in event.data.get("tool_calls", []))
            elif event.type == "tool_result":
                answered.add(event.data["call_id"])
        pending = declared - answered
        if pending:
            raise RuntimeError(f"cannot safely resume with pending tool calls: {sorted(pending)}")

    @staticmethod
    def _reply_tokens(reply: Any, key: str) -> int:
        if key == "total_tokens" and "total_tokens" not in reply.usage:
            return int(reply.usage.get("input_tokens", 0)) + int(
                reply.usage.get("output_tokens", 0)
            )
        return int(reply.usage.get(key, 0))

    @staticmethod
    def _usage(
        api_calls: int,
        tool_calls: int,
        token_totals: dict[str, int],
        has_real_usage: bool,
    ) -> dict[str, Any]:
        return {
            **(token_totals if has_real_usage else {
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
            }),
            "api_calls": api_calls,
            "tool_calls": tool_calls,
            "estimated": not has_real_usage,
        }
