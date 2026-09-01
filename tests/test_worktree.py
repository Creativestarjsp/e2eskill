from pathlib import Path

import e2e.worktree as worktree


def test_create_uses_isolated_branch_and_path(tmp_path: Path, monkeypatch):
    calls = []

    class Result:
        stdout = "abc123\n"

    def fake_git(root, *args, cwd=None):
        calls.append((root, args, cwd))
        return Result()

    monkeypatch.setattr(worktree, "_git", fake_git)
    workspace = worktree.create(tmp_path, "sd1-worker-test", base_ref="abc123")

    assert workspace.worker_id == "sd1-worker-test"
    assert workspace.branch == "e2e/sd1-worker-test"
    assert workspace.path == tmp_path / ".e2e" / "worktrees" / "sd1-worker-test"
    assert any("worktree" in call[1] and "add" in call[1] for call in calls)


def test_remove_uses_git_worktree_cleanup(tmp_path: Path, monkeypatch):
    calls = []

    class Result:
        stdout = ""

    monkeypatch.setattr(worktree, "_git", lambda root, *args, cwd=None: calls.append(args) or Result())
    workspace = worktree.WorkerWorkspace("worker", tmp_path / "workspace", "e2e/worker", "abc123")
    workspace.path.mkdir(parents=True)

    worktree.remove(tmp_path, workspace)

    assert any(args[:3] == ("worktree", "remove", "--force") for args in calls)
