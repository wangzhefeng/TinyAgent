"""Domain records for the personal agent runtime."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Any

from ..core.types import Message


@dataclass(frozen=True)
class RunRecord:
    """One durable agent run."""

    id: str
    session_id: str
    kind: str
    status: str
    input: str
    output: str
    usage: dict[str, Any]
    error: str | None
    created_at: str
    updated_at: str
    version: int

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> RunRecord:
        """Create a record from a SQLite row."""
        import json

        return cls(
            id=row["id"],
            session_id=row["session_id"],
            kind=row["kind"],
            status=row["status"],
            input=row["input"],
            output=row["output"] or "",
            usage=json.loads(row["usage_json"]),
            error=row["error"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            version=row["version"],
        )


@dataclass(frozen=True)
class EventRecord:
    """One append-only session event."""

    event_id: str
    parent_event_id: str | None
    session_id: str
    run_id: str
    seq: int
    type: str
    data: dict[str, Any]
    ts: str
    schema_version: int

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> EventRecord:
        """Create an event from a SQLite row."""
        import json

        return cls(
            event_id=row["event_id"],
            parent_event_id=row["parent_event_id"],
            session_id=row["session_id"],
            run_id=row["run_id"],
            seq=row["seq"],
            type=row["type"],
            data=json.loads(row["data_json"]),
            ts=row["ts"],
            schema_version=row["schema_version"],
        )


@dataclass
class ContextView:
    """Model-facing projection of raw session events."""

    messages: list[Message]
    source_seq: int
    artifacts: list[str] = field(default_factory=list)
    estimated: bool = True
    estimated_tokens: int = 0
    usage: dict[str, Any] = field(default_factory=dict)
    needs_compaction: bool = False
