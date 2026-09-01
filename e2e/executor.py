from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from .orchestrator import plan


class RuntimeUnavailable(RuntimeError):
    pass


def _command(runtime: str, prompt: str) -> list[str]:
    if runtime == "claude-code":
        return ["claude", "-p", "--output-format", "json", prompt]
    if runtime == "codex":
        raw = os.environ.get("E2E_CODEX_COMMAND", "codex exec")
        return raw.split() + [prompt]
    raise RuntimeUnavailable(f"unsupported runtime: {runtime}")


def runtime_available(runtime: str) -> bool:
    if runtime == "claude-code":
        return shutil.which("claude") is not None
    if runtime == "codex":
        return shutil.which("codex") is not None
    return False


def _prompt(task: str, worker: dict[str, Any]) -> str:
    context = json.dumps(worker.get("inputs", {}).get("context", {}), ensure_ascii=False, indent=2)
    return f"""You are an SD1 worker in the E2E engineering system.\n\nROLE: {worker['skill']}\nWORKER: {worker['id']}\nPHASE: {worker['phase']}\nTASK: {task}\n\nExecute only the assigned responsibility. Investigate the repository before editing. Reuse existing code and dependencies before adding new ones. Do not claim work you did not perform. Preserve security, data integrity, accessibility, and existing behavior. Do not create commits unless the user explicitly asks.\n\nPROJECT CONTEXT:\n{context}\n\nWhen finished, report: changed files, implementation summary, commands/tests run, evidence, risks, and remaining work. If blocked, explain the concrete blocker and stop rather than inventing a workaround."""


def _supervisor_prompt(task: str, results: list[dict[str, Any]]) -> str:
    evidence = json.dumps(results, ensure_ascii=False, indent=2)
    return f"""You are the SD3 Engineering Supervisor. Independently inspect the repository after SD1 execution for this task: {task}.\n\nSD1 REPORTS:\n{evidence}\n\nDo not trust worker claims without inspecting the actual files and running appropriate verification. Check requirements, architecture, integration, tests, security, regressions, and evidence. Fix nothing unless explicitly instructed; instead produce an approval decision with concrete corrective tasks when needed. Return a concise JSON-like report with decision (approved/rejected/needs-correction), evidence, failed checks, and next actions."""


def execute(root: str | Path, task: str, runtime: str = "auto", execute_agents: bool = False, max_workers: int = 4) -> dict[str, Any]:
    root = Path(root).resolve()
    selected = runtime
    if selected == "auto":
        if runtime_available("claude-code"):
            selected = "claude-code"
        elif runtime_available("codex"):
            selected = "codex"
        else:
            selected = "unavailable"

    execution = {
        "task": task,
        "runtime": selected,
        "mode": "execute" if execute_agents else "dry-run",
        "started_at": time.time(),
        "workers": [],
        "supervisor": None,
    }
    if selected == "unavailable":
        execution["status"] = "runtime-unavailable"
        execution["next"] = "Install Claude Code or Codex, or select a configured runtime."
        return execution

    if not execute_agents:
        p = plan(root, task)
        execution["status"] = "planned"
        execution["workers"] = [{"id": w["id"], "skill": w["skill"], "phase": w["phase"], "depends_on": w.get("depends_on", [])} for w in p["workers"][:max_workers]]
        execution["next"] = "Re-run with --execute to launch the selected runtime."
        return execution

    if not runtime_available(selected):
        raise RuntimeUnavailable(f"{selected} is not installed or not on PATH")

    p = plan(root, task)
    by_id = {w["id"]: w for w in p["workers"]}
    completed: set[str] = set()
    pending = list(p["workers"])
    while pending:
        ready = [w for w in pending if all(dep in completed for dep in w.get("depends_on", []))]
        if not ready:
            execution["status"] = "blocked-dependency-cycle"
            break
        for worker in ready[:max_workers]:
            started = time.time()
            try:
                proc = subprocess.run(_command(selected, _prompt(task, worker)), cwd=root, text=True, capture_output=True, timeout=int(os.environ.get("E2E_AGENT_TIMEOUT", "1800")))
                result = {"id": worker["id"], "skill": worker["skill"], "returncode": proc.returncode, "stdout": proc.stdout[-12000:], "stderr": proc.stderr[-12000:], "duration_seconds": round(time.time() - started, 3), "status": "completed" if proc.returncode == 0 else "failed"}
            except subprocess.TimeoutExpired as exc:
                result = {"id": worker["id"], "skill": worker["skill"], "returncode": None, "stdout": str(exc.stdout or "")[-12000:], "stderr": str(exc.stderr or "")[-12000:], "duration_seconds": round(time.time() - started, 3), "status": "timeout"}
            execution["workers"].append(result)
            pending.remove(worker)
            if result["status"] == "completed":
                completed.add(worker["id"])
            else:
                execution["status"] = "worker-failure"
                execution["next"] = "Inspect the worker evidence and correct the failed work before supervisor approval."
                pending.clear()
                break

    if execution.get("status") is None:
        supervisor = {"id": "sd3-supervisor", "status": "not-run"}
        started = time.time()
        proc = subprocess.run(_command(selected, _supervisor_prompt(task, execution["workers"])), cwd=root, text=True, capture_output=True, timeout=int(os.environ.get("E2E_AGENT_TIMEOUT", "1800")))
        supervisor.update({"returncode": proc.returncode, "stdout": proc.stdout[-16000:], "stderr": proc.stderr[-12000:], "duration_seconds": round(time.time() - started, 3), "status": "completed" if proc.returncode == 0 else "failed"})
        execution["supervisor"] = supervisor
        execution["status"] = "supervisor-review-complete" if proc.returncode == 0 else "supervisor-failure"

    execution["finished_at"] = time.time()
    out = root / ".e2e" / "executions"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{int(execution['started_at'] * 1000)}.json"
    path.write_text(json.dumps(execution, indent=2, ensure_ascii=False), encoding="utf-8")
    execution["report_path"] = path.relative_to(root).as_posix()
    return execution
