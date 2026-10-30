"""SQLite persistence for runs, sessions, events, and approvals."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ..agent.types import EventRecord, RunRecord

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    status TEXT NOT NULL,
    input TEXT NOT NULL,
    output TEXT,
    usage_json TEXT NOT NULL,
    error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    version INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    parent_event_id TEXT,
    session_id TEXT NOT NULL,
    run_id TEXT NOT NULL,
    seq INTEGER NOT NULL,
    type TEXT NOT NULL,
    data_json TEXT NOT NULL,
    ts TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    UNIQUE(run_id, seq)
);
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    current_leaf TEXT,
    source TEXT NOT NULL,
    state_json TEXT NOT NULL,
    version INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS approvals (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    tool_call_id TEXT NOT NULL,
    action_json TEXT NOT NULL,
    status TEXT NOT NULL,
    decided_by TEXT,
    reason TEXT,
    created_at TEXT NOT NULL,
    resolved_at TEXT
);
CREATE TABLE IF NOT EXISTS idempotency_keys (
    scope TEXT NOT NULL,
    key TEXT NOT NULL,
    request_hash TEXT NOT NULL,
    run_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY(scope, key)
);
CREATE TABLE IF NOT EXISTS context_artifacts (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    source_start INTEGER,
    source_end INTEGER,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE VIRTUAL TABLE IF NOT EXISTS session_fts USING fts5(
    event_id UNINDEXED,
    session_id UNINDEXED,
    run_id UNINDEXED,
    role,
    content
);
CREATE TABLE IF NOT EXISTS scheduled_tasks (
    id TEXT PRIMARY KEY,
    spec TEXT NOT NULL,
    prompt TEXT NOT NULL,
    deliver_to TEXT NOT NULL,
    allow_json TEXT NOT NULL,
    kind TEXT NOT NULL,
    next_run TEXT NOT NULL,
    status TEXT NOT NULL,
    run_id TEXT,
    delivered_run_id TEXT,
    last_error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    version INTEGER NOT NULL
);
"""

_TRANSITIONS = {
    "queued": {"running", "cancelled"},
    "running": {"waiting_approval", "completed", "failed", "cancelled"},
    "waiting_approval": {"running", "cancelled"},
    "failed": {"running"},
    "cancelled": {"running"},
    "completed": set(),
}


def _now() -> str:
    return datetime.now(UTC).isoformat()


