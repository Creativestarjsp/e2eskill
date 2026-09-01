# E2E Context and Rules Architecture

## Purpose

Provide a deterministic model for deciding what an agent should know and which instructions apply before execution.

## Context Layers

```text
L0 Runtime Context      runtime capabilities, tool availability
L1 Project Context      BRD, PRD, architecture, conventions, progress
L2 Repository Context   structure, relevant files, dependencies, tests
L3 Task Context         current objective, constraints, acceptance criteria
L4 Code Context         symbols, callers, dependencies, impacted tests
L5 Historical Context   decisions, failures, approved patterns
```

Agents should load the smallest context package that is sufficient for the task. Larger context is not automatically better.

## Rules Precedence

```text
Safety / platform constraints
        ↓
Repository rules
        ↓
Directory / path rules
        ↓
Project conventions
        ↓
Skill instructions
        ↓
Task-specific instructions
        ↓
Local implementation preferences
```

When two instructions conflict, the higher-precedence rule wins. Material conflicts must be surfaced rather than silently ignored.

## Context Package

Every delegated task should be representable as:

```yaml
objective: "..."
requirements: []
constraints: []
relevant_files: []
relevant_symbols: []
dependencies: []
tests: []
rules: []
skills: []
known_risks: []
assumptions: []
unknowns: []
verification: []
```

## Context Loading Workflow

1. Identify the task and acceptance criteria.
2. Load project-level source-of-truth documents.
3. Resolve applicable rules.
4. Locate relevant repository areas.
5. Ask CodeBrain for symbols/dependencies when available.
6. Add only task-relevant history and decisions.
7. Produce a bounded context package for the worker.
8. Record missing context explicitly.

## Rules Safety

Rules must never be used to bypass security controls, conceal failures, fabricate evidence, or override higher-level system constraints.
