"""The agent loop kernel — the ~30-line heart of the framework (ADR-0001)."""

from __future__ import annotations

from typing import Any

from ..codecs.base import CallCodec
from .protocols import ChatModel, Guardrail, SessionStore, Tracer
from .tools import ToolRegistry
from .types import FinalAnswer, LoopResult, Message


def _emit(tracer: Tracer | None, event: str, data: dict[str, Any] | None = None) -> None:
    if tracer is not None:
        tracer.emit(event, data)


def agent_loop(
    model: ChatModel,
    codec: CallCodec,
    registry: ToolRegistry,
    question: str,
    history: list[Message] | None = None,
    system: str = "",
    tracer: Tracer | None = None,
    session: SessionStore | None = None,
    session_id: str = "default",
    guardrail: Guardrail | None = None,
    max_steps: int = 6,
) -> LoopResult:
    """Run the ReAct iteration until a final answer or ``max_steps``.

    The loop is deliberately minimal: decode -> act -> observe -> repeat.
    All variability lives in the injected protocol implementations.
    """
    def persist(m: Message) -> None:
        if session is not None:
            session.append_message(session_id, m)

    if guardrail is not None:
        question = guardrail.on_input(question)

    messages = list(history or [])
    fragment = codec.system_fragment(registry.specs)
    system_text = "\n\n".join(x for x in (system, fragment or "") if x).strip()
    if system_text and not messages:
        messages.append(Message("system", system_text))
        persist(messages[0])
    messages.append(Message("user", question))
    persist(messages[-1])
    _emit(tracer, "run_start", {"question": question, "tools": [s.name for s in registry.specs]})

    last_text = ""
    for step in range(1, max_steps + 1):
        reply = model.chat(
            messages, tools=registry.specs if codec.use_native_tools else None
        )
        _emit(tracer, "llm_reply", {"step": step, "text": reply.text[:200],
                                    "tool_calls": len(reply.tool_calls)})
        messages.append(
            Message("assistant", reply.text,
                    tool_calls=[tc.to_dict() for tc in reply.tool_calls] or None)
        )
        persist(messages[-1])

        action = codec.parse(reply)
        if isinstance(action, FinalAnswer):
            text = action.text if guardrail is None else guardrail.on_output(action.text)
            _emit(tracer, "run_end", {"steps": step - 1, "final": True})
            return LoopResult(text=text, messages=messages, steps=step - 1)

        if guardrail is not None:
            guardrail.on_action(action.name, action.arguments)
        _emit(tracer, "tool_call", {"step": step, "name": action.name,
                                    "arguments": action.arguments})
        try:
            result = registry.call(action.name, **action.arguments)
        except Exception as e:  # noqa: BLE001
            # 错误回填（M4 泛化）：任何工具异常都转为 Observation 给模型自纠，
            # 而非让整次运行崩溃；护栏的 on_action 在上方独立执行，不被吞掉
            result = f"tool error: {type(e).__name__}: {e}"
        _emit(tracer, "tool_result", {"step": step, "name": action.name,
                                      "result": str(result)[:200]})
        messages.append(codec.observation(str(result), reply))
        persist(messages[-1])
        last_text = str(result)

    _emit(tracer, "run_end", {"steps": max_steps, "final": False})
    return LoopResult(text=last_text or "max steps reached without final answer",
                      messages=messages, steps=max_steps)
