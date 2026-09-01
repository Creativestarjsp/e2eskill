# E2E Master Engineering System Plan

## Mission

E2E is a runtime-neutral engineering system for AI-assisted software development. It combines project context, rules, specialist skills, SD1/SD2/SD3 agents, codebase intelligence, memory, guardrails, tools, verification, and runtime adapters.

Existing skills remain canonical. The roadmap expands the system around them; it does not replace them.

## Target Architecture

```text
                              E2E
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
     Context                  Rules                Skills
        │                      │                      │
        └──────────────┬───────┴──────────────┬───────┘
                       │                      │
                    CodeBrain              Memory
                       │                      │
                  Minimality                 │
                       └──────────┬───────────┘
                                  │
                           SD3 Supervisor
                                  │
                           SD2 Orchestrator
                                  │
                         ┌────────┼────────┐
                         │        │        │
                        SD1      SD1      SD1 ...
                         │        │        │
                    Specialist Skills
                         │
                    Tools / Runtime
                         │
                 Claude Code / Codex / future runtimes
```

## Phase Status

The architecture for all 12 phases is now finalized with concrete contracts under `architecture/` and `runtime/`. This does **not** claim that every runtime component is already shipped.

| Phase | Architecture | Engineering implementation |
|---|---|---|
| 1 | Complete | 🟢 Mostly implemented |
| 2 | Complete | 🟡 Context/rules runtime pending |
| 3 | Complete | 🟡 CodeBrain engine pending |
| 4 | Complete | 🟢 SD1/SD2/SD3 implemented |
| 5 | Complete | 🟢 Skills / 🟡 executable registry |
| 6 | Complete | 🟢 Browser / 🟡 broader tool integration |
| 7 | Complete | 🟡 Hook and memory runtime pending |
| 8 | Complete | 🟢 Standards / 🟡 automated gate runner pending |
| 9 | Complete | 🟡 Runtime adapter implementation pending |
| 10 | Complete | 🔴 CLI/visualization implementation pending |
| 11 | Complete | 🔴 Benchmark harness/execution pending |
| 12 | Complete | 🔴 Release automation pending |

## Completed Architecture Contracts

- `architecture/CONTEXT-AND-RULES.md`
- `architecture/CODEBRAIN.md`
- `architecture/SKILL-REGISTRY.md`
- `architecture/HOOKS-AND-GUARDRAILS.md`
- `architecture/MEMORY.md`
- `architecture/VERIFICATION.md`
- `architecture/RUNTIME-ADAPTERS.md`
- `architecture/DEVELOPER-EXPERIENCE.md`
- `architecture/BENCHMARKS.md`
- `architecture/RELEASE-GATES.md`
- `architecture/MINIMALITY-AND-CORRECTNESS.md`

Executable-facing contracts now live in:

- `runtime/e2e-manifest.yaml`
- `runtime/profiles.yaml`
- `runtime/hooks.yaml`
- `runtime/verification-gates.yaml`
- `runtime/adapters.yaml`
- `runtime/benchmark-manifest.yaml`
- `runtime/release-gates.yaml`

## Engineering Principles

1. Preserve existing skills unless a replacement has passed migration and verification.
2. Shared domain knowledge lives in `skills/` and `standards/`.
3. Claude/Codex-specific behavior belongs in runtime adapters.
4. SD1 executes; SD2 orchestrates; SD3 independently verifies.
5. Every meaningful action has inputs, outputs, verification, failure handling, and evidence.
6. Parallel work is allowed only when edits and dependencies are safe.
7. Security-sensitive actions require explicit guardrails and verification.
8. Agents must distinguish facts, inspected evidence, assumptions, and unknowns.
9. Repeated failure triggers diagnosis and escalation rather than infinite retries.
10. Before implementing, prefer the smallest correct solution: need → reuse → stdlib → native → installed dependency → simple implementation → custom abstraction.
11. Minimality never removes trust-boundary validation, data-loss protection, security, accessibility, or required correctness.
12. Benchmark claims must be reproduced with real agentic execution and executed verification, not single-shot prose comparisons alone.

## Definition of Done

The E2E system is production-ready when a supported runtime can:

```text
load project context
→ load applicable rules
→ discover relevant skills
→ retrieve targeted code context
→ apply minimality decision ladder
→ decompose work through SD2
→ execute through SD1
→ verify independently through SD3
→ record evidence and decisions
→ preserve useful memory
→ enforce hooks/guardrails
→ report a reproducible result
→ satisfy release gates
```
