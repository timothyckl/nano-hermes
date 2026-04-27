"""Tool for recalling prior sessions without polluting durable memory."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool, tool_parameters
from nanobot.session.database import SessionDatabase


@tool_parameters({
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["recent", "search", "inspect"]},
        "query": {"type": "string"},
        "session_id": {"type": "string"},
        "limit": {"type": "integer", "minimum": 1, "maximum": 50}
    },
    "required": ["action"]
})
class SessionSearchTool(Tool):
    def __init__(self, workspace: Path, database: SessionDatabase | None = None):
        self.workspace = Path(workspace)
        self._database = database

    @property
    def database(self) -> SessionDatabase:
        if self._database is None:
            self._database = SessionDatabase(self.workspace / "memory" / "sessions.db")
        return self._database

    @property
    def name(self) -> str:
        return "session_search"

    @property
    def description(self) -> str:
        return "Search or inspect past session history separately from durable memory."

    @property
    def read_only(self) -> bool:
        return True

    async def execute(self, **kwargs: Any) -> str:
        action = kwargs.get("action")
        limit = int(kwargs.get("limit") or 5)
        if action == "recent":
            return json.dumps(self.database.recent(limit), ensure_ascii=False, indent=2)
        if action == "search":
            return json.dumps(self.database.search(kwargs.get("query", ""), limit), ensure_ascii=False, indent=2)
        if action == "inspect":
            return self.database.summarize_session(kwargs.get("session_id", ""), limit=limit)
        return "Error: unknown session_search action"
