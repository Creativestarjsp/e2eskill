# E2E — Engineering Intelligence & Verification System

> A runtime-neutral engineering system for building, orchestrating, evaluating, and verifying AI-assisted software changes.

E2E is designed around a simple principle: **AI-generated engineering work should be treated as an engineering process, not just a model response.**

It combines repository intelligence, reusable specialist skills, structured context, multi-agent orchestration, deterministic guardrails, evaluation history, regression intelligence, and independent verification into one engineering workflow.

[![E2E Runtime](https://github.com/Creativestarjsp/e2eskill/actions/workflows/e2e-runtime.yml/badge.svg)](https://github.com/Creativestarjsp/e2eskill/actions/workflows/e2e-runtime.yml)

---

## Why E2E?

AI coding systems can produce useful implementations quickly, but reliable software engineering requires more than generating code. A production-oriented system must understand the repository, respect project rules, select the right expertise, verify changes, learn from previous failures, and provide evidence for its decisions.

E2E provides that engineering control plane.

### E2E focuses on

- **Repository intelligence** — understand files, symbols, imports, dependencies, callers, callees, and impact.
- **Context and rules** — combine repository, project, skill, task, and memory context with explicit precedence.
- **Specialist skills** — reusable engineering expertise for frontend, backend, APIs, databases, security, QA, DevOps, UI/UX, architecture, SEO, and more.
- **SD1 / SD2 / SD3 execution model** — separate implementation, orchestration, and independent supervision.
- **Evaluation** — measure engineering runs with deterministic graders, repeated attempts, pass@k, pass^k, latency, and baseline comparisons.
- **Regression intelligence** — use previous evaluation failures and baseline regressions to strengthen future plans.
- **Guardrails** — enforce secret detection, protected paths, lifecycle checks, and evidence requirements.
- **Runtime adapters** — provide a common engineering layer for Claude Code, Codex, and standalone execution.
- **Run evidence** — persist plans, worker reports, verification, evaluation, introspection, and final outcomes.
- **CI self-healing** — scheduled automation can inspect failed E2E Runtime results, repair the underlying defect with Claude, validate locally, and re-dispatch CI.

---

## Architecture

```text
                         ENGINEERING REQUEST
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │ Context + Rules         │
                    │ BRD / PRD / Project     │
                    │ Memory / Local Rules    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ CodeBrain                │
                    │ Repository Intelligence  │
                    │ Context / Impact         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Engineering Intelligence │
                    │ Risk / Regression /      │
                    │ Verification Planning    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ SD3 Supervisor           │
                    │ Independent Engineering  │
                    │ Policy + Quality Gate    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ SD2 Orchestrator         │
                    │ Decomposition / Workers  │
                    │ Dependencies / Parallel  │
                    └────────────┬────────────┘
                                 │
                         ┌───────┴───────┐
                         ▼               ▼
                    ┌──────────┐   ┌──────────┐
                    │ SD1      │   │ SD1      │
                    │ Worker   │   │ Worker   │   ...
                    └────┬─────┘   └────┬─────┘
                         │              │
                         └──────┬───────┘
                                ▼
                    ┌─────────────────────────┐
                    │ Testing + Evaluation     │
                    │ Regression + Evidence    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ SD3 Verification        │
                    │ Approve / Correct /     │
                    │ Reject / Escalate       │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Run Artifacts + Memory  │
                    │ Evidence / Learning     │
                    └─────────────────────────┘
```

### SD1 — Worker

Executes a bounded engineering task using a specialist skill. Workers are responsible for implementation and evidence, not final approval.

### SD2 — Orchestrator

Decomposes the request, selects and prioritizes workers, manages dependencies, parallelizes safe work, aggregates results, and coordinates corrections.

### SD3 — Engineering Supervisor

Acts as an independent engineering authority. SD3 inspects the actual repository and evidence, evaluates requirements, architecture, security, integration, tests, and regression risk, then approves, requests correction, rejects, or escalates.

---

## Engineering Intelligence

E2E does not treat every task as a fresh task.

Before execution, intelligence can combine:

```text
Task
 │
 ├── CodeBrain context + impact
 ├── Project rules
 ├── Relevant skills
 ├── Memory
 ├── Evaluation history
 └── Baseline comparison
          │
          ▼
   Regression Risk
          │
    ┌─────┼─────┐
    ▼     ▼     ▼
   LOW  MEDIUM  HIGH
          │      │
          │      ├── stronger verification
          │      ├── QA / security escalation
          │      └── SD3 regression gate
          │
          └── targeted verification
```

Historical failures are advisory signals, not authorization. High-risk regressions can strengthen the execution plan and verification requirements without bypassing independent SD3 review.

---

## Repository Intelligence

**CodeBrain** builds a lightweight repository model without requiring a heavyweight runtime dependency.

It can provide:

- file and content metadata
- language-aware symbol discovery
- imports and dependency relationships
- approximate call relationships
- caller / callee analysis
- impact analysis
- task-oriented context retrieval
- optional Tree-sitter parsing for supported languages

Supported source families include Python, JavaScript, JSX, TypeScript, Java, Go, Rust, PHP, Ruby, C#, Kotlin, and Swift.

---

## Evaluation & Verification

E2E separates **execution success** from **engineering confidence**.

The evaluation layer supports:

- deterministic command-based evaluation suites
- exit-code, content, and file-existence graders
- independent repeated attempts
- `pass@k`
- `pass^k`
- pass-rate and latency statistics
- baseline comparison
- regression detection
- persisted evaluation evidence

Verification can additionally incorporate:

- guardrail checks
- test execution
- CodeBrain freshness
- worker evidence
- SD3 review
- introspection and failure classification
- release gates

The system therefore avoids treating a single successful generation as proof that a change is production-ready.

### CI Self-Healing

The repository also contains a scheduled repair workflow:

```text
.github/workflows/e2e-self-heal.yml
```

It checks the latest `E2E Runtime` result, collects failed-run logs, asks Claude to diagnose and repair the underlying defect, runs local verification, commits only validated changes, and explicitly dispatches the runtime workflow again. The scheduler repeats on later runs if the runtime remains red.

The repair loop does **not** weaken or delete tests and does not replace SD3 verification. It requires a Claude Actions secret such as `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN`.

See [`architecture/CI-SELF-HEAL.md`](architecture/CI-SELF-HEAL.md) for the operating contract.

---

## Quick Start

### Requirements

- Python 3.10+
- Git
- `pytest` for running the test suite
- Claude Code and/or Codex when using external agent runtimes

The core runtime is dependency-light. Optional CodeBrain parsing dependencies are available through the `codebrain` extra.

### Install

```bash
git clone https://github.com/Creativestarjsp/e2eskill.git
cd e2eskill

python -m pip install -e .
```

Optional CodeBrain parser support:

```bash
python -m pip install -e '.[codebrain]'
```

### Initialize

```bash
e2e init
e2e doctor
e2e status
```

### Build repository intelligence

```bash
e2e brain build
e2e brain check
e2e brain search "authentication"
e2e brain impact AuthService
```

### Inspect task context

```bash
e2e context "add Google login"
e2e intelligence "add Google login"
```

### Plan work

```bash
e2e orchestrate "add authentication API"
```

### Execute

By default, execution is a dry run:

```bash
e2e execute "add authentication API"
```

To launch configured SD1/SD3 runtimes:

```bash
e2e execute "add authentication API" --execute
```

Runtime selection is automatic by default, or can be explicit:

```bash
e2e execute "add authentication API" --runtime claude-code

e2e execute "add authentication API" --runtime codex
```

Maximum worker concurrency is bounded by the runtime policy and CLI limit:

```bash
e2e execute "add authentication API" --execute --max-workers 4
```

### Verify

```bash
e2e verify --test "python -m pytest -q"
```

### Evaluate a suite

```bash
e2e eval-suite run evals/smoke.json
```

Compare a current evaluation against a baseline:

```bash
e2e eval-suite compare current.json baseline.json
```

### Inspect runtime contracts

```bash
e2e runtime inspect
e2e runtime parity
```

### Inspect tools and guardrails

```bash
e2e tool list
e2e tool check
e2e guardrails check --stage verification
```

### Run the full test suite

```bash
python -m pytest -q
```

---

## Project Structure

```text
.
├── architecture/          # System architecture and engineering standards
├── e2e/                   # Executable E2E runtime
├── evals/                 # Evaluation suites
├── runtime/               # Runtime contracts and execution profiles
├── skills/                # Reusable specialist engineering skills
├── standards/             # Authoring and quality standards
├── templates/             # Reusable engineering templates
├── tests/                 # Runtime and system tests
├── .codex/                # Codex-specific agent configuration
├── .github/workflows/     # Continuous integration and self-healing
├── AGENTS.md              # Repository agent instructions
├── BRD.md                 # Business requirements / system source of truth
├── E2E-PLAN.md            # Master roadmap and implementation status
├── SD-AGENT-SYSTEM.md     # SD1 / SD2 / SD3 operating model
└── pyproject.toml         # Python package and CLI configuration
```

---

## Skill System

Skills are the reusable engineering knowledge layer of E2E.

The repository includes specialist capabilities for areas such as:

- Software architecture
- Backend development
- Frontend development
- React / React Native / Expo
- API development
- Database engineering
- Mongoose / MongoDB persistence
- Security engineering
- QA engineering
- DevOps
- Code review
- UI/UX design
- SEO
- Agent and orchestration roles

Skills follow explicit authoring, quality, review, and verification standards. See [`SKILL-AUTHORING-STANDARD.md`](SKILL-AUTHORING-STANDARD.md) and [`standards/SKILL-QUALITY-SCORECARD.md`](standards/SKILL-QUALITY-SCORECARD.md).

---

## Runtime Model

E2E keeps engineering knowledge runtime-neutral while adapting execution to supported agent environments.

```text
                 E2E Engineering Layer
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
        Claude Code                Codex
             │                       │
             └───────────┬───────────┘
                         ▼
                 Runtime Contracts
                         │
                         ▼
                  Shared E2E Policy
```

Runtime-specific behavior belongs in the runtime adapter layer rather than being duplicated across domain skills.

---

## Engineering Principles

1. **Evidence over claims** — completion must be supported by observable evidence.
2. **Independent verification** — implementation and approval are separate responsibilities.
3. **Minimal correct change** — reuse existing capabilities before introducing new ones.
4. **Context before execution** — understand the repository and applicable rules before changing it.
5. **Regression-aware planning** — previous failures should influence verification depth.
6. **Deterministic guardrails** — safety-critical controls should not depend solely on model behavior.
7. **Bounded autonomy** — workers operate within explicit scope, tools, and concurrency limits.
8. **No infinite retry loops** — persistent, architectural, or integration failures are escalated.
9. **Runtime neutrality** — shared engineering knowledge should not depend on a single agent runtime.
10. **Security is a system property** — secrets, protected paths, tool access, and verification are controlled explicitly.

---

## Documentation

### Architecture

- [`E2E-PLAN.md`](E2E-PLAN.md) — master roadmap and definition of done
- [`BRD.md`](BRD.md) — business requirements and system source of truth
- [`SD-AGENT-SYSTEM.md`](SD-AGENT-SYSTEM.md) — SD1 / SD2 / SD3 operating model
- [`architecture/CONTEXT-AND-RULES.md`](architecture/CONTEXT-AND-RULES.md) — context loading and rule precedence
- [`architecture/CODEBRAIN.md`](architecture/CODEBRAIN.md) — repository intelligence
- [`architecture/REGRESSION-INTELLIGENCE.md`](architecture/REGRESSION-INTELLIGENCE.md) — regression-aware engineering planning
- [`architecture/VERIFICATION.md`](architecture/VERIFICATION.md) — evidence and verification model
- [`architecture/CI-SELF-HEAL.md`](architecture/CI-SELF-HEAL.md) — CI repair scheduler
- [`architecture/RELEASE-GATES.md`](architecture/RELEASE-GATES.md) — release requirements

### Standards

- [`CONVENTIONS.md`](CONVENTIONS.md) — repository conventions
- [`SKILL-AUTHORING-STANDARD.md`](SKILL-AUTHORING-STANDARD.md) — skill authoring
- [`AGENT-AUTHORING-STANDARD.md`](AGENT-AUTHORING-STANDARD.md) — agent authoring
- [`standards/SKILL-QUALITY-SCORECARD.md`](standards/SKILL-QUALITY-SCORECARD.md) — skill quality evaluation
- [`standards/SKILL-REVIEW-WORKFLOW.md`](standards/SKILL-REVIEW-WORKFLOW.md) — skill review process
- [`standards/BROWSER-EXECUTION-STANDARD.md`](standards/BROWSER-EXECUTION-STANDARD.md) — browser execution policy

### Runtime

- [`runtime/IMPLEMENTATION.md`](runtime/IMPLEMENTATION.md) — runtime implementation boundary
- [`runtime/RUNTIME-ADAPTER-STANDARD.md`](runtime/RUNTIME-ADAPTER-STANDARD.md) — runtime adapter contract
- [`runtime/e2e-manifest.yaml`](runtime/e2e-manifest.yaml) — system manifest
- [`runtime/profiles.yaml`](runtime/profiles.yaml) — execution profiles

---

## Development Workflow

The intended engineering loop is:

```text
UNDERSTAND
    ↓
INSPECT
    ↓
DEFINE
    ↓
DESIGN
    ↓
MINIMIZE
    ↓
IMPLEMENT
    ↓
TEST
    ↓
EVALUATE
    ↓
REVIEW
    ↓
VERIFY
    ↓
DOCUMENT
```

For contributors, start with [`AGENTS.md`](AGENTS.md), [`CONVENTIONS.md`](CONVENTIONS.md), and [`E2E-PLAN.md`](E2E-PLAN.md).

---

## Project Status

E2E is an actively developed engineering system. The repository contains an executable runtime and a growing set of architecture, skill, evaluation, verification, and runtime-adapter capabilities.

The implementation roadmap is tracked in [`E2E-PLAN.md`](E2E-PLAN.md). Runtime and system claims should be validated against the repository and CI rather than inferred from this README alone.

---

## Contributing

Contributions should preserve the system's architectural boundaries and verification model.

Before making changes:

1. Read [`AGENTS.md`](AGENTS.md).
2. Review [`CONVENTIONS.md`](CONVENTIONS.md).
3. Identify the relevant architecture and skill standards.
4. Keep changes scoped and evidence-based.
5. Add or update tests for executable behavior.
6. Run the relevant verification commands.
7. Do not claim completion without evidence.

---

## License

See the repository's license file for licensing terms.

---

## Maintainer

**Creativestarjsp**

E2E is maintained as an engineering research and implementation project focused on reliable AI-assisted software development.
