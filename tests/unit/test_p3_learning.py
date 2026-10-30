"""Tests for P3 memory, FTS5 recall, skills, and compaction."""

from __future__ import annotations

from pathlib import Path

from tests.conftest import ScriptedModel
from tinyagent.agent import ContextBuilder
from tinyagent.core.tools import ToolRegistry
from tinyagent.core.types import ModelReply, ToolCallReply
from tinyagent.memory import MemoryManager
from tinyagent.runtime import PersonalRuntime, SQLiteStore
from tinyagent.skills import SkillManager
from tinyagent.tools import make_learning_tools, make_workspace_tools


def _runtime(workspace: Path, model: ScriptedModel, context: ContextBuilder | None = None):
    store = SQLiteStore(workspace / "state.db")
    memory = MemoryManager(workspace)
    skills = SkillManager(workspace)
    registry = ToolRegistry([
        *make_workspace_tools(workspace),
        *make_learning_tools(memory, skills, store),
    ])
    return PersonalRuntime(
        store=store,
        model=model,
        registry=registry,
        memory=memory,
        skills=skills,
        context=context,
    )


def test_memory_add_replace_remove_and_snapshot(tmp_path: Path):
    memory = MemoryManager(tmp_path, user_limit=100)
    assert "Updated USER.md" in memory.remember("add", "prefer concise answers", scope="user")
    assert "concise" in memory.snapshot()["user"]
    memory.remember("replace", old="concise", text="prefer evidence", scope="user")
    assert "evidence" in memory.snapshot()["user"]
    memory.remember("remove", old="evidence", scope="user")
    assert memory.snapshot()["user"] == ""


def test_memory_limit_does_not_write(tmp_path: Path):
    memory = MemoryManager(tmp_path, memory_limit=10)
    result = memory.remember("add", "this is far too long")
    assert result.startswith("Error")
    assert not memory.memory_path.exists()


def test_skill_draft_requires_approval(tmp_path: Path):
    skills = SkillManager(tmp_path)
    skills.create_draft("weekly-report", "Write a cited weekly report", "Collect evidence first")
    assert "not found" in skills.load("weekly-report")
    skills.approve_draft("weekly-report")
    assert "Collect evidence first" in skills.load("weekly-report")
    assert "weekly-report" in skills.catalog()


def test_fts_returns_source_snippets(tmp_path: Path):
    store = SQLiteStore(tmp_path / "state.db")
    run = store.create_run("s1", "Redis timeout happened")
    store.append_event(run.id, "user_input", {"text": "Redis timeout happened"})
    store.append_event(run.id, "assistant_reply", {"text": "Increase the pool to 50"})
    hits = store.search_sessions("Redis pool")
    assert hits[0]["event_id"]
    assert "Increase the pool" in hits[0]["snippet"]


def test_memory_write_is_audited_and_snapshot_frozen(tmp_path: Path):
    memory = MemoryManager(tmp_path)
    memory.remember("add", "prefer short answers", scope="user")
    model = ScriptedModel([
        ModelReply(tool_calls=[ToolCallReply(
            "m1", "remember", '{"action":"add","text":"use uv","scope":"user"}',
        )]),
        ModelReply(text="noted"),
        ModelReply(text="second session ready"),
    ])
    runtime = _runtime(tmp_path, model)
    runtime.run("remember my tooling preference")
    state = runtime.store.get_session_state("default")
    assert "short answers" in state["prompt_snapshot"]["memory"]["user"]
    assert "use uv" not in state["prompt_snapshot"]["memory"]["user"]
    assert any(event.type == "memory_write" for event in runtime.store.session_events("default"))

    runtime.run("new session", session_id="second")
    second = runtime.store.get_session_state("second")
    assert "use uv" in second["prompt_snapshot"]["memory"]["user"]


def test_scheduled_run_cannot_write_memory(tmp_path: Path):
    runtime = _runtime(tmp_path, ScriptedModel([]))
    run = runtime.create_run("task", kind="scheduled")
    result = runtime._call_tool(run.id, "m1", "remember", {"action": "add", "text": "x"})
    assert "not preauthorized" in result
    assert not any(event.type == "memory_write" for event in runtime.store.list_events(run.id))


def test_compaction_preserves_memory_and_raw_events(tmp_path: Path):
    context = ContextBuilder(soft_limit_tokens=1, hard_limit_tokens=2)
    model = ScriptedModel([
        ModelReply(text="first answer"),
        ModelReply(tool_calls=[ToolCallReply(
            "m1", "remember", '{"action":"add","text":"keep this convention","scope":"memory"}',
        )]),
        ModelReply(text="summary of earlier work"),
        ModelReply(text="second answer"),
    ])
    runtime = _runtime(tmp_path, model, context)
    runtime.context = ContextBuilder()
    runtime.run("first task")
    runtime.context = context
    assert runtime.run("second task") == "second answer"
    events = runtime.store.session_events("default")
    assert any(event.type == "memory_write" for event in events)
    assert any(event.type == "compaction" for event in events)
    artifact = runtime.store.latest_context_artifact("default", "compaction")
    assert artifact["content"] == "summary of earlier work"
    assert any(event.type == "user_input" for event in events)


def test_single_long_turn_is_not_force_compacted(tmp_path: Path):
    context = ContextBuilder(soft_limit_tokens=1, hard_limit_tokens=2)
    model = ScriptedModel([ModelReply(text="final")])
    runtime = _runtime(tmp_path, model, context)
    assert runtime.run("one long task") == "final"
    assert runtime.store.latest_context_artifact("default", "compaction") is None
