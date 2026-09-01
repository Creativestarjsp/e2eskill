# E2E Runtime Adapter Architecture

## Goal

Keep engineering knowledge runtime-neutral while allowing Claude Code, Codex, and future agent runtimes to expose their own capabilities.

## Adapter Boundary

```text
                Shared E2E
   Skills / Standards / Context / SD / Verification
                         │
                 Runtime Adapter
                  ┌──────┴──────┐
                  │             │
             Claude Code      Codex
```

## Adapter Responsibilities

- load shared instructions
- expose available tools/capabilities
- map agent lifecycle events to E2E hooks
- invoke shared skills without copying their domain logic
- provide runtime-specific paths/configuration
- return normalized execution/evidence results

## Adapter Must Not

- fork domain skill instructions
- change SD1/SD2/SD3 responsibilities
- bypass verification
- conceal unavailable capabilities
- inject secrets into shared artifacts

## Capability Detection

Runtime integrations should advertise capabilities such as:

```yaml
browser_visible: true
browser_headless: true
terminal: true
filesystem: true
git: true
mcp: true
subagents: true
hooks: true
```

Agents must degrade explicitly when a required capability is unavailable.

## Compatibility Rule

A skill is considered cross-runtime compatible when its core workflow can execute without depending on undocumented behavior of one runtime. Runtime-specific commands belong in the adapter layer.
