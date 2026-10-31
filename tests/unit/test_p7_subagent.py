"""Tests for sub-agent delegation, toolsets, isolation, and inheritance."""

from __future__ import annotations

from pathlib import Path

from tests.conftest import ScriptedModel
from tinyagent.core.tools import ToolRegistry
from tinyagent.core.types import ModelReply, ToolCallReply
from tinyagent.execution import LocalExecutionBackend
from tinyagent.runtime import PersonalRuntime, SQLiteStore
from tinyagent.runtime.approvals import CLIApprover
from tinyagent.tools import make_subagent_tools, make_workspace_tools


def _runtime(workspace: Path, model: ScriptedModel, answers) -> PersonalRuntime:
    runtime = PersonalRuntime(
        store=SQLiteStore(workspace / "state.db"),
        model=model,
        registry=ToolRegistry(make_workspace_tools(workspace, LocalExecutionBackend())),
        approver=CLIApprover(
            {"list_dir", "read_file", "search_text", "delegate", "delegate_parallel"},
            ask=lambda _p: next(answers),
            interactive=True,
        ),
    )
    for subagent_tool in make_subagent_tools(runtime):
        runtime.registry.add(subagent_tool)
    return runtime


def _delegate_call(call_id: str, arguments: str) -> ModelReply:
    return ModelReply(tool_calls=[ToolCallReply(call_id, "delegate", arguments)])


def _parent_results(runtime: PersonalRuntime) -> list[str]:
    return [
        event.data["content"]
        for event in runtime.store.session_events("default")
        if event.type == "tool_result"
    ]


def test_explore_subagent_returns_conclusion_without_polluting_parent(tmp_path: Path):
    (tmp_path / "a.txt").write_text("alpha", encoding="utf-8")
    (tmp_path / "b.txt").write_text("beta", encoding="utf-8")
    model = ScriptedModel([
        _delegate_call("c1", '{"task":"读 a.txt 和 b.txt 并汇报内容"}'),
        ModelReply(tool_calls=[ToolCallReply("s1", "read_file", '{"path":"a.txt"}')]),
        ModelReply(tool_calls=[ToolCallReply("s2", "read_file", '{"path":"b.txt"}')]),
        ModelReply(text="a.txt=alpha；b.txt=beta"),
        ModelReply(text="汇总完成"),
    ])
    runtime = _runtime(tmp_path, model, iter([]))
    assert runtime.run("调查两个文件") == "汇总完成"
    results = _parent_results(runtime)
    assert len(results) == 1
    assert "[子Agent 的结论]" in results[0]
    assert "alpha" in results[0] and "beta" in results[0]
    user_inputs = [
        event for event in runtime.store.session_events("default")
        if event.type == "user_input"
    ]
    assert len(user_inputs) == 1


def test_explore_toolset_blocks_writes(tmp_path: Path):
    model = ScriptedModel([
        _delegate_call("c1", '{"task":"写一个文件"}'),
        ModelReply(tool_calls=[ToolCallReply("s1", "write_file", '{"path":"x.txt","content":"x"}')]),
        ModelReply(text="写入被拒：当前运行不能使用工具 write_file"),
        ModelReply(text="结束"),
    ])
    runtime = _runtime(tmp_path, model, iter([]))
    runtime.run("试试写")
    assert "不能使用工具 write_file" in _parent_results(runtime)[0]
    assert not (tmp_path / "x.txt").exists()


def test_worker_write_inherits_approval(tmp_path: Path):
    model = ScriptedModel([
        _delegate_call("c1", '{"task":"写 out.txt","kind":"worker"}'),
        ModelReply(tool_calls=[ToolCallReply("s1", "write_file", '{"path":"out.txt","content":"v"}')]),
        ModelReply(text="已写入"),
        ModelReply(text="结束"),
    ])
    runtime = _runtime(tmp_path, model, iter(["y"]))
    runtime.run("派活")
    assert (tmp_path / "out.txt").read_text(encoding="utf-8") == "v"
    assert "已写入" in _parent_results(runtime)[0]


def test_parallel_explore_runs_all_briefings(tmp_path: Path):
    (tmp_path / "a.txt").write_text("alpha", encoding="utf-8")
    model = ScriptedModel([
        ModelReply(tool_calls=[ToolCallReply(
            "c1", "delegate_parallel",
            '{"tasks":["查一","查二","查三"]}',
        )]),
        ModelReply(text="结论一"),
        ModelReply(text="结论二"),
        ModelReply(text="结论三"),
        ModelReply(text="结束"),
    ])
    runtime = _runtime(tmp_path, model, iter([]))
    runtime.run("并行查")
    result = _parent_results(runtime)[0]
    for part in ("结论一", "结论二", "结论三"):
        assert part in result
    model = ScriptedModel([
        ModelReply(tool_calls=[ToolCallReply(
            "c1", "delegate_parallel",
            '{"tasks":["1","2","3","4"]}',
        )]),
        ModelReply(text="结束"),
    ])
    runtime = _runtime(tmp_path / "second", model, iter([]))
    runtime.run("超量")
    assert "最多 3 个" in _parent_results(runtime)[0]


def test_scheduled_runs_cannot_delegate(tmp_path: Path):
    model = ScriptedModel([
        _delegate_call("c1", '{"task":"查点东西"}'),
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


def test_plan_mode_inherited_by_worker_subagent(tmp_path: Path):
    model = ScriptedModel([
        _delegate_call("c1", '{"task":"写点东西","kind":"worker"}'),
        ModelReply(tool_calls=[ToolCallReply("s1", "write_file", '{"path":"p.txt","content":"x"}')]),
        ModelReply(text="计划模式写不了"),
        ModelReply(text="结束"),
    ])
    runtime = _runtime(tmp_path, model, iter([]))
    runtime.enter_plan_mode("default")
    runtime.run("计划着来")
    assert "计划模式" in _parent_results(runtime)[0]
    assert not (tmp_path / "p.txt").exists()
    assert runtime.in_plan_mode("default")
