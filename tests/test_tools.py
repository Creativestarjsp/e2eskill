import json
from pathlib import Path

from e2e.tools import audit, check_registry, decide, load_tools, policy_for_role, write_policy


def test_registry_is_valid():
    root = Path(__file__).resolve().parents[1]
    result = check_registry(root)
    assert result["status"] == "pass"
    assert result["tools"] >= 10


def test_unknown_tool_is_denied(tmp_path: Path):
    (tmp_path / "runtime").mkdir()
    (tmp_path / "runtime" / "tools.json").write_text(json.dumps({"tools": []}), encoding="utf-8")
    decision = decide(tmp_path, "missing.tool", "sd1", set())
    assert decision.allowed is False
    assert decision.reason == "unknown-tool"


def test_explicit_approval_is_required(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    decision = decide(root, "shell.write", "sd1", {"shell.write"})
    assert decision.allowed is False
    assert decision.reason == "approval-required"
    approved = decide(root, "shell.write", "sd1", {"shell.write"}, approved=True)
    assert approved.allowed is True


def test_audit_never_writes_secret_values(tmp_path: Path):
    decision = decide(Path(__file__).resolve().parents[1], "repo.read", "sd1", {"repo.read"})
    event = audit(
        tmp_path,
        agent="sd1-worker-test",
        runtime="test",
        tool="repo.read",
        operation="read",
        decision=decision,
        arguments={"path": "README.md", "api_token": "super-secret"},
        result="ok",
    )
    assert event["arguments_fingerprint"] != "super-secret"
    text = (tmp_path / ".e2e" / "tool-audit.jsonl").read_text(encoding="utf-8")
    assert "super-secret" not in text


def test_tools_have_stable_names():
    root = Path(__file__).resolve().parents[1]
    names = [tool.name for tool in load_tools(root)]
    assert names == sorted(names) or len(names) > 0


def test_role_policy_separates_safe_and_approval_tools():
    root = Path(__file__).resolve().parents[1]
    policy = policy_for_role(root, "sd1")
    safe = {item["name"] for item in policy["allowed_tools"]}
    approval = {item["name"] for item in policy["approval_required_tools"]}
    assert "repo.read" in safe
    assert "shell.write" in approval
    assert not safe & approval


def test_write_policy_materializes_runtime_contract(tmp_path: Path):
    source = Path(__file__).resolve().parents[1]
    (tmp_path / "runtime").mkdir()
    (tmp_path / "runtime" / "tools.json").write_text((source / "runtime" / "tools.json").read_text(encoding="utf-8"), encoding="utf-8")
    path = write_policy(tmp_path, "sd3")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["role"] == "sd3"
    assert data["default_policy"] == "deny"
    assert all(item["name"] not in {x["name"] for x in data["approval_required_tools"]} for item in data["allowed_tools"])
