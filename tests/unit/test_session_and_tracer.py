"""Tests for FileSessionStore and JsonlTracer round-trips."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "packages" / "tinyagent-core" / "src"))

from tinyagent.core.session import FileSessionStore  # noqa: E402
from tinyagent.core.tracer import JsonlTracer  # noqa: E402
from tinyagent.core.types import Message  # noqa: E402


def test_session_messages_roundtrip(tmp_path: Path):
    store = FileSessionStore(tmp_path)
    store.append_message("s1", Message("user", "你好"))
    store.append_message("s1", Message("assistant", "在的"))
    loaded = store.load_messages("s1")
    assert [m.role for m in loaded] == ["user", "assistant"]
    assert loaded[0].content == "你好"
    assert store.load_messages("missing") == []


def test_session_state_roundtrip(tmp_path: Path):
    store = FileSessionStore(tmp_path)
    assert store.load_state("s1") == {}
    store.save_state("s1", {"cursor": 3, "tags": ["a", "b"]})
    assert store.load_state("s1") == {"cursor": 3, "tags": ["a", "b"]}


def test_tracer_writes_jsonl_events(tmp_path: Path):
    tracer = JsonlTracer(run_id="t1", root=tmp_path)
    tracer.emit("run_start", {"question": "q"})
    tracer.emit("run_end", {"final": True})
    lines = (tmp_path / "t1.jsonl").read_text(encoding="utf-8").splitlines()
    events = [json.loads(x) for x in lines]
    assert [e["event"] for e in events] == ["run_start", "run_end"]
    assert events[0]["data"]["question"] == "q"
    assert all("ts" in e for e in events)


def test_message_tool_fields_roundtrip():
    m = Message("tool", "42", tool_call_id="c1")
    d = m.to_dict()
    assert Message.from_dict(d) == m
