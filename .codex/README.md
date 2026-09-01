# Codex Runtime Adapter

E2E Skill System is runtime-agnostic. The domain skills under `skills/` are shared by Codex and Claude Code.

## Architecture

```text
Codex
  ↓
Runtime Adapter
  ↓
SD3 Supervisor
  ↓
SD2 Orchestrator
  ↓
SD1 Worker
  ↓
Shared Skills
  ↓
Tools / References
```

## Rules

- Do not duplicate domain skills for Codex.
- Use the shared `skills/` directory as the source of truth.
- Keep Codex-specific invocation, command, or runtime behavior in `.codex/`.
- Skills must not assume Claude-specific APIs or behavior unless explicitly documented as runtime-specific.
- Runtime-specific adapters must preserve the same SD1/SD2/SD3 responsibilities and quality gates.

## Shared Skills

Examples:

- `skills/react-js-developer/`
- `skills/react-native-cli-developer/`
- `skills/expo-developer/`
- `skills/backend-developer/`
- `skills/frontend-developer/`
- `skills/security-engineer/`

## Compatibility Principle

```text
One Skill
   ↓
Claude Code adapter ──┐
                      ├── same behavior / quality contract
Codex adapter ────────┘
```

Differences between runtimes should be handled at the adapter layer, not by forking the skill's domain knowledge.
