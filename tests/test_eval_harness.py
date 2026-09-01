from e2e.eval_harness import compare_baseline, summarize_attempts


def test_pass_at_k_uses_independent_attempts():
    result = summarize_attempts([
        {"passed": True, "latency_seconds": 1},
        {"passed": False, "latency_seconds": 2},
        {"passed": False, "latency_seconds": 3},
        {"passed": True, "latency_seconds": 4},
    ], ks=(1, 2, 4))
    assert result["pass_rate"] == 0.5
    assert result["pass_at_k"]["1"] == 0.5
    assert result["pass_at_k"]["2"] == 0.8333
    assert result["pass_power_k"]["2"] == 0.25


def test_baseline_detects_quality_regression():
    result = compare_baseline(
        {"run_id": "current", "summary": {"pass_rate": 0.75, "mean_latency_seconds": 2.0}},
        {"run_id": "baseline", "summary": {"pass_rate": 1.0, "mean_latency_seconds": 1.0}},
    )
    assert result["status"] == "regression"
    assert "pass-rate-regression" in result["regressions"]
    assert "latency-regression" in result["regressions"]
