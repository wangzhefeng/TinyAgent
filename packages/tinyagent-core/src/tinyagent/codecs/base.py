"""CallCodec protocol: how tools are presented and replies decoded (ADR-0002)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..core.types import FinalAnswer, Message, ModelReply, ToolAction, ToolSpec


@runtime_checkable
class CallCodec(Protocol):
    """Pluggable tool-call encoding/decoding strategy."""

    use_native_tools: bool

    def system_fragment(self, specs: list[ToolSpec]) -> str | None:
        """Prompt fragment describing the tools (None for native codecs)."""
        ...  # pragma: no cover

    def parse(self, reply: ModelReply) -> ToolAction | FinalAnswer:
        """Decode a model reply into one tool action or a final answer."""
        ...  # pragma: no cover

    def observation(self, result_text: str, reply: ModelReply) -> Message:
        """Wrap a tool result as the message fed back to the model."""
        ...  # pragma: no cover
