"""Tests for P4 scheduling, isolated runs, and unattended permissions."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from tests.conftest import ScriptedModel
from tinyagent.channels.cli import main
from tinyagent.core.tools import ToolRegistry
from tinyagent.core.types import ModelReply
from tinyagent.execution import LocalExecutionBackend
from tinyagent.memory import MemoryManager
from tinyagent.runtime import LocalOutbox, PersonalRuntime, Scheduler, SQLiteStore
from tinyagent.skills import SkillManager
from tinyagent.tools import make_learning_tools, make_workspace_tools


def _runtime(workspace: Path, model: ScriptedModel):
    store = SQLiteStore(workspace / "state.db")
    memory = MemoryManager(workspace)
    skills = SkillManager(workspace)
    runtime = PersonalRuntime(
        store=store,
        model=model,
        registry=ToolRegistry(make_workspace_tools(workspace, LocalExecutionBackend())),
        memory=memory,
        skills=skills,
    )
    registry = runtime.registry
    for learning_tool in make_learning_tools(memory, skills, store):
        registry.add(learning_tool)
    scheduler = Scheduler(store, runtime, LocalOutbox(workspace / "deliveries.jsonl"))
    runtime.scheduler = scheduler
    return runtime, scheduler


def test_next_run_rules_and_preauthorization_cap(tmp_path: Path):
    _, scheduler = _runtime(tmp_path, ScriptedModel([]))
    now = datetime(2026, 10, 30, 10, 0, tzinfo=UTC)
    assert scheduler.next_run("every 30m", now).minute == 30
    assert scheduler.next_run("daily 09:00", now).day == 31
    with pytest.raises(ValueError, match="minimum interval"):
        scheduler.next_run("every 1m", now)
    with pytest.raises(ValueError, match="cannot be preauthorized"):
        scheduler.add("every 30m", "task", allow={"run_shell"})


def test_due_task_uses_fresh_scheduled_session_and_delivers_once(tmp_path: Path):
    model = ScriptedModel([ModelReply(text="scheduled answer")])
    runtime, scheduler = _runtime(tmp_path, model)
    scheduler.add("every 5m", "do work", immediate=True)
    outcomes = scheduler.run_due()
    assert outcomes[0]["delivered"] is True
    run = runtime.store.get_run(outcomes[0]["run_id"])
    assert run.kind == "scheduled"
    assert run.session_id != "default"
    delivery = json.loads((tmp_path / "deliveries.jsonl").read_text().splitlines()[0])
    assert delivery["content"] == "scheduled answer"
    assert scheduler.run_due() == []


def test_heartbeat_ok_is_silent_but_usage_is_recorded(tmp_path: Path):
    model = ScriptedModel([ModelReply(text="HEARTBEAT_OK")])
    runtime, scheduler = _runtime(tmp_path, model)
    scheduler.add("every 5m", "check for updates", kind="heartbeat", immediate=True)
    outcomes = scheduler.run_due()
    assert outcomes[0]["delivered"] is False
    assert not (tmp_path / "deliveries.jsonl").exists()
    usage = runtime.store.get_run(outcomes[0]["run_id"]).usage
    assert usage["api_calls"] == 1


def test_unattended_permissions_enforce_preauthorization(tmp_path: Path):
    (tmp_path / "note.txt").write_text("note", encoding="utf-8")
    runtime, scheduler = _runtime(tmp_path, ScriptedModel([]))
    task = scheduler.add("every 5m", "task", allow={"write_file"}, immediate=True)
    run = runtime.create_run("task", session_id="task-test", kind="scheduled")
    runtime.store.attach_scheduled_run(task["id"], run.id)
    assert runtime._call_tool(run.id, "r1", "read_file", {"path": "note.txt"}) == "note"
    assert "Wrote" in runtime._call_tool(run.id, "w1", "write_file", {"path": "new.txt", "content": "x"})
    for name, arguments in [
        ("run_shell", {"command": "uv run pytest"}),
        ("remember", {"action": "add", "text": "x"}),
        ("create_skill_draft", {"name": "x", "description": "x", "body": "x"}),
        ("schedule_task", {"spec": "every 30m", "prompt": "nested"}),
    ]:
        result = runtime._call_tool(run.id, name, name, arguments)
        assert "not preauthorized" in result


def test_cli_schedule_add_list_and_run(tmp_path: Path, capsys: pytest.CaptureFixture):
    model = ScriptedModel([ModelReply(text="done")])
    state = tmp_path / "cli.db"
    assert main([
        "--workspace", str(tmp_path), "--state", str(state),
        "schedule", "add", "every 5m", "do work", "--immediate",
    ], model=model) == 0
    task = json.loads(capsys.readouterr().out)
    assert task["kind"] == "task"
    assert main(["--state", str(state), "schedule", "list"], model=model) == 0
    assert task["id"] in capsys.readouterr().out
    assert main(["--state", str(state), "schedule", "run"], model=model) == 0
    outcome = json.loads(capsys.readouterr().out)
    assert outcome[0]["delivered"] is True
