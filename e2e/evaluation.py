from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

AXES = ("accuracy", "completeness", "correctness", "security", "integration", "evidence", "efficiency")


def _git(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def evaluate_run(root: str | Path, task: str, worker_reports: list[dict[str, Any]], changed_files: list[str] | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    changed = changed_files if changed_files is not None else [x for x in _git(root, "diff", "--name-only", "HEAD~1", "HEAD").splitlines() if x]
    scores = {axis: 3 for axis in AXES}
    evidence: list[str] = []
    failures: list[str] = []
    if changed:
        scores["completeness"] = 4
        evidence.append(f"{len(changed)} changed file(s) observed in repository state")
    else:
        scores["completeness"] = 2
        failures.append("No changed files were observed")
    completed = [r for r in worker_reports if r.get("status") == "completed" and r.get("returncode") == 0]
    if completed:
        scores["correctness"] = 4
        evidence.append(f"{len(completed)} worker report(s) have successful exit codes")
    else:
        scores["correctness"] = 1
        failures.append("No successful worker execution evidence")
    for report in worker_reports:
        if report.get("status") in {"failed", "timeout", "workspace-failure"}:
            failures.append(f"Worker {report.get('id', 'unknown')} ended with {report.get('status')}")
            scores["evidence"] = min(scores["evidence"], 2)
    result = {"task": task, "axes": scores, "aggregate": round(sum(scores.values()) / len(scores), 2), "evidence": evidence, "failed_checks": failures, "changed_files": changed, "blocking": bool(failures)}
    out = root / ".e2e" / "evaluation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result
