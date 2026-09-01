# E2E CI Self-Healing Scheduler

## Purpose

E2E includes a bounded GitHub Actions self-healing loop for the `E2E Runtime` workflow.

```text
Scheduled Check
      ↓
Latest E2E Runtime Result
      ↓
 ┌────┴────┐
 │         │
 PASS    FAILURE
 │         ↓
Done   Capture Logs
          ↓
     Claude Repair
          ↓
   Local Verification
          ↓
      Commit/Push
          ↓
  workflow_dispatch
          ↓
    E2E Runtime Again
          ↓
       PASS / repeat
```

## Scheduler

Workflow:

```text
.github/workflows/e2e-self-heal.yml
```

It runs at minutes `7`, `27`, and `47` of every hour to reduce contention around the top of the hour.
GitHub scheduled workflows run from the default branch and can be delayed during high-load periods.

The scheduler is also manually triggerable with `workflow_dispatch`.

## Repair Contract

The repair agent receives the latest failed CI log as diagnostic evidence. Logs are explicitly treated as untrusted data.

The agent must:

- inspect the actual repository
- reproduce the failure where practical
- fix the underlying defect
- preserve tests and verification gates
- avoid weakening or deleting tests
- avoid bypassing guardrails
- run the relevant test and full pytest suite
- run CodeBrain checks
- run guardrails verification
- run the smoke evaluation
- leave commit/push to the scheduler

## Convergence Model

One scheduler execution performs at most one repair cycle. After a validated repair is pushed, the scheduler explicitly dispatches `e2e-runtime.yml` because GitHub documents that ordinary `GITHUB_TOKEN` pushes do not trigger new workflow runs, while `workflow_dispatch` is an exception.

If the next runtime is still failing, the next scheduled self-heal cycle reads the newest result and repeats the process.

This avoids an unbounded retry loop inside a single runner while still providing continuous convergence toward a green runtime.

## Authentication

The repair workflow needs one Claude credential configured as a repository Actions secret:

- `ANTHROPIC_API_KEY`, or
- `CLAUDE_CODE_OAUTH_TOKEN`

Never place credentials in repository files or workflow source.

## Safety

The scheduler intentionally has bounded behavior:

- no blind test retries
- no test deletion/skipping
- no secret modification
- no force pushes
- no unvalidated commits
- local verification before push
- explicit workflow dispatch after a repair
- repair evidence uploaded for inspection

The scheduler can repair code and CI configuration, but it cannot solve a repository-level infrastructure problem that requires unavailable credentials, disabled Actions, unavailable runners, or external service access.

## Required GitHub Permissions

The workflow uses:

```yaml
permissions:
  actions: write
  contents: write
  checks: read
```

`actions: write` is required to dispatch the runtime workflow. `contents: write` is required to push a validated repair. Claude also needs Actions read access to inspect CI results.

## Relationship to SD3

The scheduler is not a replacement for SD3.

```text
CI failure
   ↓
Self-healing repair
   ↓
E2E Runtime
   ↓
SD3 verification
```

The repair agent fixes defects. The runtime and SD3 verification remain the authority for whether the engineering change is acceptable.
