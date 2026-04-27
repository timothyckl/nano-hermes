"""Tool for skill discovery and maintenance."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nanobot.agent.skill_index import SkillIndex
from nanobot.agent.skill_validator import SkillValidator
from nanobot.agent.tools.base import Tool, tool_parameters

_ALLOWED_SUPPORT_DIRS = {"references", "templates", "scripts", "assets"}


@tool_parameters({
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["list", "search", "view", "create", "patch", "validate", "write_file", "remove_file"]},
        "name": {"type": "string"},
        "query": {"type": "string"},
        "content": {"type": "string"},
        "old_text": {"type": "string"},
        "new_text": {"type": "string"},
        "file_path": {"type": "string"},
        "limit": {"type": "integer", "minimum": 1, "maximum": 50}
    },
    "required": ["action"]
})
class SkillsTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = Path(workspace)
        self.skills_dir = self.workspace / "skills"

    @property
    def name(self) -> str:
        return "skills"

    @property
    def description(self) -> str:
        return "List, search, view, create, patch, and validate nanobot skills."

    def _skill_dir(self, name: str) -> Path:
        if not name or "/" in name or ".." in name:
            raise ValueError("invalid skill name")
        return self.skills_dir / name

    def _safe_support_path(self, name: str, file_path: str) -> Path:
        rel = Path(file_path)
        if rel.is_absolute() or ".." in rel.parts or not rel.parts or rel.parts[0] not in _ALLOWED_SUPPORT_DIRS:
            raise ValueError("supporting files must be under references/, templates/, scripts/, or assets/")
        base = self._skill_dir(name).resolve()
        target = (base / rel).resolve()
        if not str(target).startswith(str(base)):
            raise ValueError("path escapes skill directory")
        return target

    async def execute(self, **kwargs: Any) -> str:
        action = kwargs.get("action")
        name = kwargs.get("name") or ""
        if action == "list":
            return json.dumps(SkillIndex(self.workspace).entries(), ensure_ascii=False, indent=2)
        if action == "search":
            return json.dumps(SkillIndex(self.workspace).search(kwargs.get("query", ""), int(kwargs.get("limit") or 5)), ensure_ascii=False, indent=2)
        if action == "view":
            path = self._skill_dir(name) / "SKILL.md"
            file_path = kwargs.get("file_path")
            if file_path:
                path = self._safe_support_path(name, file_path)
            return path.read_text(encoding="utf-8")
        if action == "create":
            path = self._skill_dir(name) / "SKILL.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                return "Error: skill already exists"
            path.write_text(kwargs.get("content", ""), encoding="utf-8")
            report = SkillValidator().validate(path)
            if not report.valid:
                return "Error: invalid skill: " + "; ".join(report.errors)
            return f"Skill created: {name}"
        if action == "patch":
            path = self._skill_dir(name) / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            old = kwargs.get("old_text", "")
            if old not in text:
                return "Error: old_text not found"
            path.write_text(text.replace(old, kwargs.get("new_text", ""), 1), encoding="utf-8")
            report = SkillValidator().validate(path)
            if not report.valid:
                return "Error: patched skill invalid: " + "; ".join(report.errors)
            return f"Skill patched: {name}"
        if action == "validate":
            report = SkillValidator().validate(self._skill_dir(name) / "SKILL.md")
            return json.dumps({"valid": report.valid, "errors": report.errors, "warnings": report.warnings, "metadata": report.metadata}, ensure_ascii=False, indent=2)
        if action == "write_file":
            path = self._safe_support_path(name, kwargs.get("file_path", ""))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(kwargs.get("content", ""), encoding="utf-8")
            return f"Skill support file written: {path}"
        if action == "remove_file":
            path = self._safe_support_path(name, kwargs.get("file_path", ""))
            path.unlink()
            return f"Skill support file removed: {path}"
        return "Error: unknown skills action"
