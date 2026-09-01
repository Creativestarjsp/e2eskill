# SD Agent System

## Overview

The SD system is a three-level software engineering agent model:

```text
                         SD3
                  Engineering Supervisor
                            │
                            ▼
                         SD2
                    Agent Orchestrator
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
            SD1            SD1           SD1
          Worker          Worker        Worker
              │             │             │
          Specialist      Specialist    Specialist
            Skills          Skills        Skills
```

## SD1 — Worker

**Question answered:** "How do I execute this task?"

SD1 performs the assigned engineering task.

Responsibilities:

- inspect relevant code
- implement
- test
- verify
- report

SD1 should remain focused on its assigned scope.

## SD2 — Orchestrator

**Question answered:** "Who should do what, and in what order?"

SD2 converts a high-level objective into executable SD1 tasks.

Responsibilities:

- understand requirements
- inspect the project
- decompose work
- select workers
- identify dependencies
- parallelize safe work
- pass context
- aggregate results
- coordinate integration
- escalate to SD3

Default maximum active SD1 workers: 4.

## SD3 — Supervisor

**Question answered:** "Is the result actually correct and complete?"

SD3 independently verifies the work.

Responsibilities:

- inspect actual implementation
- verify requirements
- review architecture
- review security
- verify tests
- identify risks
- create corrective tasks
- approve or block completion

## Example

User request:

> Add authentication to the application.

### SD3

Understands the project-level objective and supervises the process.

### SD2

Creates tasks:

```text
AUTH-01 → Database worker → user/session data model
AUTH-02 → Backend worker  → authentication API
AUTH-03 → Frontend worker → login/register UI
AUTH-04 → Security worker → authentication security review
```

If AUTH-01 is required before AUTH-02:

```text
AUTH-01
   ↓
AUTH-02
   ↓
AUTH-03
```

AUTH-04 may run independently when the required context is available.

### SD1

Each worker performs its assigned task and returns a structured result.

### SD2

Aggregates results and coordinates integration.

### SD3

Inspects the resulting implementation, runs or reviews verification, identifies issues, and either approves or sends corrective work back through SD2.

## Core Rules

### 1. Scope

SD1 executes.

SD2 orchestrates.

SD3 supervises.

Do not blur these responsibilities without a clear reason.

### 2. Evidence

Agents must distinguish between:

- known facts
- inspected evidence
- assumptions
- unverified claims

### 3. Parallelism

Parallelize only independent work.

Do not allow concurrent workers to create unsafe conflicting edits.

### 4. Verification

Every meaningful task should have an explicit verification method.

### 5. Escalation

Use SD3 for:

- architectural conflicts
- persistent failures
- security blockers
- ambiguous requirements with material impact
- integration problems that cannot be safely resolved by SD2

### 6. No Infinite Agent Loops

Repeated failure must trigger diagnosis and escalation, not blind retries.

## Recommended Project Integration

Projects using the SD system should provide:

```text
CLAUDE.md
PRD.md
ARCHITECTURE.md
API.md
DATABASE.md
PROGRESS.md
```

These documents provide shared project context while individual tasks should receive only the context they require.

## Skill Mapping

Typical SD1 specialist skills:

```text
frontend-developer
backend-developer
database-engineer
api-developer
ui-ux-designer
security-engineer
qa-engineer
devops-engineer
code-reviewer
```

SD2 and SD3 should route work to these skills rather than duplicating specialist implementation instructions.
