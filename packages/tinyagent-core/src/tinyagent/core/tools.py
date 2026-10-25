"""``@tool`` decorator and ToolRegistry with type-hint schema generation."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any, get_type_hints

from .types import ToolSpec

_PY_TO_JSON: dict[type, str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


def _build_schema(fn: Callable) -> dict[str, Any]:
    """Build a JSON Schema object from the function signature type hints."""
    sig = inspect.signature(fn)
    hints = get_type_hints(fn)
    properties: dict[str, Any] = {}
    required: list[str] = []
    for name, param in sig.parameters.items():
        json_type = _PY_TO_JSON.get(hints.get(name, str), "string")
        properties[name] = {"type": json_type}
        if param.default is inspect.Parameter.empty:
            required.append(name)
    schema: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return schema


class ToolWrapper:
    """Adapt a plain function into the Tool protocol (spec + call)."""

    def __init__(self, fn: Callable) -> None:
        self.fn = fn
        doc = (inspect.getdoc(fn) or "").strip()
        self._spec = ToolSpec(
            name=fn.__name__,
            description=doc.split("\n", 1)[0] if doc else fn.__name__,
            parameters=_build_schema(fn),
        )

    @property
    def spec(self) -> ToolSpec:
        """Declarative description of the wrapped function."""
        return self._spec

    def call(self, **kwargs: Any) -> str:
        """Invoke the wrapped function and stringify the result."""
        return str(self.fn(**kwargs))


def tool(fn: Callable) -> ToolWrapper:
    """Turn a typed function into a framework Tool."""
    return ToolWrapper(fn)


class ToolRegistry:
    """Name-keyed tool set: exposes specs and dispatches calls."""

    def __init__(self, tools: list[ToolWrapper] | None = None) -> None:
        self._tools: dict[str, ToolWrapper] = {t.spec.name: t for t in (tools or [])}

    def add(self, t: ToolWrapper) -> None:
        """Register one more tool."""
        self._tools[t.spec.name] = t

    @property
    def specs(self) -> list[ToolSpec]:
        """Declarative specs of all registered tools."""
        return [t.spec for t in self._tools.values()]

    def call(self, name: str, /, **kwargs: Any) -> str:
        """Dispatch one tool call by name.

        Raises:
            ValueError: unknown tool, missing required arguments, or
                unexpected arguments. ``name`` is positional-only so tool
                parameters never collide with it.
        """
        if name not in self._tools:
            raise ValueError(
                f"unknown tool: {name} (available: {sorted(self._tools)})"
            )
        t = self._tools[name]
        required = t.spec.parameters.get("required", [])
        missing = [k for k in required if k not in kwargs]
        if missing:
            raise ValueError(f"{name}: missing required arguments {missing}")
        known = set(t.spec.parameters.get("properties", {}))
        unknown = [k for k in kwargs if k not in known]
        if unknown:
            raise ValueError(f"{name}: unexpected arguments {unknown}")
        return t.call(**kwargs)
