from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .runtime_contract import parity
from .tools import check_registry, load_tools


def capabilities(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root).resolve()
    tools = load_tools(root)
    transports = sorted({tool.transport for tool in tools})
    gateway = (root / "e2e" / "tool_gateway.py").exists()
    return {
        "terminal": True,
        "filesystem": True,
        "git": shutil.which("git") is not None,
        "python": shutil.which("python3") is not None or shutil.which("python") is not None,
        "browser_visible": False,
        "browser_headless": False,
        "mcp": "mcp" in transports,
        "mcp_gateway": gateway,
        "registered_tools": len(tools),
        "tool_registry": check_registry(root),
        "subagents": shutil.which("claude") is not None or shutil.which("codex") is not None,
        "hooks": True,
        "agent_runtimes": {
            "claude-code": shutil.which("claude") is not None,
            "codex": shutil.which("codex") is not None,
        },
        "runtime_files": {"claude-code": (root / "CLAUDE.md").exists(), "codex": (root / "AGENTS.md").exists()},
        "runtime_contract": {"sd1": parity(root, "sd1"), "sd3": parity(root, "sd3")},
    }


def detect(root: str | Path = ".") -> str:
    root = Path(root).resolve()
    if (root / ".codex").exists() or (root / "AGENTS.md").exists():
        if (root / ".claude").exists() or (root / "CLAUDE.md").exists():
            return "claude-code+codex"
        return "codex"
    if (root / ".claude").exists() or (root / "CLAUDE.md").exists():
        return "claude-code"
    return "standalone"
