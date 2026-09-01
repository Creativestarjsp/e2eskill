from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from .orchestrator import plan
from .tool_gateway import write_mcp_configs
from .tools import write_policy
from .worktree import WorktreeError, WorkerWorkspace, commit_changes, create, ensure_clean, merge, remove


class RuntimeUnavailable(RuntimeError):
    pass


MAX_CORRECTIONS = 2


def _command(runtime: str, prompt: str, mcp_config: str | None = None) -> list[str]:
    if runtime == "claude-code":
        command = ["claude", "-p", "--output-format", "json"]
        if mcp_config:
            command += ["--mcp-config", mcp_config, "--strict-mcp-config"]
        return command + [prompt]
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


def _prompt(task: str, worker: dict[str, Any], policy_path: str | None = None, mcp_config: str | None = None) -> str:
    context = json.dumps(worker.get("inputs", {}).get("context", {}), ensure_ascii=False, indent=2)
    policy = f"\nTOOL POLICY: {policy_path}\nRead this policy before using tools. Default is deny. Do not use approval-required tools without explicit approval." if policy_path else ""
    gateway = f"\nE2E MCP GATEWAY: {mcp_config}\nUse the E2E gateway for registered tools. Do not bypass its authorization boundary." if mcp_config else ""
    return f"""You are an SD1 worker in the E2E engineering system.\n\nROLE: {worker['skill']}\nWORKER: {worker['id']}\nPHASE: {worker['phase']}\nTASK: {task}\n{policy}{gateway}\n\nExecute only the assigned responsibility. Investigate the repository before editing. Reuse existing code and dependencies before adding new ones. Do not claim work you did not perform. Preserve security, data integrity, accessibility, and existing behavior. Work only inside the provided isolated workspace. Do not modify or inspect sibling worktrees. Do not create commits unless the runtime requires it.\n\nPROJECT CONTEXT:\n{context}\n\nWhen finished, report: changed files, implementation summary, commands/tests run, evidence, risks, and remaining work. If blocked, explain the concrete blocker and stop rather than inventing a workaround."""


def _supervisor_prompt(task: str, results: list[dict[str, Any]], correction_round: int = 0, policy_path: str | None = None, mcp_config: str | None = None) -> str:
    evidence = json.dumps(results, ensure_ascii=False, indent=2)
    policy = f"\nTOOL POLICY: {policy_path}\nUse only the read/verification capabilities allowed to SD3. Do not mutate the repository or external systems through tools." if policy_path else ""
    gateway = f"\nE2E MCP GATEWAY: {mcp_config}\nUse the gateway for registered read/verification tools. Do not bypass its authorization boundary." if mcp_config else ""
    return f"""You are the SD3 Engineering Supervisor. Independently inspect the integrated repository after SD1 execution for this task: {task}.\n\nCORRECTION ROUND: {correction_round}\n{policy}{gateway}\n\nSD1 REPORTS:\n{evidence}\n\nDo not trust worker claims without inspecting the actual files and running appropriate verification. Check requirements, architecture, integration, tests, security, regressions, and evidence. Fix nothing. Return valid JSON only with this shape:\n{{\"decision\":\"approved|needs-correction|rejected\",\"evidence\":[\"...\"],\"failed_checks\":[\"...\"],\"correction_tasks\":[{{\"task\":\"specific corrective task\",\"skill\":\"best specialist skill\"}}],\"next_actions\":[\"...\"]}}\n\nUse needs-correction when concrete fixable work remains. Use rejected when the architecture/requirements are fundamentally unacceptable. Keep correction_tasks minimal and actionable. If approved, correction_tasks must be empty."""


def _parse_supervisor_output(stdout: str) -> dict[str, Any]:
    candidates = re.findall(r"\{.*\}", stdout, flags=re.DOTALL)
    for candidate in reversed(candidates):
        try:
            value = json.loads(candidate)
            if isinstance(value, dict) and value.get("decision"):
                return value
        except json.JSONDecodeError:
            continue
    return {"decision": "unknown", "evidence": [], "failed_checks": ["supervisor output was not valid JSON"], "correction_tasks": [], "next_actions": []}


def _runtime_config(workspace: Path, runtime: str, role: str) -> Path:
    configs = write_mcp_configs(workspace, role)
    return Path(configs["claude"] if runtime == "claude-code" else configs["codex"])


def _codex_environment(workspace: Path, config_path: Path) -> dict[str, str]:
    home = workspace / ".e2e" / "mcp" / "codex-home"
    home.mkdir(parents=True, exist_ok=True)
    (home / "config.toml").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")
    env = os.environ.copy()
    env["CODEX_HOME"] = str(home)
    return env


