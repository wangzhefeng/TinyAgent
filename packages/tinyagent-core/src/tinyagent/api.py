"""Versioned public API of tinyagent (the only stable import surface)."""

from __future__ import annotations

from .agents.react_agent import TinyAgent
from .codecs.native import NativeCodec
from .codecs.react_text import ReactTextCodec
from .core.guardrails import AllowlistGuardrail, CompositeGuardrail
from .core.llm import PROVIDER_PRESETS, OpenAIChatModel
from .core.loop import agent_loop
from .core.protocols import (
    ChatModel,
    Guardrail,
    Memory,
    SessionStore,
    Tool,
    Tracer,
)
from .core.session import FileSessionStore
from .core.tools import ToolRegistry, ToolWrapper, tool
from .core.tracer import JsonlTracer
from .core.types import (
    FinalAnswer,
    LoopResult,
    Message,
    ModelReply,
    ToolAction,
    ToolCallReply,
    ToolSpec,
)

__all__ = [
    "AllowlistGuardrail",
    "ChatModel",
    "CompositeGuardrail",
    "FileSessionStore",
    "FinalAnswer",
    "Guardrail",
    "JsonlTracer",
    "LoopResult",
    "Memory",
    "Message",
    "ModelReply",
    "NativeCodec",
    "OpenAIChatModel",
    "PROVIDER_PRESETS",
    "ReactTextCodec",
    "SessionStore",
    "TinyAgent",
    "Tool",
    "ToolAction",
    "ToolCallReply",
    "ToolRegistry",
    "ToolSpec",
    "ToolWrapper",
    "Tracer",
    "agent_loop",
    "tool",
]
