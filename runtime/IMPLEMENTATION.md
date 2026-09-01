# E2E Runtime Implementation

The repository contains an executable Python runtime with no mandatory third-party runtime dependency.

## Implemented

- `e2e.brain` — repository graph with file hashes, symbols, imports, approximate calls, search, callers/callees, dependencies, impact, map, and context retrieval.
- `e2e.tree_sitter_provider` — optional structural parser for Python, JavaScript, JSX, TypeScript, and TSX when the CodeBrain extra is installed.
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

## CodeBrain parser strategy

CodeBrain uses an explicit provider boundary:

1. `auto` — prefer Tree-sitter for supported languages when its bindings are installed; otherwise use the deterministic regex fallback.
2. `tree-sitter` — structural provider path for supported languages.
3. `regex` — dependency-free portability mode.

Install the optional parser stack with:

```bash
pip install -e '.[codebrain]'
```

The Tree-sitter provider currently covers Python, JavaScript, JSX, TypeScript, and TSX. Unsupported languages continue through the fallback path instead of blocking repository analysis.

Parser provenance is stored in `.e2e/brain.json`, including provider counts and diagnostics. Syntax-error diagnostics lower reported coverage to `partial`; they are never silently treated as a clean parse.

## Runtime state

Generated indexes, memory, verification and benchmark reports are stored under `.e2e/` and ignored by Git.