def _run_worker(root: Path, task: str, runtime: str, worker: dict[str, Any], base_ref: str) -> tuple[dict[str, Any], WorkerWorkspace | None]:
    started = time.time()
    workspace: WorkerWorkspace | None = None
    try:
        workspace = create(root, worker["id"], base_ref=base_ref)
        policy_path = write_policy(workspace.path, "sd1")
        mcp_config = _runtime_config(workspace.path, runtime, "sd1")
        env = _codex_environment(workspace.path, mcp_config) if runtime == "codex" else None
        prompt = _prompt(task, worker, policy_path.relative_to(workspace.path).as_posix(), mcp_config.relative_to(workspace.path).as_posix())
        config_arg = mcp_config.relative_to(workspace.path).as_posix() if runtime == "claude-code" else None
        proc = subprocess.run(_command(runtime, prompt, config_arg), cwd=workspace.path, env=env, text=True, capture_output=True, timeout=int(os.environ.get("E2E_AGENT_TIMEOUT", "1800")))
        status = "completed" if proc.returncode == 0 else "failed"
        commit_sha = commit_changes(workspace, f"e2e: implement {worker['id']}") if status == "completed" else None
        return {"id": worker["id"], "skill": worker["skill"], "phase": worker["phase"], "workspace": str(workspace.path), "branch": workspace.branch, "commit": commit_sha, "tool_policy": str(policy_path.relative_to(workspace.path)), "mcp_config": str(mcp_config.relative_to(workspace.path)), "returncode": proc.returncode, "stdout": proc.stdout[-12000:], "stderr": proc.stderr[-12000:], "duration_seconds": round(time.time() - started, 3), "status": status}, workspace
    except subprocess.TimeoutExpired as exc:
        return {"id": worker["id"], "skill": worker["skill"], "phase": worker["phase"], "workspace": str(workspace.path) if workspace else None, "returncode": None, "stdout": str(exc.stdout or "")[-12000:], "stderr": str(exc.stderr or "")[-12000:], "duration_seconds": round(time.time() - started, 3), "status": "timeout"}, workspace
    except (WorktreeError, OSError) as exc:
        return {"id": worker["id"], "skill": worker["skill"], "phase": worker["phase"], "workspace": str(workspace.path) if workspace else None, "returncode": None, "stdout": "", "stderr": str(exc), "duration_seconds": round(time.time() - started, 3), "status": "workspace-failure"}, workspace


def _merge_workspace(root: Path, workspace: WorkerWorkspace, worker_id: str) -> tuple[bool, str | None]:
    try:
        ensure_clean(root)
        return True, merge(root, workspace, f"e2e: integrate {worker_id}")
    except WorktreeError:
        subprocess.run(["git", "merge", "--abort"], cwd=root, text=True, capture_output=True)
        return False, None


def _refresh_brain(root: Path) -> dict[str, Any]:
    proc = subprocess.run(["python", "-m", "e2e", "brain", "build"], cwd=root, text=True, capture_output=True, timeout=300)
    return {"returncode": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:], "status": "pass" if proc.returncode == 0 else "failed"}


def _correction_worker(root: Path, task: str, skill: str, runtime: str, round_no: int, base_ref: str) -> tuple[dict[str, Any], WorkerWorkspace | None]:
    worker = {"id": f"sd1-correction-{round_no}", "skill": skill or "software-architect", "phase": "correction", "inputs": {"context": {"correction_round": round_no}}}
    return _run_worker(root, task, runtime, worker, base_ref)


def _supervise(root: Path, task: str, runtime: str, workers: list[dict[str, Any]], correction_round: int) -> dict[str, Any]:
    started = time.time()
    policy_path = write_policy(root, "sd3")
    mcp_config = _runtime_config(root, runtime, "sd3")
    env = _codex_environment(root, mcp_config) if runtime == "codex" else None
    prompt = _supervisor_prompt(task, workers, correction_round, policy_path.relative_to(root).as_posix(), mcp_config.relative_to(root).as_posix())
    config_arg = mcp_config.relative_to(root).as_posix() if runtime == "claude-code" else None
    proc = subprocess.run(_command(runtime, prompt, config_arg), cwd=root, env=env, text=True, capture_output=True, timeout=int(os.environ.get("E2E_AGENT_TIMEOUT", "1800")))
    report = _parse_supervisor_output(proc.stdout)
    return {"id": "sd3-supervisor", "returncode": proc.returncode, "stdout": proc.stdout[-16000:], "stderr": proc.stderr[-12000:], "duration_seconds": round(time.time() - started, 3), "status": "completed" if proc.returncode == 0 else "failed", "report": report, "tool_policy": str(policy_path.relative_to(root)), "mcp_config": str(mcp_config.relative_to(root))}


