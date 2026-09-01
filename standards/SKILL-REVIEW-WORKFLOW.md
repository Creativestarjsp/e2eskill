# Skill Review Workflow

## Goal

Every new or materially changed skill should pass a repeatable review before being considered production-ready.

## Workflow

```text
AUTHOR
  ↓
SELF-CHECK
  ↓
SCORECARD
  ↓
DOMAIN REVIEW
  ↓
SD3 REVIEW
  ↓
CORRECT
  ↓
RE-SCORE
  ↓
APPROVE
```

## 1. Author

Create the skill according to `SKILL-AUTHORING-STANDARD.md`.

## 2. Self-Check

The author verifies:

- purpose
- triggers
- scope
- workflow
- decisions
- anti-patterns
- quality bar
- verification
- failure handling
- security/safety
- references/examples/tooling

## 3. Scorecard

Use `SKILL-QUALITY-SCORECARD.md`.

A production skill should score at least **22/30** and pass every mandatory gate.

Core/reference skills should target **27/30 or higher**.

## 4. Domain Review

A reviewer familiar with the skill's domain checks whether the instructions are materially correct, useful, and practical.

## 5. SD3 Review

SD3 evaluates:

- consistency with E2E standards
- clarity for SD1 workers
- delegation suitability for SD2
- objective verification for SD3
- scope boundaries
- failure handling
- security implications
- maintainability

## 6. Correction

Findings must be resolved rather than merely acknowledged.

If a finding requires broader architecture or project policy changes, escalate it instead of weakening the skill to hide the conflict.

## 7. Re-score

After material changes, repeat the scorecard and mandatory gates.

## 8. Approval

Only skills that pass the quality gate should be marked production-ready.

## Review Principles

### Prefer evidence

Review actual behavior, examples, tests, and tools where available.

### Avoid verbosity without value

A long skill is not automatically a good skill. Every instruction should improve agent behavior.

### Prefer explicitness

Critical decisions and failure conditions should not be left implicit.

### Prefer composability

A skill should do one domain job well and compose with other skills rather than becoming a giant general-purpose prompt.

### Preserve domain character

The common standard defines quality and reliability. It should not erase domain-specific workflows or expert judgment.
