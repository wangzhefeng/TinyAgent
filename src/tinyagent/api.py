"""Versioned public API of tinyagent (the stable personal-agent surface)."""

from .agent import ContextBuilder, ContextView, EventRecord, RunRecord
from .core.llm import PROVIDER_PRESETS, OpenAIChatModel
from .core.protocols import ChatModel, Tool
from .core.tools import ToolRegistry, ToolWrapper, tool
from .core.types import Message, ModelReply, ToolCallReply, ToolSpec
from .runtime import (
    LocalOutbox,
    PersonalRuntime,
    RunCancelled,
    Scheduler,
    SQLiteStore,
)

__all__ = [
    "ChatModel",
    "ContextBuilder",
    "ContextView",
    "EventRecord",
    "LocalOutbox",
    "Message",
    "ModelReply",
    "OpenAIChatModel",
    "PROVIDER_PRESETS",
    "PersonalRuntime",
    "RunCancelled",
    "RunRecord",
    "SQLiteStore",
    "Scheduler",
    "Tool",
    "ToolCallReply",
    "ToolRegistry",
    "ToolSpec",
    "ToolWrapper",
    "tool",
]
