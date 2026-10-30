"""Risk-based approval policy and the CLI implementation."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from enum import Enum
from typing import Any


class Risk(Enum):
    """Tool risk levels used before execution."""

    SAFE = "safe"
    CONFIRM = "confirm"
    DENY = "deny"


class CLIApprover:
    """Allow safe tools, deny forbidden tools, and confirm the rest."""

    def __init__(
        self,
        safe_tools: set[str],
        ask: Callable[[str], str] | None = None,
        interactive: bool | None = None,
    ) -> None:
        self.safe_tools = safe_tools
        self.ask = ask or input
        self.interactive = interactive

    def check(self, name: str, arguments: dict[str, Any]) -> tuple[bool, str]:
        """Return whether a tool may run and the reason for the decision."""
        risk = Risk.SAFE if name in self.safe_tools else Risk.CONFIRM
        if risk is Risk.SAFE:
            return True, "safe tool"
        if self.interactive is False or (self.interactive is None and not sys.stdin.isatty()):
            return False, "non-interactive environment cannot confirm"
        rendered = json.dumps({"tool": name, "arguments": arguments}, ensure_ascii=False)
        answer = self.ask(f"Allow {rendered}? [y/N] ").strip().lower()
        if answer in {"y", "yes"}:
            return True, "approved by user"
        return False, "denied by user; do not retry the same operation"
