from pathlib import Path

import pytest

from e2e.guardrails import check, write_policy
from e2e.worktree import WorkerWorkspace, WorktreeError, commit_changes


def _root(tmp_path: Path) -> Path:
    (tmp_path / ".git").mkdir()
    (tmp_path / "runtime").mkdir()
    return tmp_path


def test_guardrail_policy_is_materialized(tmp_path: Path):
    path = write_policy(tmp_path)
    assert path.exists()
    assert "pre-commit" in path.read_text(encoding="utf-8")


def test_protected_runtime_path_is_blocked(tmp_path: Path):
    result = check(tmp_path, "pre-commit", [".e2e/worktrees/worker/file.txt"])
    assert result["status"] == "block"
    assert "runtime-protected-paths" in result["blocked_rules"]


def test_secret_like_content_is_blocked(tmp_path: Path):
    (tmp_path / "bad.py").write_text('api_key = "abcdefghijklmnopqrstuvwxyz"\n', encoding="utf-8")
    result = check(tmp_path, "pre-commit", ["bad.py"])
    assert result["status"] == "block"
    assert "secrets" in result["blocked_rules"]


def test_commit_boundary_blocks_secret(tmp_path: Path, monkeypatch):
    workspace = WorkerWorkspace("worker", tmp_path, "e2e/worker", "HEAD")
    (tmp_path / "bad.py").write_text('token = "abcdefghijklmnopqrstuvwxyz"\n', encoding="utf-8")
    monkeypatch.setattr("e2e.worktree.has_changes", lambda _: True)
    with pytest.raises(RuntimeError):
        commit_changes(workspace, "test")
