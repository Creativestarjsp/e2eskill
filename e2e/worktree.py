from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


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


def commit_changes(workspace: WorkerWorkspace, message: str) -> str | None:
    if not has_changes(workspace):
        return None
    _git(workspace.path, "add", "-A")
    proc = _git(workspace.path, "commit", "-m", message)
    return proc.stdout.splitlines()[-1].strip() if proc.stdout else None


def merge(root: str | Path, workspace: WorkerWorkspace, message: str) -> str:
    root = Path(root).resolve()
    ensure_clean(root)
    _git(root, "merge", "--no-ff", workspace.branch, "-m", message)
    return current_ref(root)


def remove(root: str | Path, workspace: WorkerWorkspace, delete_branch: bool = True) -> None:
    root = Path(root).resolve()
    if workspace.path.exists():
        _git(root, "worktree", "remove", "--force", str(workspace.path))
    if delete_branch:
        proc = subprocess.run(["git", "branch", "-D", workspace.branch], cwd=root, text=True, capture_output=True)
        if proc.returncode != 0 and workspace.branch in proc.stderr:
            raise WorktreeError(proc.stderr.strip())


def cleanup_root(root: str | Path) -> None:
    root = Path(root).resolve()
    worktrees = root / ".e2e" / "worktrees"
    if not worktrees.exists():
        return
    for child in worktrees.iterdir():
        if child.is_dir():
            shutil.rmtree(child, ignore_errors=True)
