"""Tests for P1 context views and read-only workspace tools."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.conftest import ScriptedModel
from tinyagent.agent import ContextBuilder
from tinyagent.agent.types import EventRecord
from tinyagent.channels.cli import build_runtime
from tinyagent.core.tools import ToolRegistry
from tinyagent.runtime.approvals import CLIApprover, render_call
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


def test_render_call_shows_real_arguments():
    assert render_call("run_shell", {"command": "ls -la"}).strip() == "$ ls -la"
    rendered = render_call("write_file", {"path": "a.txt", "content": "x" * 500})
    assert "路径：a.txt" in rendered
    assert "已截断" in rendered
    assert render_call("fetch_url", {"url": "https://e.com"}).strip() == "URL：https://e.com"
    assert "{" in render_call("list_dir", {"path": "."})


def test_approver_deny_note_and_always_allow():
    answers = iter(["n 先列出来给我看", "a", "a"])
    approver = CLIApprover(set(), ask=lambda _p: next(answers), interactive=True)
    allowed, reason = approver.check("write_file", {"path": "x", "content": "c"})
    assert not allowed
    assert "user note: 先列出来给我看" in reason
    # 第二次回答 a：批准，且 write_file 进入本次运行白名单
    assert approver.check("write_file", {"path": "y", "content": "c"}) == (
        True, "approved for the rest of this run",
    )
    # 第三次命中白名单快路径，不再触发 ask（多问一次会在末尾耗尽迭代器）
    assert approver.check("write_file", {"path": "z", "content": "c"}) == (
        True, "approved for the rest of this run",
    )
    # a 对非 REMEMBERABLE 工具不生效，明确拒绝
    allowed, reason = approver.check("fetch_url", {"url": "https://e.com"})
    assert not allowed
    assert "always-allow" in reason


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
        "update_plan",
        "submit_plan",
        "delegate",
        "delegate_parallel",
        "schedule_task",
        "list_tasks",
        "cancel_task",
    }


def test_project_notes_in_system_prompt():
    events = [_event("user_input", {"text": "hi"}, 1)]
    view = ContextBuilder(project_notes="项目规范：不要提交密钥").build(events, "system")
    assert "## 项目说明（来自工作区 AGENTS.md）" in view.messages[0].content
    assert "不要提交密钥" in view.messages[0].content


def test_project_notes_truncated_to_cap():
    notes = "x" * 4000
    view = ContextBuilder(project_notes=notes).build(
        [_event("user_input", {"text": "hi"}, 1)], "system"
    )
    assert "x" * 3000 in view.messages[0].content
    assert "x" * 3001 not in view.messages[0].content


def test_skill_results_survive_clearing():
    events = _tool_events(["[skill] demo\n长技能正文", "older", "new"])
    view = ContextBuilder(
        soft_limit_tokens=1,
        hard_limit_tokens=1000,
        keep_recent_tool_results=1,
    ).build(events, "system")
    tool_messages = [message for message in view.messages if message.role == "tool"]
    assert tool_messages[0].content.startswith("[skill] demo")
    assert tool_messages[1].content.startswith("[旧工具结果已清理")
    assert tool_messages[2].content == "new"


def test_build_runtime_reads_workspace_agents_md(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("# 项目说明\n- 保持只读", encoding="utf-8")
    runtime = build_runtime(tmp_path, tmp_path / "state.db", ScriptedModel([]))
    assert "保持只读" in runtime.context.project_notes
