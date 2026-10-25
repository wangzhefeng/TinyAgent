"""Tests for @tool schema generation and registry dispatch."""

from __future__ import annotations

import pytest

from tinyagent.core.tools import ToolRegistry, tool


@tool
def calculator(expression: str) -> str:
    """四则算术计算器。"""
    return str(eval(expression, {"__builtins__": {}}, {}))  # noqa: S307


@tool
def greet(name: str, times: int = 1) -> str:
    """问候生成器。"""
    return "hi " + name * times


def test_spec_from_type_hints():
    assert calculator.spec.name == "calculator"
    assert calculator.spec.description == "四则算术计算器。"
    assert calculator.spec.parameters["properties"]["expression"] == {"type": "string"}
    assert calculator.spec.parameters["required"] == ["expression"]
    # 默认参数不进 required
    assert "times" not in greet.spec.parameters.get("required", [])


def test_registry_dispatch_and_errors():
    registry = ToolRegistry([calculator, greet])
    assert [s.name for s in registry.specs] == ["calculator", "greet"]

    assert registry.call("calculator", expression="1+1") == "2"
    assert registry.call("greet", name="a", times=2) == "hi aa"

    with pytest.raises(ValueError, match="unknown tool"):
        registry.call("nope")
    with pytest.raises(ValueError, match="missing required"):
        registry.call("calculator")
