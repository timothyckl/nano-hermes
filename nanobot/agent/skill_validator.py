"""Validation for Nano Hermes skill packages."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SECRET_HINTS = ("api_key", "secret", "password", "token", "private_key", "access_token", "refresh_token")


@dataclass
class SkillValidationReport:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class SkillValidator:
    allowed_support_dirs = {"references", "templates", "scripts", "assets"}

    def validate(self, path: Path) -> SkillValidationReport:
        errors: list[str] = []
        warnings: list[str] = []
        metadata: dict[str, Any] = {}
        path = Path(path)
        if path.name != "SKILL.md":
            errors.append("skill file must be named SKILL.md")
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return SkillValidationReport(False, ["SKILL.md not found"], [])
        match = _FRONTMATTER.match(text)
        if not match:
            errors.append("missing YAML frontmatter")
        else:
            try:
                parsed = yaml.safe_load(match.group(1)) or {}
                if isinstance(parsed, dict):
                    metadata = parsed
                else:
                    errors.append("frontmatter must be a mapping")
            except yaml.YAMLError as exc:
                errors.append(f"invalid YAML frontmatter: {exc}")
        name = str(metadata.get("name") or path.parent.name)
        if not _NAME.match(name):
            errors.append("skill name must be kebab-case")
        if not metadata.get("description"):
            errors.append("missing description")
        body = text[match.end():] if match else text
        if "#" not in body:
            warnings.append("skill body should contain markdown headings")
        low = text.lower()
        if any(hint in low for hint in _SECRET_HINTS):
            warnings.append("skill mentions secret-like fields; ensure no credentials are persisted")
        if len(text) > 80_000:
            errors.append("skill is too large")
        if path.parent.exists():
            for child in path.parent.iterdir():
                if child.name == "SKILL.md":
                    continue
                if child.is_dir() and child.name not in self.allowed_support_dirs:
                    errors.append(f"unsupported skill subdirectory: {child.name}")
        return SkillValidationReport(not errors, errors, warnings, metadata)
