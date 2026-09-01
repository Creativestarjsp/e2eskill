from pathlib import Path

from e2e.brain import CodeBrain


def test_brain_build_and_search(tmp_path: Path):
    (tmp_path / "app.py").write_text("def login():\n    return True\n\ndef handle():\n    return login()\n")
    brain = CodeBrain(tmp_path, provider="regex")
    data = brain.build()
    assert any(s["name"] == "login" for s in data["symbols"])
    assert brain.search("login")
    assert brain.callers("login")
    assert brain.check()["fresh"]
    assert data["provider"] == "regex"


def test_impact_reports_coverage(tmp_path: Path):
    (tmp_path / "app.py").write_text("def login():\n    return True\n\ndef handle():\n    return login()\n")
    brain = CodeBrain(tmp_path, provider="regex")
    brain.build()
    impact = brain.impact("login")
    assert impact["affected_files"] == ["app.py"]
    assert impact["coverage"] == "structural"


def test_auto_provider_keeps_fallback_portable(tmp_path: Path):
    (tmp_path / "app.py").write_text("def login():\n    return True\n")
    brain = CodeBrain(tmp_path, provider="auto")
    data = brain.build()
    assert data["providers"]
    assert data["provider"] in {"tree-sitter", "regex", "regex-fallback"}
    assert any(s["name"] == "login" for s in data["symbols"])
