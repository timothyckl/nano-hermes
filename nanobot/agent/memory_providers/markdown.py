"""Markdown/file-backed memory provider."""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nanobot.agent.memory_providers.base import BaseMemoryProvider

_TARGETS = {"user", "soul", "memory"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class MarkdownMemoryProvider(BaseMemoryProvider):
    def __init__(self, workspace: Path):
        self.workspace = Path(workspace)
        self.memory_dir = self.workspace / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.user_file = self.workspace / "USER.md"
        self.soul_file = self.workspace / "SOUL.md"
        self.memory_file = self.memory_dir / "MEMORY.md"
        self.learning_file = self.memory_dir / "learning_queue.jsonl"

    @staticmethod
    def _normalize_target(target: str) -> str:
        target = (target or "memory").lower().strip()
        target = {"project": "memory", "agent": "soul", "profile": "user"}.get(target, target)
        if target not in _TARGETS:
            raise ValueError(f"target must be one of {sorted(_TARGETS)}")
        return target

    def _path_for(self, target: str) -> Path:
        return {"user": self.user_file, "soul": self.soul_file, "memory": self.memory_file}[self._normalize_target(target)]

    @staticmethod
    def _read(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return ""

    @staticmethod
    def _write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def read_user(self) -> str: return self._read(self.user_file)
    def write_user(self, content: str) -> None: self._write(self.user_file, content)
    def read_soul(self) -> str: return self._read(self.soul_file)
    def write_soul(self, content: str) -> None: self._write(self.soul_file, content)
    def read_memory(self) -> str: return self._read(self.memory_file)
    def write_memory(self, content: str) -> None: self._write(self.memory_file, content)

    def add_entry(self, target: str, content: str, metadata: dict[str, Any] | None = None) -> str:
        content = content.strip()
        if not content:
            raise ValueError("content must not be empty")
        entry_id = uuid.uuid4().hex[:12]
        suffix = f"  <!-- memory:{entry_id}"
        if metadata:
            suffix += " " + json.dumps(metadata, ensure_ascii=False, sort_keys=True)
        suffix += " -->"
        path = self._path_for(target)
        existing = self._read(path).rstrip()
        self._write(path, (existing + "\n" if existing else "") + f"- {content}{suffix}\n")
        return entry_id

    def replace_entry(self, target: str, old_text: str, new_text: str) -> None:
        path = self._path_for(target)
        text = self._read(path)
        if old_text not in text:
            raise ValueError("old_text not found")
        self._write(path, text.replace(old_text, new_text, 1))

    def remove_entry(self, target: str, old_text: str) -> None:
        path = self._path_for(target)
        lines = self._read(path).splitlines()
        kept = [line for line in lines if old_text not in line]
        if len(kept) == len(lines):
            raise ValueError("old_text not found")
        self._write(path, "\n".join(kept).rstrip() + ("\n" if kept else ""))

    def search_memory(self, query: str, limit: int = 8) -> list[dict[str, Any]]:
        terms = [t.lower() for t in re.findall(r"\w+", query or "")]
        results: list[dict[str, Any]] = []
        for target in ("user", "soul", "memory"):
            for i, line in enumerate(self._read(self._path_for(target)).splitlines(), start=1):
                score = sum(1 for term in terms if term in line.lower()) if terms else 1
                if score:
                    results.append({"target": target, "line": i, "content": line, "score": score})
        results.sort(key=lambda r: (-r["score"], r["target"], r["line"]))
        return results[: max(0, limit)]

    def append_learning_event(self, event: dict[str, Any]) -> str:
        event_id = str(event.get("id") or uuid.uuid4().hex[:12])
        record = {**event, "id": event_id, "status": event.get("status", "pending"), "created_at": event.get("created_at", _now()), "updated_at": _now()}
        self.learning_file.parent.mkdir(parents=True, exist_ok=True)
        with self.learning_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return event_id

    def _read_all_events(self) -> list[dict[str, Any]]:
        events = []
        try:
            lines = self.learning_file.read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            return []
        for line in lines:
            if line.strip():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return events

    def read_learning_events(self, status: str = "pending", limit: int = 50) -> list[dict[str, Any]]:
        events = [e for e in self._read_all_events() if status == "all" or e.get("status") == status]
        return events[: max(0, limit)]

    def update_learning_event(self, event_id: str, status: str, reason: str | None = None) -> None:
        events = self._read_all_events()
        found = False
        for event in events:
            if event.get("id") == event_id:
                event["status"] = status
                event["updated_at"] = _now()
                if reason is not None:
                    event["reason"] = reason
                found = True
        if not found:
            raise ValueError("learning event not found")
        self.learning_file.write_text("".join(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n" for e in events), encoding="utf-8")
