# Regression Intelligence

E2E treats evaluation history as engineering evidence, not as a replacement for verification.

## Flow

```text
Task
 ↓
CodeBrain + Memory + Eval History
 ↓
Regression Risk
 ├─ historical failures
 ├─ baseline deltas
 └─ recommended verification
 ↓
SD2 worker selection
 ↓
SD1 execution
 ↓
Eval Harness
 ↓
SD3 independent review
```

## Policy

- Historical failures increase verification requirements.
- High regression risk adds QA and security review where applicable.
- Baseline regressions are release-blocking evidence unless SD3 explicitly resolves them.
- Memory is advisory and never authorizes an operation.
- Deterministic graders remain the first evaluation layer; repeated-run reliability is preferred over a single pass result.
- SD3 independently verifies the repository and evidence before approval.

Repeated independent attempts matter because pass@k measures whether at least one attempt succeeds, while pass^k measures whether all k attempts succeed; conflating the two can overstate reliability. citeturn0academia13turn0search0
