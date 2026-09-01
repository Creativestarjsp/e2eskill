from __future__ import annotations

import re
from pathlib import Path
from typing import Any

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)sk-[A-Za-z0-9]{20,}"),
]
PROTECTED = {".env", ".env.production", ".env.local", "id_rsa", "id_ed25519"}


def secret_scan(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root).resolve()
    findings = []
    for p in root.rglob("*"):
        if not p.is_file() or any(x in {".git", "node_modules", ".e2e", "__pycache__"} for x in p.parts):
            continue
        if p.name in PROTECTED or p.stat().st_size > 1_000_000:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(p.relative_to(root).as_posix())
                break
    return {"status": "block" if findings else "pass", "rule": "secrets", "evidence": sorted(set(findings)), "message": "Potential secret-like content found." if findings else "No secret patterns found.", "remediation": "Remove secrets and use the project secret manager." if findings else "None."}


def protected_path(path: str) -> dict[str, Any]:
    name = Path(path).name
    blocked = name in PROTECTED or path.startswith(".git/")
    return {"status": "block" if blocked else "pass", "rule": "protected-paths", "evidence": [path] if blocked else [], "message": "Protected path requires explicit handling." if blocked else "Path is allowed.", "remediation": "Use an approved secret/configuration workflow." if blocked else "None."}


def run(stage: str, root: str | Path = ".", changed_files: list[str] | None = None) -> list[dict[str, Any]]:
    results = []
    if stage in {"pre-edit", "pre-commit", "verification"}:
        results.append(secret_scan(root))
    if changed_files:
        results.extend(protected_path(p) for p in changed_files)
    return results
