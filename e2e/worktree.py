from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .guardrails import enforce as enforce_guardrails


class WorktreeError(RuntimeError):
    pass


@dataclass(frozen=True)
class WorkerWorkspace:
    worker_id: str
    path: Path
    branch: str
    base_ref: str


def _git(root: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(["git", *args], cwd=cwd or root, text=True, capture_output=True)
    if proc.returncode != 0:
        raise WorktreeError(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc


def ensure_clean(root: str | Path) -> None:
    root = Path(root).resolve()
    status = _git(root, "status", "--porcelain").stdout.strip()
    if status:
        raise WorktreeError("main working tree must be clean before parallel agent execution")


def current_ref(root: str | Path) -> str:
    root = Path(root).resolve()
    return _git(root, "rev-parse", "HEAD").stdout.strip()


def create(root: str | Path, worker_id: str, base_ref: str | None = None) -> WorkerWorkspace:
    root = Path(root).resolve()
    ensure_clean(root)
    base_ref = base_ref or current_ref(root)
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in worker_id)
    branch = f"e2e/{safe}"
    path = root / ".e2e" / "worktrees" / safe
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise WorktreeError(f"worker workspace already exists: {path}")
    _git(root, "worktree", "add", "-b", branch, str(path), base_ref)
    return WorkerWorkspace(worker_id=worker_id, path=path, branch=branch, base_ref=base_ref)


def has_changes(workspace: WorkerWorkspace) -> bool:
    return bool(_git(workspace.path, "status", "--porcelain").stdout.strip())


def _tracked_changes(workspace: WorkerWorkspace) -> list[str]:
    proc = _git(workspace.path, "status", "--porcelain").stdout
    return sorted({line[3:].strip() for line in proc.splitlines() if len(line) >= 4})


def commit_changes(workspace: WorkerWorkspace, message: str) -> str | None:
    if not has_changes(workspace):
        return None
    enforce_guardrails(workspace.path, "pre-commit", _tracked_changes(workspace))
    _git(workspace.path, "add", "-A")
    enforce_guardrails(workspace.path, "pre-commit")
    _git(workspace.path, "commit", "-m", message)
    return _git(workspace.path, "rev-parse", "HEAD").stdout.strip()


def merge(root: str | Path, workspace: WorkerWorkspace, message: str) -> str:
    root = Path(root).resolve()
    ensure_clean(root)
    enforce_guardrails(workspace.path, "pre-merge", _tracked_changes(workspace))
    _git(root, "merge", "--no-ff", workspace.branch, "-m", message)
    try:
        enforce_guardrails(root, "verification")
    except RuntimeError as exc:
        _git(root, "merge", "--abort")
        raise WorktreeError(f"post-merge guardrail blocked integration: {exc}") from exc
    return current_ref(root)


def remove(root: str | Path, workspace: WorkerWorkspace, delete_branch: bool = True) -> None:
    root = Path(root).resolve()
    if workspace.path.exists():
        _git(root, "worktree", "remove", "--force", str(workspace.path))
    if delete_branch:
        try:
            _git(root, "branch", "-D", workspace.branch)
        except WorktreeError as exc:
            if workspace.branch in str(exc):
                raise


def cleanup_root(root: str | Path) -> None:
    root = Path(root).resolve()
    worktrees = root / ".e2e" / "worktrees"
    if not worktrees.exists():
        return
    for child in worktrees.iterdir():
        if child.is_dir():
            shutil.rmtree(child, ignore_errors=True)
