"""Tests for P1 context views and read-only workspace tools."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.conftest import ScriptedModel
from tinyagent.agent import ContextBuilder
from tinyagent.agent.types import EventRecord
from tinyagent.channels.cli import build_runtime
from tinyagent.core.tools import ToolRegistry
from tinyagent.runtime.approvals import CLIApprover
from tinyagent.tools import make_workspace_tools


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


def test_context_truncates_view_without_mutating_raw_events():
    raw = "x" * 200
    events = _tool_events([raw])
    view = ContextBuilder(max_tool_chars=40).build(events, "system")
    assert "省略" in view.messages[-1].content
    assert len(view.messages[-1].content) < 100
    assert events[-1].data["content"] == raw


def test_context_clears_old_tools_and_keeps_pairing():
    events = _tool_events(["old", "older", "new"])
    view = ContextBuilder(
        soft_limit_tokens=1,
        hard_limit_tokens=1000,
        keep_recent_tool_results=1,
    ).build(events, "system")
    tool_messages = [message for message in view.messages if message.role == "tool"]
    assert tool_messages[0].content.startswith("[旧工具结果已清理")
    assert tool_messages[-1].content == "new"


def test_context_rejects_orphan_tool_result():
    events = [_event("tool_result", {"call_id": "missing", "content": "x"}, 1)]
    with pytest.raises(ValueError, match="isolated tool result"):
        ContextBuilder().build(events, "system")


def test_workspace_read_search_and_path_boundary(tmp_path: Path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "note.txt").write_text("alpha\nbeta\n", encoding="utf-8")
    registry = ToolRegistry(make_workspace_tools(tmp_path))
    assert registry.call("read_file", path="docs/note.txt") == "alpha\nbeta\n"
    assert "note.txt:2:beta" in registry.call("search_text", query="beta")
    assert "docs/" in registry.call("list_dir")
    with pytest.raises(PermissionError):
        registry.call("read_file", path="../outside.txt")


def test_unknown_tool_needs_confirmation_and_fails_closed():
    approver = CLIApprover({"read_file"}, interactive=False)
    allowed, reason = approver.check("write_file", {"path": "x"})
    assert not allowed
    assert "non-interactive" in reason


def test_cli_runtime_construction(tmp_path: Path):
    model = ScriptedModel([])
    runtime = build_runtime(tmp_path, tmp_path / "state.db", model)
    assert {tool.name for tool in runtime.registry.specs} == {
        "list_dir",
        "read_file",
        "search_text",
        "fetch_url",
        "remember",
        "search_sessions",
        "load_skill",
        "create_skill_draft",
        "schedule_task",
        "list_tasks",
        "cancel_task",
    }
