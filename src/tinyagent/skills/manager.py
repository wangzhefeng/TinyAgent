"""Manage reviewed skills and separately staged drafts."""

from __future__ import annotations

import os
import re
from pathlib import Path

_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


class SkillManager:
    """Load reviewed skills and keep unreviewed drafts separate."""

    def __init__(self, state_dir: str | Path) -> None:
        self.state_dir = Path(state_dir).expanduser().resolve()
        self.skills_dir = self.state_dir / "skills"
        self.drafts_dir = self.state_dir / "skill-drafts"
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.drafts_dir.mkdir(parents=True, exist_ok=True)

    def catalog(self) -> str:
        """Return the name-and-description catalog for the system prompt."""
        lines = []
        for path in sorted(self.skills_dir.glob("*/SKILL.md")):
            meta, _ = self._parse(path.read_text(encoding="utf-8"))
            if meta.get("description"):
                lines.append(f"- {meta.get('name') or path.parent.name}: {meta['description']}")
        return "\n".join(lines)

    def load(self, name: str) -> str:
        """Load one reviewed skill body and list optional attachments."""
        path = self.skills_dir / name / "SKILL.md"
        if not path.is_file():
            return f"Error: reviewed skill not found: {name}"
        _, body = self._parse(path.read_text(encoding="utf-8"))
        extras = sorted(item.name for item in path.parent.iterdir() if item.name != "SKILL.md")
        suffix = f"\n\nAttachments: {', '.join(extras)}" if extras else ""
        return f"[skill] {name}\n{body}{suffix}"

    def create_draft(self, name: str, description: str, body: str) -> str:
        """Write one skill draft that cannot be loaded as a reviewed skill."""
        if not _NAME_PATTERN.fullmatch(name):
            return "Error: skill name must contain only lowercase letters, digits, and hyphens"
        if not description.strip() or not body.strip():
            return "Error: description and body are required"
        target_dir = self.drafts_dir / name
        target_dir.mkdir(exist_ok=True)
        target = target_dir / "SKILL.md"
        target.write_text(
            f"---\nname: {name}\ndescription: {description.strip()}\n---\n{body.strip()}\n",
            encoding="utf-8",
        )
        return f"Draft created: {target}; human approval is required before use"

    def approve_draft(self, name: str) -> Path:
        """Move a draft into the reviewed read-only skills directory."""
        source = self.drafts_dir / name / "SKILL.md"
        if not source.is_file():
            raise FileNotFoundError(f"draft not found: {name}")
        target_dir = self.skills_dir / name
        target_dir.mkdir(exist_ok=True)
        target = target_dir / "SKILL.md"
        os.replace(source, target)
        try:
            (self.drafts_dir / name).rmdir()
        except OSError:
            pass
        return target

    @staticmethod
    def _parse(text: str) -> tuple[dict[str, str], str]:
        lines = text.splitlines()
        if not lines or lines[0].strip() != "---":
            return {}, text.strip()
        meta: dict[str, str] = {}
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                return meta, "\n".join(lines[index + 1:]).strip()
            key, separator, value = line.partition(":")
            if separator:
                meta[key.strip()] = value.strip()
        return {}, text.strip()
