from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any


def capabilities(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root).resolve()
    return {
        "terminal": True,
        "filesystem": True,
        "git": shutil.which("git") is not None,
        "python": shutil.which("python3") is not None or shutil.which("python") is not None,
        "browser_visible": False,
        "browser_headless": False,
        "mcp": False,
        "subagents": shutil.which("claude") is not None or shutil.which("codex") is not None,
        "hooks": True,
        "agent_runtimes": {
            "claude-code": shutil.which("claude") is not None,
            "codex": shutil.which("codex") is not None,
        },
        "runtime_files": {"claude-code": (root / "CLAUDE.md").exists(), "codex": (root / "AGENTS.md").exists()},
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
