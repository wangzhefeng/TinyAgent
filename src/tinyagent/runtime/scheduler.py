"""Persistent scheduler with isolated runs and local delivery."""

from __future__ import annotations

import json
import re
import time
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from .runtime import PersonalRuntime
from .store import SQLiteStore

HEARTBEAT_OK = "HEARTBEAT_OK"
PREAUTHORIZABLE = {"write_file"}
MAX_TASKS = 20


class LocalOutbox:
    """Append local delivery records as JSONL."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, task_id: str, run_id: str, content: str) -> None:
        """Append one delivery record."""
        record = {
            "ts": datetime.now(UTC).isoformat(),
            "task_id": task_id,
            "run_id": run_id,
            "content": content,
        }
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


class Scheduler:
    """Execute due tasks with fresh sessions and limited preauthorization."""

    def __init__(self, store: SQLiteStore, runtime: PersonalRuntime, outbox: LocalOutbox) -> None:
        self.store = store
        self.runtime = runtime
        self.outbox = outbox

    def add(
        self,
        spec: str,
        prompt: str,
        deliver_to: str = "cli",
        allow: set[str] | None = None,
        kind: str = "task",
        immediate: bool = False,
    ) -> dict[str, Any]:
        """Create a task with capped preauthorization and next execution time."""
        if len(self.store.list_scheduled_tasks()) >= MAX_TASKS:
            raise ValueError(f"maximum scheduled tasks reached: {MAX_TASKS}")
        allow = allow or set()
        unsupported = allow - PREAUTHORIZABLE
        if unsupported:
            raise ValueError(f"tools cannot be preauthorized: {sorted(unsupported)}")
        if kind not in {"task", "heartbeat"}:
            raise ValueError("kind must be task or heartbeat")
        now = datetime.now(UTC)
        next_run = now if immediate else self.next_run(spec, now)
        return self.store.create_scheduled_task(
            spec, prompt, deliver_to, allow, kind, next_run.isoformat()
        )

    def run_due(self) -> list[dict[str, Any]]:
        """Run every due task once and return execution outcomes."""
        outcomes = []
        for task in self.store.due_scheduled_tasks(datetime.now(UTC).isoformat()):
            due_at = task["next_run"]
            self.store.mark_scheduled_started(
                task["id"], self.next_run(task["spec"], datetime.now(UTC)).isoformat()
            )
            if task["kind"] == "heartbeat" and not task["prompt"].strip():
                self.store.mark_scheduled_delivered(task["id"], "no-content")
                continue
            run = self.runtime.create_run(
                self._task_input(task),
                session_id=f"task-{task['id']}-{due_at}",
                idempotency_key=f"scheduled:{task['id']}:{due_at}",
                kind="scheduled",
            )
            self.store.attach_scheduled_run(task["id"], run.id)
            if task["delivered_run_id"] == run.id and run.status == "completed":
                continue
            try:
                if run.status != "completed":
                    self.store.update_run_status(run.id, "running")
                    output = self.runtime._execute(run.id, append_input=True)
                else:
                    output = run.output
                if task["kind"] == "heartbeat" and output.strip() == HEARTBEAT_OK:
                    delivered = False
                else:
                    self.outbox.append(task["id"], run.id, output)
                    delivered = True
                self.store.mark_scheduled_delivered(task["id"], run.id)
                outcomes.append({
                    "task_id": task["id"], "run_id": run.id,
                    "output": output, "delivered": delivered,
                })
            except Exception as error:  # noqa: BLE001
                self.store.mark_scheduled_error(task["id"], str(error))
                outcomes.append({
                    "task_id": task["id"], "run_id": run.id,
                    "output": str(error), "delivered": False,
                })
        return outcomes

    @staticmethod
    def _task_input(task: dict[str, Any]) -> str:
        if task["kind"] != "heartbeat":
            return task["prompt"]
        return (
            "This is an unattended routine check. If there is no meaningful update, "
            f"respond exactly {HEARTBEAT_OK}. Otherwise summarize the update with evidence.\n"
            f"Check: {task['prompt']}"
        )

    @staticmethod
    def next_run(spec: str, after: datetime) -> datetime:
        """Calculate the next run from a small every/daily specification."""
        spec = spec.strip().lower()
        match = re.fullmatch(r"every\s+(\d+)\s*([mh])", spec)
        if match:
            amount = int(match.group(1))
            delta = timedelta(minutes=amount) if match.group(2) == "m" else timedelta(hours=amount)
            if delta < timedelta(minutes=5):
                raise ValueError("minimum interval is 5 minutes")
            return after + delta
        match = re.fullmatch(r"daily\s+(\d{1,2}):(\d{2})", spec)
        if not match:
            raise ValueError("spec must be every 30m / every 2h / daily 09:00")
        hour, minute = int(match.group(1)), int(match.group(2))
        if hour > 23 or minute > 59:
            raise ValueError("invalid daily time")
        candidate = after.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return candidate if candidate > after else candidate + timedelta(days=1)


def run_daemon_loop(
    scheduler: Scheduler,
    interval: float = 30.0,
    ticks: int | None = None,
    log: Callable[[str], None] = print,
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    """Run due scheduled tasks in a loop for the CLI daemon command."""
    done = 0
    while ticks is None or done < ticks:
        for outcome in scheduler.run_due():
            summary = str(outcome["output"]).replace("\n", " ")[:200]
            log(f"[{outcome['task_id']}] delivered={outcome['delivered']} {summary}")
        sleep(interval)
        done += 1
