"""Tests for plan tools, plan-mode enforcement, and plan folding."""

from __future__ import annotations

from pathlib import Path

from tests.conftest import ScriptedModel
from tinyagent.agent import ContextBuilder
from tinyagent.agent.types import EventRecord
from tinyagent.core.tools import ToolRegistry
from tinyagent.core.types import ModelReply, ToolCallReply
from tinyagent.execution import LocalExecutionBackend
from tinyagent.runtime import PersonalRuntime, SQLiteStore
from tinyagent.runtime.approvals import CLIApprover, render_call
from tinyagent.tools import make_plan_tools, make_workspace_tools


def _event(event_type: str, data: dict, seq: int) -> EventRecord:
    return EventRecord(
        event_id=f"e{seq}",
        parent_event_id=f"e{seq - 1}" if seq > 1 else None,
        session_id="s",
        run_id="r",
        seq=seq,
        type=event_type,
        data=data,
        ts="2026-10-30T00:00:00+00:00",
        schema_version=1,
    )


def _tool_events(contents: list[str]) -> list[EventRecord]:
    events = []
    for index, content in enumerate(contents, 1):
        call_id = f"c{index}"
        events.extend([
            _event("assistant_reply", {"text": "", "tool_calls": [{"id": call_id}]}, index * 2 - 1),
            _event("tool_result", {"call_id": call_id, "content": content}, index * 2),
        ])
    return events


def _runtime(workspace: Path, model: ScriptedModel, answers) -> PersonalRuntime:
    return PersonalRuntime(
        store=SQLiteStore(workspace / "state.db"),
        model=model,
        registry=ToolRegistry([
            *make_workspace_tools(workspace, LocalExecutionBackend()),
            *make_plan_tools(),
        ]),
        approver=CLIApprover(
            {"list_dir", "read_file", "search_text", "update_plan"},
            ask=lambda _p: next(answers),
            interactive=True,
        ),
    )


def test_update_plan_validation_and_rendering():
    registry = ToolRegistry(make_plan_tools())
    assert "status" in registry.call(
        "update_plan", steps=[{"step": "调查", "status": "nope"}]
    )
    assert "in_progress" in registry.call(
        "update_plan",
        steps=[
            {"step": "a", "status": "in_progress"},
            {"step": "b", "status": "in_progress"},
        ],
    )
    result = registry.call(
        "update_plan",
        steps=[
            {"step": "调查", "status": "completed"},
            {"step": "修改", "status": "pending"},
        ],
    )
    assert result.startswith("[plan] 当前计划（1/2 完成）")
    assert "[x] 调查" in result
    assert "[ ] 修改" in result


def test_render_call_shows_full_plan():
    rendered = render_call("submit_plan", {"plan": "1. 改 a.py\n2. 跑测试"})
    assert "1. 改 a.py" in rendered
    assert "2. 跑测试" in rendered


def test_plan_mode_blocks_writes_until_plan_approved(tmp_path: Path):
    (tmp_path / "in.txt").write_text("data", encoding="utf-8")
    answers = iter(["y", "y"])
    model = ScriptedModel([
        ModelReply(tool_calls=[ToolCallReply("c0", "read_file", '{"path":"in.txt"}')]),
        ModelReply(tool_calls=[ToolCallReply("c1", "write_file", '{"path":"out.txt","content":"v1"}')]),
        ModelReply(tool_calls=[ToolCallReply("c2", "submit_plan", '{"plan":"1. 写 out.txt"}')]),
        ModelReply(tool_calls=[ToolCallReply("c3", "write_file", '{"path":"out.txt","content":"v2"}')]),
        ModelReply(text="done"),
    ])
    runtime = _runtime(tmp_path, model, answers)
    runtime.enter_plan_mode("default")
    assert runtime.run("task", session_id="default") == "done"
    results = [
        event.data["content"]
        for event in runtime.store.session_events("default")
        if event.type == "tool_result"
    ]
    assert results[0] == "data"
    assert "计划模式" in results[1]
    assert "用户批准了计划" in results[2]
    assert (tmp_path / "out.txt").read_text(encoding="utf-8") == "v2"
    assert not runtime.in_plan_mode("default")


def test_plan_results_fold_and_survive_clearing():
    events = _tool_events([
        "[plan] 当前计划（0/1 完成）\n[ ] a",
        "[plan] 当前计划（1/1 完成）\n[x] a",
        "older",
        "new",
    ])
    view = ContextBuilder(
        soft_limit_tokens=1, hard_limit_tokens=1000, keep_recent_tool_results=1
    ).build(events, "system")
    tool_messages = [message for message in view.messages if message.role == "tool"]
    assert tool_messages[0].content == "[plan] 这是旧版计划，已被后面的版本取代"
    assert tool_messages[1].content.startswith("[plan] 当前计划（1/1")
    assert tool_messages[2].content.startswith("[旧工具结果已清理")
    assert tool_messages[3].content == "new"


def test_scheduled_runs_cannot_use_plan_tools(tmp_path: Path):
    model = ScriptedModel([
        ModelReply(tool_calls=[ToolCallReply("c1", "submit_plan", '{"plan":"x"}')]),
        ModelReply(text="ok"),
    ])
    runtime = _runtime(tmp_path, model, iter([]))
    runtime.run("check", session_id="sched", kind="scheduled")
    results = [
        event.data["content"]
        for event in runtime.store.session_events("sched")
        if event.type == "tool_result"
    ]
    assert "not preauthorized" in results[0]
