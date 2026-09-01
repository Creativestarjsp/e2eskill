from pathlib import Path

from e2e.executor import _command, execute


def test_execute_is_safe_dry_run(tmp_path: Path):
    result = execute(tmp_path, "build login", runtime="claude-code", execute_agents=False)
    assert result["mode"] == "dry-run"
    assert result["status"] == "planned"
    assert result["workers"]


def test_execute_dry_run_never_launches_agent(tmp_path: Path, monkeypatch):
    called = []

    def fake(*args, **kwargs):
        called.append(args)
        raise AssertionError("agent must not launch in dry-run")

    monkeypatch.setattr("e2e.executor.subprocess.run", fake)
    result = execute(tmp_path, "build login", runtime="claude-code", execute_agents=False)
    assert result["status"] == "planned"
    assert not called


def test_runtime_command_shapes():
    assert _command("claude-code", "hello")[:4] == ["claude", "-p", "--output-format", "json"]
    assert _command("codex", "hello")[0:2] == ["codex", "exec"]
