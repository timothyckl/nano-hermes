"""SQLite session index with FTS search for past conversation recall."""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class SessionDatabase:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        return db

    def _init_db(self) -> None:
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                key TEXT,
                channel TEXT,
                chat_id TEXT,
                title TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata_json TEXT DEFAULT '{}'
            );
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                content_json TEXT,
                timestamp TEXT NOT NULL,
                tool_name TEXT,
                tool_call_id TEXT,
                metadata_json TEXT DEFAULT '{}',
                token_count INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS turns (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_message_id TEXT,
                assistant_message_id TEXT,
                summary TEXT,
                outcome TEXT,
                tools_used_json TEXT DEFAULT '[]',
                created_at TEXT NOT NULL
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS session_fts USING fts5(message_id UNINDEXED, session_id UNINDEXED, title, content, summary);
            """)

    def ensure_session(self, session_id: str, *, key: str | None = None, channel: str | None = None, chat_id: str | None = None, title: str | None = None, metadata: dict[str, Any] | None = None) -> None:
        now = _now()
        with self._connect() as db:
            db.execute(
                "INSERT INTO sessions(id,key,channel,chat_id,title,created_at,updated_at,metadata_json) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET updated_at=excluded.updated_at,title=COALESCE(excluded.title,sessions.title)",
                (session_id, key, channel, chat_id, title, now, now, json.dumps(metadata or {}, ensure_ascii=False)),
            )

    def append_message(self, session_id: str, *, role: str, content: str, title: str | None = None, metadata: dict[str, Any] | None = None, tool_name: str | None = None, tool_call_id: str | None = None, timestamp: str | None = None) -> str:
        self.ensure_session(session_id, title=title)
        message_id = uuid.uuid4().hex[:12]
        ts = timestamp or _now()
        with self._connect() as db:
            db.execute(
                "INSERT INTO messages(id,session_id,role,content,timestamp,tool_name,tool_call_id,metadata_json) VALUES(?,?,?,?,?,?,?,?)",
                (message_id, session_id, role, content, ts, tool_name, tool_call_id, json.dumps(metadata or {}, ensure_ascii=False)),
            )
            db.execute("UPDATE sessions SET updated_at=?, title=COALESCE(title, ?) WHERE id=?", (ts, title, session_id))
            db.execute("INSERT INTO session_fts(message_id,session_id,title,content,summary) VALUES(?,?,?,?,?)", (message_id, session_id, title or "", content, ""))
        return message_id

    def recent(self, limit: int = 10) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute("SELECT * FROM sessions ORDER BY updated_at DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        with self._connect() as db:
            try:
                rows = db.execute(
                    "SELECT f.session_id, f.message_id, f.title, f.content, bm25(session_fts) AS rank, m.role, m.timestamp FROM session_fts f JOIN messages m ON m.id=f.message_id WHERE session_fts MATCH ? ORDER BY rank LIMIT ?",
                    (query, limit),
                ).fetchall()
            except sqlite3.OperationalError:
                rows = db.execute("SELECT session_id, id AS message_id, '' AS title, content, 0 AS rank, role, timestamp FROM messages WHERE content LIKE ? ORDER BY timestamp DESC LIMIT ?", (f"%{query}%", limit)).fetchall()
        return [dict(r) for r in rows]

    def summarize_session(self, session_id: str, limit: int = 20) -> str:
        with self._connect() as db:
            rows = db.execute("SELECT role, content FROM messages WHERE session_id=? ORDER BY timestamp DESC LIMIT ?", (session_id, limit)).fetchall()
        return "\n".join(f"{r['role']}: {r['content']}" for r in reversed(rows))
