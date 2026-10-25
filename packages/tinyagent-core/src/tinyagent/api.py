"""Versioned public API of tinyagent (the only stable import surface)."""

from __future__ import annotations

from .agents.react_agent import TinyAgent
from .agents.swarm import Swarm
from .codecs.native import NativeCodec
from .codecs.react_text import ReactTextCodec
from .core.guardrails import AllowlistGuardrail, CompositeGuardrail
from .core.handoff import HANDOFF_MARKER, extract_handoff, make_transfer_tools
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
    "HANDOFF_MARKER",
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
    "Swarm",
    "TinyAgent",
    "Tool",
    "ToolAction",
    "ToolCallReply",
    "ToolRegistry",
    "ToolSpec",
    "ToolWrapper",
    "Tracer",
    "agent_loop",
    "extract_handoff",
    "make_transfer_tools",
    "tool",
]
