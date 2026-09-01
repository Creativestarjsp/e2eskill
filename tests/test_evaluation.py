from e2e.evaluation import evaluate_run


def test_evaluate_run_records_success(tmp_path):
    result = evaluate_run(tmp_path, "add feature", [{"id": "w1", "status": "completed", "returncode": 0}], ["app.py"])
    assert result["axes"]["correctness"] == 4
    assert result["blocking"] is False


def test_evaluate_run_blocks_failed_worker(tmp_path):
    result = evaluate_run(tmp_path, "add feature", [{"id": "w1", "status": "timeout", "returncode": None}], ["app.py"])
    assert result["blocking"] is True
    assert result["axes"]["evidence"] <= 2
