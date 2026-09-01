from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from .eval_harness import compare_baseline

SCHEMA_VERSION = "1.0"


def _git(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _task_terms(task: str) -> set[str]:
    return {x.lower() for x in re.findall(r"[A-Za-z_][\w-]{2,}", task)}


def load_eval_history(root: str | Path, limit: int = 20) -> list[dict[str, Any]]:
    root = Path(root).resolve()
    directory = root / ".e2e" / "evals"
    if not directory.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        item = _load_json(path)
        if item:
            item["_path"] = path.relative_to(root).as_posix()
            rows.append(item)
        if len(rows) >= limit:
            break
    return rows


def find_regressions(root: str | Path, task: str, limit: int = 20) -> list[dict[str, Any]]:
    terms = _task_terms(task)
    matches = []
    for item in load_eval_history(root, limit=limit):
        hay = " ".join(str(item.get(k, "")) for k in ("suite", "suite_id", "description", "task", "id")).lower()
        if terms and not any(term in hay for term in terms):
            continue
        summary = item.get("summary", item.get("aggregate", {}))
        if not isinstance(summary, dict):
            continue
        attempts = int(summary.get("attempts", 0))
        passed = int(summary.get("passed", summary.get("successes", 0)))
        failed = int(summary.get("failed", max(0, attempts - passed)))
        if failed:
            matches.append({"suite": item.get("suite", item.get("suite_id", item.get("id"))), "path": item["_path"], "failed": failed, "passed": passed, "signal": "historical-failure"})
    return matches


def analyze_regression_risk(root: str | Path, task: str, current: dict[str, Any] | None = None, baseline: dict[str, Any] | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    historical = find_regressions(root, task)
    comparison = compare_baseline(current, baseline) if current and baseline else {"regression": False, "reasons": []}
    reasons = list(comparison.get("reasons", []))
    if historical:
        reasons.append(f"{len(historical)} related evaluation history item(s) contain failures")
    level = "high" if comparison.get("regression") or len(historical) >= 2 else ("medium" if historical else "low")
    return {
        "schema_version": SCHEMA_VERSION,
        "level": level,
        "historical_failures": historical,
        "baseline_comparison": comparison,
        "reasons": reasons,
        "recommended_action": "expand targeted evals and require SD3 regression review" if level == "high" else ("run targeted regression evals" if level == "medium" else "standard regression checks"),
    }


def persist_regression(root: str | Path, report: dict[str, Any]) -> Path:
    root = Path(root).resolve()
    path = root / ".e2e" / "regression.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return path
