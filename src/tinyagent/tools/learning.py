"""Tools for personal memory, session recall, and reviewed skills."""

from __future__ import annotations

from ..core.tools import ToolWrapper, tool
from ..memory import MemoryManager
from ..runtime.store import SQLiteStore
from ..skills import SkillManager


def make_learning_tools(
    memory: MemoryManager,
    skills: SkillManager,
    store: SQLiteStore,
) -> list[ToolWrapper]:
    """Create memory, retrieval, and skill tools."""
    @tool
    def remember(action: str, text: str = "", old: str = "", scope: str = "memory") -> str:
        """Store stable long-term facts, never one-time task progress.

        Use add, replace, or remove. scope=user is for user preferences; scope=memory
        is for environment conventions and repeated lessons. Writes are audited.
        """
        return memory.remember(action, text=text, old=old, scope=scope)

    @tool
    def search_sessions(query: str) -> str:
        """Search past conversations with FTS5 and return short cited snippets."""
        hits = store.search_sessions(query)
        if not hits:
            return "No matching past conversations"
        return "\n".join(
            f"[{hit['session_id']}:{hit['event_id']} · {hit['role']}] {hit['snippet']}"
            for hit in hits
        )

    @tool
    def load_skill(name: str) -> str:
        """Load the full body of a reviewed skill by name."""
        return skills.load(name)

    @tool
    def create_skill_draft(name: str, description: str, body: str) -> str:
        """Create a skill draft that requires human approval before it can be used."""
        return skills.create_draft(name, description, body)

    return [remember, search_sessions, load_skill, create_skill_draft]
