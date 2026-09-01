# E2E Skill Registry and Composition

## Purpose

Define how agents discover, select, compose, and verify specialist skills without duplicating skill instructions inside agents.

## Registry Entry

Each skill should expose metadata equivalent to:

```yaml
name: skill-name
version: 1.0.0
level: L2
purpose: "..."
triggers: []
inputs: []
outputs: []
capabilities: []
required_context: []
verification: []
security_class: normal
compatible_runtimes: [claude-code, codex]
```

## Discovery

Discovery order:

1. exact task/domain match
2. required capability match
3. repository technology match
4. verification/security requirements
5. runtime compatibility

Do not load unrelated skills merely because they are available.

## Composition

Skills may be composed when their scopes are complementary.

Example:

```text
feature request
  → software-architect
  → database-engineer
  → api-developer
  → frontend-developer
  → qa-engineer
  → security-engineer
  → code-reviewer
```

SD2 owns task decomposition and routing. Skills do not become hidden orchestrators.

## Versioning

Breaking changes require a major version. Additive capabilities should normally use a minor version. Documentation-only fixes may use a patch version.

## Deprecation

Never remove an existing skill solely because a new skill exists. Mark it deprecated, define the replacement, migrate references, verify the replacement, then remove only after a deliberate release decision.
