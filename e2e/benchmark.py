from __future__ import annotations

import json
import statistics
import subprocess
import time
from pathlib import Path
from typing import Any


def run_case(root: str | Path, command: str, repetitions: int = 1) -> dict[str, Any]:
    root = Path(root).resolve(); runs = []
    for i in range(repetitions):
        start = time.perf_counter()
        p = subprocess.run(command, cwd=root, shell=True, text=True, capture_output=True, timeout=900)
        runs.append({"run": i + 1, "status": "pass" if p.returncode == 0 else "fail", "exit_code": p.returncode, "latency_seconds": round(time.perf_counter() - start, 4), "stdout": p.stdout[-1000:], "stderr": p.stderr[-1000:]})
    latencies = [r["latency_seconds"] for r in runs]
    result = {"command": command, "repetitions": repetitions, "runs": runs, "median_latency_seconds": statistics.median(latencies) if latencies else None, "variance": statistics.pvariance(latencies) if len(latencies) > 1 else 0.0, "success_rate": sum(r["status"] == "pass" for r in runs) / len(runs) if runs else 0.0}
    out = root / ".e2e" / "benchmark.json"; out.parent.mkdir(exist_ok=True); out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
