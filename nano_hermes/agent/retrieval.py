"""Simple lexical ranking shared by memory, session, and skill retrieval."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any


def _terms(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_./-]+", (text or "").lower())


def rank_documents(query: str, documents: list[dict[str, Any]], *, limit: int = 8) -> list[dict[str, Any]]:
    q = _terms(query)
    ranked: list[dict[str, Any]] = []
    for doc in documents:
        score = 0.0
        reasons: list[str] = []
        for field, weight in (("title", 4), ("tags", 3), ("description", 3), ("content", 1), ("summary", 2), ("source", 1)):
            value = doc.get(field, "")
            text = " ".join(map(str, value)) if isinstance(value, list) else str(value)
            hits = sum(1 for term in q if term in text.lower())
            if hits:
                score += hits * weight
                reasons.append(field)
        if doc.get("timestamp") or doc.get("updated_at"):
            try:
                ts = datetime.fromisoformat(str(doc.get("timestamp") or doc.get("updated_at")).replace("Z", "+00:00"))
                score += max(0.0, 1.0 - (datetime.now(ts.tzinfo) - ts).days / 365)
            except Exception:
                pass
        if score:
            item = dict(doc)
            item["score"] = score
            item["reason"] = ",".join(sorted(set(reasons)))
            ranked.append(item)
    ranked.sort(key=lambda d: (-float(d.get("score", 0)), str(d.get("title") or d.get("name") or "")))
    return ranked[: max(0, limit)]
