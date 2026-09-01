from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

FORBIDDEN = ("password", "secret", "token", "private_key", "api_key", "credential")


def _safe(text: str) -> bool:
    lower = text.lower()
    return not any(x in lower for x in FORBIDDEN)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class Memory:
    """Small, durable, secret-rejecting project memory store.

    Memory is intentionally explicit: callers choose the type/scope and must provide
    a short summary plus evidence. Search ignores expired records, while superseded
    records remain available for audit/history but are not returned by default.
    """

    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root).resolve()
        self.path = self.root / ".e2e" / "memory.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.records = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else []
        except (json.JSONDecodeError, OSError) as exc:
            raise ValueError(f"Memory store is invalid: {exc}") from exc
        if not isinstance(self.records, list):
            raise ValueError("Memory store must contain a JSON list")

    def add(
        self,
        kind: str,
        scope: str,
        summary: str,
        evidence: list[str] | None = None,
        source: str = "runtime",
        confidence: str = "verified",
        expires_days: int | None = None,
        supersedes: str | None = None,
    ) -> dict[str, Any]:
        evidence = evidence or []
        fields = [kind, scope, summary, source, confidence, *(str(x) for x in evidence)]
        if any(not _safe(x) for x in fields):
            raise ValueError("Memory rejected: possible secret or credential content")
        if expires_days is not None and expires_days < 0:
            raise ValueError("expires_days must be non-negative")
        if supersedes and not any(r.get("id") == supersedes for r in self.records):
            raise ValueError("supersedes must reference an existing memory record")

        created = _now()
        expires = created + timedelta(days=expires_days) if expires_days is not None else None
        record = {
            "id": "MEM-" + uuid.uuid4().hex[:8].upper(),
            "type": kind,
            "scope": scope,
            "summary": summary,
            "evidence": evidence,
            "source": source,
            "confidence": confidence,
            "created_at": created.isoformat(),
            "expires_at": expires.isoformat() if expires else None,
            "supersedes": supersedes,
        }
        self.records.append(record)
        self._save()
        return record

    def search(
        self,
        query: str,
        scope: str | None = None,
        limit: int = 20,
        include_superseded: bool = False,
    ) -> list[dict[str, Any]]:
        if limit < 1:
            return []
        terms = {x.lower() for x in query.split() if x.strip()}
        rows: list[tuple[int, datetime, dict[str, Any]]] = []
        superseded_ids = {r.get("supersedes") for r in self.records if r.get("supersedes")}
        now = _now()
        for record in self.records:
            if scope and record.get("scope") != scope:
                continue
            if not include_superseded and record.get("id") in superseded_ids:
                continue
            expires = _parse(record.get("expires_at"))
            if expires and expires <= now:
                continue
            hay = (
                str(record.get("type", ""))
                + " "
                + str(record.get("scope", ""))
                + " "
                + str(record.get("summary", ""))
                + " "
                + " ".join(str(x) for x in record.get("evidence", []))
            ).lower()
            score = sum(t in hay for t in terms) if terms else 1
            if score:
                created = _parse(record.get("created_at")) or datetime.min.replace(tzinfo=timezone.utc)
                rows.append((score, created, record))
        rows.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [record for _, _, record in rows[:limit]]

    def list(self, scope: str | None = None, include_expired: bool = False) -> list[dict[str, Any]]:
        now = _now()
        rows = []
        for record in self.records:
            if scope and record.get("scope") != scope:
                continue
            expires = _parse(record.get("expires_at"))
            if expires and expires <= now and not include_expired:
                continue
            rows.append(record)
        return sorted(rows, key=lambda record: record.get("created_at", ""), reverse=True)

    def _save(self) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.records, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self.path)
