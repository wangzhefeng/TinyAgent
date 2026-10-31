import os

import agent
import memory
import scheduler
from context import save_session
from fake import FakeClient, tool_call
from permissions import PermissionManager


def setup_function():
    memory.MEMORY_FILE.unlink(missing_ok=True)


def test_add_replace_remove_and_limit():
    assert "已更新" in memory.remember("add", "用户喜欢简短的回答")
    assert "已更新" in memory.remember("add", "项目用 pnpm，不用 npm")
    assert memory.remember("replace", "项目用 pnpm（不是 npm）", old="pnpm") .startswith("已更新")
    assert memory.load_entries() == ["用户喜欢简短的回答", "项目用 pnpm（不是 npm）"]
    assert memory.remember("remove", old="用户").startswith("已更新")
    assert memory.remember("remove", old="不存在").startswith("Error")
    assert memory.remember("add", "x" * 3000).startswith("Error: 记忆会超过")
    assert memory.load_entries() == ["项目用 pnpm（不是 npm）"]          # 超限的没写进去


def test_memory_file_outside_workspace():
    assert not str(memory.MEMORY_FILE).startswith(os.environ["NAMI_WORKSPACE"])


def test_snapshot_at_session_start():
    memory.remember("add", "回答用中文")
    s = agent.Session("m1", persist=False)
    assert "回答用中文" in s.messages[0]["content"]
    memory.remember("add", "新记的一条")
    assert "新记的一条" not in s.messages[0]["content"]                 # 本会话不变
    assert "新记的一条" in agent.Session("m2", persist=False).messages[0]["content"]


def test_remember_needs_confirmation_and_shows_text():
    seen = []
    pm = PermissionManager(ask=lambda n, a: (seen.append((n, a)) or "n", "不用记"))
    d = pm.check("remember", {"action": "add", "text": "用户住在上海"})
    assert not d.allowed and seen[0][0] == "remember"


def test_unattended_task_cannot_write_memory():
    pm = PermissionManager(ask=scheduler.make_task_ask({"allow": ["fetch_url", "write_file"]}))
    assert not pm.check("remember", {"action": "add", "text": "x"}).allowed


def test_subagent_cannot_remember():
    import subagent
    assert "remember" not in subagent.toolset("worker")


def test_search_sessions():
    save_session("old-chat", [{"role": "system", "content": "s"},
                              {"role": "user", "content": "上次那个 Redis 连接超时的问题怎么解决的"},
                              {"role": "assistant", "content": "把连接池上限从 10 调到 50，超时就消失了"}])
    out = memory.search_sessions("连接池 超时")
    assert "old-chat · assistant" in out and "50" in out
    assert memory.search_sessions("完全无关的词").startswith("没有找到")
