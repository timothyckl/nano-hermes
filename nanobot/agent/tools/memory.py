"""Tool for curated durable memory operations."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nanobot.agent.memory_providers.markdown import MarkdownMemoryProvider
from nanobot.agent.tools.base import Tool, tool_parameters


@tool_parameters({
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["read", "add", "replace", "remove", "search", "queue", "events", "update_event"]},
        "target": {"type": "string", "enum": ["user", "soul", "memory", "project", "agent", "profile"]},
        "content": {"type": "string"},
        "old_text": {"type": "string"},
        "new_text": {"type": "string"},
        "query": {"type": "string"},
        "event_id": {"type": "string"},
        "status": {"type": "string"},
        "reason": {"type": "string"},
        "limit": {"type": "integer", "minimum": 1, "maximum": 50}
    },
    "required": ["action"]
})
class MemoryTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = Path(workspace)
        self._provider: MarkdownMemoryProvider | None = None

    @property
    def provider(self) -> MarkdownMemoryProvider:
        if self._provider is None:
            self._provider = MarkdownMemoryProvider(self.workspace)
        return self._provider

    @property
    def name(self) -> str:
        return "memory"

    @property
    def description(self) -> str:
        return "Read, search, and update curated durable memory; queue learning events for later review."

    async def execute(self, **kwargs: Any) -> str:
        action = kwargs.get("action")
        target = kwargs.get("target") or "memory"
        if action == "read":
            return {"user": self.provider.read_user, "soul": self.provider.read_soul, "memory": self.provider.read_memory, "project": self.provider.read_memory, "agent": self.provider.read_soul, "profile": self.provider.read_user}[target]()
        if action == "add":
            entry_id = self.provider.add_entry(target, kwargs.get("content", ""), {"source": "memory_tool"})
            return f"Memory added: {entry_id}"
        if action == "replace":
            self.provider.replace_entry(target, kwargs.get("old_text", ""), kwargs.get("new_text", ""))
            return "Memory replaced."
        if action == "remove":
            self.provider.remove_entry(target, kwargs.get("old_text", ""))
            return "Memory removed."
        if action == "search":
            return json.dumps(self.provider.search_memory(kwargs.get("query", ""), int(kwargs.get("limit") or 8)), ensure_ascii=False, indent=2)
        if action == "queue":
            event_id = self.provider.append_learning_event({"kind": "memory_candidate", "target": target, "content": kwargs.get("content", "")})
            return f"Learning event queued: {event_id}"
        if action == "events":
            return json.dumps(self.provider.read_learning_events(kwargs.get("status", "pending"), int(kwargs.get("limit") or 20)), ensure_ascii=False, indent=2)
        if action == "update_event":
            self.provider.update_learning_event(kwargs.get("event_id", ""), kwargs.get("status", "pending"), kwargs.get("reason"))
            return "Learning event updated."
        return "Error: unknown memory action"
