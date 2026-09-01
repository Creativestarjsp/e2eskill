import json

from e2e.run_artifacts import persist_run


def test_persist_run_writes_structured_artifacts(tmp_path):
    execution = {
        "task": "add feature",
        "runtime": "codex",
        "mode": "execute",
        "status": "approved",
        "workers": [
            {
                "id": "w1",
                "status": "completed",
                "returncode": 0,
                "stdout": "done",
                "stderr": "",
            }
        ],
        "supervisor": {"status": "completed", "report": {"decision": "approved"}},
    }
    evaluation = {"blocking": False, "aggregate": 4.0}
    introspection = {"failure_class": "unknown", "escalate_to_sd3": False}

    path = persist_run(tmp_path, execution, evaluation, introspection)
    run_dir = tmp_path / path

    assert (run_dir / "execution.json").exists()
    assert (run_dir / "workers" / "w1" / "report.json").exists()
    assert (run_dir / "workers" / "w1" / "stdout.txt").read_text() == "done"
    assert json.loads((run_dir / "evaluation.json").read_text())["blocking"] is False
    assert json.loads((run_dir / "final.json").read_text())["status"] == "approved"
