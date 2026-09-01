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
- `e2e.adapters` — Claude/Codex/standalone detection, registered-tool reporting, and MCP gateway capability reporting.
- `e2e.tools` — role/scope/approval registry, policy materialization, secret-safe audit ledger, and registry validation.
- `e2e.tool_gateway` — E2E-owned stdio MCP gateway with role-scoped discovery, allowlisted native handlers, path confinement, approval enforcement, and audit logging.
- `e2e.orchestrator` — SD2 planning with bounded SD1 workers and dependency-aware phases.
- `e2e.executor` — dry-run/execute bridge that launches SD1 workers through Claude Code or Codex, integrates isolated worktrees, refreshes CodeBrain, and runs an independent SD3 review with bounded correction rounds.
- `e2e.worktree` — isolated Git worktree lifecycle, branch creation, change detection, commit, merge, and cleanup.
- `e2e.benchmark` — repeated command benchmark runner with success rate, median latency and variance.
- `e2e.release` — release gate checker for skills, security, CodeBrain freshness, tests and diff hygiene.
- `e2e.cli` — developer CLI surface.

## Tool / MCP gateway

E2E keeps authorization above the protocol boundary. MCP provides the interoperability protocol; E2E decides which role can see and invoke which registered capability. This is important because MCP tools are model-controlled and the specification recommends human control for tool invocations. The current MCP specification also supports authorization at the transport layer for protected HTTP servers. citeturn0search2turn0search1

The gateway currently exposes only registered, approval-free native read tools:

```text
repo.read
 git.read
shell.read
```

Write/destructive/network/secret tools remain registry capabilities but are not exposed by the gateway until their runtime-specific execution and approval path is implemented. The gateway therefore cannot silently turn an explicit-approval tool into an automatic tool.

Generate runtime configuration artifacts:

```bash
python -m e2e tool gateway --role sd1
python -m e2e tool gateway --role sd3
```

This writes ignored runtime state under `.e2e/mcp/`:

```text
.e2e/mcp/claude.json
.e2e/mcp/codex.toml
```

Claude Code supports loading MCP servers through `--mcp-config` and can restrict discovery to that configuration with `--strict-mcp-config`. citeturn1search1 Codex supports MCP servers through its MCP configuration, including stdio servers and per-server tool allowlists. citeturn1search0turn1search2

E2E generates both artifacts without mutating the user's global runtime configuration. Automatic Claude injection into worker execution is the next adapter step; Codex configuration remains an explicit runtime-adapter concern rather than silently modifying `~/.codex`.

### Gateway security boundary

1. Unknown tools are denied.
2. Unauthorized roles are denied.
3. Explicit-approval tools are denied unless an approval token is supplied by the execution layer.
4. Repository reads cannot escape the worker repository root.
5. Shell reads use a fixed command allowlist.
6. Tool arguments are fingerprinted rather than persisted verbatim in the audit ledger.
7. Failed calls are auditable.
8. The gateway never receives secret values unless a future handler explicitly requires them; secret-bearing handlers must remain runtime-managed.

The MCP 2026-07-28 specification moved to a stateless protocol core and added authorization hardening, so E2E should keep its gateway stateless and avoid building new behavior around legacy session assumptions. citeturn0search0turn0search11

## Agent execution

Planning is safe by default:

```bash
python -m e2e execute "implement the requested feature"
```

This generates the SD2 plan without launching an agent. Actual execution requires an explicit opt-in:

```bash
python -m e2e execute "implement the requested feature" --runtime auto --execute
```

The runtime detects `claude` first, then `codex`. Claude Code is invoked in print mode with JSON output; Codex uses the configured `E2E_CODEX_COMMAND` value or its current adapter default. Set `E2E_CODEX_COMMAND` if the installed Codex CLI exposes a different execution command. Set `E2E_AGENT_TIMEOUT` to change the per-agent timeout; the default is 30 minutes.

### Isolated SD1 execution

When execution is enabled, dependency-ready SD1 workers run in separate Git worktrees under `.e2e/worktrees/`. The active worker limit remains four. Independent workers can therefore execute concurrently without mutating the primary checkout. After a successful batch, each worker branch is integrated into the primary checkout in deterministic plan order. Merge conflicts stop the pipeline and preserve the relevant workspace for debugging.

Failed or timed-out worker workspaces are preserved rather than silently discarded. Successful integrated workspaces are cleaned up after merge. The primary checkout must be clean before execution begins.

### SD3 correction loop

After integration, CodeBrain is refreshed and SD3 independently reviews the actual repository. SD3 must return structured JSON containing a decision and, when needed, minimal corrective tasks. The executor supports at most **two correction rounds**. Each correction is executed in a fresh isolated worktree, integrated, followed by another CodeBrain refresh and SD3 review.

The loop terminates with one of these meaningful states:

- `approved` — SD3 accepted the integrated implementation.
- `rejected` — SD3 found a fundamental requirements or architecture problem.
- `correction-limit-reached` — fixable issues remain after the bounded correction budget.
- `supervisor-invalid-report` — SD3 did not produce the required structured decision.
- `correction-worker-failure` / `correction-merge-conflict` — correction could not be safely integrated.

There are no blind retries. Persistent blockers remain explicit in the execution report under `.e2e/executions/`.

## Commands

```bash
python -m e2e doctor
python -m e2e status
python -m e2e brain build
python -m e2e brain check
python -m e2e brain search "authentication"
python -m e2e brain impact AuthService
python -m e2e context "implement the requested feature"
python -m e2e skill list
python -m e2e tool list
python -m e2e tool check
python -m e2e tool policy sd1
python -m e2e tool gateway --role sd1
python -m e2e orchestrate "implement the requested feature"
python -m e2e execute "implement the requested feature"
python -m e2e execute "implement the requested feature" --runtime claude-code --execute
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

Generated indexes, memory, verification, benchmark reports, tool policies, MCP configuration artifacts, and gateway audit logs are stored under `.e2e/` and ignored by Git.
