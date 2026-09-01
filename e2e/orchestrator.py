from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from .brain import CodeBrain
from .context import build_context
from .intelligence import build_intelligence
from .regression import analyze_regression_risk
from .skills import discover, match

MAX_ACTIVE_WORKERS = 4


def _id(task: str, skill: str, index: int) -> str:
    raw = f"{task}:{skill}:{index}".encode()
    return "sd1-" + hashlib.sha1(raw).hexdigest()[:10]


def _phase(skill: str) -> str:
    name = skill.lower()
    if any(x in name for x in ("architect", "database", "api")):
        return "foundation"
    if any(x in name for x in ("frontend", "react", "native", "expo", "ui-ux")):
        return "implementation"
    if any(x in name for x in ("security", "qa", "code-review")):
        return "verification"
    if "devops" in name:
        return "delivery"
    if name in {"research-first-engineering", "agent-introspection-debugging"}:
        return "foundation"
    return "implementation"


def _needs_research(task: str) -> bool:
    terms = {"add", "build", "create", "implement", "integrate", "replace", "refactor", "design", "new"}
    return any(term in task.lower().split() for term in terms)


def _skill_by_name(skills: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    return next((skill for skill in skills if skill.get("name") == name), None)


def _prioritize_regression_workers(matched: list[dict[str, Any]], regression: dict[str, Any], available: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if regression["level"] == "low":
        return matched
    result = list(matched)
    qa = _skill_by_name(available, "qa-engineer")
    security = _skill_by_name(available, "security-engineer") if regression["level"] == "high" else None
    for required in (qa, security):
        if required and required["name"] in {s["name"] for s in result}:
            continue
        if required:
            if len(result) >= MAX_ACTIVE_WORKERS:
                result[-1] = required
            else:
                result.append(required)
    deduped = []
    seen = set()
    for skill in result:
        if skill["name"] not in seen:
            seen.add(skill["name"])
            deduped.append(skill)
    return deduped


def plan(root: str | Path, task: str, brain: CodeBrain | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    brain = brain or CodeBrain(root)
    if not brain.store.exists():
        brain.build()
    context = build_context(root, task, brain)
    matched = match(root, task)
    if _needs_research(task):
        research = next((s for s in discover(root) if s["name"] == "research-first-engineering"), None)
        if research and research["name"] not in {s["name"] for s in matched}:
            matched.insert(0, research)
    if not matched:
        matched = [{"name": "software-architect", "path": "skills/software-architect/SKILL.md", "purpose": "Clarify architecture and implementation boundaries.", "triggers": "ambiguous engineering tasks"}]

    available = discover(root)
    regression = analyze_regression_risk(root, task)
    matched = _prioritize_regression_workers(matched, regression, available)

    workers = []
    for index, skill in enumerate(matched[:MAX_ACTIVE_WORKERS], start=1):
        workers.append({
            "id": _id(task, skill["name"], index),
            "role": "SD1",
            "skill": skill["name"],
            "phase": _phase(skill["name"]),
            "objective": f"Execute the {skill['name']} work required by: {task}",
            "inputs": {"task": task, "context": context},
            "outputs": ["implementation", "verification-evidence", "risks", "handoff"],
            "status": "ready",
        })

    foundation = [w["id"] for w in workers if w["phase"] == "foundation"]
    implementation = [w["id"] for w in workers if w["phase"] in {"foundation", "implementation", "delivery"}]
    verification = [w["id"] for w in workers if w["phase"] == "verification"]
    for worker in workers:
        if worker["phase"] in {"implementation", "delivery"}:
            worker["depends_on"] = foundation.copy()
        elif worker["phase"] == "verification":
            worker["depends_on"] = [x for x in implementation if x != worker["id"]]
        else:
            worker["depends_on"] = []

    draft = {
        "plan_id": hashlib.sha1(f"{task}:{time.time_ns()}".encode()).hexdigest()[:12],
        "role": "SD2",
        "task": task,
        "max_active_workers": MAX_ACTIVE_WORKERS,
        "context": context,
        "workers": workers,
        "preflight": {"research_first": _needs_research(task), "rule": "research before custom implementation when existing solutions may exist"},
        "regression": regression,
        "supervisor_gate": {"role": "SD3", "required": True, "checks": ["requirements", "architecture", "integration", "tests", "security", "evidence", "agent-evaluation", "regression"], "decision": "pending-runtime-agent-review"},
        "policy": {
            "parallelize": True,
            "do_not_exceed_worker_limit": True,
            "no_blind_retries": True,
            "escalate_architectural_blockers": True,
            "evaluate_non_trivial_runs": True,
            "regression_aware": True,
        },
    }
    draft["intelligence"] = build_intelligence(root, task, draft)
    return draft


def write_plan(root: str | Path, task: str) -> dict[str, Any]:
    root = Path(root).resolve()
    result = plan(root, task)
    out = root / ".e2e" / "plans"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{result['plan_id']}.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    result["plan_path"] = path.relative_to(root).as_posix()
    return result
