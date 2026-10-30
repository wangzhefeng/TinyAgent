"""Swarm: a minimal multi-agent runner over handoff tools (ADR-0004)."""

from __future__ import annotations

import logging

from ..core.handoff import HANDOFF_MARKER, extract_handoff, make_transfer_tools
from ..core.types import LoopResult
from .react_agent import TinyAgent

logger = logging.getLogger(__name__)


class Swarm:
    """Route one question across agents via explicit handoff tools.

    Each member gets ``transfer_to_<peer>`` tools injected; when a run's
    messages contain a handoff marker, control (and the transfer reason)
    moves to the target agent with a fresh context.
    """

    def __init__(
        self,
        agents: dict[str, TinyAgent],
        initial: str,
        max_handoffs: int = 3,
    ) -> None:
        if initial not in agents:
            raise ValueError(f"unknown initial agent: {initial}")
        self.agents = agents
        self.initial = initial
        self.max_handoffs = max_handoffs
        for name, agent in agents.items():
            for t in make_transfer_tools(list(agents), name):
                agent.registry.add(t)

    def run(self, question: str, session_id: str = "swarm") -> LoopResult:
        """Run agents in turn until one finishes without handing off."""
        current = self.initial
        carrying = question
        result: LoopResult | None = None
        for _ in range(self.max_handoffs + 1):
            result = self.agents[current].run(carrying, session_id=session_id)
            nxt = extract_handoff(result)
            if not nxt or nxt not in self.agents:
                return result
            reason = _handoff_reason(result.messages)
            logger.info("[swarm] %s -> %s（%s）", current, nxt, reason)
            carrying = f"{question}\n\n（由智能体 {current} 移交：{reason}）"
            current = nxt
        assert result is not None
        return result


def _handoff_reason(messages: list) -> str:  # noqa: ANN001
    """Extract the transfer reason from the handoff marker text."""
    for m in reversed(messages):
        pos = m.content.find(HANDOFF_MARKER)
        if pos >= 0:
            tail = m.content[pos + len(HANDOFF_MARKER):]
            if "（理由：" in tail:
                return tail.split("（理由：", 1)[1].rstrip("）").strip()
            if "(" in tail:
                return tail.split("(", 1)[1].rstrip(")").strip()
            return "未说明"
    return "未说明"
