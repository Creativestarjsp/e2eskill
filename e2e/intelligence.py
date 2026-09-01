from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any

RISK_PATTERNS = {
    "security": re.compile(r"\b(auth|authentication|authorization|token|password|secret|permission|security|oauth|jwt)\b", re.I),
    "data": re.compile(r"\b(database|migration|schema|delete|payment|transaction|data\s+loss)\b", re.I),
    "integration": re.compile(r"\b(api|endpoint|integration|webhook|queue|event|service)\b", re.I),
    "ui": re.compile(r"\b(ui|ux|frontend|react|native|accessibility|responsive)\b", re.I),
    "infrastructure": re.compile(r"\b(deploy|deployment|docker|kubernetes|cloud|ci|cd|infra|production)\b", re.I),
}


def _hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _risk_profile(task: str) -> dict[str, Any]:
    risks = [name for name, pattern in RISK_PATTERNS.items() if pattern.search(task)]
    if not risks:
        risks = ["correctness"]
    return {"levels": risks, "high_risk": any(x in risks for x in ("security", "data", "infrastructure"))}


def build_intelligence(root: str | Path, task: str, plan: dict[str, Any] | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    plan = plan or {}
    context = plan.get("context", {})
    matched = plan.get("skills", [])
    workers = plan.get("workers", [])
    risk = _risk_profile(task)
    research_first = bool(plan.get("preflight", {}).get("research_first"))
    verification = [
        "inspect actual repository state",
        "run targeted tests for changed behavior",
        "run repository guardrails",
        "refresh CodeBrain and inspect impact",
        "independent SD3 review before approval",
    ]
    if risk["high_risk"]:
        verification.insert(3, "perform explicit security/data/infrastructure verification for identified risk areas")
    report = {
        "schema_version": "1.0",
        "task": task,
        "task_fingerprint": _hash(task),
        "generated_at": time.time(),
        "risk": risk,
        "research_first": research_first,
        "matched_skills": matched,
        "worker_count": len(workers),
        "context_sources": sorted(context.keys()) if isinstance(context, dict) else [],
        "codebrain_expected": True,
        "verification_plan": verification,
        "quality_gates": [
            "requirements satisfied",
            "no unauthorized tool use",
            "tests/evidence support claims",
            "integration remains coherent",
            "SD3 independently approves",
        ],
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
