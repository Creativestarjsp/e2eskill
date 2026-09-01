# Agent Authoring Standard

## Purpose

Agents coordinate or execute work using repository skills. Every agent must have a clear role, scope, input contract, output contract, verification behavior, and escalation path.

## Agent Layers

```text
SD3 — Supervisor
  ↓
SD2 — Orchestrator
  ↓
SD1 — Worker
  ↓
Skill / Tool
```

### SD3

Owns quality and final verification.

### SD2

Owns task decomposition, worker selection, dependencies, parallel execution, and result aggregation.

### SD1

Owns execution of a focused task.

### Skill

Provides reusable specialist knowledge and workflow.

### Tool

Provides deterministic operations where appropriate.

## Required Agent Contract

Every agent definition should specify:

```text
Role:
Purpose:
When to invoke:
Inputs:
Responsibilities:
Non-responsibilities:
Workflow:
Tools / skills:
Output format:
Failure handling:
Escalation:
Definition of done:
```

## Delegation Rules

Delegate only when the work benefits from another agent's specialization or independent execution.

Do not delegate trivial work merely to increase agent count.

Do not create recursive delegation without an explicit limit.

## Parallel Execution

Parallelize only independent tasks.

Avoid concurrent modifications to the same critical files unless the orchestrator explicitly manages the integration.

Default SD2 maximum active SD1 workers: 4.

## Context Passing

Pass the smallest sufficient context:

- objective
- relevant requirements
- relevant files
- dependencies
- acceptance criteria
- constraints
- verification requirements

Avoid passing unrelated project history.

## Verification

Agent reports are not proof.

Higher-level agents should inspect actual results when practical.

## Failure Handling

Agents must return explicit failure states rather than pretending success.

Use:

```text
completed
partial
blocked
failed
```

Persistent failures should be escalated rather than retried indefinitely.

## Security

Agents must never expose secrets or bypass security controls.

Agents that modify production-sensitive systems must explicitly consider authorization, validation, secrets, and rollback/recovery where relevant.

## Reporting

Reports should contain:

- status
- work completed
- files changed
- verification performed
- issues
- assumptions
- next action

Keep reports factual and concise.
