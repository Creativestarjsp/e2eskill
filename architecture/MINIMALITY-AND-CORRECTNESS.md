# E2E Minimality and Correctness Standard

## Purpose

Prevent AI agents from over-building while preserving correctness, security, accessibility, data integrity, and explicit requirements.

## Core Principle

> Be lazy about implementation, never lazy about understanding or safety.

Before adding code, the agent must understand the affected flow and inspect the existing repository context.

## Decision Ladder

1. Does this need to exist? If no, do not add it.
2. Does the repository already provide it? Reuse it.
3. Does the standard library/platform provide it? Prefer that.
4. Does the native framework/platform provide it? Prefer that.
5. Is an installed dependency already capable of it? Reuse it.
6. Can the requirement be satisfied directly with a simple implementation? Prefer the smallest clear solution.
7. Add a new abstraction/dependency only when the evidence shows it is necessary.

## Non-Negotiable Protections

Minimality must never remove:

- authentication and authorization checks
- trust-boundary validation
- input/output safety
- data-loss protections
- required error handling
- accessibility requirements
- privacy/security controls
- required observability
- acceptance criteria
- tests required to establish correctness

## CodeBrain Integration

Before choosing an implementation rung, query available repository intelligence for:

- existing symbols
- existing utilities/components/services
- callers and dependants
- installed dependencies
- relevant tests
- architecture constraints

## Review Questions

SD3 should ask:

- Was anything added that was not required?
- Could existing code have been reused?
- Was a new dependency necessary?
- Was a custom abstraction used where a native/platform feature sufficed?
- Did minimality accidentally remove a safety or correctness requirement?
- Is the resulting implementation easier to understand and maintain?

## Evidence

A minimality review should record:

```yaml
reuse_candidates: []
new_dependencies: []
new_abstractions: []
removed_complexity: []
safety_exceptions: []
justification: "..."
```

## Relationship to Ponytail

This standard adopts the useful principles demonstrated by Ponytail: reuse before invention, native/platform capabilities before dependencies, and minimum necessary implementation. E2E extends those principles with CodeBrain context, explicit SD3 verification, security gates, and runtime-neutral execution.