from e2e.regression import analyze_regression_risk, find_regressions


def test_regression_risk_detects_related_failed_history(tmp_path):
    evals = tmp_path / ".e2e" / "evals"
    evals.mkdir(parents=True)
    (evals / "auth.json").write_text('{"suite":"authentication","summary":{"passed":2,"failed":1}}', encoding="utf-8")

    result = analyze_regression_risk(tmp_path, "add authentication")

    assert result["level"] == "medium"
    assert result["historical_failures"]
    assert "historical-failure" == result["historical_failures"][0]["signal"]


def test_regression_risk_is_low_without_history(tmp_path):
    result = analyze_regression_risk(tmp_path, "add dashboard")
    assert result["level"] == "low"
    assert result["historical_failures"] == []
