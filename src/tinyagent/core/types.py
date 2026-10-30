"""Core data types shared across the framework."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Message:
    """A single conversation message.

    Attributes:
        role: one of ``system`` / ``user`` / ``assistant`` / ``tool``.
        content: text content.
        tool_call_id: id of the tool call this message answers (role="tool").
        tool_calls: raw assistant tool_calls payload (OpenAI shape) for
            history replay with native function calling.
    """

    role: str
    content: str
    tool_call_id: str | None = None
    tool_calls: list[dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dict."""
        d: dict[str, Any] = {"role": self.role, "content": self.content}
        if self.tool_call_id is not None:
            d["tool_call_id"] = self.tool_call_id
        if self.tool_calls is not None:
            d["tool_calls"] = self.tool_calls
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Message:
        """Deserialize from a dict."""
        return cls(
            role=d["role"],
            content=d.get("content", ""),
            tool_call_id=d.get("tool_call_id"),
            tool_calls=d.get("tool_calls"),
        )


@dataclass
class ToolSpec:
    """Declarative description of a tool (JSON Schema parameters)."""

    name: str
    description: str
    parameters: dict[str, Any]


@dataclass
class ToolCallReply:
    """A raw tool call as returned by the model (native function calling)."""

    id: str
    name: str
    arguments: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize to the OpenAI tool_calls entry shape."""
        return {
            "id": self.id,
            "type": "function",
            "function": {"name": self.name, "arguments": self.arguments},
        }


@dataclass
class ModelReply:
    """Unified model reply: plain text, tool calls, and optional token usage."""

    text: str = ""
    tool_calls: list[ToolCallReply] = field(default_factory=list)
    usage: dict[str, Any] = field(default_factory=dict)
