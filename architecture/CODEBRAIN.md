# E2E CodeBrain Specification

## Purpose

CodeBrain is E2E's codebase-intelligence layer. It turns a repository into deterministic structural and optional semantic knowledge that agents can query for focused context and impact analysis.

## Architecture

```text
Repository
   ↓
Parser / Tree-sitter or equivalent
   ↓
File + Symbol Index
   ├── imports / exports
   ├── definitions
   ├── references
   ├── calls
   ├── tests
   └── configuration relationships
   ↓
Graph Store
   ↓
Optional Semantic Layer
   ↓
Context Retrieval + Impact Analysis
```

## MVP Graph Entities

- repository
- package/module
- file
- class
- function/method
- variable/constant
- type/interface
- endpoint
- database model/table
- test
- configuration entry

## MVP Edges

- contains
- imports
- exports
- calls
- references
- implements
- extends
- tests
- depends_on
- configures

## Required Queries

```text
search(query)
map(path)
find_symbol(name)
callers(symbol)
callees(symbol)
dependencies(path_or_symbol)
impact(path_or_symbol)
context(task)
```

## Determinism

Structural facts must be reproducible from the same repository revision. Semantic summaries are advisory and must never overwrite structural truth.

## Freshness

Each graph snapshot should identify:

- repository revision
- indexed files
- parser version
- schema version
- generated timestamp
- content hashes
- stale/error entries

Incremental refresh should invalidate changed files and affected relationships rather than rebuilding everything when safe.

## Context Retrieval Contract

A `context(task)` result should prefer:

1. acceptance criteria
2. directly relevant files/symbols
3. dependency and caller/callee context
4. affected tests
5. configuration/security boundaries
6. relevant historical decisions

It should return provenance for every retrieved fact.

## Impact Analysis

Impact should distinguish:

- direct impact
- transitive impact
- test impact
- API/public contract impact
- database/data impact
- security impact
- deployment/configuration impact

Unknown graph coverage must be reported. CodeBrain must never claim exhaustive impact when indexing is incomplete.

## Provider Model

E2E should expose a provider-neutral contract so CodeBrain can be backed by the native implementation or an external provider without changing agent skills.

```text
CodeBrainProvider
  ├── build()
  ├── refresh()
  ├── search()
  ├── symbol()
  ├── callers()
  ├── dependencies()
  ├── impact()
  └── context()
```

External systems may be adapters/providers; E2E remains independent of them.
