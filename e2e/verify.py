from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from .hooks import run as run_hooks


def _cmd(root: Path, command: str) -> dict[str, Any]:
    try:
        p = subprocess.run(command, cwd=root, shell=True, text=True, capture_output=True, timeout=300)
        return {"command": command, "status": "pass" if p.returncode == 0 else "fail", "exit_code": p.returncode, "stdout": p.stdout[-4000:], "stderr": p.stderr[-4000:]}
    except Exception as exc:
        return {"command": command, "status": "fail", "error": str(exc)}


def verify(root: str | Path = ".", test_command: str | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    checks = []
    checks.extend(run_hooks("verification", root))
    if test_command:
        checks.append(_cmd(root, test_command))
    else:
        checks.append({"command": "not supplied", "status": "not-run", "reason": "No test command was provided."})
    failures = [c for c in checks if c.get("status") == "fail" or c.get("status") == "block"]
    result = {"status": "fail" if failures else "pass", "independent_supervisor": "pending-runtime-agent-review", "checks": checks, "evidence": "executed-runtime-checks"}
    out = root / ".e2e" / "verification.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
