"""Tests for the agent_loop kernel with a scripted model."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "packages" / "tinyagent-core" / "src"))

from tinyagent.codecs.react_text import ReactTextCodec  # noqa: E402
from tinyagent.core.loop import agent_loop  # noqa: E402
from tinyagent.core.tools import ToolRegistry, tool  # noqa: E402
from tinyagent.core.types import ModelReply  # noqa: E402

from tests.conftest import ScriptedModel  # noqa: E402


@tool
def double(n: int) -> str:
    """将整数翻倍。"""
    return str(n * 2)


def _registry() -> ToolRegistry:
    return ToolRegistry([double])


def test_loop_executes_tool_then_finalizes():
    model = ScriptedModel([
        ModelReply(text='Thought: 翻倍\nAction: double\nAction Input: {"n": 21}'),
        ModelReply(text="Final Answer: 42"),
    ])
    result = agent_loop(model, ReactTextCodec(), _registry(), "21 翻倍是多少？")
    assert result.text == "Final Answer: 42"
    assert result.steps == 1
    # 第二次调用应带上 Observation 回填
    assert any(
        "Observation: 42" in m.content for m in result.messages if m.role == "user"
    )


def test_loop_direct_final_answer():
    model = ScriptedModel([ModelReply(text="直接回答：你好！")])
    result = agent_loop(model, ReactTextCodec(), _registry(), "你好")
    assert result.steps == 0
    assert result.text == "直接回答：你好！"


def test_loop_max_steps_cap():
    action_reply = ModelReply(
        text='Action: double\nAction Input: {"n": 1}'
    )
    model = ScriptedModel([action_reply] * 3)
    result = agent_loop(
        model, ReactTextCodec(), _registry(), "q", max_steps=3
    )
    assert result.steps == 3
    assert not result.text.startswith("Final")


def test_loop_feeds_tool_error_back_for_self_correction():
    model = ScriptedModel([
        ModelReply(text='Action: double\nAction Input: {"n": 1, "extra": 1}'),
        ModelReply(text="Final Answer: recovered"),
    ])
    result = agent_loop(model, ReactTextCodec(), _registry(), "q")
    # double(n=1, extra=1) 因未知参数 TypeError → loop 不崩溃，错误回填后模型收敛
    assert result.text == "Final Answer: recovered"


def test_loop_react_codec_passes_no_native_tools():
    model = ScriptedModel([ModelReply(text="ok")])
    agent_loop(model, ReactTextCodec(), _registry(), "q")
    assert model.calls[0]["tools"] == []
