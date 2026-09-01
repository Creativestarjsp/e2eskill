from e2e.executor import _parse_supervisor_output


def test_supervisor_json_is_parsed():
    result = _parse_supervisor_output('''review\n{"decision":"needs-correction","evidence":["test failed"],"failed_checks":["tests"],"correction_tasks":[{"task":"fix failing test","skill":"qa-engineer"}],"next_actions":["rerun verification"]}\n''')
    assert result["decision"] == "needs-correction"
    assert result["correction_tasks"][0]["skill"] == "qa-engineer"


def test_invalid_supervisor_output_does_not_trigger_correction():
    result = _parse_supervisor_output("not json")
    assert result["decision"] == "unknown"
    assert result["correction_tasks"] == []
