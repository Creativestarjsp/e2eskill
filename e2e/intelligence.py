from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any

from .brain import CodeBrain
from .memory import Memory
from .regression import analyze_regression_risk

RISK_PATTERNS = {
    "security": re.compile(r"\b(auth|authentication|authorization|token|password|secret|permission|security|oauth|jwt|login)\b", re.I),
    "data": re.compile(r"\b(database|migration|schema|delete|payment|transaction|data\s+loss|destructive)\b", re.I),
    "integration": re.compile(r"\b(api|endpoint|integration|webhook|queue|event|service|sdk)\b", re.I),
    "ui": re.compile(r"\b(ui|ux|frontend|react|native|accessibility|responsive|screen|component)\b", re.I),
    "infrastructure": re.compile(r"\b(deploy|deployment|docker|kubernetes|cloud|ci|cd|infra|production|release)\b", re.I),
}


def _hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _risk_profile(task: str) -> dict[str, Any]:
    risks = [name for name, pattern in RISK_PATTERNS.items() if pattern.search(task)]
    if not risks:
        risks = ["correctness"]
    return {"levels": risks, "high_risk": any(x in risks for x in ("security", "data", "infrastructure"))}


def _requirements(task: str) -> dict[str, Any]:
    text = task.strip()
    explicit = re.findall(r"(?:must|should|needs? to|required to|acceptance criteria)[:\s]+([^.;]+)", text, re.I)
    criteria = [x.strip() for x in explicit if x.strip()]
    return {
        "objective": text,
        "acceptance_criteria": criteria,
        "criteria_source": "task-text" if criteria else "implicit-task",
        "missing_explicit_criteria": not bool(criteria),
    }


def _load_eval_history(root: Path, limit: int = 10) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    directory = root / ".e2e" / "evals"
    if not directory.exists():
        return rows
    for path in sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            rows.append({"file": path.relative_to(root).as_posix(), "suite": data.get("suite", data.get("suite_id", data.get("id", path.stem))), "summary": data.get("summary", {}), "schema_version": data.get("schema_version")})
        except (OSError, json.JSONDecodeError):
            continue
        if len(rows) >= limit:
            break
    return rows


def _affected_risk(root: Path, task: str, context: dict[str, Any]) -> dict[str, Any]:
    brain = CodeBrain(root)
    if not brain.store.exists():
        brain.build()
    if not brain.check().get("fresh"):
        brain.build()
    relevant_files = context.get("relevant_files", [])
    impacted: dict[str, Any] = {}
    for path in relevant_files[:10]:
        impacted[path] = brain.impact(path)
    return {
        "relevant_files": relevant_files[:20],
        "impacts": impacted,
        "codebrain": context.get("provenance", {}),
        "risk_score": min(10, len(relevant_files) + sum(len(v.get("affected_files", [])) for v in impacted.values())),
    }


def build_intelligence(root: str | Path, task: str, plan: dict[str, Any] | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    plan = plan or {}
    context = plan.get("context", {})
    matched = plan.get("skills", [])
    workers = plan.get("workers", [])
    risk = _risk_profile(task)
    requirements = _requirements(task)
    research_first = bool(plan.get("preflight", {}).get("research_first"))
    codebrain = CodeBrain(root)
    if not codebrain.store.exists() or not codebrain.check().get("fresh"):
        codebrain.build()
    context = context or codebrain.context(task)
    impact = _affected_risk(root, task, context)
    memory = Memory(root).search(task, limit=8)
    eval_history = _load_eval_history(root)
    failure_history = [m for m in memory if m.get("type") in {"failure", "regression", "incident"}]
    regression = analyze_regression_risk(root, task)
    verification = [
        "inspect actual repository state",
        "validate acceptance criteria against implementation",
        "run targeted tests for changed behavior",
        "run repository guardrails",
        "refresh CodeBrain and inspect impact",
        "independent SD3 review before approval",
    ]
    if risk["high_risk"]:
        verification.insert(4, "perform explicit security/data/infrastructure verification for identified risk areas")
    if regression["level"] == "medium":
        verification.insert(-1, "run targeted historical regression evaluations")
    elif regression["level"] == "high":
        verification.insert(-1, "expand regression evaluation coverage and require SD3 regression review")
    required_tests = ["targeted tests for affected behavior", "regression tests for impacted callers/dependencies"]
    if risk["high_risk"]:
        required_tests.append("security/data/infrastructure regression checks")
    if regression["level"] in {"medium", "high"}:
        required_tests.append("historically failing or related evaluation cases")
    evidence_contract = [
        "changed-file evidence",
        "test command and result evidence",
        "guardrail result",
        "CodeBrain freshness and impact evidence",
        "SD3 decision with evidence",
    ]
    if requirements["missing_explicit_criteria"]:
        evidence_contract.append("explicit acceptance criteria derived from task")
    if regression["level"] != "low":
        evidence_contract.append("regression-risk analysis and targeted evaluation evidence")
    report = {
        "schema_version": "2.1",
        "task": task,
        "task_fingerprint": _hash(task),
        "generated_at": time.time(),
        "confidence": "medium" if requirements["missing_explicit_criteria"] else "high",
        "risk": risk,
        "requirements": requirements,
        "research_first": research_first,
        "matched_skills": matched,
        "recommended_workers": [{"id": w.get("id"), "skill": w.get("skill"), "phase": w.get("phase")} for w in workers[:4]],
        "worker_count": len(workers),
        "context_sources": sorted(context.keys()) if isinstance(context, dict) else [],
        "repository_impact": impact,
        "memory": {"matches": memory, "failure_history": failure_history},
        "eval_history": eval_history,
        "regression": regression,
        "required_tests": required_tests,
        "evidence_contract": evidence_contract,
        "codebrain_expected": True,
        "verification_plan": verification,
        "quality_gates": [
            "requirements satisfied",
            "no unauthorized tool use",
            "tests/evidence support claims",
            "integration remains coherent",
            "SD3 independently approves",
        ],
        "advisory_only": True,
    }
    report["intelligence_fingerprint"] = _hash(report)
    out = root / ".e2e" / "intelligence.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def synthesize_run(execution: dict[str, Any], evaluation: dict[str, Any], introspection: dict[str, Any]) -> dict[str, Any]:
    supervisor = execution.get("supervisor") or {}
    decision = (supervisor.get("report") or {}).get("decision")
    blocking = bool(evaluation.get("blocking"))
    status = str(execution.get("status", "unknown"))
    if decision == "approved" and not blocking and status == "approved":
        readiness = "ship-candidate"
    elif decision in {"needs-correction", "rejected"} or blocking:
        readiness = "do-not-ship"
    else:
        readiness = "needs-independent-verification"
    evidence_gaps = list(evaluation.get("failed_checks", []))
    if decision != "approved":
        evidence_gaps.append("SD3 approval is not established")
    if not execution.get("brain_refresh"):
        evidence_gaps.append("CodeBrain refresh evidence is missing")
    return {
        "schema_version": "1.0",
        "readiness": readiness,
        "execution_status": status,
        "sd3_decision": decision or "unknown",
        "evaluation_aggregate": evaluation.get("aggregate"),
        "evidence_gaps": evidence_gaps,
        "failure_class": introspection.get("failure_class"),
        "escalate_to_sd3": bool(introspection.get("escalate_to_sd3")) or decision != "approved",
        "principle": "evidence before approval; intelligence guides execution but never replaces independent verification",
    }
