"""Offline end-to-end tests for the P1 personal runtime."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.conftest import ScriptedModel
from tinyagent.channels.cli import main
from tinyagent.core.tools import ToolRegistry
from tinyagent.core.types import ModelReply, ToolCallReply
from tinyagent.runtime import PersonalRuntime, SQLiteStore
from tinyagent.tools import make_workspace_tools


def _runtime(workspace: Path, model: ScriptedModel, state: Path | None = None) -> PersonalRuntime:
    return PersonalRuntime(
        store=SQLiteStore(state or workspace / "state.db"),
        model=model,
        registry=ToolRegistry(make_workspace_tools(workspace)),
    )


def test_runtime_executes_tool_and_persists_raw_events(tmp_path: Path):
    (tmp_path / "note.txt").write_text("concrete evidence", encoding="utf-8")
    model = ScriptedModel([
        ModelReply(tool_calls=[ToolCallReply("c1", "read_file", '{"path":"note.txt"}')]),
        ModelReply(text="The file contains concrete evidence."),
    ])
    runtime = _runtime(tmp_path, model)
    answer = runtime.run("Read note.txt", idempotency_key="read-1")
    assert "concrete evidence" in answer
    run = runtime.store.get_run(
        runtime.store.session_events("default")[0].run_id
    )
    assert run.status == "completed"
    assert run.usage["api_calls"] == 2
    events = runtime.store.list_events(run.id)
    assert [event.type for event in events] == [
        "run_start",
        "user_input",
        "assistant_reply",
        "tool_call",
        "tool_result",
        "assistant_reply",
        "run_end",
    ]
    assert events[4].data["content"] == "concrete evidence"
    exported = runtime.store.export_session("default").splitlines()
    assert len(exported) == len(events)
    assert all(json.loads(line)["schema_version"] == 1 for line in exported)


def test_idempotency_reuses_result_and_rejects_different_input(tmp_path: Path):
    model = ScriptedModel([ModelReply(text="done")])
    runtime = _runtime(tmp_path, model)
    assert runtime.run("task", idempotency_key="same") == "done"
    assert runtime.run("task", idempotency_key="same") == "done"
    assert len(model.calls) == 1
    with pytest.raises(ValueError, match="different input"):
        runtime.run("different", idempotency_key="same")


def test_second_run_loads_previous_session_history(tmp_path: Path):
    model = ScriptedModel([ModelReply(text="first"), ModelReply(text="second")])
    runtime = _runtime(tmp_path, model)
    runtime.run("first question")
    runtime.run("second question")
    first_call_size = model.calls[0]["n_messages"]
    second_call_size = model.calls[1]["n_messages"]
    assert second_call_size > first_call_size


def test_resume_completed_run_does_not_call_model_again(tmp_path: Path):
    model = ScriptedModel([ModelReply(text="done")])
    runtime = _runtime(tmp_path, model)
    runtime.run("task", idempotency_key="stable")
    run_id = runtime.store.session_events("default")[0].run_id
    assert runtime.resume_run(run_id) == "done"
    assert len(model.calls) == 1


def test_resume_rejects_unanswered_tool_call(tmp_path: Path):
    runtime = _runtime(tmp_path, ScriptedModel([]))
    run = runtime.create_run("task")
    runtime.store.append_event(
        run.id,
        "assistant_reply",
        {"text": "", "tool_calls": [{"id": "pending"}]},
    )
    runtime.store.update_run_status(run.id, "running")
    runtime.store.update_run_status(run.id, "failed", error="interrupted")
    with pytest.raises(RuntimeError, match="pending tool calls"):
        runtime.resume_run(run.id)


def test_cancel_persists_terminal_status(tmp_path: Path):
    runtime = _runtime(tmp_path, ScriptedModel([]))
    run = runtime.create_run("task")
    runtime.store.update_run_status(run.id, "running")
    runtime.cancel_run(run.id)
    assert runtime.store.get_run(run.id).status == "cancelled"


def test_unknown_tool_is_denied_without_crashing(tmp_path: Path):
    model = ScriptedModel([
        ModelReply(tool_calls=[ToolCallReply("bad", "write_file", '{"path":"x"}')]),
        ModelReply(text="I cannot write files."),
    ])
    runtime = _runtime(tmp_path, model)
    assert runtime.run("write something") == "I cannot write files."
    results = [
        event for event in runtime.store.session_events("default")
        if event.type == "tool_result"
    ]
    assert "Permission denied" in results[0].data["content"]
    assert not (tmp_path / "x").exists()


def test_cli_run_and_export(tmp_path: Path, capsys: pytest.CaptureFixture):
    model = ScriptedModel([ModelReply(text="offline answer")])
    state = tmp_path / "cli.db"
    assert main([
        "--workspace", str(tmp_path),
        "--state", str(state),
        "run", "hello",
    ], model=model) == 0
    assert "offline answer" in capsys.readouterr().out
    assert main(["--state", str(state), "export"], model=model) == 0
    exported = capsys.readouterr().out.strip().splitlines()
    assert any(json.loads(line)["type"] == "run_end" for line in exported)
