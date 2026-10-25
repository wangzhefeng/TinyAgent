"""Tests for the ReAct text codec, including the M1 colon-bug regression."""

from __future__ import annotations

from tinyagent.codecs.react_text import ReactTextCodec
from tinyagent.core.types import FinalAnswer, ModelReply, ToolSpec


def _spec() -> ToolSpec:
    return ToolSpec(
        name="calculator",
        description="四则算术计算器",
        parameters={
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    )


def test_system_fragment_contains_tools_and_rules():
    fragment = ReactTextCodec().system_fragment([_spec()])
    assert "calculator" in fragment
    assert "Action: the action to take" in fragment
    assert "NEVER write, guess, or imagine any Observation" in fragment


def test_parse_action_with_colon_regression():
    # M1 回归：解析出的工具名不能带前导冒号
    reply = ModelReply(
        text="Thought: 需要计算\nAction: calculator\nAction Input:"
        ' {"expression": "(123 + 456) * 2"}'
    )
    action = ReactTextCodec().parse(reply)
    assert action.name == "calculator"  # 而非 ": calculator"
    assert action.arguments == {"expression": "(123 + 456) * 2"}


def test_parse_missing_obsation_completion():
    reply = ModelReply(
        text='Thought: x\nAction: calculator\nAction Input: {"expression": "1+1"}\n'
        "Thought: I now know the final answer\nFinal Answer: 2"
    )
    action = ReactTextCodec().parse(reply)
    assert action.name == "calculator"


def test_parse_final_answer():
    reply = ModelReply(text="Final Answer: 42")
    parsed = ReactTextCodec().parse(reply)
    assert isinstance(parsed, FinalAnswer)
    assert parsed.text == "Final Answer: 42"


def test_observation_wrapped_as_user_message():
    msg = ReactTextCodec().observation("1158", ModelReply(text=""))
    assert msg.role == "user"
    assert msg.content == "Observation: 1158"
