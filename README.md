# E2E Engineering Skill System

A runtime-neutral engineering system for AI-assisted software development. E2E combines reusable specialist skills with project context, rules, CodeBrain, SD1/SD2/SD3 orchestration, memory, guardrails, tools, verification, minimality controls, and runtime adapters.

## Core Architecture

```text
BRD / PRD
   ↓
Context + Rules
   ↓
CodeBrain context retrieval
   ↓
Minimality + Correctness decision
   ↓
SD3 Supervisor
   ↓
SD2 Orchestrator
   ↓
SD1 Workers
   ↓
Specialist Skills
   ↓
Tools / Implementation
   ↓
Testing + Verification
   ↓
SD3 Approval
   ↓
Memory / Reports
```

## Executable Runtime

E2E now includes an executable, dependency-light Python runtime under `e2e/`.

```bash
python -m e2e doctor
python -m e2e status
python -m e2e brain build
python -m e2e brain search "authentication"
python -m e2e brain impact AuthService
python -m e2e context "add Google login"
python -m e2e skill list
python -m e2e verify --test "python -m pytest -q"
python -m e2e benchmark "python -m pytest -q" --repetitions 5
python -m e2e release
```

See `runtime/IMPLEMENTATION.md` for the implementation boundary and parser strategy.

## Existing Skills

Existing skills are preserved and remain the canonical domain layer.

See `skills/` for the full library.

## System Architecture Documents

- `E2E-PLAN.md` — master roadmap, phase status, and definition of done
- `BRD.md` — business source of truth for E2E
- `SD-AGENT-SYSTEM.md` — SD1/SD2/SD3 operating model
- `architecture/CONTEXT-AND-RULES.md` — context loading and rule precedence
- `architecture/CODEBRAIN.md` — repository intelligence architecture
- `architecture/SKILL-REGISTRY.md` — skill discovery and composition
- `architecture/HOOKS-AND-GUARDRAILS.md` — deterministic safety and lifecycle checks
- `architecture/MEMORY.md` — durable agent/project memory model
- `architecture/VERIFICATION.md` — evidence and verification model
- `architecture/RUNTIME-ADAPTERS.md` — Claude Code/Codex adapter boundary
- `architecture/DEVELOPER-EXPERIENCE.md` — CLI, status, reports, and observability
- `architecture/BENCHMARKS.md` — benchmark methodology
- `architecture/RELEASE-GATES.md` — production release gates
- `architecture/MINIMALITY-AND-CORRECTNESS.md` — minimal implementation and safety standard

## Runtime Contracts

- `runtime/e2e-manifest.yaml` — system manifest
- `runtime/profiles.yaml` — lite/standard/strict execution profiles
- `runtime/hooks.yaml` — lifecycle hook contract
- `runtime/verification-gates.yaml` — verification gate contract
- `runtime/adapters.yaml` — Claude/Codex adapter contract
- `runtime/benchmark-manifest.yaml` — benchmark execution contract
- `runtime/release-gates.yaml` — release gate contract

## Development Loop

```text
UNDERSTAND
→ INSPECT
→ DEFINE
→ DESIGN
→ MINIMIZE
→ IMPLEMENT
→ VALIDATE
→ REVIEW
→ VERIFY
→ DOCUMENT
```

## Key Principles

- Preserve and improve existing skills rather than replacing them casually.
- Keep shared engineering knowledge runtime-neutral.
- Use CodeBrain to reduce irrelevant context and support impact analysis.
- Keep SD1 execution, SD2 orchestration, and SD3 independent verification distinct.
- Prefer the smallest correct implementation: reuse before invention.
- Never trade security, accessibility, validation, data integrity, or required correctness for fewer lines.
- Require evidence for completion claims.
- Prefer deterministic guardrails for security and safety.
- Never store secrets in skills, memory, or generated project context.
- Escalate persistent or architectural failures instead of retrying forever.

## Verification

A GitHub Actions workflow runs the runtime tests and smoke checks. Real agentic benchmark claims still require configured Claude/Codex execution, a fixed task corpus, and independent SD3 evaluation.
