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

| Phase | Scope | Status | Primary artifacts |
|---|---|---|---|
| 1 | Foundation | Complete | BRD, standards, conventions |
| 2 | Context + Rules | Complete | context/rules architecture |
| 3 | CodeBrain MVP | Architecture complete | CodeBrain specification and provider contract |
| 4 | SD1 / SD2 / SD3 | Complete | agent system and runtime agents |
| 5 | Skills + Registry | Complete | skill standard, registry and composition model |
| 6 | Tools + Browser | Complete | browser standard and tool model |
| 7 | Hooks + Memory | Complete | guardrail and memory specifications |
| 8 | Verification | Complete | verification gates and evidence model |
| 9 | Runtime Adapters | Complete | Claude/Codex adapter contracts |
| 10 | Developer Experience | Complete | CLI/status/reporting specification |
| 11 | Benchmarks | Complete | benchmark methodology |
| 12 | Production Release | Complete | release and quality gates |

**Important:** phases marked "Complete" mean the repository-level architecture, contracts, standards, and integration surfaces are defined and usable by agent runtimes. CodeBrain's parser/graph engine itself remains an implementation project and must not be represented as already shipped.

## Execution Rules

1. Preserve existing skills unless a replacement has passed migration and verification.
2. Shared domain knowledge lives in `skills/` and `standards/`.
3. Claude/Codex-specific behavior belongs in runtime adapters.
4. SD1 executes; SD2 orchestrates; SD3 independently verifies.
5. Every meaningful action has inputs, outputs, verification, failure handling, and evidence.
6. Parallel work is allowed only when edits and dependencies are safe.
7. Security-sensitive actions require explicit guardrails and verification.
8. Agents must distinguish facts, inspected evidence, assumptions, and unknowns.
9. Repeated failure triggers diagnosis and escalation rather than infinite retries.
10. Documentation and implementation contracts must remain synchronized.

## Definition of Done

The E2E system is production-ready when a supported runtime can:

```text
load project context
→ load applicable rules
→ discover relevant skills
→ retrieve targeted code context
→ decompose work through SD2
→ execute through SD1
→ verify independently through SD3
→ record evidence and decisions
→ preserve useful memory
→ enforce hooks/guardrails
→ report a reproducible result
```
