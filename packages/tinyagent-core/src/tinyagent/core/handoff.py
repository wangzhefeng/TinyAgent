"""Handoff: control transfer between agents as plain tools (ADR-0004)."""

from __future__ import annotations

from ..core.tools import ToolWrapper, tool
from ..core.types import LoopResult

HANDOFF_MARKER = "HANDOFF_TO:"


def make_transfer_tools(agent_names: list[str], my_name: str) -> list[ToolWrapper]:
    """Build one ``transfer_to_<name>`` tool for every other agent."""
    tools: list[ToolWrapper] = []
    for name in agent_names:
        if name == my_name:
            continue

        def _transfer(reason: str, _name: str = name) -> str:
            return f"{HANDOFF_MARKER}{_name}（理由：{reason}）"

        _transfer.__name__ = f"transfer_to_{name}"
        _transfer.__doc__ = f"把当前任务移交给智能体 {name}，并说明移交理由。"
        tools.append(tool(_transfer))
    return tools


def extract_handoff(result: LoopResult) -> str | None:
    """Return the target agent name if the run's messages contain a handoff."""
    for m in reversed(result.messages):
        pos = m.content.find(HANDOFF_MARKER)
        if pos >= 0:
            name = m.content[pos + len(HANDOFF_MARKER):].strip()
            name = name.split("（")[0].split("(")[0].strip()
            return name or None
    return None
