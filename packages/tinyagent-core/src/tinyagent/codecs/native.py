"""Native function-calling codec (ADR-0002)."""

from __future__ import annotations

from ..core.llm import parse_tool_arguments
from ..core.types import (
    FinalAnswer,
    Message,
    ModelReply,
    ToolAction,
    ToolSpec,
)


class NativeCodec:
    """Tools passed natively to the API; tool_calls decoded from the reply."""

    use_native_tools = True

    def system_fragment(self, specs: list[ToolSpec]) -> str | None:
        """No prompt fragment needed for native tools."""
        return None

    def parse(self, reply: ModelReply) -> ToolAction | FinalAnswer:
        """Decode the first tool call, else treat the text as final."""
        if reply.tool_calls:
            tc = reply.tool_calls[0]
            return ToolAction(
                name=tc.name, arguments=parse_tool_arguments(tc.arguments)
            )
        return FinalAnswer(text=reply.text.strip())

    def observation(self, result_text: str, reply: ModelReply) -> Message:
        """Feed the tool result back as a tool-role message."""
        call_id = reply.tool_calls[0].id if reply.tool_calls else ""
        return Message("tool", result_text, tool_call_id=call_id)
