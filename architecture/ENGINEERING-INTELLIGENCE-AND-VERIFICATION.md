# Engineering Intelligence + Verification System

E2E is an engineering control plane, not a code-generation wrapper.

## Objective

Turn every non-trivial engineering task into an evidence-producing loop:

```text
Task
 ↓
Research-first preflight
 ↓
Context + CodeBrain + Skills
 ↓
Engineering Intelligence
 ↓
SD2 decomposition
 ↓
SD1 execution
 ↓
Guardrails + tools
 ↓
Integration
 ↓
CodeBrain refresh
 ↓
Evaluation
 ↓
Introspection
 ↓
Independent SD3 verification
 ↓
Approved / Correct / Escalate
```

## Engineering Intelligence

`e2e/intelligence.py` produces a bounded preflight report containing:

- task fingerprint
- risk profile
- research-first requirement
- matched skills and worker count
- context sources
- verification plan
- quality gates
- intelligence fingerprint

The report is advisory. It does not authorize tools, approve code, or replace SD3.

## Verification model

Verification is layered:

1. **Worker evidence** — changed files, commands, tests, risks and blockers.
2. **Repository verification** — actual integrated files and CodeBrain refresh.
3. **Evaluation** — accuracy, completeness, correctness, security, integration, evidence and efficiency.
4. **Introspection** — failure classification, correction count and escalation decision.
5. **SD3** — independent supervisor inspection and explicit approval/correction/rejection.

Approval requires evidence. A worker exit code is not equivalent to correctness.

## Run intelligence

Post-run synthesis maps execution + evaluation + introspection to:

- `ship-candidate`
- `do-not-ship`
- `needs-independent-verification`

This is a readiness signal, not a substitute for SD3 approval.

## Durable evidence

Executed runs are persisted under `.e2e/runs/<run-id>/` with:

- plan snapshot
- execution report
- worker reports and stdout/stderr
- supervisor report
- verification evidence
- evaluation
- introspection
- intelligence synthesis
- final readiness

This creates a replayable engineering evidence trail rather than a single final answer.

## CLI

```bash
e2e intelligence "add authentication API"
e2e execute "add authentication API"
```

Use `e2e intelligence` to inspect the preflight before launching agents.

## Core rule

> Intelligence can guide execution; only evidence and independent verification can establish approval.

This separation is intentional: agentic systems increasingly require explicit observability, containment and independent validation rather than trusting the agent's own claims.
