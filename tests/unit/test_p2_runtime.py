"""Tests for P2 runtime safety, writable tools, and usage accounting."""

from __future__ import annotations

from pathlib import Path

from tests.conftest import ScriptedModel
from tinyagent.channels.cli import build_runtime
from tinyagent.core.tools import ToolRegistry
from tinyagent.core.types import ModelReply, ToolCallReply
from tinyagent.execution import LocalExecutionBackend
from tinyagent.runtime import PersonalRuntime, SQLiteStore
from tinyagent.runtime.approvals import CLIApprover
from tinyagent.tools import make_workspace_tools


def _writable_runtime(workspace: Path, model: ScriptedModel, interactive: bool = True) -> PersonalRuntime:
    return PersonalRuntime(
        store=SQLiteStore(workspace / "state.db"),
        model=model,
        registry=ToolRegistry(make_workspace_tools(workspace, LocalExecutionBackend())),
        approver=CLIApprover(
            {"list_dir", "read_file", "search_text"},
            ask=lambda _prompt: "y",
            interactive=interactive,
        ),
    )


def _broken_fixture(workspace: Path) -> None:
    (workspace / "order.py").write_text(
        "def total(prices, discount):\n    return sum(prices) * (1 + discount)\n",
        encoding="utf-8",
    )
    (workspace / "config.txt").write_text("default tax rate: 0.2\n", encoding="utf-8")
    (workspace / "test_order.py").write_text(
        "from order import total\n\n"
        "def test_total():\n"
        "    assert total([100, 50], 0.1) == 135\n",
        encoding="utf-8",
    )


def test_writable_agent_edits_and_runs_checks(tmp_path: Path):
    _broken_fixture(tmp_path)
    model = ScriptedModel([
        ModelReply(tool_calls=[ToolCallReply(
            "c1", "edit_file",
            '{"path":"order.py","old":"(1 + discount)","new":"(1 - discount)"}',
        )]),
        ModelReply(tool_calls=[ToolCallReply(
            "c2", "edit_file",
            '{"path":"config.txt","old":"0.2","new":"0.1"}',
        )]),
        ModelReply(tool_calls=[ToolCallReply("c3", "run_shell", '{"command":"python -m pytest -q"}')]),
        ModelReply(text="Fixed and verified."),
    ])
    runtime = _writable_runtime(tmp_path, model)
    assert runtime.run("repair") == "Fixed and verified."
    assert "(1 - discount)" in (tmp_path / "order.py").read_text()
    assert "0.1" in (tmp_path / "config.txt").read_text()
    events = runtime.store.session_events("default")
    assert any(event.type == "approval_resolved" for event in events)
    shell_results = [
        event for event in events
        if event.type == "tool_result" and "[exit 0]" in event.data.get("content", "")
    ]
    assert shell_results


def test_write_is_denied_in_noninteractive_mode(tmp_path: Path):
    model = ScriptedModel([
        ModelReply(tool_calls=[ToolCallReply("c1", "write_file", '{"path":"x.txt","content":"x"}')]),
        ModelReply(text="I cannot write without approval."),
    ])
    runtime = _writable_runtime(tmp_path, model, interactive=False)
    assert "cannot write" in runtime.run("write")
    assert not (tmp_path / "x.txt").exists()


def test_real_usage_is_accumulated(tmp_path: Path):
    model = ScriptedModel([
        ModelReply(
            tool_calls=[ToolCallReply("c1", "read_file", '{"path":"note.txt"}')],
            usage={"input_tokens": 10, "output_tokens": 2, "total_tokens": 12},
        ),
        ModelReply(
            text="done",
            usage={"input_tokens": 20, "output_tokens": 4, "total_tokens": 24},
        ),
    ])
    (tmp_path / "note.txt").write_text("note", encoding="utf-8")
    runtime = _writable_runtime(tmp_path, model)
    runtime.run("read")
    run_id = runtime.store.session_events("default")[0].run_id
    usage = runtime.store.get_run(run_id).usage
    assert usage["input_tokens"] == 30
    assert usage["output_tokens"] == 6
    assert usage["total_tokens"] == 36
    assert usage["api_calls"] == 2
    assert not usage["estimated"]


def test_cli_writable_opt_in_keeps_read_tools_safe(tmp_path: Path):
    model = ScriptedModel([])
    runtime = build_runtime(
        tmp_path,
        tmp_path / "state.db",
        model,
        writable=True,
        auto_approve=True,
    )
    assert {"write_file", "edit_file", "run_shell"}.issubset(
        {tool.name for tool in runtime.registry.specs}
    )
    assert runtime.approver.safe_tools == {
        "list_dir",
        "read_file",
        "search_text",
        "remember",
        "search_sessions",
        "load_skill",
        "list_tasks",
    }
