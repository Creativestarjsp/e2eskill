# E2E Verification and Evidence Model

## Verification Pipeline

```text
requirements
  ↓
implementation
  ↓
static checks
  ↓
tests
  ↓
integration
  ↓
security
  ↓
browser/UI when applicable
  ↓
impact review
  ↓
SD3 independent verification
```

## Evidence Record

```yaml
check: "..."
status: pass | fail | partial | not-run
command_or_method: "..."
observed_result: "..."
artifacts: []
limitations: []
```

## Verification Levels

- Level 0: syntax/basic sanity
- Level 1: focused unit/component checks
- Level 2: integration and contract checks
- Level 3: end-to-end behavior
- Level 4: security and operational verification
- Level 5: SD3 independent acceptance review

Not every task needs every level. The required level must be explicit before completion.

## Evidence Rules

- Never claim a test passed if it was not run or otherwise verified.
- Separate inspected evidence from assumptions.
- Record skipped checks and why they were skipped.
- Browser-visible verification should use the browser execution standard when applicable.
- Security findings must include reproduction/evidence when safe and possible.

## Completion

A task is complete only when acceptance criteria are mapped to evidence or an explicit, approved limitation.
