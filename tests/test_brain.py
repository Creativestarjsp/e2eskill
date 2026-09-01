from pathlib import Path

from e2e.brain import CodeBrain


def test_brain_build_and_search(tmp_path: Path):
    (tmp_path / "app.py").write_text("def login():\n    return True\n\ndef handle():\n    return login()\n")
    brain = CodeBrain(tmp_path)
    data = brain.build()
    assert any(s["name"] == "login" for s in data["symbols"])
    assert brain.search("login")
    assert brain.callers("login")
    assert brain.check()["fresh"]


def test_impact_reports_coverage(tmp_path: Path):
    (tmp_path / "app.py").write_text("def login():\n    return True\n\ndef handle():\n    return login()\n")
    brain = CodeBrain(tmp_path)
    brain.build()
    impact = brain.impact("login")
    assert impact["affected_files"] == ["app.py"]
    assert impact["coverage"] == "structural"
