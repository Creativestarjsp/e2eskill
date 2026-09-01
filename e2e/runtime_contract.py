from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

RUNTIMES = ("claude-code", "codex")
ROLES = ("sd1", "sd2", "sd3")


def _runtime_available(runtime: str) -> bool:
    return shutil.which("claude" if runtime == "claude-code" else "codex") is not None


def contract(root: str | Path = ".", runtime: str = "claude-code", role: str = "sd1") -> dict[str, Any]:
    root = Path(root).resolve()
    if runtime not in RUNTIMES:
        raise ValueError(f"unsupported runtime: {runtime}")
    if role not in ROLES:
        raise ValueError(f"unsupported role: {role}")

    runtime_file = "CLAUDE.md" if runtime == "claude-code" else "AGENTS.md"
    mcp_path = ".e2e/mcp/claude.json" if runtime == "claude-code" else ".e2e/mcp/codex.toml"
    command = ["claude", "-p", "--output-format", "json"] if runtime == "claude-code" else os.environ.get("E2E_CODEX_COMMAND", "codex exec").split()

    return {
        "contract_version": "1.0",
        "runtime": runtime,
        "runtime_available": _runtime_available(runtime),
        "role": role,
        "project_root": str(root),
        "context_sources": [
            "BRD.md", "PRD.md", "CLAUDE.md", "AGENTS.md", "CONVENTIONS.md",
            "E2E-PLAN.md", "SD-AGENT-SYSTEM.md", ".e2e/memory.json", ".e2e/brain.json",
        ],
        "runtime_instruction_file": runtime_file,
        "runtime_instruction_present": (root / runtime_file).exists(),
        "tool_policy": f".e2e/tool-policy-{role}.json",
        "mcp_config": mcp_path,
        "mcp_transport": "stdio",
        "browser_policy": {"visible_default": True, "headless_allowed": True, "visible_required_for": ["local-development", "interactive-qa", "ui-review", "sd3-verification"]},
        "execution": {"timeout_seconds": int(os.environ.get("E2E_AGENT_TIMEOUT", "1800")), "max_workers": 4, "dry_run_default": True},
        "evidence": {"required": True, "report_fields": ["changed_files", "commands", "tests", "evidence", "risks", "remaining_work"]},
        "approval_boundary": "E2E tool policy and MCP gateway are authoritative; memory is advisory only",
        "command_shape": command,
    }


def parity(root: str | Path = ".", role: str = "sd1") -> dict[str, Any]:
    contracts = {runtime: contract(root, runtime, role) for runtime in RUNTIMES}
    shared = {
        "contract_version": [contracts[r]["contract_version"] for r in RUNTIMES],
        "role": [contracts[r]["role"] for r in RUNTIMES],
        "context_sources": [contracts[r]["context_sources"] for r in RUNTIMES],
        "browser_policy": [contracts[r]["browser_policy"] for r in RUNTIMES],
        "execution": [contracts[r]["execution"] for r in RUNTIMES],
        "evidence": [contracts[r]["evidence"] for r in RUNTIMES],
        "approval_boundary": [contracts[r]["approval_boundary"] for r in RUNTIMES],
    }
    shared_equal = all(values[0] == values[1] for values in shared.values())
    return {"status": "pass" if shared_equal else "fail", "role": role, "shared_equal": shared_equal, "runtimes": contracts}
