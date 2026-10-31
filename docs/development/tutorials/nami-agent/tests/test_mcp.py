import json
import sys
from pathlib import Path

import pytest

import mcp_client
from permissions import PermissionManager
from tools import TOOLS, execute

DEMO = str(Path(__file__).resolve().parents[1] / "demo_mcp_server.py")


@pytest.fixture
def server():
    s = mcp_client.MCPServer("demo", sys.executable, [DEMO])
    yield s
    s.close()


def test_handshake_and_list(server):
    info = server.initialize()
    assert info["serverInfo"]["name"] == "demo"
    names = [t["name"] for t in server.list_tools()]
    assert names == ["now", "word_count"]


def test_call_tool(server):
    server.initialize()
    assert server.call_tool("word_count", {"text": "你好\n世界"}) == "5 个字符，2 行"
    assert server.call_tool("nope", {}).startswith("Error:")      # isError 变成 Error 前缀


def test_unknown_method_raises(server):
    server.initialize()
    with pytest.raises(mcp_client.MCPError):
        server.request("resources/list")


def test_register_and_execute_through_registry(server):
    server.initialize()
    mcp_client.register_server(server, safe={"now"})
    assert "mcp__demo__word_count" in TOOLS
    # 通过第 2 课的统一执行器调用，和本地工具没有区别
    assert execute("mcp__demo__word_count", {"text": "abc"}) == "3 个字符，1 行"
    pm = PermissionManager(ask=lambda n, a: ("n", ""))
    assert pm.check("mcp__demo__now", {}).allowed               # 配置里点名的只读工具
    assert not pm.check("mcp__demo__word_count", {}).allowed    # 其他默认要确认
    mcp_client.SERVERS.clear()


def test_load_servers_from_config(tmp_path):
    cfg = tmp_path / "mcp.json"
    cfg.write_text(json.dumps({"servers": {
        "demo2": {"command": sys.executable, "args": [DEMO]},
        "broken": {"command": "/没有这个程序"},
    }}), encoding="utf-8")
    logs = []
    mcp_client.load_servers(cfg, log=logs.append)
    try:
        assert "mcp__demo2__now" in TOOLS
        assert any("broken 启动失败" in x for x in logs)            # 坏的不影响好的
    finally:
        mcp_client.close_all()


def test_config_lives_outside_workspace():
    import os
    assert not str(mcp_client.CONFIG_FILE).startswith(os.environ["NAMI_WORKSPACE"])
