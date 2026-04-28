"""Searchable index for builtin and workspace skills."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from nano_hermes.agent.skills import BUILTIN_SKILLS_DIR

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def _terms(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class SkillIndex:
    def __init__(self, workspace: Path, builtin_skills_dir: Path | None = None):
        self.workspace = Path(workspace)
        self.workspace_skills = self.workspace / "skills"
        self.builtin_skills = builtin_skills_dir or BUILTIN_SKILLS_DIR

    def _parse(self, skill_file: Path, source: str) -> dict[str, Any]:
        text = skill_file.read_text(encoding="utf-8")
        meta: dict[str, Any] = {}
        body = text
        match = _FRONTMATTER.match(text)
        if match:
            try:
                parsed = yaml.safe_load(match.group(1)) or {}
                if isinstance(parsed, dict):
                    meta = parsed
                body = text[match.end():]
            except yaml.YAMLError:
                pass
        raw_metadata = meta.get("metadata", {})
        nb = raw_metadata.get("nanohermes", {}) if isinstance(raw_metadata, dict) else {}
        return {
            "name": str(meta.get("name") or skill_file.parent.name),
            "path": str(skill_file),
            "source": source,
            "description": str(meta.get("description") or skill_file.parent.name),
            "tags": list(nb.get("tags", meta.get("tags", [])) or []),
            "triggers": list(nb.get("triggers", meta.get("triggers", [])) or []),
            "available": True,
            "body": body,
            "mtime": skill_file.stat().st_mtime,
        }

    def entries(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        seen: set[str] = set()
        for base, source in ((self.workspace_skills, "workspace"), (self.builtin_skills, "builtin")):
            if not base or not base.exists():
                continue
            for skill_file in sorted(base.glob("*/SKILL.md")):
                entry = self._parse(skill_file, source)
                if entry["name"] in seen:
                    continue
                seen.add(entry["name"])
                out.append(entry)
        return out

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        qterms = _terms(query)
        scored: list[dict[str, Any]] = []
        for entry in self.entries():
            fields = {
                "triggers": " ".join(map(str, entry.get("triggers", []))),
                "tags": " ".join(map(str, entry.get("tags", []))),
                "description": entry.get("description", ""),
                "name": entry.get("name", ""),
                "body": entry.get("body", ""),
            }
            score = 0
            reasons: list[str] = []
            for term in qterms:
                for field, text in fields.items():
                    if term in text.lower():
                        weight = {"triggers": 5, "tags": 4, "description": 3, "name": 3, "body": 1}[field]
                        score += weight
                        reasons.append(field)
            if score:
                item = {k: v for k, v in entry.items() if k != "body"}
                item.update({"score": score, "reason": ",".join(sorted(set(reasons)))})
                scored.append(item)
        scored.sort(key=lambda e: (-e["score"], e["name"]))
        return scored[: max(0, limit)]
