"""Tests for MCP tool mounting, naming, safe marking, and CLI wiring."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from tests.conftest import ScriptedModel
from tinyagent.channels.cli import build_runtime
from tinyagent.core.types import ModelReply, ToolCallReply, ToolSpec

pytest.importorskip("mcp")

from tinyagent.ext.mcp import (  # noqa: E402
    MCPToolSource,
    mounted_mcp_tools,
    safe_tool_names,
)

SERVER_CODE = '''\
import json
import sys
from datetime import datetime

TOOLS = [
    {"name": "now", "description": "返回当前的本地时间。",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "word_count", "description": "统计一段文字的字符数和行数。",
     "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}},
                     "required": ["text"]}},
]


def call_tool(name, args):
    if name == "now":
        return datetime.now().isoformat(timespec="seconds"), False
    if name == "word_count":
        text = args.get("text", "")
        return f"{len(text)} 个字符", False
    return f"没有工具 {name}", True


def handle(msg):
    method, params = msg.get("method"), msg.get("params") or {}
    if method == "initialize":
        return {"protocolVersion": params.get("protocolVersion", "2025-06-18"),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "demo", "version": "1.0"}}
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        text, is_error = call_tool(params.get("name"), params.get("arguments") or {})
        return {"content": [{"type": "text", "text": text}], "isError": is_error}
    raise KeyError(method)


for line in sys.stdin:
    msg = json.loads(line)
    if "id" not in msg:
        continue
    try:
        reply = {"jsonrpc": "2.0", "id": msg["id"], "result": handle(msg)}
    except KeyError:
        reply = {"jsonrpc": "2.0", "id": msg["id"],
                 "error": {"code": -32601, "message": f"未知方法 {msg.get('method')}"}}
    print(json.dumps(reply, ensure_ascii=False), flush=True)
'''


def _write_server(tmp_path: Path) -> Path:
    server = tmp_path / "demo_server.py"
    server.write_text(SERVER_CODE, encoding="utf-8")
    return server


def test_mcp_source_lists_and_calls_demo_server(tmp_path: Path):
    server = _write_server(tmp_path)
    with MCPToolSource(sys.executable, [str(server)]).tools() as tools:
        assert {tool.spec.name for tool in tools} == {"now", "word_count"}
        word_count = next(tool for tool in tools if tool.spec.name == "word_count")
        assert "5 个字符" in word_count.call(text="hello")


def test_mounted_tools_use_prefixed_names_and_safe_split(tmp_path: Path):
    server = _write_server(tmp_path)
    config = tmp_path / "mcp.json"
    config.write_text(
        json.dumps({"servers": {"demo": {
            "command": sys.executable, "args": [str(server)], "safe_tools": ["now"],
        }}}, ensure_ascii=False),
        encoding="utf-8",
    )
    assert safe_tool_names(config) == {"mcp__demo__now"}
    with mounted_mcp_tools(config, log=lambda _m: None) as tools:
        by_name = {tool.spec.name: tool for tool in tools}
        assert set(by_name) == {"mcp__demo__now", "mcp__demo__word_count"}
        assert by_name["mcp__demo__now"].spec.description.startswith("[MCP:demo]")
        assert ":" in by_name["mcp__demo__now"].call()


class _DummyMcpTool:
    def __init__(self, name: str) -> None:
        self._spec = ToolSpec(
            name=name,
            description=f"dummy {name}",
            parameters={"type": "object", "properties": {}},
        )

    @property
    def spec(self) -> ToolSpec:
        return self._spec

    def call(self, **_kwargs) -> str:
        return f"called {self._spec.name}"


def test_build_runtime_mounts_extra_tools_with_safe_split(tmp_path: Path):
    model = ScriptedModel([
        ModelReply(tool_calls=[ToolCallReply("c1", "mcp__demo__now", "{}")]),
        ModelReply(tool_calls=[ToolCallReply("c2", "mcp__demo__write", "{}")]),
        ModelReply(text="done"),
    ])
    runtime = build_runtime(
        tmp_path,
        tmp_path / "state.db",
        model,
        extra_tools=[
            _DummyMcpTool("mcp__demo__now"),
            _DummyMcpTool("mcp__demo__write"),
        ],
        extra_safe_tools={"mcp__demo__now"},
    )
    assert runtime.run("go") == "done"
    results = [
        event.data["content"]
        for event in runtime.store.session_events("default")
        if event.type == "tool_result"
    ]
    assert results[0] == "called mcp__demo__now"
    assert "Permission denied" in results[1]
