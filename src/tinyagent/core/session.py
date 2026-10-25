"""FileSessionStore: per-session JSONL messages plus a state file (ADR-0003)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .types import Message


class FileSessionStore:
    """Persist session messages and state under ``<root>/<session_id>/``."""

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path("logs/tinyagent/sessions")

    def _dir(self, session_id: str) -> Path:
        return self.root / session_id

    def append_message(self, session_id: str, message: Message) -> None:
        """Append one message as a JSONL line."""
        d = self._dir(session_id)
        d.mkdir(parents=True, exist_ok=True)
        (d / "messages.jsonl").open("a", encoding="utf-8").write(
            json.dumps(message.to_dict(), ensure_ascii=False) + "\n"
        )

    def load_messages(self, session_id: str) -> list[Message]:
        """Load all messages of a session (empty list if none)."""
        f = self._dir(session_id) / "messages.jsonl"
        if not f.exists():
            return []
        return [
            Message.from_dict(json.loads(line))
            for line in f.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def save_state(self, session_id: str, state: dict[str, Any]) -> None:
        """Persist an arbitrary JSON-able state dict."""
        d = self._dir(session_id)
        d.mkdir(parents=True, exist_ok=True)
        (d / "state.json").write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def load_state(self, session_id: str) -> dict[str, Any]:
        """Load the state dict of a session (empty dict if none)."""
        f = self._dir(session_id) / "state.json"
        if not f.exists():
            return {}
        return json.loads(f.read_text(encoding="utf-8"))
