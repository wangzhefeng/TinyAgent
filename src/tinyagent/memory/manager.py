"""Manage capped USER/MEMORY files and frozen session snapshots."""

from __future__ import annotations

import os
from pathlib import Path


class MemoryManager:
    """Persist stable user preferences and long-term environment notes."""

    def __init__(
        self,
        state_dir: str | Path,
        user_limit: int = 2000,
        memory_limit: int = 3000,
    ) -> None:
        self.state_dir = Path(state_dir).expanduser().resolve()
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.user_path = self.state_dir / "USER.md"
        self.memory_path = self.state_dir / "MEMORY.md"
        self.user_limit = user_limit
        self.memory_limit = memory_limit

    def snapshot(self) -> dict[str, str]:
        """Return the memory snapshot used at session start."""
        return {
            "user": self.user_path.read_text(encoding="utf-8") if self.user_path.exists() else "",
            "memory": self.memory_path.read_text(encoding="utf-8") if self.memory_path.exists() else "",
        }

    def remember(
        self,
        action: str,
        text: str = "",
        old: str = "",
        scope: str = "memory",
    ) -> str:
        """Add, replace, or remove one stable memory entry."""
        path, limit = self._target(scope)
        entries = self._entries(path)
        text = " ".join(text.split())
        if action == "add":
            if not text:
                return "Error: add requires text"
            entries.append(text)
        elif action in {"replace", "remove"}:
            matches = [index for index, entry in enumerate(entries) if old and old in entry]
            if len(matches) != 1:
                return f"Error: old must match exactly one entry, got {len(matches)}"
            index = matches[0]
            if action == "replace":
                if not text:
                    return "Error: replace requires text"
                entries[index] = text
            else:
                entries.pop(index)
        else:
            return "Error: action must be add, replace, or remove"
        total = sum(len(entry) + 3 for entry in entries)
        if total > limit:
            return f"Error: memory exceeds {limit} characters ({total}); merge or remove entries first"
        self._write(path, entries)
        return f"Updated {path.name} ({len(entries)} entries, {total}/{limit} characters)"

    def _target(self, scope: str) -> tuple[Path, int]:
        if scope == "user":
            return self.user_path, self.user_limit
        if scope == "memory":
            return self.memory_path, self.memory_limit
        raise ValueError("scope must be user or memory")

    @staticmethod
    def _entries(path: Path) -> list[str]:
        if not path.exists():
            return []
        return [
            line[2:].strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.startswith("- ") and line[2:].strip()
        ]

    @staticmethod
    def _write(path: Path, entries: list[str]) -> None:
        temporary = path.with_suffix(".tmp")
        temporary.write_text("".join(f"- {entry}\n" for entry in entries), encoding="utf-8")
        os.replace(temporary, path)
