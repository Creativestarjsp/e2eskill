# E2E Benchmark Methodology

## Goal

Measure whether E2E improves engineering outcomes without optimizing for a single superficial metric.

## Benchmark Dimensions

### Correctness

- acceptance criteria satisfied
- regression rate
- independent verification success

### Efficiency

- tokens consumed
- tool calls
- elapsed time
- repeated/redundant work

### Context Quality

- relevant files retrieved
- irrelevant context ratio
- missing-context rate
- stale-context rate

### Agent Quality

- successful task completion
- escalation quality
- retry count
- evidence completeness

### Safety

- secret leakage
- blocked unsafe actions
- security regressions
- incorrect high-confidence claims

## Benchmark Protocol

1. Fix repository revision and task set.
2. Define acceptance criteria before execution.
3. Run baseline and E2E conditions on comparable tasks.
4. Capture identical evidence fields.
5. Use independent verification.
6. Report confidence intervals or meaningful variation where sample size permits.
7. Do not generalize from a small benchmark to universal performance claims.

## Required Reporting

Every published benchmark should state dataset/task selection, runtime/model configuration, repository revision, tool availability, retries, failures, verification method, and limitations.
