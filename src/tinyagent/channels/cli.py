"""CLI for running and inspecting personal agent sessions."""

from __future__ import annotations

import argparse
import json
import sys
from contextlib import nullcontext
from pathlib import Path

from ..agent import ContextBuilder
from ..core.llm import OpenAIChatModel
from ..core.protocols import ChatModel
from ..core.tools import ToolRegistry
from ..execution import make_execution_backend
from ..memory import MemoryManager
from ..runtime import LocalOutbox, PersonalRuntime, Scheduler, SQLiteStore
from ..runtime.approvals import CLIApprover
from ..skills import SkillManager
from ..tools import (
    make_learning_tools,
    make_plan_tools,
    make_scheduler_tools,
    make_workspace_tools,
)
from ..tools.planning import PLAN_MODE_PROMPT

_SAFE_TOOLS = {"list_dir", "read_file", "search_text", "remember", "search_sessions", "load_skill", "list_tasks", "update_plan"}


def build_runtime(
    workspace: str | Path,
    state: str | Path,
    model: ChatModel | None = None,
    writable: bool = False,
    auto_approve: bool = False,
    extra_tools: list | None = None,
    extra_safe_tools: set[str] | None = None,
) -> PersonalRuntime:
    """Assemble a runtime with optional safe write, shell, and mounted tools."""
    execution = make_execution_backend(Path(state).parent) if writable else None
    store = SQLiteStore(state)
    memory = MemoryManager(Path(state).parent)
    skills = SkillManager(Path(state).parent)
    notes_path = Path(workspace).expanduser() / "AGENTS.md"
    project_notes = notes_path.read_text(encoding="utf-8") if notes_path.is_file() else ""
    registry = ToolRegistry([
        *make_workspace_tools(workspace, execution=execution),
        *make_learning_tools(memory, skills, store),
        *make_plan_tools(),
    ])
    approver = CLIApprover(
        _SAFE_TOOLS | set(extra_safe_tools or set()),
        ask=(lambda _prompt: "y") if auto_approve else None,
        interactive=True if auto_approve else None,
    )
    if execution is not None and not execution.sandboxed:
        print(
            "Warning: sandbox unavailable; writes and shell require per-call approval "
            "and run without hard isolation.",
            file=sys.stderr,
        )
    runtime = PersonalRuntime(
        store=store,
        model=model or OpenAIChatModel(),
        registry=registry,
        approver=approver,
        context=ContextBuilder(project_notes=project_notes),
        execution_name=execution.name if execution is not None else "local",
        memory=memory,
        skills=skills,
    )
    scheduler = Scheduler(
        store,
        runtime,
        LocalOutbox(Path(state).parent / "deliveries.jsonl"),
    )
    for extra_tool in extra_tools or []:
        runtime.registry.add(extra_tool)
    for scheduler_tool in make_scheduler_tools(scheduler):
        runtime.registry.add(scheduler_tool)
    runtime.scheduler = scheduler
    return runtime


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(prog="tinyagent")
    parser.add_argument("--workspace", default=".", help="Workspace visible to tools")
    parser.add_argument("--state", default="~/.tinyagent/state.db", help="SQLite state path")
    parser.add_argument("--session", default="default", help="Session ID")
    parser.add_argument("--writable", action="store_true", help="Enable approved writes and shell")
    parser.add_argument("--yes", action="store_true", help="Approve every write/shell for this invocation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Run one task")
    run.add_argument("task", help="Task to execute")
    run.add_argument("--key", help="Optional idempotency key")

    subparsers.add_parser("chat", help="Chat in one persistent session")

    resume = subparsers.add_parser("resume", help="Resume a run by ID")
    resume.add_argument("run_id")

    usage = subparsers.add_parser("usage", help="Show a run's token and call usage")
    usage.add_argument("run_id")

    subparsers.add_parser("events", help="Print recent session events")
    subparsers.add_parser("export", help="Export raw session events as JSONL")

    schedule = subparsers.add_parser("schedule", help="Manage and run scheduled tasks")
    schedule_sub = schedule.add_subparsers(dest="schedule_command", required=True)
    add = schedule_sub.add_parser("add", help="Add a scheduled task")
    add.add_argument("spec", help="every 30m / every 2h / daily 09:00")
    add.add_argument("prompt")
    add.add_argument("--kind", default="task", choices=["task", "heartbeat"])
    add.add_argument("--allow", default="", help="Comma-separated preauthorized tools")
    add.add_argument("--immediate", action="store_true")
    schedule_sub.add_parser("list", help="List active tasks")
    cancel = schedule_sub.add_parser("cancel", help="Cancel a task")
    cancel.add_argument("task_id")
    schedule_sub.add_parser("run", help="Run due tasks")
    return parser


