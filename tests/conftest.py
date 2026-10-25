"""Shared fixtures: a scripted ChatModel for offline loop tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "packages" / "tinyagent-core" / "src"))

from tinyagent.core.types import ModelReply  # noqa: E402


class ScriptedModel:
    """Pop scripted replies; record every call for assertions."""

    def __init__(self, replies: list[ModelReply]) -> None:
        self.replies = list(replies)
        self.calls: list[dict] = []

    def chat(self, messages, tools=None):  # noqa: ANN001, ANN202
        self.calls.append(
            {"n_messages": len(messages), "tools": [t.name for t in (tools or [])]}
        )
        return self.replies.pop(0)


@pytest.fixture
def scripted_model():
    """Factory fixture building a ScriptedModel."""
    return ScriptedModel
