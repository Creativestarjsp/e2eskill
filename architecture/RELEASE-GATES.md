# E2E Production Release Gates

A release is eligible only when all required gates are satisfied or explicitly waived by an authorized maintainer.

## Gates

1. **Documentation** — architecture, standards, skills, and runtime adapters are synchronized.
2. **Skill quality** — changed skills pass the E2E quality scorecard and mandatory gates.
3. **Agent quality** — SD1/SD2/SD3 responsibilities remain clear and escalation works.
4. **Security** — no known critical/high blocker is left unexplained; secrets are absent.
5. **Verification** — required automated and manual checks have evidence.
6. **Compatibility** — supported runtime adapters load shared skills correctly.
7. **Regression** — existing skills remain discoverable and usable.
8. **CodeBrain** — if changed, graph freshness/schema/coverage checks pass.
9. **Observability** — failures are diagnosable from structured reports.
10. **Benchmarking** — performance claims are based on reproducible methodology.

## Release Checklist

```text
BRD / requirements aligned
→ standards aligned
→ skills validated
→ agents validated
→ context/rules validated
→ tools/hooks validated
→ verification evidence collected
→ security reviewed
→ runtime compatibility checked
→ regression checked
→ release notes written
→ SD3 approval
```

## Post-Release

Track defects, regressions, failed agent patterns, stale skills, and user-reported issues. Feed verified lessons into standards or memory rather than accumulating ad-hoc exceptions.
