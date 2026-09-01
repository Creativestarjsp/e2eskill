from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FORBIDDEN = ("password", "secret", "token", "private_key", "api_key", "credential")


def _safe(text: str) -> bool:
    lower = text.lower()
    return not any(x in lower for x in FORBIDDEN)


class Memory:
    def __init__(self, root: str | Path = ".") -> None:
        self.path = Path(root).resolve() / ".e2e" / "memory.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.records = json.loads(self.path.read_text()) if self.path.exists() else []

    def add(self, kind: str, scope: str, summary: str, evidence: list[str] | None = None, source: str = "runtime", confidence: str = "verified") -> dict[str, Any]:
        if not _safe(summary) or any(not _safe(x) for x in (evidence or [])):
            raise ValueError("Memory rejected: possible secret or credential content")
        record = {"id": "MEM-" + uuid.uuid4().hex[:8].upper(), "type": kind, "scope": scope, "summary": summary, "evidence": evidence or [], "source": source, "confidence": confidence, "created_at": datetime.now(timezone.utc).isoformat(), "expires_at": None, "supersedes": None}
        self.records.append(record)
        self._save()
        return record

    def search(self, query: str, scope: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        terms = {x.lower() for x in query.split() if x}
        rows = []
        for r in self.records:
            if scope and r["scope"] != scope:
                continue
            hay = (r["summary"] + " " + " ".join(r.get("evidence", []))).lower()
            score = sum(t in hay for t in terms)
            if score:
                rows.append((score, r))
        return [r for _, r in sorted(rows, key=lambda x: -x[0])[:limit]]

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.records, indent=2, sort_keys=True), encoding="utf-8")
