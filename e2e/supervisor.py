from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .executor import RuntimeUnavailable, _supervise, runtime_available


def run_independent_review(root: str | Path, task: str, runtime: str, reports: str | Path) -> dict[str, Any]:
    """Run a separate, read-only SD3 review over a completed SD1 execution report.

    The execution report is the source of truth for the completed task. This prevents
    callers from accidentally downgrading an independent review to a generic family
    label or unrelated summary string.
    """
    root = Path(root).resolve()
    report_path = Path(reports)
    if not report_path.is_absolute():
        report_path = root / report_path
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("workers"), list):
        raise ValueError("reports must be an E2E execution JSON object with workers")
    if not runtime_available(runtime):
        raise RuntimeUnavailable(f"{runtime} is not installed or not on PATH")

    requested_task = str(task or "").strip()
    completed_task = str(payload.get("task") or "").strip()
    review_task = completed_task or requested_task
    if not review_task:
        raise ValueError("independent review requires a completed task in reports or an explicit task")

    result = _supervise(root, review_task, runtime, payload["workers"], 0)
    result["mode"] = "independent-read-only"
    result["requested_task"] = requested_task
    result["review_task"] = review_task
    result["source_reports"] = str(report_path)
    return result
