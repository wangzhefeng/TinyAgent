"""JsonlTracer: append-only event stream for observability (ADR-0003)."""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any


class JsonlTracer:
    """Write one JSONL line per event under ``<root>/<run_id>.jsonl``."""

    def __init__(self, run_id: str | None = None, root: str | Path | None = None) -> None:
        self.run_id = run_id or uuid.uuid4().hex[:12]
        self.root = Path(root) if root is not None else Path("logs/tinyagent/traces")
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / f"{self.run_id}.jsonl"

    def emit(self, event: str, data: dict[str, Any] | None = None) -> None:
        """Record one event with a timestamp."""
        record = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "event": event,
                  "data": data or {}}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
