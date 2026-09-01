from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def _section(text: str, headings: tuple[str, ...]) -> str:
    lines = text.splitlines()
    wanted = {h.lower() for h in headings}
    for i, line in enumerate(lines):
        if line.strip().lower().lstrip("# ") in wanted:
            out = []
            for x in lines[i + 1:]:
                if x.startswith("#"):
                    break
                out.append(x)
            return "\n".join(out).strip()
    return ""


def discover(root: str | Path = ".") -> list[dict[str, Any]]:
    root = Path(root).resolve()
    skills_root = root / "skills"
    if not skills_root.exists():
        return []
    result = []
    for p in sorted(skills_root.glob("*/SKILL.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        result.append({
            "name": p.parent.name,
            "path": p.relative_to(root).as_posix(),
            "purpose": _section(text, ("Purpose",))[:800],
            "triggers": _section(text, ("Use When", "Triggers"))[:1200],
            "size": len(text),
        })
    return result


def match(root: str | Path, task: str, limit: int = 8) -> list[dict[str, Any]]:
    skills = discover(root)
    terms = {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", task)}
    scored = []
    for skill in skills:
        hay = f"{skill['name']} {skill['purpose']} {skill['triggers']}".lower()
        score = sum(1 for t in terms if t in hay)
        if skill["name"].replace("-", " ") in task.lower():
            score += 5
        scored.append((score, skill))
    return [x[1] for x in sorted(scored, key=lambda x: (-x[0], x[1]["name"])) if x[0] > 0][:limit]
