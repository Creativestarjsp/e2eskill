from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def persist_run(root: str | Path, execution: dict[str, Any], evaluation: dict[str, Any] | None = None, introspection: dict[str, Any] | None = None) -> str:
    root = Path(root).resolve()
    run_id = str(execution.get("report_path", "")).rsplit("/", 1)[-1].removesuffix(".json") or str(int(time.time() * 1000))
    run_dir = root / ".e2e" / "runs" / run_id
    _write(run_dir / "plan.json", {"task": execution.get("task"), "runtime": execution.get("runtime"), "mode": execution.get("mode"), "max_workers": execution.get("max_workers")})
    _write(run_dir / "execution.json", execution)
    for worker in execution.get("workers", []):
        worker_id = str(worker.get("id", "unknown"))
        _write(run_dir / "workers" / worker_id / "report.json", worker)
        if worker.get("stdout") is not None:
            (run_dir / "workers" / worker_id).mkdir(parents=True, exist_ok=True)
            (run_dir / "workers" / worker_id / "stdout.txt").write_text(str(worker.get("stdout", "")), encoding="utf-8")
        if worker.get("stderr") is not None:
            (run_dir / "workers" / worker_id).mkdir(parents=True, exist_ok=True)
            (run_dir / "workers" / worker_id / "stderr.txt").write_text(str(worker.get("stderr", "")), encoding="utf-8")
    if execution.get("supervisor") is not None:
        _write(run_dir / "supervisor.json", execution["supervisor"])
    if execution.get("brain_refresh") is not None:
        _write(run_dir / "verification.json", execution["brain_refresh"])
    if evaluation is not None:
        _write(run_dir / "evaluation.json", evaluation)
    if introspection is not None:
        _write(run_dir / "introspection.json", introspection)
    final = {
        "status": execution.get("status"),
        "task": execution.get("task"),
        "runtime": execution.get("runtime"),
        "evaluation_blocking": bool(evaluation and evaluation.get("blocking")),
        "failure_class": introspection.get("failure_class") if introspection else None,
    }
    _write(run_dir / "final.json", final)
    return run_dir.relative_to(root).as_posix()
