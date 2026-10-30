"""Tools for creating, listing, and cancelling scheduled tasks."""

from __future__ import annotations

from ..core.tools import ToolWrapper, tool
from ..runtime.scheduler import Scheduler


def make_scheduler_tools(scheduler: Scheduler) -> list[ToolWrapper]:
    """Create scheduler tools for interactive use only."""
    @tool
    def schedule_task(spec: str, prompt: str, kind: str = "task", allow: str = "") -> str:
        """Create a scheduled task with limited preauthorization.

        spec supports every 30m / every 2h / daily 09:00. kind may be task or heartbeat.
        allow is a comma-separated subset of write_file; shell is never preauthorized.
        """
        allowed = {item.strip() for item in allow.split(",") if item.strip()}
        task = scheduler.add(spec, prompt, allow=allowed, kind=kind)
        return f"Created task {task['id']} at {task['next_run']} with allow={allow or '(none)'}"

    @tool
    def list_tasks() -> str:
        """List active scheduled tasks and their preauthorization."""
        tasks = scheduler.store.list_scheduled_tasks()
        if not tasks:
            return "No scheduled tasks"
        return "\n".join(
            f"{task['id']} {task['spec']} next={task['next_run']} kind={task['kind']} "
            f"allow={task['allow_json']} prompt={task['prompt'][:80]}"
            for task in tasks
        )

    @tool
    def cancel_task(task_id: str) -> str:
        """Cancel a scheduled task owned by the CLI user."""
        cancelled = scheduler.store.cancel_scheduled_task(task_id, "cli")
        return f"Cancelled {task_id}" if cancelled else f"Error: task not found: {task_id}"

    return [schedule_task, list_tasks, cancel_task]
