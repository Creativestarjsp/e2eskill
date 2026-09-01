# Engineering Evaluation Harness

E2E treats the **harness + model/runtime + task + tools + policies** as the unit being evaluated. A model score without its harness is incomplete because the harness controls context, tools, continuation, and verification.

## Evaluation model

```text
Task
  ↓
Versioned fixture
  ↓
Independent attempts
  ↓
Deterministic graders
  ↓
Per-task outcomes
  ↓
pass@k + pass^k
  ↓
Baseline comparison
  ↓
Regression gate
```

## Reliability rules

- `pass@k` measures whether at least one independent attempt succeeds.
- `pass^k` measures consistency across repeated attempts.
- `k` counts independent rollouts, never test cases inside one rollout.
- Functional correctness and security are separate gates.
- Latency is tracked beside quality rather than hidden behind a single score.
- Baselines are versioned and compared per task/suite.
- A regression is evidence that the harness/runtime changed behavior; it is not automatically a model regression.

These rules align with current agent-evaluation practice: non-deterministic agents require repeated trials, and both capability and consistency matter. citeturn0search7turn0academia13

## Fixture format

An evaluation suite is JSON with an `id`, `version`, and `cases` array. A case contains a command plus deterministic graders.

Supported graders:

- `exit-code`
- `contains`
- `files-exist`

Example:

```json
{
  "id": "smoke",
  "version": "1",
  "cases": [
    {
      "id": "cli-help",
      "command": ["python", "-m", "e2e", "--help"],
      "graders": [
        {"type": "exit-code", "expected": 0},
        {"type": "contains", "text": "E2E engineering runtime"}
      ]
    }
  ]
}
```

## Commands

```bash
e2e eval-suite run evals/smoke.json
e2e eval-suite compare .e2e/evals/current.json .e2e/evals/baseline.json
```

The harness writes structured reports under `.e2e/evals/`.

## Why deterministic first

LLM judges can be useful for subjective dimensions, but deterministic acceptance checks should remain the first line for code because they are reproducible, auditable, and resistant to grader drift. Current evaluation guidance similarly emphasizes versioned datasets, explicit metrics, thresholds, and regression gates. citeturn0search0turn0search11

## E2E verification relationship

Evaluation does **not** replace SD3. The evaluation harness answers: "What happened across measured attempts?" SD3 answers: "Is this implementation independently acceptable to ship?"

```text
Evaluation = measurement
Introspection = diagnosis
SD3 = independent verification
Release = evidence-backed decision
```
