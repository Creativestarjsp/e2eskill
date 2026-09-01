from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

PRECEDENCE = ["safety", "repository", "path", "project", "skill", "task", "local"]
SOURCE_DOCS = ["BRD.md", "PRD.md", "CLAUDE.md", "AGENTS.md", "CONVENTIONS.md", "E2E-PLAN.md", "SD-AGENT-SYSTEM.md"]


def _read(root: Path, name: str, limit: int = 12000) -> str:
    p = root / name
    return p.read_text(encoding="utf-8", errors="replace")[:limit] if p.exists() else ""


def resolve_rules(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root).resolve()
    files = []
    for name in SOURCE_DOCS:
        if (root / name).exists():
            files.append({"source": name, "precedence": "project" if name not in {"CLAUDE.md", "AGENTS.md"} else "repository"})
    for p in root.rglob("*.md"):
        if any(part in {".git", ".e2e", "node_modules"} for part in p.parts):
            continue
        if p.name.lower() in {"rules.md", "claude.md", "agents.md"} and p.name not in SOURCE_DOCS:
            files.append({"source": p.relative_to(root).as_posix(), "precedence": "path"})
    return {"precedence": PRECEDENCE, "sources": files, "conflicts": []}


def build_context(root: str | Path, task: str, brain: Any | None = None, max_chars: int = 30000) -> dict[str, Any]:
    root = Path(root).resolve()
    rules = resolve_rules(root)
    package: dict[str, Any] = {
        "objective": task,
        "requirements": [],
        "constraints": [],
        "relevant_files": [],
        "relevant_symbols": [],
        "dependencies": [],
        "tests": [],
        "rules": rules,
        "skills": [],
        "known_risks": [],
        "assumptions": [],
        "unknowns": [],
        "verification": [],
        "sources": [],
    }
    for name in SOURCE_DOCS:
        text = _read(root, name)
        if text:
            package["sources"].append({"file": name, "excerpt": text[:4000]})
    if brain:
        cb = brain.context(task)
        package["relevant_files"] = cb["relevant_files"]
        package["relevant_symbols"] = cb["relevant_symbols"]
        package["tests"] = cb["tests"]
        package["sources"].append({"codebrain": cb["provenance"]})
    blob = json.dumps(package, ensure_ascii=False)
    if len(blob) > max_chars:
        package["sources"] = package["sources"][:4]
        package["unknowns"].append("Context package was bounded; some source excerpts were omitted.")
    return package
