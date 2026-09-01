from __future__ import annotations

import json
import math
import subprocess
import time
from pathlib import Path
from typing import Any, Callable

SCHEMA_VERSION = "1.0"


def _run(root: Path, command: list[str], timeout: int = 120) -> dict[str, Any]:
    started = time.perf_counter()
    proc = subprocess.run(command, cwd=root, text=True, capture_output=True, timeout=timeout, check=False)
    elapsed = time.perf_counter() - started
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "latency_seconds": round(elapsed, 4),
    }


def grade_exit_code(result: dict[str, Any], expected: int = 0) -> dict[str, Any]:
    passed = result.get("returncode") == expected
    return {"grader": "exit-code", "passed": passed, "score": 1.0 if passed else 0.0, "evidence": f"returncode={result.get('returncode')} expected={expected}"}


def grade_contains(result: dict[str, Any], text: str) -> dict[str, Any]:
    haystack = f"{result.get('stdout', '')}\n{result.get('stderr', '')}"
    passed = text in haystack
    return {"grader": "contains", "passed": passed, "score": 1.0 if passed else 0.0, "evidence": f"required={text!r}"}


def grade_files_exist(root: Path, paths: list[str]) -> dict[str, Any]:
    missing = [path for path in paths if not (root / path).exists()]
    score = 1.0 if not paths else (len(paths) - len(missing)) / len(paths)
    return {"grader": "files-exist", "passed": not missing, "score": round(score, 4), "missing": missing}


def _pass_at_k(successes: int, attempts: int, k: int) -> float:
    if k <= 0 or attempts <= 0 or successes <= 0:
        return 0.0
    k = min(k, attempts)
    if successes >= attempts:
        return 1.0
    failures = attempts - successes
    if k > failures:
        return 1.0
    return 1.0 - math.comb(failures, k) / math.comb(attempts, k)


def _pass_power_k(successes: int, attempts: int, k: int) -> float:
    if attempts <= 0 or k <= 0:
        return 0.0
    rate = successes / attempts
    return rate ** k


def summarize_attempts(attempts: list[dict[str, Any]], ks: tuple[int, ...] = (1, 3, 5)) -> dict[str, Any]:
    total = len(attempts)
    successes = sum(1 for attempt in attempts if attempt.get("passed") is True)
    latencies = [float(a["latency_seconds"]) for a in attempts if a.get("latency_seconds") is not None]
    return {
        "attempts": total,
        "successes": successes,
        "pass_rate": round(successes / total, 4) if total else 0.0,
        "pass_at_k": {str(k): round(_pass_at_k(successes, total, k), 4) for k in ks},
        "pass_power_k": {str(k): round(_pass_power_k(successes, total, k), 4) for k in ks},
        "mean_latency_seconds": round(sum(latencies) / len(latencies), 4) if latencies else None,
        "p95_latency_seconds": round(sorted(latencies)[max(0, math.ceil(len(latencies) * 0.95) - 1)], 4) if latencies else None,
    }


def _metric_delta(current: dict[str, Any], baseline: dict[str, Any], key: str) -> float | None:
    left = current.get(key)
    right = baseline.get(key)
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return round(float(left) - float(right), 4)
    return None


def compare_baseline(current: dict[str, Any], baseline: dict[str, Any], minimum_pass_rate: float = 0.0, maximum_latency_regression: float = 0.25) -> dict[str, Any]:
    current_summary = current.get("summary", current)
    baseline_summary = baseline.get("summary", baseline)
    pass_delta = _metric_delta(current_summary, baseline_summary, "pass_rate")
    latency_delta = _metric_delta(current_summary, baseline_summary, "mean_latency_seconds")
    regressions: list[str] = []
    if pass_delta is not None and current_summary.get("pass_rate", 0) < minimum_pass_rate:
        regressions.append("pass-rate-below-threshold")
    if pass_delta is not None and pass_delta < 0:
        regressions.append("pass-rate-regression")
    if latency_delta is not None and baseline_summary.get("mean_latency_seconds") not in (None, 0):
        ratio = latency_delta / baseline_summary["mean_latency_seconds"]
        if ratio > maximum_latency_regression:
            regressions.append("latency-regression")
    return {
        "status": "regression" if regressions else "pass",
        "pass_rate_delta": pass_delta,
        "mean_latency_delta_seconds": latency_delta,
        "regressions": regressions,
        "baseline_id": baseline.get("run_id") or baseline.get("id"),
    }


def run_suite(root: str | Path, suite: dict[str, Any], runner: Callable[[Path, dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
    root = Path(root).resolve()
    attempts: list[dict[str, Any]] = []
    cases = suite.get("cases", [])
    for case in cases:
        repetitions = max(1, int(case.get("repetitions", 1)))
        for index in range(repetitions):
            result = runner(root, case)
            graders: list[dict[str, Any]] = []
            for grader in case.get("graders", []):
                kind = grader.get("type")
                if kind == "exit-code":
                    graders.append(grade_exit_code(result, int(grader.get("expected", 0))))
                elif kind == "contains":
                    graders.append(grade_contains(result, str(grader.get("text", ""))))
                elif kind == "files-exist":
                    graders.append(grade_files_exist(root, [str(x) for x in grader.get("paths", [])]))
            passed = bool(graders) and all(g["passed"] for g in graders)
            attempts.append({
                "case_id": case.get("id", f"case-{len(attempts) + 1}"),
                "attempt": index + 1,
                "passed": passed,
                "latency_seconds": result.get("latency_seconds"),
                "graders": graders,
            })
    summary = summarize_attempts(attempts)
    report = {
        "schema_version": SCHEMA_VERSION,
        "suite_id": suite.get("id", "unnamed"),
        "suite_version": suite.get("version", "1"),
        "attempts": attempts,
        "summary": summary,
    }
    out = root / ".e2e" / "evals" / f"{suite.get('id', 'suite')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def command_runner(root: Path, case: dict[str, Any]) -> dict[str, Any]:
    command = case.get("command")
    if not isinstance(command, list) or not command:
        raise ValueError(f"case {case.get('id')} requires a non-empty command list")
    return _run(root, [str(x) for x in command], int(case.get("timeout", 120)))


def load_suite(path: str | Path) -> dict[str, Any]:
    suite = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(suite, dict) or not isinstance(suite.get("cases"), list):
        raise ValueError("evaluation suite must be an object with a cases array")
    return suite
