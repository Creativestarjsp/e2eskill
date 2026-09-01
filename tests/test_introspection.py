from e2e.introspection import diagnose


def test_introspection_escalates_merge_conflict(tmp_path):
    result = diagnose(tmp_path, {"status": "merge-conflict", "workers": [], "corrections": []})
    assert result["failure_class"] == "integration"
    assert result["escalate_to_sd3"] is True


def test_introspection_detects_timeout(tmp_path):
    result = diagnose(tmp_path, {"status": "worker-failure", "workers": [{"status": "timeout"}], "corrections": []})
    assert result["failure_class"] == "worker"
    assert result["escalate_to_sd3"] is False
