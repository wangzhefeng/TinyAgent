"""Short-term list memory plus file-backed long-term memory (ADR-0007).

`hello_agents/src/memory/` 的设计意图（README 承诺的 embedding 检索长期记忆）
在此兑现为无重依赖的实现：JSONL 存储 + 可选 embedding 余弦检索，
无 API key 时自动退化为关键词检索。
"""

from __future__ import annotations

import json
import math
import os
import time
from pathlib import Path
from typing import Any

from .types import Message


class ListMemory:
    """Minimal short-term memory: an in-memory message buffer."""

    def __init__(self) -> None:
        self._messages: list[Message] = []

    def add(self, message: Message) -> None:
        """Buffer one message."""
        self._messages.append(message)

    def all(self) -> list[Message]:
        """Return the buffered messages."""
        return list(self._messages)

    def clear(self) -> None:
        """Drop all buffered messages."""
        self._messages.clear()


class FileLongTermMemory:
    """Long-term memory persisted as JSONL with best-effort retrieval.

    Retrieval uses embedding cosine similarity when the configured
    OpenAI-compatible endpoint is reachable; otherwise it falls back to
    keyword overlap scoring so the memory stays usable offline.
    """

    def __init__(self, path: str | Path | None = None, embed: bool = True) -> None:
        self.path = Path(path) if path is not None else Path(
            "logs/tinyagent/memory.jsonl"
        )
        self.embed = embed
        self._client = None

    # ---------------- storage ----------------
    def add(self, text: str, meta: dict[str, Any] | None = None) -> None:
        """Append one memory record (text + optional metadata)."""
        record: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "text": text,
            "meta": meta or {},
        }
        vec = self._embed_one(text)
        if vec is not None:
            record["vec"] = vec
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def all(self) -> list[dict[str, Any]]:
        """Load all records (oldest first)."""
        if not self.path.exists():
            return []
        return [
            json.loads(line)
            for line in self.path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    # ---------------- retrieval ----------------
    def retrieve(self, query: str, k: int = 3) -> list[dict[str, Any]]:
        """Return the top-k most relevant records for the query."""
        records = self.all()
        if not records:
            return []
        query_vec = self._embed_one(query)
        if query_vec is not None and any("vec" in r for r in records):
            scored = [
                (self._cosine(query_vec, r["vec"]), r)
                for r in records
                if "vec" in r
            ]
        else:
            scored = [(self._keyword_score(query, r["text"]), r) for r in records]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _s, r in scored[:k]]

    # ---------------- internals ----------------
    def _get_client(self):
        if self._client is None and self.embed:
            try:
                from dotenv import load_dotenv
                from openai import OpenAI

                load_dotenv()
                api_key = os.environ.get("LLM_API_KEY")
                if not api_key:
                    return None
                self._client = OpenAI(
                    api_key=api_key,
                    base_url=os.environ.get(
                        "LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"
                    ),
                )
            except Exception:  # noqa: BLE001
                return None
        return self._client

    def _embed_one(self, text: str) -> list[float] | None:
        client = self._get_client()
        if client is None:
            return None
        try:
            resp = client.embeddings.create(
                model=os.environ.get("LLM_EMBEDDING_MODEL", "embedding-3"),
                input=text,
            )
            return list(resp.data[0].embedding)
        except Exception:  # noqa: BLE001
            return None

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        return dot / (na * nb) if na and nb else 0.0

    @staticmethod
    def _keyword_score(query: str, text: str) -> float:
        """Offline fallback: character bigram overlap between query and text."""
        def bigrams(s: str) -> set[str]:
            s = "".join(s.split())
            return {s[i:i + 2] for i in range(len(s) - 1)} or {s}

        qa, ta = bigrams(query), bigrams(text)
        return len(qa & ta) / len(qa) if qa else 0.0
