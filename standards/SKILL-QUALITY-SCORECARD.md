# Skill Quality Scorecard

Use this scorecard when creating or reviewing any E2E skill.

## Scoring

Score each category from 0 to 2:

- **0** = missing or poor
- **1** = acceptable
- **2** = strong / production quality

Maximum score: **30**.

## Categories

| Category | Score |
|---|---:|
| Purpose and identity | /2 |
| Trigger conditions | /2 |
| Scope and boundaries | /2 |
| Inputs and outputs | /2 |
| Workflow | /2 |
| Decision framework | /2 |
| Domain quality bar | /2 |
| Anti-patterns | /2 |
| Verification | /2 |
| Failure / uncertainty handling | /2 |
| Security / safety | /2 |
| References / examples / tooling | /2 |
| Agent compatibility | /2 |
| Maintainability | /2 |
| Documentation consistency | /2 |

## Quality Gates

### 0–14: Draft

Do not publish as a production skill.

### 15–21: Usable

Suitable for experimentation. Improve before making it a core dependency.

### 22–26: Production

Acceptable for normal use.

### 27–30: Reference Quality

Suitable as a core/reference skill and as an example for future skill authors.

## Mandatory Gates

Regardless of score, the following cannot be missing for a production skill:

- purpose
- trigger
- scope
- actionable workflow
- quality bar
- verification
- failure handling
- applicable security/safety guidance

A high score does not override a mandatory gate failure.

## Review Questions

Before approval, ask:

1. Would a new agent know when to use this skill?
2. Would it know when not to use it?
3. Could it execute the workflow without guessing critical steps?
4. Does the skill explain important decisions?
5. Does it actively prevent common bad outcomes?
6. Can the result be verified?
7. Does it handle uncertainty honestly?
8. Is the skill appropriately scoped?
9. Can SD1 execute it safely?
10. Can SD2 delegate it clearly?
11. Can SD3 review its result objectively?
12. Would this skill remain useful across multiple projects?

## Review Output

Use this format:

```text
Skill:
Reviewer:
Date:

Score: __ / 30
Quality level: Draft | Usable | Production | Reference Quality

Mandatory gates:
- Purpose: PASS/FAIL
- Trigger: PASS/FAIL
- Scope: PASS/FAIL
- Workflow: PASS/FAIL
- Quality bar: PASS/FAIL
- Verification: PASS/FAIL
- Failure handling: PASS/FAIL
- Security/safety: PASS/FAIL/N/A

Strengths:
- ...

Findings:
- ...

Required changes:
- ...

Final decision:
APPROVE | REVISE | REJECT
```
