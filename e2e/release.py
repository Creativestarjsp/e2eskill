from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from .brain import CodeBrain
from .hooks import secret_scan
from .skills import discover


def release_check(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root).resolve()
    checks = []
    checks.append({"gate": "skills-discoverable", "status": "pass" if discover(root) else "fail", "count": len(discover(root))})
    checks.append({"gate": "security-scan", "status": secret_scan(root)["status"]})
    brain = CodeBrain(root)
    checks.append({"gate": "codebrain-fresh", "status": "pass" if brain.check().get("fresh") else "fail"})
    for command, gate in [("python -m pytest -q", "required-tests"), ("git diff --check", "diff-check")]:
        try:
            p = subprocess.run(command, cwd=root, shell=True, text=True, capture_output=True, timeout=600)
            checks.append({"gate": gate, "status": "pass" if p.returncode == 0 else "fail", "exit_code": p.returncode})
        except Exception as exc:
            checks.append({"gate": gate, "status": "fail", "error": str(exc)})
    failed = [c for c in checks if c["status"] != "pass"]
    return {"status": "fail" if failed else "pass", "checks": checks, "approval": "SD3 + explicit release owner required"}
