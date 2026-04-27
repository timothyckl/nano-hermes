"""SQLite-backed memory provider with FTS search."""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nanobot.agent.memory_providers.base import BaseMemoryProvider


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class SQLiteMemoryProvider(BaseMemoryProvider):
    def __init__(self, workspace: Path, db_path: Path | None = None):
        self.workspace = Path(workspace)
        self.memory_dir = self.workspace / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path or self.memory_dir / "memory.db"
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS memory_entries (
                id TEXT PRIMARY KEY,
                target TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT NOT NULL DEFAULT '[]',
                source TEXT,
                confidence REAL DEFAULT 1.0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                deleted_at TEXT
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS memory_entries_fts USING fts5(id UNINDEXED, target UNINDEXED, content, tags);
            CREATE TABLE IF NOT EXISTS learning_events (
                id TEXT PRIMARY KEY,
                kind TEXT,
                target TEXT,
                content TEXT,
                evidence TEXT,
                confidence REAL DEFAULT 0.0,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                retry_count INTEGER DEFAULT 0,
                reason TEXT
            );
            """)

    def _read_target(self, target: str) -> str:
        with self._connect() as db:
            rows = db.execute("SELECT content FROM memory_entries WHERE target=? AND deleted_at IS NULL ORDER BY created_at", (target,)).fetchall()
        return "\n".join(f"- {r['content']}" for r in rows)

    def _write_target(self, target: str, content: str) -> None:
        with self._connect() as db:
            now = _now()
            db.execute("UPDATE memory_entries SET deleted_at=?, updated_at=? WHERE target=? AND deleted_at IS NULL", (now, now, target))
            for line in content.splitlines():
                clean = line.strip().lstrip("- ").strip()
                if clean:
                    self._insert_entry(db, target, clean, {})

    def read_user(self) -> str: return self._read_target("user")
    def write_user(self, content: str) -> None: self._write_target("user", content)
    def read_soul(self) -> str: return self._read_target("soul")
    def write_soul(self, content: str) -> None: self._write_target("soul", content)
    def read_memory(self) -> str: return self._read_target("memory")
    def write_memory(self, content: str) -> None: self._write_target("memory", content)

    def _insert_entry(self, db: sqlite3.Connection, target: str, content: str, metadata: dict[str, Any]) -> str:
        entry_id = uuid.uuid4().hex[:12]
        now = _now()
        tags = metadata.get("tags", []) if isinstance(metadata, dict) else []
        tags_json = json.dumps(tags, ensure_ascii=False)
        db.execute(
            "INSERT INTO memory_entries(id,target,content,tags,source,confidence,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
            (entry_id, target, content, tags_json, metadata.get("source") if metadata else None, float(metadata.get("confidence", 1.0)) if metadata else 1.0, now, now),
        )
        db.execute("INSERT INTO memory_entries_fts(id,target,content,tags) VALUES(?,?,?,?)", (entry_id, target, content, tags_json))
        return entry_id

    def add_entry(self, target: str, content: str, metadata: dict[str, Any] | None = None) -> str:
        target = {"project": "memory", "agent": "soul", "profile": "user"}.get(target, target)
        if target not in {"user", "soul", "memory"}:
            raise ValueError("invalid target")
        with self._connect() as db:
            return self._insert_entry(db, target, content.strip(), metadata or {})

    def replace_entry(self, target: str, old_text: str, new_text: str) -> None:
        with self._connect() as db:
            row = db.execute("SELECT id, content FROM memory_entries WHERE target=? AND content LIKE ? AND deleted_at IS NULL LIMIT 1", (target, f"%{old_text}%")).fetchone()
            if not row:
                raise ValueError("old_text not found")
            content = row["content"].replace(old_text, new_text, 1)
            now = _now()
            db.execute("UPDATE memory_entries SET content=?, updated_at=? WHERE id=?", (content, now, row["id"]))
            db.execute("UPDATE memory_entries_fts SET content=? WHERE id=?", (content, row["id"]))

    def remove_entry(self, target: str, old_text: str) -> None:
        now = _now()
        with self._connect() as db:
            cur = db.execute("UPDATE memory_entries SET deleted_at=?, updated_at=? WHERE target=? AND content LIKE ? AND deleted_at IS NULL", (now, now, target, f"%{old_text}%"))
            if cur.rowcount == 0:
                raise ValueError("old_text not found")

    def search_memory(self, query: str, limit: int = 8) -> list[dict[str, Any]]:
        with self._connect() as db:
            try:
                rows = db.execute(
                    "SELECT m.id,m.target,m.content,m.tags,bm25(memory_entries_fts) AS rank FROM memory_entries_fts JOIN memory_entries m USING(id) WHERE memory_entries_fts MATCH ? AND m.deleted_at IS NULL ORDER BY rank LIMIT ?",
                    (query, limit),
                ).fetchall()
            except sqlite3.OperationalError:
                rows = db.execute("SELECT id,target,content,tags,0 AS rank FROM memory_entries WHERE deleted_at IS NULL AND content LIKE ? LIMIT ?", (f"%{query}%", limit)).fetchall()
        return [{"id": r["id"], "target": r["target"], "content": r["content"], "tags": json.loads(r["tags"] or "[]"), "score": -float(r["rank"] or 0)} for r in rows]

    def append_learning_event(self, event: dict[str, Any]) -> str:
        event_id = str(event.get("id") or uuid.uuid4().hex[:12])
        now = _now()
        with self._connect() as db:
            db.execute(
                "INSERT INTO learning_events(id,kind,target,content,evidence,confidence,status,created_at,updated_at,reason) VALUES(?,?,?,?,?,?,?,?,?,?)",
                (event_id, event.get("kind"), event.get("target"), event.get("content"), event.get("evidence"), float(event.get("confidence", 0.0)), event.get("status", "pending"), event.get("created_at", now), now, event.get("reason")),
            )
        return event_id

    def read_learning_events(self, status: str = "pending", limit: int = 50) -> list[dict[str, Any]]:
        sql = "SELECT * FROM learning_events" if status == "all" else "SELECT * FROM learning_events WHERE status=?"
        params: tuple[Any, ...] = () if status == "all" else (status,)
        with self._connect() as db:
            rows = db.execute(sql + " ORDER BY created_at LIMIT ?", (*params, limit)).fetchall()
        return [dict(r) for r in rows]

    def update_learning_event(self, event_id: str, status: str, reason: str | None = None) -> None:
        with self._connect() as db:
            cur = db.execute("UPDATE learning_events SET status=?, reason=COALESCE(?, reason), updated_at=? WHERE id=?", (status, reason, _now(), event_id))
            if cur.rowcount == 0:
                raise ValueError("learning event not found")
