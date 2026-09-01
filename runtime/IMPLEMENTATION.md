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
- `e2e.orchestrator` — SD2 planning with bounded SD1 workers and dependency-aware phases.
- `e2e.executor` — explicit dry-run/execute bridge that launches SD1 workers through Claude Code or Codex and then requests an independent SD3 review.
- `e2e.benchmark` — repeated command benchmark runner with success rate, median latency and variance.
- `e2e.release` — release gate checker for skills, security, CodeBrain freshness, tests and diff hygiene.
- `e2e.cli` — developer CLI surface.

## Agent execution

Planning is safe by default:

```bash
python -m e2e execute "add Google login"
```

This generates the SD2 plan without launching an agent. Actual execution requires an explicit opt-in:

```bash
python -m e2e execute "add Google login" --runtime auto --execute
```

The runtime detects `claude` first, then `codex`. Claude Code is invoked in print mode with JSON output; Codex uses `codex exec` by default. Set `E2E_CODEX_COMMAND` if the installed Codex CLI exposes a different execution command. Set `E2E_AGENT_TIMEOUT` to change the per-agent timeout; the default is 30 minutes.

The executor never silently turns a dry-run into execution. Worker output is captured as evidence under `.e2e/executions/`. A successful worker phase is followed by an SD3 supervisor invocation that is instructed to independently inspect the repository rather than trusting worker claims.

The current executor processes dependency-ready workers safely within the SD2 worker bound. It does not claim simultaneous repository editing is safe; true parallel mutation should be added only with isolated worktrees or another conflict-safe workspace strategy.

Claude Code's CLI supports non-interactive print mode and JSON output, which makes it suitable for a scripted adapter. citeturn1search0

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
python -m e2e orchestrate "add Google login"
python -m e2e execute "add Google login"
python -m e2e execute "add Google login" --runtime claude-code --execute
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
