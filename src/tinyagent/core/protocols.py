"""Model and tool protocols used by the personal agent."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from .types import Message, ModelReply, ToolSpec


@runtime_checkable
class ChatModel(Protocol):
    """The only model abstraction: one chat method."""

    def chat(
        self, messages: list[Message], tools: list[ToolSpec] | None = None
    ) -> ModelReply:
        """Reply to the given messages, optionally with native tools."""
        ...  # pragma: no cover


@runtime_checkable
class Tool(Protocol):
    """A tool: declarative spec plus a callable."""

    @property
    def spec(self) -> ToolSpec:
        """Declarative description used in prompts / API calls."""
        ...  # pragma: no cover

    def call(self, **kwargs: Any) -> str:
        """Execute the tool and return a text result."""
        ...  # pragma: no cover
