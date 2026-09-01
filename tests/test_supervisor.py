import json

import e2e.supervisor as supervisor


def test_independent_review_uses_completed_execution_task(tmp_path, monkeypatch):
    report = tmp_path / "execution.json"
    report.write_text(
        json.dumps(
            {
                "task": "Implement discount-aware calculate_total and focused tests.",
                "workers": [{"id": "w1", "status": "completed"}],
            }
        ),
        encoding="utf-8",
    )

    captured = {}
    monkeypatch.setattr(supervisor, "runtime_available", lambda runtime: True)

    def fake_supervise(root, task, runtime, workers, correction_round):
        captured["task"] = task
        captured["workers"] = workers
        return {"report": {"decision": "approved"}}

    monkeypatch.setattr(supervisor, "_supervise", fake_supervise)

    result = supervisor.run_independent_review(
        tmp_path,
        "api-backend",
        "claude-code",
        report,
    )

    assert captured["task"] == "Implement discount-aware calculate_total and focused tests."
    assert result["requested_task"] == "api-backend"
    assert result["review_task"] == captured["task"]
    assert result["mode"] == "independent-read-only"
