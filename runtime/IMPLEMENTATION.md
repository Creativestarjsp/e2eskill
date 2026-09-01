# E2E Runtime Implementation

The repository now contains an executable Python runtime with no mandatory third-party runtime dependency.

## Implemented

- `e2e.brain` — deterministic native CodeBrain MVP with file hashes, symbols, imports, approximate calls, search, callers/callees, dependencies, impact, map, and context retrieval.
- `e2e.context` — bounded project/rules context loader with precedence metadata.
- `e2e.skills` — executable skill discovery and task matching.
- `e2e.hooks` — secret and protected-path guardrails with pass/block results.
- `e2e.memory` — scoped durable JSON memory with secret rejection.
- `e2e.verify` — executable verification/evidence runner.
- `e2e.adapters` — Claude/Codex/standalone detection and capability reporting.
- `e2e.benchmark` — repeated command benchmark runner with success rate, median latency and variance.
- `e2e.release` — release gate checker for skills, security, CodeBrain freshness, tests and diff hygiene.
- `e2e.cli` — developer CLI surface.

## Commands

```bash
python -m e2e doctor
python -m e2e status
python -m e2e brain build
python -m e2e brain check
python -m e2e brain search "authentication"
python -m e2e brain impact AuthService
python -m e2e context "add Google login"
python -m e2e skill list
python -m e2e run "add Google login"
python -m e2e verify --test "python -m pytest -q"
python -m e2e benchmark "python -m pytest -q" --repetitions 5
python -m e2e release
```

## Parser strategy

The MVP uses a deterministic dependency-free parser fallback. Tree-sitter is the preferred future structural provider for richer language coverage and incremental parsing. The provider boundary keeps this migration from changing agent skills.

## Runtime state

Generated indexes, memory, verification and benchmark reports are stored under `.e2e/` and ignored by Git.
