from pathlib import Path

from e2e.executor import execute


def test_execute_defaults_to_plan_when_runtime_exists_or_not(tmp_path: Path):
    result = execute(tmp_path, "build login")
    assert result["mode"] == "dry-run"
    assert result["status"] in {"planned", "runtime-unavailable"}


def test_execute_dry_run_never_launches_agent(tmp_path: Path, monkeypatch):
    called = []

    def fake(*args, **kwargs):
        called.append(args)
        raise AssertionError("agent must not launch in dry-run")

    monkeypatch.setattr("e2e.executor.subprocess.run", fake)
    result = execute(tmp_path, "build login", runtime="claude-code", execute_agents=False)
    assert result["status"] == "planned"
    assert not called
