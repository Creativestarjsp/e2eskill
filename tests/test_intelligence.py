from e2e.intelligence import build_intelligence, synthesize_run
from e2e.orchestrator import plan


def test_build_intelligence_creates_risk_and_verification_plan(tmp_path):
    plan_data = {
        "skills": [{"name": "backend-developer"}],
        "workers": [{"id": "w1", "skill": "backend-developer", "phase": "implementation"}],
        "context": {"brain": "context"},
        "preflight": {"research_first": True},
    }
    result = build_intelligence(tmp_path, "add authentication API", plan_data)

    assert result["risk"]["high_risk"] is True
    assert "security" in result["risk"]["levels"]
    assert result["research_first"] is True
    assert result["required_tests"]
    assert result["evidence_contract"]
    assert result["advisory_only"] is True
    assert "independent SD3 review before approval" in result["verification_plan"]
    assert result["intelligence_fingerprint"]


def test_orchestrator_plan_contains_intelligence(tmp_path):
    result = plan(tmp_path, "add authentication API")

    assert result["intelligence"]["schema_version"] == "2.0"
    assert result["intelligence"]["task"] == "add authentication API"
    assert result["intelligence"]["repository_impact"]["codebrain"]["revision"]


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
