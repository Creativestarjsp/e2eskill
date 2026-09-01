from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

FAILURE_CLASSES = {"timeout": "runtime", "workspace-failure": "environment", "worker-failure": "worker", "merge-conflict": "integration", "supervisor-failure": "verification"}


def diagnose(root: str | Path, run: dict[str, Any]) -> dict[str, Any]:
    root = Path(root).resolve()
    status = str(run.get("status", "unknown"))
    worker_statuses = [str(w.get("status")) for w in run.get("workers", [])]
    if status in FAILURE_CLASSES:
        failure_class = FAILURE_CLASSES[status]
    elif "timeout" in worker_statuses:
        failure_class = "runtime"
    elif "failed" in worker_statuses:
        failure_class = "worker"
    else:
        failure_class = "unknown"
    repeated = len(run.get("corrections", []))
    escalate = failure_class in {"integration", "verification"} or repeated >= 2
    result = {"run_status": status, "failure_class": failure_class, "worker_statuses": worker_statuses, "correction_rounds": repeated, "escalate_to_sd3": escalate, "recommended_action": "capture evidence and apply one contained correction" if not escalate else "stop blind retries and escalate to SD3", "timestamp": time.time()}
    out = root / ".e2e" / "introspection.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result
