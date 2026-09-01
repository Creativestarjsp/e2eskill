from e2e.introspection import diagnose


def test_introspection_escalates_merge_conflict(tmp_path):
    result = diagnose(tmp_path, {"status": "merge-conflict", "workers": [], "corrections": []})
    assert result["failure_class"] == "integration"
    assert result["escalate_to_sd3"] is True


def test_introspection_detects_timeout(tmp_path):
    result = diagnose(tmp_path, {"status": "worker-failure", "workers": [{"status": "timeout"}], "corrections": []})
    assert result["failure_class"] == "worker"
    assert result["escalate_to_sd3"] is False


def test_introspection_separates_test_failure(tmp_path):
    result = diagnose(
        tmp_path,
        {"status": "test-failure", "workers": [], "corrections": []},
    )
    assert result["failure_class"] == "test"
    assert result["skill_runtime_independent"] is True
    assert result["escalate_to_sd3"] is False


def test_introspection_separates_skill_failure(tmp_path):
    result = diagnose(
        tmp_path,
        {"status": "skill-failure", "workers": [], "corrections": []},
    )
    assert result["failure_class"] == "skill"
    assert result["skill_runtime_independent"] is False


def test_introspection_escalates_infrastructure_failure(tmp_path):
    result = diagnose(
        tmp_path,
        {"status": "infrastructure-failure", "workers": [], "corrections": []},
    )
    assert result["failure_class"] == "infrastructure"
    assert result["escalate_to_sd3"] is True