def _print_events(runtime: PersonalRuntime, session_id: str) -> None:
    events = runtime.store.session_events(session_id)
    for event in events[-20:]:
        print(f"{event.run_id[:8]} #{event.seq} {event.type} {event.data}")


def _mount_mcp_tools(state_dir: Path):
    """Mount configured MCP servers when the optional extra is installed."""
    config = state_dir / "mcp.json"
    if not config.is_file():
        return nullcontext([])
    try:
        from ..ext.mcp import mounted_mcp_tools
    except ImportError:
        print(
            "Warning: mcp.json found but tinyagent[mcp] is not installed; skipping MCP tools.",
            file=sys.stderr,
        )
        return nullcontext([])
    return mounted_mcp_tools(config)


def _mcp_safe_names(state_dir: Path) -> set[str]:
    """Prefixed names of MCP tools explicitly marked safe in the config."""
    try:
        from ..ext.mcp import safe_tool_names
    except ImportError:
        return set()
    return safe_tool_names(state_dir / "mcp.json")


def main(argv: list[str] | None = None, model: ChatModel | None = None) -> int:
    """Run the personal agent CLI."""
    args = build_parser().parse_args(argv)
    state_dir = Path(args.state).expanduser().parent
    try:
        with _mount_mcp_tools(state_dir) as mcp_tools:
            runtime = build_runtime(
                args.workspace,
                args.state,
                model,
                writable=args.writable,
                auto_approve=args.yes,
                extra_tools=mcp_tools,
                extra_safe_tools=_mcp_safe_names(state_dir) if mcp_tools else set(),
            )
            if args.command == "run":
                print(runtime.run(args.task, session_id=args.session, idempotency_key=args.key))
            elif args.command == "resume":
                print(runtime.resume_run(args.run_id))
            elif args.command == "usage":
                print(json.dumps(runtime.store.get_run(args.run_id).usage, ensure_ascii=False))
            elif args.command == "events":
                _print_events(runtime, args.session)
            elif args.command == "export":
                print(runtime.store.export_session(args.session))
            elif args.command == "schedule":
                if args.schedule_command == "add":
                    allowed = {item.strip() for item in args.allow.split(",") if item.strip()}
                    task = runtime.scheduler.add(
                        args.spec,
                        args.prompt,
                        allow=allowed,
                        kind=args.kind,
                        immediate=args.immediate,
                    )
                    print(json.dumps(task, ensure_ascii=False))
                elif args.schedule_command == "list":
                    print(json.dumps(runtime.scheduler.store.list_scheduled_tasks(), ensure_ascii=False))
                elif args.schedule_command == "cancel":
                    cancelled = runtime.scheduler.store.cancel_scheduled_task(args.task_id, "cli")
                    print(json.dumps({"cancelled": cancelled}))
                elif args.schedule_command == "run":
                    print(json.dumps(runtime.scheduler.run_due(), ensure_ascii=False))
            elif args.command == "chat":
                print("TinyAgent personal CLI. Use /events or /exit.")
                while True:
                    try:
                        task = input("you> ").strip()
                    except (EOFError, KeyboardInterrupt):
                        print()
                        break
                    if task in {"/exit", "/quit"}:
                        break
                    if task == "/events":
                        _print_events(runtime, args.session)
                    elif task:
                        if task.startswith("/plan "):
                            runtime.enter_plan_mode(args.session)
                            task = PLAN_MODE_PROMPT + task[len("/plan "):]
                        print(runtime.run(task, session_id=args.session))
        return 0
    except (RuntimeError, ValueError, KeyError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
