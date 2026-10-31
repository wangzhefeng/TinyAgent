import json
import threading
from types import SimpleNamespace as NS

from openai.types.chat import ChatCompletionMessage

import agent
import subagent
from fake import FakeClient, tool_call
from permissions import WORKSPACE


def test_explore_toolset_is_read_only():
    names = subagent.toolset("explore")
    assert {"read_file", "list_dir", "load_skill"} <= names
    assert not names & {"write_file", "run_shell", "delegate", "schedule_task"}
    worker = subagent.toolset("worker")
    assert {"write_file", "run_shell"} <= worker and "delegate" not in worker


def test_delegate_returns_only_conclusion():
    (WORKSPACE / "big.txt").write_text("x" * 5000)
    c = FakeClient([
        [tool_call("p1", "delegate", {"task": "读 big.txt，告诉我它有多长", "kind": "explore"})],
        [tool_call("s1", "read_file", {"path": "big.txt"})],     # 子 Agent 读文件
        "big.txt 有 5000 个字符",                                  # 子 Agent 的结论
        "子 Agent 说文件有 5000 个字符",                            # 主 Agent 的回答
    ])
    s = agent.Session("main", ask=lambda n, a: ("n", ""), persist=False)
    out = agent.run(s, "big.txt 多长？", c, log=lambda *_: None)
    assert out == "子 Agent 说文件有 5000 个字符"
    # 主 Agent 的上下文里只有结论，没有 5000 个 x
    tool_msgs = [m["content"] for m in s.messages if m["role"] == "tool"]
    assert len(tool_msgs) == 1 and "5000 个字符" in tool_msgs[0] and "xxxx" not in tool_msgs[0]
    # 子 Agent 只拿到了只读工具，而且有自己的 system prompt
    sub_request = c.seen[1]
    assert sub_request[0]["content"].startswith("你是一个子 Agent")
    assert len(sub_request) == 2          # system + 任务，没有主对话的历史


def test_sub_cannot_use_tools_it_was_not_given():
    c = FakeClient([[tool_call("s1", "write_file", {"path": "sub-should-not-write.txt", "content": "x"})], "写不了"])
    sub = agent.Session("sub", ask=lambda n, a: ("y", ""), persist=False,
                        tools=subagent.toolset("explore"), system="sub", depth=1)
    agent.run(sub, "写个文件", c, log=lambda *_: None)
    assert "当前不能使用工具 write_file" in sub.messages[3]["content"]
    assert not (WORKSPACE / "sub-should-not-write.txt").exists()


def test_no_nested_delegation():
    c = FakeClient(["x"])
    sub = agent.Session("sub", persist=False, tools=None, system="sub", depth=1)
    token = agent.CURRENT.set((sub, c, "m", print))
    try:
        assert "不能再派生" in subagent.delegate("再派一个")
    finally:
        agent.CURRENT.reset(token)


class ParallelClient:
    """线程安全的假模型：子 Agent 直接回答自己的任务；主 Agent 第一轮派活，第二轮汇总"""
    def __init__(self):
        self.lock = threading.Lock(); self.main_calls = 0; self.threads = set()
        self.chat = NS(completions=NS(create=self.create))

    def create(self, model, messages, tools=None):
        if messages[0]["content"].startswith("你是一个子 Agent"):
            with self.lock:
                self.threads.add(threading.get_ident())
            msg = ChatCompletionMessage(role="assistant", content=f"完成：{messages[1]['content']}")
        else:
            with self.lock:
                self.main_calls += 1
                n = self.main_calls
            if n == 1:
                msg = ChatCompletionMessage(role="assistant", content=None, tool_calls=[
                    tool_call("p", "delegate_parallel", {"tasks": ["查 A", "查 B", "查 C"]})])
            else:
                msg = ChatCompletionMessage(role="assistant", content="汇总完毕")
        return NS(choices=[NS(message=msg)], usage=NS(prompt_tokens=10))


def test_parallel_explorers():
    c = ParallelClient()
    s = agent.Session("main2", persist=False)
    assert agent.run(s, "三件事一起查", c, log=lambda *_: None) == "汇总完毕"
    result = s.messages[3]["content"]
    for x in ("完成：查 A", "完成：查 B", "完成：查 C"):
        assert x in result
    assert len(c.threads) >= 2                 # 确实在多个线程里跑


def test_parallel_limit():
    s = agent.Session("main3", persist=False)
    token = agent.CURRENT.set((s, None, "m", print))
    try:
        assert subagent.delegate_parallel(["a", "b", "c", "d"]).startswith("Error")
    finally:
        agent.CURRENT.reset(token)
