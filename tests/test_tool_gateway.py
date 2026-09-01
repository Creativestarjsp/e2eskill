import json
from pathlib import Path

from e2e.tool_gateway import handle


def test_tools_list_is_role_scoped(tmp_path: Path):
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    (runtime / "tools.json").write_text(
        json.dumps({"tools": [
            {"name": "repo.read", "description": "read", "transport": "native", "risk": "read", "scopes": ["repo.read"], "roles": ["sd1", "sd3"], "approval": "none"},
            {"name": "git.write", "description": "write", "transport": "native", "risk": "write", "scopes": ["git.write"], "roles": ["sd1"], "approval": "explicit"},
        ]}),
        encoding="utf-8",
    )
    response = handle(tmp_path, "sd1", {"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert [tool["name"] for tool in response["result"]["tools"]] == ["repo.read"]


def test_repo_read_executes_and_audits(tmp_path: Path):
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    (runtime / "tools.json").write_text(
        json.dumps({"tools": [{"name": "repo.read", "description": "read", "transport": "native", "risk": "read", "scopes": ["repo.read"], "roles": ["sd1"], "approval": "none"}]}),
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")
    response = handle(tmp_path, "sd1", {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "repo.read", "arguments": {"path": "README.md"}}})
    assert response["result"]["structuredContent"]["content"] == "hello"
    assert (tmp_path / ".e2e" / "tool-audit.jsonl").exists()


def test_repo_read_blocks_path_escape(tmp_path: Path):
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    (runtime / "tools.json").write_text(
        json.dumps({"tools": [{"name": "repo.read", "description": "read", "transport": "native", "risk": "read", "scopes": ["repo.read"], "roles": ["sd1"], "approval": "none"}]}),
        encoding="utf-8",
    )
    response = handle(tmp_path, "sd1", {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "repo.read", "arguments": {"path": "../secret.txt"}}})
    assert response["error"]["code"] == -32005
