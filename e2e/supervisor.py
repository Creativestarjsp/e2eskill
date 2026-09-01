from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .executor import RuntimeUnavailable, _supervise, runtime_available


def run_independent_review(root: str | Path, task: str, runtime: str, reports: str | Path) -> dict[str, Any]:
    """Run a separate, read-only SD3 review over a completed SD1 execution report."""
    root = Path(root).resolve()
    report_path = Path(reports)
    if not report_path.is_absolute():
        report_path = root / report_path
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("workers"), list):
        raise ValueError("reports must be an E2E execution JSON object with workers")
    if not runtime_available(runtime):
        raise RuntimeUnavailable(f"{runtime} is not installed or not on PATH")
    result = _supervise(root, task, runtime, payload["workers"], 0)
    result["mode"] = "independent-read-only"
    result["source_reports"] = str(report_path)
    return result
