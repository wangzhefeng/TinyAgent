"""The six pluggable protocols (see ADR-0001).

Every protocol is a ``typing.Protocol``: bring your own implementation and
inject it into :func:`tinyagent.core.loop.agent_loop`.
"""

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


@runtime_checkable
class SessionStore(Protocol):
    """Message/state persistence (LangGraph checkpointer-compatible subset)."""

    def append_message(self, session_id: str, message: Message) -> None:
        """Persist one message."""
        ...  # pragma: no cover

    def load_messages(self, session_id: str) -> list[Message]:
        """Load all messages of a session."""
        ...  # pragma: no cover

    def save_state(self, session_id: str, state: dict[str, Any]) -> None:
        """Persist an arbitrary JSON-able state dict."""
        ...  # pragma: no cover

    def load_state(self, session_id: str) -> dict[str, Any]:
        """Load the state dict of a session."""
        ...  # pragma: no cover


@runtime_checkable
class Tracer(Protocol):
    """Event stream for observability."""

    def emit(self, event: str, data: dict[str, Any] | None = None) -> None:
        """Record one event."""
        ...  # pragma: no cover


@runtime_checkable
class Guardrail(Protocol):
    """Validation/transformation hooks around the loop."""

    def on_input(self, text: str) -> str:
        """Inspect/transform the user input; raise to block."""
        ...  # pragma: no cover

    def on_action(self, name: str, arguments: dict[str, Any]) -> None:
        """Validate a tool action; raise to block."""
        ...  # pragma: no cover

    def on_output(self, text: str) -> str:
        """Inspect/transform the final output; raise to block."""
        ...  # pragma: no cover


@runtime_checkable
class Memory(Protocol):
    """Short-term conversation memory."""

    def add(self, message: Message) -> None:
        """Append one message."""
        ...  # pragma: no cover

    def all(self) -> list[Message]:
        """Return the buffered messages."""
        ...  # pragma: no cover

    def clear(self) -> None:
        """Drop all buffered messages."""
        ...  # pragma: no cover
