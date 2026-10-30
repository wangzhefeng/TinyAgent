"""Tests for handoff tools and the Swarm runner (ADR-0004)."""

from __future__ import annotations

from tests.conftest import ScriptedModel
from tinyagent import (
    Swarm,
    TinyAgent,
    extract_handoff,
    make_transfer_tools,
)
from tinyagent.codecs.react_text import ReactTextCodec
from tinyagent.core.types import LoopResult, Message, ModelReply


def test_transfer_tools_schema_and_marker():
    tools = make_transfer_tools(["analyst", "reporter"], "analyst")
    assert [t.spec.name for t in tools] == ["transfer_to_reporter"]
    assert "移交" in tools[0].spec.description
    assert tools[0].call(reason="需要写报告").startswith("HANDOFF_TO:reporter")


def test_extract_handoff_from_messages():
    result = LoopResult(
        text="x",
        messages=[Message("user", "Observation: HANDOFF_TO:reporter（理由：写报告）")],
        steps=1,
    )
    assert extract_handoff(result) == "reporter"
    plain = LoopResult(text="ok", messages=[Message("user", "plain")], steps=0)
    assert extract_handoff(plain) is None


def test_swarm_switches_and_finishes():
    model_a = ScriptedModel([
        ModelReply(text='Action: transfer_to_b\nAction Input: {"reason": "数据"}'),
        ModelReply(text="Final Answer: 已移交给 b"),
    ])
    model_b = ScriptedModel([ModelReply(text="Final Answer: b 的专业结论")])
    swarm = Swarm(
        {
            "a": TinyAgent(model=model_a, codec=ReactTextCodec()),
            "b": TinyAgent(model=model_b, codec=ReactTextCodec()),
        },
        initial="a",
    )

    result = swarm.run("测试问题")

    assert result.text.endswith("b 的专业结论")
    assert len(model_b.calls) == 1  # b 恰好运行一轮并给出最终答案
    assert any("由智能体 a 移交" in m.content for m in result.messages)