def execute(root: str | Path, task: str, runtime: str = "auto", execute_agents: bool = False, max_workers: int = 4) -> dict[str, Any]:
    root = Path(root).resolve()
    selected = runtime
    if selected == "auto":
        selected = "claude-code" if runtime_available("claude-code") else ("codex" if runtime_available("codex") else "unavailable")
    execution = {"task": task, "runtime": selected, "mode": "execute" if execute_agents else "dry-run", "started_at": time.time(), "workers": [], "supervisor": None, "corrections": [], "parallel": bool(execute_agents), "max_workers": max(1, min(max_workers, 4)), "max_corrections": MAX_CORRECTIONS}
    if selected == "unavailable":
        execution["status"] = "runtime-unavailable"; execution["next"] = "Install Claude Code or Codex, or select a configured runtime."; return execution
    p = plan(root, task)
    if not execute_agents:
        execution["status"] = "planned"; execution["workers"] = [{"id": w["id"], "skill": w["skill"], "phase": w["phase"], "depends_on": w.get("depends_on", [])} for w in p["workers"][: execution["max_workers"]]]; execution["next"] = "Re-run with --execute to launch the selected runtime."; return execution
    if not runtime_available(selected):
        raise RuntimeUnavailable(f"{selected} is not installed or not on PATH")
    try: ensure_clean(root)
    except WorktreeError as exc:
        execution["status"] = "dirty-working-tree"; execution["next"] = str(exc); return execution
    completed: set[str] = set(); pending = list(p["workers"]); preserved_workspaces: list[str] = []
    base_ref = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=True).stdout.strip()
    while pending and execution.get("status") is None:
        ready = [w for w in pending if all(dep in completed for dep in w.get("depends_on", []))]
        if not ready: execution["status"] = "blocked-dependency-cycle"; break
        batch = ready[: execution["max_workers"]]
        with ThreadPoolExecutor(max_workers=len(batch)) as pool:
            futures = {pool.submit(_run_worker, root, task, selected, worker, base_ref): worker for worker in batch}; results = [(futures[f], *f.result()) for f in as_completed(futures)]
        results.sort(key=lambda item: batch.index(item[0]))
        for worker, result, workspace in results:
            execution["workers"].append(result); pending.remove(worker)
            if result["status"] != "completed" or workspace is None:
                execution["status"] = "worker-failure"; preserved_workspaces.extend([str(x.path) for _, _, x in results if x and (workspace is None or str(x.path) != str(workspace.path))]);
                if workspace: preserved_workspaces.append(str(workspace.path))
                break
        if execution.get("status"): break
        for worker, result, workspace in results:
            ok, merged_sha = _merge_workspace(root, workspace, worker["id"]); result["merged"] = ok; result["integrated_commit"] = merged_sha
            if not ok: execution["status"] = "merge-conflict"; preserved_workspaces.append(str(workspace.path)); break
            completed.add(worker["id"])
            try: remove(root, workspace)
            except WorktreeError: preserved_workspaces.append(str(workspace.path))
        if execution.get("status"): break
        base_ref = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=True).stdout.strip()
    if preserved_workspaces: execution["preserved_workspaces"] = preserved_workspaces
    if execution.get("status") is None:
        execution["brain_refresh"] = _refresh_brain(root)
        for correction_round in range(MAX_CORRECTIONS + 1):
            supervisor = _supervise(root, task, selected, execution["workers"], correction_round); execution["supervisor"] = supervisor
            if supervisor["status"] != "completed": execution["status"] = "supervisor-failure"; break
            decision = supervisor["report"].get("decision")
            if decision == "approved": execution["status"] = "approved"; break
            if decision == "rejected": execution["status"] = "rejected"; execution["next"] = supervisor["report"].get("next_actions", []); break
            if decision != "needs-correction": execution["status"] = "supervisor-invalid-report"; break
            if correction_round >= MAX_CORRECTIONS: execution["status"] = "correction-limit-reached"; execution["next"] = supervisor["report"].get("next_actions", []); break
            tasks = supervisor["report"].get("correction_tasks", [])
            if not tasks: execution["status"] = "correction-without-task"; break
            base_ref = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=True).stdout.strip()
            item = tasks[0]; correction_task = str(item.get("task", "Fix SD3-identified issues")); correction_skill = str(item.get("skill", "software-architect"))
            result, workspace = _correction_worker(root, correction_task, correction_skill, selected, correction_round + 1, base_ref); execution["corrections"].append(result)
            if result["status"] != "completed" or workspace is None:
                execution["status"] = "correction-worker-failure"; execution.setdefault("preserved_workspaces", []).append(str(workspace.path) if workspace else "unknown"); break
            ok, merged_sha = _merge_workspace(root, workspace, result["id"]); result["merged"] = ok; result["integrated_commit"] = merged_sha
            if not ok: execution["status"] = "correction-merge-conflict"; execution.setdefault("preserved_workspaces", []).append(str(workspace.path)); break
            try: remove(root, workspace)
            except WorktreeError: execution.setdefault("preserved_workspaces", []).append(str(workspace.path))
            execution["brain_refresh"] = _refresh_brain(root)
    if execution.get("status") is None: execution["status"] = "completed-without-supervisor"
    execution["finished_at"] = time.time(); out = root / ".e2e" / "executions"; out.mkdir(parents=True, exist_ok=True); path = out / f"{int(execution['finished_at'] * 1000)}.json"; path.write_text(json.dumps(execution, indent=2, sort_keys=True), encoding="utf-8"); execution["report_path"] = path.relative_to(root).as_posix(); return execution
