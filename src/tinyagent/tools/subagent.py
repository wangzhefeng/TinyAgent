"""Sub-agent delegation with isolated context and inherited approvals."""

from __future__ import annotations

import uuid
from concurrent.futures import ThreadPoolExecutor

from ..core.tools import ToolWrapper, tool
from ..runtime.runtime import _CURRENT_SESSION, PersonalRuntime

MAX_PARALLEL = 3
RESULT_LIMIT = 3000

NEVER_FOR_SUB = {
    "delegate", "delegate_parallel", "schedule_task", "cancel_task", "list_tasks",
    "submit_plan", "remember", "create_skill_draft",
}
EXPLORE_TOOLS = {
    "list_dir", "read_file", "search_text", "search_sessions", "load_skill", "update_plan",
}

SUB_TASK_PREFIX = (
    "你是一个子 Agent，被主 Agent 派来完成一件边界清楚的子任务，看不到主对话。"
    "完成后用简洁文字汇报结论并写清依据（读了什么、看到什么），不要贴大段原文；"
    "做不到就直接说明原因。\n任务："
)


def _toolset(runtime: PersonalRuntime, kind: str) -> set[str]:
    available = {spec.name for spec in runtime.registry.specs}
    if kind == "explore":
        return EXPLORE_TOOLS & available
    return available - NEVER_FOR_SUB


def _run_sub(runtime: PersonalRuntime, task: str, kind: str, parent: str, idx: int | None) -> str:
    tag = f"子Agent{idx if idx is not None else ''}"
    sub_session = f"{parent}/sub-{uuid.uuid4().hex[:6]}"
    inherits_plan = runtime.in_plan_mode(parent)
    if inherits_plan:
        runtime.enter_plan_mode(sub_session)
    try:
        result = runtime.run(
            SUB_TASK_PREFIX + task,
            session_id=sub_session,
            tools=_toolset(runtime, kind),
        )
    except Exception as error:  # noqa: BLE001
        return f"[{tag} 出错] {type(error).__name__}: {error}"
    finally:
        if inherits_plan:
            runtime._plan_sessions.discard(sub_session)
    if len(result) > RESULT_LIMIT:
        result = result[:RESULT_LIMIT] + "\n...（子 Agent 的结论过长，已截断）"
    return f"[{tag} 的结论]\n{result}"


def _parent_session() -> str | None:
    return _CURRENT_SESSION.get()


def make_subagent_tools(runtime: PersonalRuntime) -> list[ToolWrapper]:
    """Create the delegation tools bound to one runtime."""

    @tool
    def delegate(task: str, kind: str = "explore") -> str:
        """Delegate one bounded subtask to a sub-agent with its own context.

        kind=explore allows read-only investigation; kind=worker additionally
        allows writes and shell, each still approved by the user. Write the
        goal, scope, and desired report format in task; only the conclusion
        returns to this conversation.
        """
        if kind not in {"explore", "worker"}:
            return "Error: kind must be explore or worker"
        parent = _parent_session()
        if parent is None:
            return "Error: delegate 只能在 Agent 运行中使用"
        return _run_sub(runtime, task, kind, parent, None)

    @tool
    def delegate_parallel(tasks: list) -> str:
        """Run up to 3 independent read-only investigations in parallel.

        tasks is a list of self-contained investigation briefings; each
        sub-agent returns its own conclusion. Read-only, no writes.
        """
        parent = _parent_session()
        if parent is None:
            return "Error: delegate_parallel 只能在 Agent 运行中使用"
        if not tasks:
            return "Error: tasks 不能为空"
        if len(tasks) > MAX_PARALLEL:
            return f"Error: 一次最多 {MAX_PARALLEL} 个子 Agent，你给了 {len(tasks)} 个"
        with ThreadPoolExecutor(MAX_PARALLEL) as pool:
            futures = [
                pool.submit(_run_sub, runtime, task, "explore", parent, index + 1)
                for index, task in enumerate(tasks)
            ]
            return "\n\n".join(future.result() for future in futures)

    return [delegate, delegate_parallel]
