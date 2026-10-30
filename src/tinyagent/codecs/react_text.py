"""ReAct text codec — the L1 handwritten protocol, hardened (ADR-0002).

Fixes ported from M1: the colon-slicing parse bug, the missing-Observation
completion, and the four anti-hallucination prompt rules.
"""

from __future__ import annotations

from ..core.llm import parse_tool_arguments
from ..core.types import (
    FinalAnswer,
    Message,
    ModelReply,
    ToolAction,
    ToolSpec,
)

TOOL_DESC = (
    "{name}: Call this tool to interact with the {name_for_human} API. "
    "What is the {name_for_human} API useful for? {description} "
    "Parameters: {parameters} Format the arguments as a JSON object."
)

REACT_TEMPLATE = """Answer the following questions as best you can. You have access to the following tools:

{tool_descs}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can be repeated zero or more times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Rules (MUST follow):
1. The Observation line is filled in ONLY by the system after the Action is executed. NEVER write, guess, or imagine any Observation content yourself.
2. Before calling a tool that needs a path, you MUST first call the corresponding list tool and use a REAL path from its result. NEVER guess or invent file paths.
3. If an Observation reports an error, adapt your next Action to fix it. NEVER pretend the call succeeded or fabricate its result.
4. Your Final Answer must be based strictly on the Observation contents actually returned by the system.

Begin!
"""


class ReactTextCodec:
    """Tools in the system prompt; replies parsed from plain text."""

    use_native_tools = False

    def system_fragment(self, specs: list[ToolSpec]) -> str | None:
        """Render tool descriptions in the ReAct prompt template."""
        descs = "\n\n".join(
            TOOL_DESC.format(
                name=s.name,
                name_for_human=s.name,
                description=s.description,
                parameters=s.parameters,
            )
            for s in specs
        )
        names = ",".join(s.name for s in specs)
        return REACT_TEMPLATE.format(tool_descs=descs, tool_names=names)

    def parse(self, reply: ModelReply) -> ToolAction | FinalAnswer:
        """Extract the latest Action / Action Input pair, else a final answer."""
        text = reply.text.rstrip()
        i = text.rfind("\nAction:")
        j = text.rfind("\nAction Input:")
        k = text.rfind("\nObservation:")
        if 0 <= i < j:
            if k < j:
                text = text + "\nObservation:"
                k = text.rfind("\nObservation:")
            # 切片从 "\nAction:" 之后开始（M1 修复：原课程代码少切冒号）
            name = text[i + len("\nAction:"):j].strip()
            raw_args = text[j + len("\nAction Input:"):k].strip()
            return ToolAction(name=name, arguments=parse_tool_arguments(raw_args))
        if text.startswith("Action:"):  # 首行即为 Action 的情形
            j2 = text.find("\nAction Input:")
            if 0 <= j2:
                name = text[len("Action:"):j2].strip()
                rest = text[j2 + len("\nAction Input:"):].strip()
                raw_args = rest.split("\nObservation:")[0].strip()
                return ToolAction(name=name, arguments=parse_tool_arguments(raw_args))
        return FinalAnswer(text=reply.text.strip())

    def observation(self, result_text: str, reply: ModelReply) -> Message:
        """Feed the tool result back as a user message."""
        return Message("user", f"Observation: {result_text}")
