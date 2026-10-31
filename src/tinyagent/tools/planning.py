"""Planning tools: a step list and the approval-gated plan-mode exit."""

from __future__ import annotations

from ..core.tools import ToolWrapper, tool

STATUS = {"pending": "[ ]", "in_progress": "[→]", "completed": "[x]"}
PLAN_MARK = "[plan]"
OLD_PLAN = "[plan] 这是旧版计划，已被后面的版本取代"

PLAN_MODE_PROMPT = (
    "[计划模式] 先调查，不要修改任何东西（有副作用的工具会被拒绝）。"
    "想清楚之后调用 submit_plan 提交分步骤的计划，等用户批准后再执行。\n任务："
)


def make_plan_tools() -> list[ToolWrapper]:
    """Create the step-list tool and the plan-submission tool."""

    @tool
    def update_plan(steps: list) -> str:
        """Record or update the step plan for the current task.

        Pass the complete steps list every time; each item is an object with
        step (str) and status (pending | in_progress | completed); at most one
        step may be in_progress. Start a plan before tasks longer than 3 steps.
        """
        if not steps:
            return "Error: steps must not be empty"
        bad = [
            s for s in steps
            if not isinstance(s, dict)
            or s.get("status") not in STATUS
            or not str(s.get("step", "")).strip()
        ]
        if bad:
            return f"Error: invalid step format {bad!r}; status must be one of {sorted(STATUS)}"
        if sum(s["status"] == "in_progress" for s in steps) > 1:
            return "Error: at most one step may be in_progress"
        done = sum(s["status"] == "completed" for s in steps)
        lines = [f"{STATUS[s['status']]} {s['step']}" for s in steps]
        return f"{PLAN_MARK} 当前计划（{done}/{len(steps)} 完成）\n" + "\n".join(lines)

    @tool
    def submit_plan(plan: str) -> str:
        """Submit the complete execution plan to leave plan mode.

        The user reviews the full plan text before approving. After approval,
        execute the plan; explain before any deviation from it.
        """
        if not plan.strip():
            return "Error: plan must not be empty"
        return "用户批准了计划。已退出计划模式，现在按计划执行；如需偏离计划，先说明原因再操作。"

    return [update_plan, submit_plan]
