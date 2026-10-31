"""Risk-based approval policy and the CLI implementation."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from enum import Enum
from textwrap import indent
from typing import Any


class Risk(Enum):
    """Tool risk levels used before execution."""

    SAFE = "safe"
    CONFIRM = "confirm"
    DENY = "deny"


#: tools that may be allowed for the rest of one CLI run (answer "a")
REMEMBERABLE = {"write_file"}

_PREVIEW_CHARS = 400


def render_call(name: str, arguments: dict[str, Any], max_chars: int = _PREVIEW_CHARS) -> str:
    """Render the exact arguments a confirmation prompt shows for one tool."""
    if name == "run_shell":
        return f"  $ {arguments.get('command', '')}"
    if name == "write_file":
        content = str(arguments.get("content", ""))
        preview = content[:max_chars]
        if len(content) > max_chars:
            preview += f"\n...（已截断，共 {len(content)} 字符）"
        return f"  路径：{arguments.get('path')}\n{indent(preview, '    ')}"
    if name == "edit_file":
        old = str(arguments.get("old", ""))[:max_chars]
        new = str(arguments.get("new", ""))[:max_chars]
        return f"  路径：{arguments.get('path')}\n{indent(f'- {old}\n+ {new}', '    ')}"
    if name == "fetch_url":
        return f"  URL：{arguments.get('url', '')}"
    if name == "submit_plan":
        return indent(str(arguments.get("plan", "")), "  ")
    if name == "remember":
        old = f"\n  原来那条（包含）：{arguments.get('old')}" if arguments.get("old") else ""
        return f"  {arguments.get('action')}：{arguments.get('text', '')}{old}"
    return "  " + json.dumps(arguments, ensure_ascii=False)


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
        self.always_allowed: set[str] = set()

    def check(self, name: str, arguments: dict[str, Any]) -> tuple[bool, str]:
        """Return whether a tool may run and the reason for the decision."""
        risk = Risk.SAFE if name in self.safe_tools else Risk.CONFIRM
        if risk is Risk.SAFE:
            return True, "safe tool"
        if name in self.always_allowed:
            return True, "approved for the rest of this run"
        if self.interactive is False or (self.interactive is None and not sys.stdin.isatty()):
            return False, "non-interactive environment cannot confirm"
        answer, note = self._prompt(name, arguments)
        if answer in {"y", "yes"}:
            return True, "approved by user"
        if answer in {"a", "always"}:
            if name in REMEMBERABLE:
                self.always_allowed.add(name)
                return True, "approved for the rest of this run"
            return False, f"{name} does not support always-allow; answer y or n"
        reason = "denied by user; do not retry the same operation"
        if note:
            reason += f"; user note: {note}"
        return False, reason

    def _prompt(self, name: str, arguments: dict[str, Any]) -> tuple[str, str]:
        options = "[y]允许 / [n]拒绝（可附原因，如：n 先列出来）"
        if name in REMEMBERABLE:
            options += " / [a]本次运行一直允许"
        line = self.ask(
            f"⚠️  Agent 想执行：{name}\n{render_call(name, arguments)}\n{options} > "
        ).strip()
        answer, _, note = line.partition(" ")
        return answer.lower(), note.strip()
