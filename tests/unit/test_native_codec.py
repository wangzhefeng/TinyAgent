"""Tests for the native function-calling codec."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "packages" / "tinyagent-core" / "src"))

from tinyagent.codecs.native import NativeCodec  # noqa: E402
from tinyagent.core.types import FinalAnswer, ModelReply, ToolCallReply  # noqa: E402


def test_no_system_fragment_and_native_flag():
    codec = NativeCodec()
    assert codec.use_native_tools is True
    assert codec.system_fragment([]) is None


def test_parse_tool_call():
    reply = ModelReply(
        text="",
        tool_calls=[ToolCallReply(id="call_1", name="calculator",
                                  arguments='{"expression": "6*7"}')],
    )
    action = NativeCodec().parse(reply)
    assert action.name == "calculator"
    assert action.arguments == {"expression": "6*7"}


def test_parse_plain_text_as_final():
    parsed = NativeCodec().parse(ModelReply(text="The answer is 42."))
    assert isinstance(parsed, FinalAnswer)
    assert parsed.text == "The answer is 42."


def test_observation_uses_tool_role_with_id():
    reply = ModelReply(
        tool_calls=[ToolCallReply(id="call_9", name="calculator", arguments="{}")]
    )
    msg = NativeCodec().observation("42", reply)
    assert msg.role == "tool"
    assert msg.tool_call_id == "call_9"
