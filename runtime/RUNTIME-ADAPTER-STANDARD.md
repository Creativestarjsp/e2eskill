# Runtime Adapter Standard

## Purpose

Claude Code and Codex are interchangeable execution runtimes for E2E. Domain skills, SD1/SD2/SD3 roles, context, memory, evidence requirements, browser policy, and tool authorization must remain runtime-neutral.

## Shared contract

Every runtime receives the same:

1. project and task context;
2. applicable repository/runtime instructions;
3. relevant CodeBrain context;
4. relevant durable memory as advisory context;
5. matched specialist skills;
6. role-specific tool policy;
7. E2E MCP gateway configuration;
8. visible/headless browser policy;
9. timeout and concurrency limits;
10. evidence/report requirements.

The canonical machine-readable contract is exposed by `e2e runtime contract` and parity is checked by `e2e runtime parity`.

## Runtime-specific boundary

Only transport and launcher details may differ:

- Claude Code uses its project instructions and `--mcp-config` with strict MCP configuration.
- Codex uses `AGENTS.md` plus an isolated `CODEX_HOME` configuration for the E2E MCP gateway.
- The same role policy and authorization boundary apply to both.

Runtime-specific configuration must never weaken the shared policy.

## Browser policy

Visible/headed browser execution is the default for local development, interactive QA, UI review, developer demonstrations, and SD3 verification. Headless execution is permitted for CI and non-interactive bulk checks. A request for visible execution must not be silently converted to headless execution.

## Evidence

Workers report changed files, commands/tests, evidence, risks, and remaining work. SD3 independently verifies the repository and does not accept worker claims as proof.

## Security

Memory is advisory, not authorization. Tool policy and the E2E MCP gateway are authoritative. Approval-required tools remain blocked without explicit approval regardless of runtime.
