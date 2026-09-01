# Repository Conventions

## Engineering Model

This repository separates responsibilities into four layers:

```text
SD3 Supervisor
    ↓
SD2 Orchestrator
    ↓
SD1 Worker
    ↓
Skill / Tool
```

## Skill Standards

All production skills should follow `SKILL-AUTHORING-STANDARD.md`.

Minimum target: L2 Production.

Core reusable skills should target L3 Mature.

## Agent Standards

All agent definitions should follow `AGENT-AUTHORING-STANDARD.md`.

## Task Standards

All delegated work should follow `TASK-AUTHORING-STANDARD.md`.

## Repository Inspection

Agents must inspect existing project structure, conventions, relevant source, tests, and documentation before making non-trivial changes.

## Evidence

Never fabricate:

- files
- APIs
- test results
- tool output
- requirements
- implementation status

## Changes

Prefer small, focused changes.

Avoid unrelated refactors unless explicitly required.

## Verification

Meaningful implementation must be verified with the strongest practical checks available.

## Documentation

When behavior changes, update the relevant documentation and examples.

## Security

Never commit secrets, credentials, private tokens, or sensitive user data.
