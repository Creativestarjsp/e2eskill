from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from .orchestrator import plan
from .worktree import WorktreeError, WorkerWorkspace, commit_changes, create, ensure_clean, merge, remove


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
    return f"""You are an SD1 worker in the E2E engineering system.\n\nROLE: {worker['skill']}\nWORKER: {worker['id']}\nPHASE: {worker['phase']}\nTASK: {task}\n\nExecute only the assigned responsibility. Investigate the repository before editing. Reuse existing code and dependencies before adding new ones. Do not claim work you did not perform. Preserve security, data integrity, accessibility, and existing behavior. Work only inside the provided isolated workspace. Do not modify or inspect sibling worktrees. Do not create commits unless the runtime requires it.\n\nPROJECT CONTEXT:\n{context}\n\nWhen finished, report: changed files, implementation summary, commands/tests run, evidence, risks, and remaining work. If blocked, explain the concrete blocker and stop rather than inventing a workaround."""


def _supervisor_prompt(task: str, results: list[dict[str, Any]]) -> str:
    evidence = json.dumps(results, ensure_ascii=False, indent=2)
    return f"""You are the SD3 Engineering Supervisor. Independently inspect the integrated repository after SD1 execution for this task: {task}.\n\nSD1 REPORTS:\n{evidence}\n\nDo not trust worker claims without inspecting the actual files and running appropriate verification. Check requirements, architecture, integration, tests, security, regressions, and evidence. Fix nothing unless explicitly instructed; instead produce an approval decision with concrete corrective tasks when needed. Return a concise JSON-like report with decision (approved/rejected/needs-correction), evidence, failed checks, and next actions."""


def _run_worker(root: Path, task: str, runtime: str, worker: dict[str, Any], base_ref: str) -> tuple[dict[str, Any], WorkerWorkspace | None]:
    started = time.time()
    workspace: WorkerWorkspace | None = None
    try:
        workspace = create(root, worker["id"], base_ref=base_ref)
        proc = subprocess.run(
            _command(runtime, _prompt(task, worker)),
            cwd=workspace.path,
            text=True,
            capture_output=True,
            timeout=int(os.environ.get("E2E_AGENT_TIMEOUT", "1800")),
        )
        status = "completed" if proc.returncode == 0 else "failed"
        commit_sha = None
        if status == "completed":
            commit_sha = commit_changes(workspace, f"e2e: implement {worker['id']}")
        result = {
            "id": worker["id"],
            "skill": worker["skill"],
            "phase": worker["phase"],
            "workspace": str(workspace.path),
            "branch": workspace.branch,
            "commit": commit_sha,
            "returncode": proc.returncode,
            "stdout": proc.stdout[-12000:],
            "stderr": proc.stderr[-12000:],
            "duration_seconds": round(time.time() - started, 3),
            "status": status,
        }
        return result, workspace
    except subprocess.TimeoutExpired as exc:
        return {
            "id": worker["id"],
            "skill": worker["skill"],
            "phase": worker["phase"],
            "workspace": str(workspace.path) if workspace else None,
            "returncode": None,
            "stdout": str(exc.stdout or "")[-12000:],
            "stderr": str(exc.stderr or "")[-12000:],
            "duration_seconds": round(time.time() - started, 3),
            "status": "timeout",
        }, workspace
    except (WorktreeError, OSError) as exc:
        return {
            "id": worker["id"],
            "skill": worker["skill"],
            "phase": worker["phase"],
            "workspace": str(workspace.path) if workspace else None,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "duration_seconds": round(time.time() - started, 3),
            "status": "workspace-failure",
        }, workspace


def _merge_workspace(root: Path, workspace: WorkerWorkspace, worker_id: str) -> tuple[bool, str | None]:
    try:
        ensure_clean(root)
        sha = merge(root, workspace, f"e2e: integrate {worker_id}")
        return True, sha
    except WorktreeError:
        subprocess.run(["git", "merge", "--abort"], cwd=root, text=True, capture_output=True)
        return False, None


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
        "parallel": bool(execute_agents),
        "max_workers": max(1, min(max_workers, 4)),
    }
    if selected == "unavailable":
        execution["status"] = "runtime-unavailable"
        execution["next"] = "Install Claude Code or Codex, or select a configured runtime."
        return execution

    p = plan(root, task)
    if not execute_agents:
        execution["status"] = "planned"
        execution["workers"] = [{"id": w["id"], "skill": w["skill"], "phase": w["phase"], "depends_on": w.get("depends_on", [])} for w in p["workers"][: execution["max_workers"]]]
        execution["next"] = "Re-run with --execute to launch the selected runtime."
        return execution

    if not runtime_available(selected):
        raise RuntimeUnavailable(f"{selected} is not installed or not on PATH")

    try:
        ensure_clean(root)
    except WorktreeError as exc:
        execution["status"] = "dirty-working-tree"
        execution["next"] = str(exc)
        return execution

    completed: set[str] = set()
    pending = list(p["workers"])
    preserved_workspaces: list[str] = []
    base_ref = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=True).stdout.strip()

    while pending:
        ready = [w for w in pending if all(dep in completed for dep in w.get("depends_on", []))]
        if not ready:
            execution["status"] = "blocked-dependency-cycle"
            break

        batch = ready[: execution["max_workers"]]
        with ThreadPoolExecutor(max_workers=len(batch)) as pool:
            futures = {pool.submit(_run_worker, root, task, selected, worker, base_ref): worker for worker in batch}
            results = []
            for future in as_completed(futures):
                worker = futures[future]
                result, workspace = future.result()
                results.append((worker, result, workspace))

        results.sort(key=lambda item: batch.index(item[0]))
        for worker, result, workspace in results:
            execution["workers"].append(result)
            pending.remove(worker)
            if result["status"] != "completed" or workspace is None:
                execution["status"] = "worker-failure"
                if workspace:
                    preserved_workspaces.append(str(workspace.path))
                for _, _, other_workspace in results:
                    if other_workspace and str(other_workspace.path) != str(workspace.path):
                        try:
                            remove(root, other_workspace)
                        except WorktreeError:
                            pass
                execution["preserved_workspaces"] = preserved_workspaces
                execution["next"] = "Inspect the isolated worker evidence and correct the failed work before integration."
                pending.clear()
                break

        if execution.get("status"):
            break

        for worker, result, workspace in results:
            ok, merged_sha = _merge_workspace(root, workspace, worker["id"])
            result["merged"] = ok
            result["integrated_commit"] = merged_sha
            if not ok:
                execution["status"] = "merge-conflict"
                preserved_workspaces.append(str(workspace.path))
                execution["preserved_workspaces"] = preserved_workspaces
                execution["next"] = "Resolve the integration conflict before continuing."
                pending.clear()
                break
            completed.add(worker["id"])
            try:
                remove(root, workspace)
            except WorktreeError:
                preserved_workspaces.append(str(workspace.path))

        if execution.get("status"):
            break
        base_ref = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=True).stdout.strip()

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