class SQLiteStore:
    """Own the single-writer SQLite state for the personal agent."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 30000")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(_SCHEMA)
            conn.execute(
                "INSERT INTO session_fts(event_id, session_id, run_id, role, content) "
                "SELECT event_id, session_id, run_id, "
                "CASE type WHEN 'user_input' THEN 'user' WHEN 'assistant_reply' THEN 'assistant' "
                "ELSE 'tool' END, "
                "CASE WHEN type = 'tool_result' THEN json_extract(data_json, '$.content') "
                "ELSE json_extract(data_json, '$.text') END "
                "FROM events WHERE type IN ('user_input', 'assistant_reply', 'tool_result') "
                "AND event_id NOT IN (SELECT event_id FROM session_fts)"
            )

    def create_run(
        self,
        session_id: str,
        input_text: str,
        idempotency_key: str | None = None,
        kind: str = "interactive",
    ) -> RunRecord:
        """Create a run and its start event atomically."""
        key = idempotency_key or uuid.uuid4().hex
        scope = f"{kind}:{session_id}"
        request_hash = hashlib.sha256(input_text.encode("utf-8")).hexdigest()
        run_id = uuid.uuid4().hex
        now = _now()
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT request_hash, run_id FROM idempotency_keys WHERE scope = ? AND key = ?",
                (scope, key),
            ).fetchone()
            if existing:
                if existing["request_hash"] != request_hash:
                    raise ValueError("idempotency key already used with different input")
                return self.get_run(existing["run_id"])
            conn.execute(
                "INSERT INTO runs VALUES (?, ?, ?, 'queued', ?, '', '{}', NULL, ?, ?, 1)",
                (run_id, session_id, kind, input_text, now, now),
            )
            conn.execute(
                "INSERT INTO idempotency_keys VALUES (?, ?, ?, ?, ?)",
                (scope, key, request_hash, run_id, now),
            )
            self._append_event(conn, run_id, session_id, "run_start", {"input": input_text})
        return self.get_run(run_id)

    def get_run(self, run_id: str) -> RunRecord:
        """Load one run by ID."""
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        if row is None:
            raise KeyError(f"unknown run: {run_id}")
        return RunRecord.from_row(row)

    def update_run_status(
        self,
        run_id: str,
        status: str,
        output: str | None = None,
        error: str | None = None,
        usage: dict[str, Any] | None = None,
    ) -> RunRecord:
        """Transition a run and optionally set output, error, and usage."""
        current = self.get_run(run_id)
        if status != current.status and status not in _TRANSITIONS[current.status]:
            raise ValueError(f"invalid run transition: {current.status} -> {status}")
        with self._connect() as conn:
            conn.execute(
                "UPDATE runs SET status = ?, output = ?, error = ?, usage_json = ?, "
                "updated_at = ?, version = version + 1 WHERE id = ?",
                (
                    status,
                    current.output if output is None else output,
                    current.error if error is None else error,
                    json.dumps(usage if usage is not None else current.usage),
                    _now(),
                    run_id,
                ),
            )
        return self.get_run(run_id)

    def append_event(
        self,
        run_id: str,
        event_type: str,
        data: dict[str, Any],
        parent_event_id: str | None = None,
    ) -> EventRecord:
        """Append one immutable event and advance the session leaf."""
        run = self.get_run(run_id)
        with self._connect() as conn:
            event_id = self._append_event(
                conn, run_id, run.session_id, event_type, data, parent_event_id
            )
        return self.get_event(event_id)

    def _append_event(
        self,
        conn: sqlite3.Connection,
        run_id: str,
        session_id: str,
        event_type: str,
        data: dict[str, Any],
        parent_event_id: str | None = None,
    ) -> str:
        now = _now()
        event_id = uuid.uuid4().hex
        row = conn.execute("SELECT MAX(seq) AS seq FROM events WHERE run_id = ?", (run_id,)).fetchone()
        seq = (row["seq"] or 0) + 1
        leaf = parent_event_id or self._current_leaf(conn, session_id)
        conn.execute(
            "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)",
            (event_id, leaf, session_id, run_id, seq, event_type, json.dumps(data), now),
        )
        if event_type in {"user_input", "assistant_reply", "tool_result"}:
            role = {"user_input": "user", "assistant_reply": "assistant", "tool_result": "tool"}[event_type]
            content = str(data.get("text" if event_type != "tool_result" else "content", ""))
            if content:
                conn.execute(
                    "INSERT INTO session_fts(event_id, session_id, run_id, role, content) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (event_id, session_id, run_id, role, content),
                )
        conn.execute(
            "INSERT INTO sessions(session_id, current_leaf, source, state_json, version, "
            "created_at, updated_at) VALUES (?, ?, 'cli', '{}', 1, ?, ?) "
            "ON CONFLICT(session_id) DO UPDATE SET current_leaf = excluded.current_leaf, "
            "version = sessions.version + 1, updated_at = excluded.updated_at",
            (session_id, event_id, now, now),
        )
        return event_id

    @staticmethod
    def _current_leaf(conn: sqlite3.Connection, session_id: str) -> str | None:
        row = conn.execute(
            "SELECT current_leaf FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        return row["current_leaf"] if row else None

    def get_event(self, event_id: str) -> EventRecord:
        """Load one event by ID."""
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
        if row is None:
            raise KeyError(f"unknown event: {event_id}")
        return EventRecord.from_row(row)

    def list_events(self, run_id: str) -> list[EventRecord]:
        """List one run's events in sequence order."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM events WHERE run_id = ? ORDER BY seq", (run_id,)
            ).fetchall()
        return [EventRecord.from_row(row) for row in rows]

    def session_events(self, session_id: str) -> list[EventRecord]:
        """List all events in one session following insertion order."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM events WHERE session_id = ? ORDER BY rowid", (session_id,)
            ).fetchall()
        return [EventRecord.from_row(row) for row in rows]

    def export_session(self, session_id: str) -> str:
        """Export raw session events as versioned JSONL."""
        records = [
            {"schema_version": event.schema_version, "run_id": event.run_id, "seq": event.seq,
             "event_id": event.event_id, "parent_event_id": event.parent_event_id,
             "type": event.type, "data": event.data, "ts": event.ts}
            for event in self.session_events(session_id)
        ]
        return "\n".join(json.dumps(record, ensure_ascii=False) for record in records)

    def create_approval(self, run_id: str, tool_call_id: str, action: dict[str, Any]) -> str:
        """Persist a pending approval request."""
        approval_id = uuid.uuid4().hex
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO approvals VALUES (?, ?, ?, ?, 'pending', NULL, NULL, ?, NULL)",
                (approval_id, run_id, tool_call_id, json.dumps(action), _now()),
            )
        return approval_id

    def resolve_approval(self, approval_id: str, allowed: bool, reason: str = "") -> None:
        """Resolve an approval once; conflicting decisions are rejected."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT status FROM approvals WHERE id = ?", (approval_id,)
            ).fetchone()
            if row is None:
                raise KeyError(f"unknown approval: {approval_id}")
            expected = "allowed" if allowed else "denied"
            if row["status"] != "pending" and row["status"] != expected:
                raise ValueError("approval already resolved with a conflicting decision")
            conn.execute(
                "UPDATE approvals SET status = ?, decided_by = 'user', reason = ?, "
                "resolved_at = ? WHERE id = ?",
                (expected, reason, _now(), approval_id),
            )

    def get_session_state(self, session_id: str) -> dict[str, Any]:
        """Load JSON state for one session."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT state_json FROM sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
        return json.loads(row["state_json"]) if row else {}

    def save_session_state(self, session_id: str, state: dict[str, Any]) -> None:
        """Persist JSON state without changing the session leaf."""
        with self._connect() as conn:
            conn.execute(
                "UPDATE sessions SET state_json = ?, version = version + 1, "
                "updated_at = ? WHERE session_id = ?",
                (json.dumps(state, ensure_ascii=False), _now(), session_id),
            )

    def create_context_artifact(
        self,
        session_id: str,
        kind: str,
        content: str,
        source_start: int | None,
        source_end: int | None,
    ) -> str:
        """Persist a derived context artifact such as a compaction summary."""
        artifact_id = uuid.uuid4().hex
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO context_artifacts VALUES (?, ?, ?, ?, ?, ?, ?)",
                (artifact_id, session_id, kind, source_start, source_end, content, _now()),
            )
        return artifact_id

    def latest_context_artifact(self, session_id: str, kind: str) -> dict[str, Any] | None:
        """Load the newest artifact of one kind."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM context_artifacts WHERE session_id = ? AND kind = ? "
                "ORDER BY created_at DESC, rowid DESC LIMIT 1",
                (session_id, kind),
            ).fetchone()
        return dict(row) if row else None

    def search_sessions(
        self,
        query: str,
        limit: int = 5,
        include_tools: bool = False,
    ) -> list[dict[str, Any]]:
        """Search indexed messages with FTS5 and return short source snippets."""
        words = query.split()
        if not words:
            return []
        role_filter = "" if include_tools else " AND role IN ('user', 'assistant')"
        candidates: dict[str, dict[str, Any]] = {}
        sessions_by_word: list[set[str]] = []
        with self._connect() as conn:
            for word in words:
                fts_query = f'"{word.replace(chr(34), chr(34) * 2)}"'
                rows = conn.execute(
                    "SELECT rowid, event_id, session_id, run_id, role, "
                    "snippet(session_fts, 4, '', '', '…', 16) AS snippet "
                    "FROM session_fts WHERE session_fts MATCH ?" + role_filter,
                    (fts_query,),
                ).fetchall()
                sessions_by_word.append({row["session_id"] for row in rows})
                for row in rows:
                    candidates[row["event_id"]] = dict(row)
        required_sessions = set.intersection(*sessions_by_word) if sessions_by_word else set()
        hits = [
            record for record in candidates.values()
            if record["session_id"] in required_sessions
        ]
        hits.sort(key=lambda record: record["rowid"], reverse=True)
        return hits[:limit]

    def create_scheduled_task(
        self,
        spec: str,
        prompt: str,
        deliver_to: str,
        allow: set[str],
        kind: str,
        next_run: str,
    ) -> dict[str, Any]:
        """Create one persistent scheduled task."""
        task_id = uuid.uuid4().hex[:8]
        now = _now()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO scheduled_tasks VALUES (?, ?, ?, ?, ?, ?, ?, 'active', NULL, NULL, "
                "NULL, ?, ?, 1)",
                (task_id, spec, prompt, deliver_to, json.dumps(sorted(allow)), kind, next_run, now, now),
            )
        return self.get_scheduled_task(task_id)

    def get_scheduled_task(self, task_id: str) -> dict[str, Any]:
        """Load one scheduled task."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM scheduled_tasks WHERE id = ?", (task_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"unknown scheduled task: {task_id}")
        return dict(row)

    def list_scheduled_tasks(self, deliver_to: str | None = None) -> list[dict[str, Any]]:
        """List active tasks, optionally scoped to one delivery target."""
        with self._connect() as conn:
            if deliver_to is None:
                rows = conn.execute(
                    "SELECT * FROM scheduled_tasks WHERE status = 'active' ORDER BY next_run"
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM scheduled_tasks WHERE status = 'active' AND deliver_to = ? "
                    "ORDER BY next_run",
                    (deliver_to,),
                ).fetchall()
        return [dict(row) for row in rows]

    def cancel_scheduled_task(self, task_id: str, deliver_to: str) -> bool:
        """Cancel one task owned by the delivery target."""
        with self._connect() as conn:
            cursor = conn.execute(
                "UPDATE scheduled_tasks SET status = 'cancelled', updated_at = ?, "
                "version = version + 1 WHERE id = ? AND deliver_to = ? AND status = 'active'",
                (_now(), task_id, deliver_to),
            )
        return cursor.rowcount > 0

    def due_scheduled_tasks(self, now: str) -> list[dict[str, Any]]:
        """Return tasks due at or before a timestamp."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM scheduled_tasks WHERE status = 'active' AND next_run <= ? "
                "ORDER BY next_run",
                (now,),
            ).fetchall()
        return [dict(row) for row in rows]

    def mark_scheduled_started(self, task_id: str, next_run: str) -> None:
        """Persist the next run before executing the current one."""
        with self._connect() as conn:
            conn.execute(
                "UPDATE scheduled_tasks SET next_run = ?, updated_at = ?, version = version + 1 "
                "WHERE id = ?",
                (next_run, _now(), task_id),
            )

    def attach_scheduled_run(self, task_id: str, run_id: str) -> None:
        """Attach a scheduled task to its current Run."""
        with self._connect() as conn:
            conn.execute(
                "UPDATE scheduled_tasks SET run_id = ?, last_error = NULL, updated_at = ?, "
                "version = version + 1 WHERE id = ?",
                (run_id, _now(), task_id),
            )

    def mark_scheduled_delivered(self, task_id: str, run_id: str) -> None:
        """Record a delivered Run to prevent duplicate delivery."""
        with self._connect() as conn:
            conn.execute(
                "UPDATE scheduled_tasks SET delivered_run_id = ?, updated_at = ?, "
                "version = version + 1 WHERE id = ?",
                (run_id, _now(), task_id),
            )

    def mark_scheduled_error(self, task_id: str, error: str) -> None:
        """Record a scheduled execution error."""
        with self._connect() as conn:
            conn.execute(
                "UPDATE scheduled_tasks SET last_error = ?, updated_at = ?, version = version + 1 "
                "WHERE id = ?",
                (error, _now(), task_id),
            )

    def scheduled_task_by_run(self, run_id: str) -> dict[str, Any] | None:
        """Find the scheduled task owning a Run."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM scheduled_tasks WHERE run_id = ?", (run_id,)
            ).fetchone()
        return dict(row) if row else None
