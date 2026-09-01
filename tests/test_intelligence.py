from e2e.intelligence import build_intelligence, synthesize_run


def test_build_intelligence_creates_risk_and_verification_plan(tmp_path):
    plan = {
        "skills": ["backend-developer"],
        "workers": [{"id": "w1"}],
        "context": {"brain": "context"},
        "preflight": {"research_first": True},
    }
    result = build_intelligence(tmp_path, "add authentication API", plan)

    assert result["risk"]["high_risk"] is True
    assert "security" in result["risk"]["levels"]
    assert result["research_first"] is True
    assert "independent SD3 review before approval" in result["verification_plan"]
    assert result["intelligence_fingerprint"]


def test_synthesize_run_blocks_unverified_execution():
    execution = {
        "status": "supervisor-failure",
        "supervisor": {"report": {"decision": "unknown"}},
    }
    evaluation = {"blocking": True, "aggregate": 2.0, "failed_checks": ["test failure"]}
    introspection = {"failure_class": "verification", "escalate_to_sd3": True}

    result = synthesize_run(execution, evaluation, introspection)

    assert result["readiness"] == "do-not-ship"
    assert result["escalate_to_sd3"] is True
    assert "SD3 approval is not established" in result["evidence_gaps"]
