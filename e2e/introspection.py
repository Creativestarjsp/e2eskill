from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

FAILURE_CLASSES = {
    "timeout": "runtime",
    "workspace-failure": "environment",
    "infrastructure-failure": "infrastructure",
    "worker-failure": "worker",
    "skill-failure": "skill",
    "test-failure": "test",
    "merge-conflict": "integration",
    "supervisor-failure": "verification",
}


def _failure_class(run: dict[str, Any]) -> str:
    status = str(run.get("status", "unknown"))
    worker_statuses = [str(w.get("status")) for w in run.get("workers", [])]
    checks = run.get("checks", [])

    if status in FAILURE_CLASSES:
        return FAILURE_CLASSES[status]
    if "timeout" in worker_statuses:
        return "runtime"
    if "skill-failure" in worker_statuses:
        return "skill"
    if "failed" in worker_statuses:
        return "worker"
    if any(str(c.get("failure_class")) == "skill" for c in checks):
        return "skill"
    if any(str(c.get("failure_class")) == "test" or str(c.get("type")) in {"pytest", "test"} and c.get("status") == "fail" for c in checks):
        return "test"
    if any(str(c.get("failure_class")) == "infrastructure" for c in checks):
        return "infrastructure"
    if any(c.get("status") == "fail" for c in checks):
        return "unknown"
    return "unknown"


def diagnose(root: str | Path, run: dict[str, Any]) -> dict[str, Any]:
    root = Path(root).resolve()
    status = str(run.get("status", "unknown"))
    worker_statuses = [str(w.get("status")) for w in run.get("workers", [])]
    failure_class = _failure_class(run)
    repeated = len(run.get("corrections", []))
    escalate = failure_class in {"integration", "verification", "infrastructure"} or repeated >= 2

    actions = {
        "skill": "repair or validate the affected skill before blaming the implementation",
        "test": "inspect the failing test and implementation evidence; keep the skill runtime available",
        "worker": "capture worker evidence and apply one contained correction",
        "runtime": "inspect runtime availability, timeout, and execution evidence",
        "environment": "repair workspace/environment state before retrying",
        "integration": "stop blind retries and escalate to SD3",
        "verification": "stop blind retries and escalate to SD3",
        "infrastructure": "stop blind retries and repair the CI/runtime infrastructure",
        "unknown": "capture evidence and classify the failure before retrying",
    }

    result = {
        "run_status": status,
        "failure_class": failure_class,
        "worker_statuses": worker_statuses,
        "correction_rounds": repeated,
        "escalate_to_sd3": escalate,
        "recommended_action": actions[failure_class],
        "skill_runtime_independent": failure_class != "skill",
        "timestamp": time.time(),
    }
    out = root / ".e2e" / "introspection.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result
