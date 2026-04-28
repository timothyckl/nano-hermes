"""Verification evidence extracted from a turn's tool activity."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VerificationEvidence:
    tools_called: list[str] = field(default_factory=list)
    successful_tools: list[str] = field(default_factory=list)
    failed_tools: list[str] = field(default_factory=list)
    files_changed: list[str] = field(default_factory=list)
    commands_run: list[str] = field(default_factory=list)
    tests_run: list[str] = field(default_factory=list)
    web_sources_used: list[str] = field(default_factory=list)
    user_confirmed: bool = False
    verified: bool = False
    confidence: float = 0.0
    notes: str = ""


def classify_tool_events(events: list[dict[str, Any]]) -> VerificationEvidence:
    evidence = VerificationEvidence()
    for event in events:
        name = str(event.get("name") or event.get("tool") or "")
        if name:
            evidence.tools_called.append(name)
        ok = not str(event.get("result") or event.get("error") or "").lower().startswith("error") and not event.get("error")
        (evidence.successful_tools if ok else evidence.failed_tools).append(name)
        args = event.get("arguments") or event.get("args") or {}
        if name in {"exec", "shell"} and isinstance(args, dict):
            cmd = str(args.get("command") or "")
            if cmd:
                evidence.commands_run.append(cmd)
                if any(token in cmd for token in ("pytest", "unittest", "npm test", "ruff", "mypy")):
                    evidence.tests_run.append(cmd)
        if name in {"web_search", "web_fetch"}:
            evidence.web_sources_used.append(str(args.get("url") or args.get("query") or ""))
    evidence.verified = bool(evidence.tests_run or evidence.web_sources_used or evidence.successful_tools)
    evidence.confidence = 0.8 if evidence.verified and not evidence.failed_tools else (0.4 if evidence.successful_tools else 0.0)
    return evidence
