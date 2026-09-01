from pathlib import Path

from e2e.runtime_contract import contract, parity


def test_claude_and_codex_share_contract_surface(tmp_path: Path):
    result = parity(tmp_path, "sd1")
    assert result["status"] == "pass"
    assert result["shared_equal"] is True
    assert result["runtimes"]["claude-code"]["mcp_config"].endswith("claude.json")
    assert result["runtimes"]["codex"]["mcp_config"].endswith("codex.toml")


def test_contract_has_runtime_specific_instruction_file(tmp_path: Path):
    (tmp_path / "CLAUDE.md").write_text("claude", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("codex", encoding="utf-8")
    claude = contract(tmp_path, "claude-code", "sd1")
    codex = contract(tmp_path, "codex", "sd3")
    assert claude["runtime_instruction_file"] == "CLAUDE.md"
    assert codex["runtime_instruction_file"] == "AGENTS.md"
    assert claude["role"] == "sd1"
    assert codex["role"] == "sd3"


def test_invalid_runtime_is_rejected(tmp_path: Path):
    try:
        contract(tmp_path, "other", "sd1")
    except ValueError as exc:
        assert "unsupported runtime" in str(exc)
    else:
        raise AssertionError("invalid runtime must be rejected")
