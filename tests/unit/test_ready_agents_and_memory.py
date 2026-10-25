"""Tests for the ready-made agents and memory (ported capabilities)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "packages" / "tinyagent-core" / "src"))

from tinyagent import (  # noqa: E402
    FileLongTermMemory,
    ListMemory,
    Message,
    ModelReply,
    PlanAndSolveAgent,
    ReflectionAgent,
)

from tests.conftest import ScriptedModel  # noqa: E402


def test_reflection_agent_converges():
    model = ScriptedModel([
        ModelReply(text="def primes(n):\n    ..."),          # 初始
        ModelReply(text="当前是试除法，建议改用筛法"),         # 反思 1
        ModelReply(text="def primes(n):  # 埃氏筛"),          # 优化
        ModelReply(text="已是筛法，无需改进"),                 # 反思 2
    ])
    agent = ReflectionAgent(model, max_iterations=2)
    final = agent.run("写素数函数")
    assert "埃氏筛" in final


def test_plan_and_solve_agent_steps():
    model = ScriptedModel([
        ModelReply(text='```python\n["第一步", "第二步"]\n```'),
        ModelReply(text="答案一"),
        ModelReply(text="答案二"),
    ])
    agent = PlanAndSolveAgent(model)
    assert agent.plan("测试") == ["第一步", "第二步"]
    assert agent.run("测试") == "答案二"


def test_plan_fallback_on_bad_output():
    model = ScriptedModel([
        ModelReply(text="我不会输出列表"),  # planner 失败
        ModelReply(text="直接回答"),
    ])
    agent = PlanAndSolveAgent(model)
    assert agent.run("问题") == "直接回答"  # 退化为单步执行


def test_list_memory_roundtrip():
    m = ListMemory()
    m.add(Message("user", "hi"))
    m.add(Message("assistant", "hello"))
    assert [x.content for x in m.all()] == ["hi", "hello"]
    m.clear()
    assert m.all() == []


def test_long_term_memory_keyword_mode(tmp_path: Path):
    m = FileLongTermMemory(tmp_path / "mem.jsonl", embed=False)
    m.add("时序预测是能源行业的基础能力")
    m.add("Python 之禅胜过 Perl 之禅")
    m.add("回测口径必须一致才能比较模型")
    hits = m.retrieve("模型比较的回测口径", k=2)
    assert any("口径" in r["text"] for r in hits)
    assert len(m.all()) == 3
