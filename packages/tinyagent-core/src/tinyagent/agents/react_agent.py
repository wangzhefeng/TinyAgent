"""TinyAgent facade: assemble protocols into a friendly runnable agent."""

from __future__ import annotations

from ..codecs.base import CallCodec
from ..codecs.native import NativeCodec
from ..codecs.react_text import ReactTextCodec
from ..core.guardrails import CompositeGuardrail
from ..core.llm import OpenAIChatModel
from ..core.loop import agent_loop
from ..core.protocols import ChatModel, Guardrail, SessionStore, Tracer
from ..core.tools import ToolRegistry, ToolWrapper
from ..core.types import LoopResult, Message


class TinyAgent:
    """One-line agent over the six protocols.

    Example:
        agent = TinyAgent(tools=[calculator], codec="react")
        result = agent.run("Compute (1+2)*3 with the calculator.")
    """

    def __init__(
        self,
        tools: list[ToolWrapper] | None = None,
        codec: str | CallCodec = "react",
        model: ChatModel | None = None,
        system: str = "",
        tracer: Tracer | None = None,
        session: SessionStore | None = None,
        guardrail: Guardrail | CompositeGuardrail | None = None,
        max_steps: int = 6,
    ) -> None:
        self.model = model if model is not None else OpenAIChatModel()
        self.codec: CallCodec = (
            codec if not isinstance(codec, str)
            else ReactTextCodec() if codec == "react"
            else NativeCodec()
        )
        self.registry = ToolRegistry(tools)
        self.system = system
        self.tracer = tracer
        self.session = session
        self.guardrail = guardrail
        self.max_steps = max_steps

    def run(
        self,
        question: str,
        history: list[Message] | None = None,
        session_id: str = "default",
    ) -> LoopResult:
        """Run the agent loop for one question."""
        return agent_loop(
            model=self.model,
            codec=self.codec,
            registry=self.registry,
            question=question,
            history=history,
            system=self.system,
            tracer=self.tracer,
            session=self.session,
            session_id=session_id,
            guardrail=self.guardrail,
            max_steps=self.max_steps,
        )
