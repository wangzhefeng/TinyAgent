"""Shared fixtures: a scripted ChatModel for offline loop tests."""

from __future__ import annotations

import pytest

from tinyagent.core.types import ModelReply


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
