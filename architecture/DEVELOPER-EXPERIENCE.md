# E2E Developer Experience

## Goal

Make E2E observable, debuggable, and easy to operate without hiding agent decisions.

## Proposed CLI Surface

```bash
e2e init
e2e doctor
e2e status
e2e context <task>
e2e skill list
e2e skill inspect <name>
e2e brain build
e2e brain check
e2e brain map <path>
e2e brain search <query>
e2e brain impact <target>
e2e run <task>
e2e verify <task>
e2e report <run-id>
```

The CLI is a target interface, not a claim that every command is already implemented.

## Status Output

A useful status view should show:

- runtime
- project/repository revision
- context health
- CodeBrain freshness
- active agents
- task graph
- verification state
- blocked actions
- warnings

## Reports

Reports should be reproducible and include:

- objective
- plan
- workers and skills used
- changed files
- tests/checks
- evidence
- assumptions/limitations
- security findings
- SD3 decision

## Observability

Prefer structured events internally so a future UI can render the same run data without changing agent semantics.
