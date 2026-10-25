"""Guardrail composition and the allowlist guardrail (safety seed for Copilot)."""

from __future__ import annotations

from typing import Any

from .protocols import Guardrail


class CompositeGuardrail:
    """Fold multiple guardrails; first raised error blocks the run."""

    def __init__(self, guardrails: list[Guardrail] | None = None) -> None:
        self.guardrails = guardrails or []

    def on_input(self, text: str) -> str:
        """Apply every guardrail's input hook in order."""
        for g in self.guardrails:
            text = g.on_input(text)
        return text

    def on_action(self, name: str, arguments: dict[str, Any]) -> None:
        """Apply every guardrail's action validation."""
        for g in self.guardrails:
            g.on_action(name, arguments)

    def on_output(self, text: str) -> str:
        """Apply every guardrail's output hook in order."""
        for g in self.guardrails:
            text = g.on_output(text)
        return text


class AllowlistGuardrail:
    """Block tool calls whose name is not on the allowlist."""

    def __init__(self, allowed: list[str]) -> None:
        self.allowed = set(allowed)

    def on_input(self, text: str) -> str:
        """No-op for inputs."""
        return text

    def on_action(self, name: str, arguments: dict[str, Any]) -> None:
        """Raise unless the tool is allowlisted."""
        if name not in self.allowed:
            raise PermissionError(f"tool not allowed: {name}")

    def on_output(self, text: str) -> str:
        """No-op for outputs."""
        return text
