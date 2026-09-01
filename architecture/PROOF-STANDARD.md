# E2E Proof Standard

## Purpose

A green CI workflow proves only the checks that workflow executes. E2E is considered **proven** only when the runtime demonstrates repeatable engineering performance on representative tasks, not merely that its own source code passes unit tests.

## Evidence levels

| Level | Evidence | Required | Meaning |
|---|---|---:|---|
| P0 | Syntax, packaging, unit tests | Yes | Runtime is internally healthy |
| P1 | Deterministic eval suite | Yes | Core commands behave reproducibly |
| P2 | Orchestration proof cases | Yes | SD2 can plan real engineering tasks and select evidence/skills |
| P3 | Real SD1 execution | Yes | A supported agent runtime changes a fixture repository successfully |
| P4 | Independent SD3 verification | Yes | The result is independently inspected and accepted/rejected |
| P5 | Failure/recovery proof | Yes | Intentional failures are diagnosed and corrected without weakening tests |
| P6 | Repeated benchmark | Yes | Results remain reliable across repeated independent runs and task families |

## Production-proof gate

A release claim of `PROVEN` requires:

- P0 and P1 green on every protected commit.
- P2 green across the complete proof task catalog.
- At least 10 successful P3/P4 task runs across at least 3 task families.
- No unresolved P3/P4 security or integration failure.
- At least 3 P5 recovery scenarios completed without modifying or deleting the failing test to make it pass.
- P6 pass rate >= 90% across independent attempts, with no critical task below 80%.
- Evidence artifacts retained for each proof run: plan, worker reports, changed files, tests, evaluation, introspection, SD3 decision, and final result.

## Required task families

The proof catalog must include representative tasks for:

1. API/backend behavior
2. Database/persistence behavior
3. Frontend/UI behavior
4. Authentication/security-sensitive behavior
5. Regression repair

Tasks should be small enough to grade deterministically and realistic enough to exercise CodeBrain, context, skills, SD1, SD2, SD3, verification, and recovery.

## Anti-cheating rules

A proof run is invalid if it:

- deletes, skips, weakens, or rewrites a required grader/test solely to pass;
- reports success without executable evidence;
- bypasses SD3 verification;
- reuses the same successful attempt as multiple independent attempts;
- treats a dry-run as proof of successful implementation;
- ignores a failed required check.

## CI architecture

```text
                    E2E PROOF PIPELINE
                           |
        +------------------+------------------+
        |                  |                  |
       P0                 P1                 P2
   Unit/package      Deterministic       Orchestration
        |             eval suites          proof
        +------------------+------------------+
                           |
                          P3
                    Real SD1 execution
                           |
                          P4
                 Independent SD3 review
                           |
                          P5
                  Failure + recovery
                           |
                          P6
                 Repeated benchmark
                           |
                    PROVEN / NOT PROVEN
```

## Reporting

The repository should distinguish:

- `HEALTHY`: internal CI is green.
- `VALIDATED`: P0-P2 are green.
- `PROVEN`: all production-proof gates above are satisfied.
- `NOT PROVEN`: any mandatory level is missing or below threshold.

Do not use `PROVEN` merely because the main CI workflow is green.
