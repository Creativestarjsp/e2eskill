from pathlib import Path
import subprocess

from e2e.worktree import create, current_ref, has_changes, remove


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=True).stdout.strip()


def test_isolated_worktree_lifecycle(tmp_path: Path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "e2e@example.com")
    _git(tmp_path, "config", "user.name", "E2E Test")
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-m", "base")

    workspace = create(tmp_path, "sd1-worker-test", base_ref=current_ref(tmp_path))
    (workspace.path / "worker.txt").write_text("worker\n", encoding="utf-8")
    assert has_changes(workspace)
    _git(workspace.path, "add", "worker.txt")
    _git(workspace.path, "commit", "-m", "worker change")
    remove(tmp_path, workspace)

    assert not workspace.path.exists()
    assert "worker.txt" not in _git(tmp_path, "ls-files")
