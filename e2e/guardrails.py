from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .hooks import run


PROTECTED_PREFIXES = (".git/", ".e2e/worktrees/")


def changed_files(root: str | Path) -> list[str]:
    root = Path(root).resolve()
    import subprocess

    proc = subprocess.run(
        ["git", "diff", "--name-only", "--cached"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode:
        return []
    return sorted({line.strip() for line in proc.stdout.splitlines() if line.strip()})


def check(root: str | Path, stage: str, files: list[str] | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    files = files if files is not None else changed_files(root)
    hook_results = run(stage, root, files)
    protected = [path for path in files if path.startswith(PROTECTED_PREFIXES)]
    if protected:
        hook_results.extend(
            {
                "status": "block",
                "rule": "runtime-protected-paths",
                "evidence": protected,
                "message": "Runtime-managed paths cannot be committed or integrated by workers.",
                "remediation": "Keep .e2e runtime state and Git internals outside worker changes.",
            }
            for _ in [0]
        )
    blocked = [item for item in hook_results if item.get("status") == "block"]
    return {
        "status": "block" if blocked else "pass",
        "stage": stage,
        "changed_files": files,
        "checks": hook_results,
        "blocked_rules": sorted({item.get("rule", "unknown") for item in blocked}),
    }


def enforce(root: str | Path, stage: str, files: list[str] | None = None) -> dict[str, Any]:
    result = check(root, stage, files)
    if result["status"] != "pass":
        raise RuntimeError(json.dumps(result, sort_keys=True))
    return result


def policy() -> dict[str, Any]:
    return {
        "default": "deny-on-violation",
        "stages": {
            "pre-edit": ["secrets", "protected-paths"],
            "pre-commit": ["secrets", "protected-paths", "runtime-protected-paths"],
            "pre-merge": ["secrets", "protected-paths", "runtime-protected-paths"],
            "verification": ["secrets", "protected-paths"],
        },
        "invariants": [
            "Workers may modify only their isolated worktree.",
            "Secrets must never be committed or emitted into audit evidence.",
            "Git internals and E2E runtime state cannot be worker deliverables.",
            "A failed guardrail blocks commit or integration rather than being retried blindly.",
        ],
    }


def write_policy(root: str | Path) -> Path:
    root = Path(root).resolve()
    path = root / ".e2e" / "guardrails.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(policy(), indent=2, sort_keys=True), encoding="utf-8")
    return path
