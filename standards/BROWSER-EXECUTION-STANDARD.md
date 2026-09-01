# Browser Execution Standard

## Purpose

Define the standard execution modes for browser automation across E2E Skill System.

## Two Supported Modes

### Visible Mode

Visible/headed browser execution is the default for local development and human-observable work.

Use it for:

- development
- debugging
- interactive QA
- UI review
- visual regression investigation
- demonstrations
- SD3 verification

The developer or reviewer should be able to observe the browser actions when the environment supports a display.

### Headless Mode

Headless execution is intended for automation where human observation is unnecessary or unavailable.

Use it for:

- CI/CD
- scheduled regression tests
- repeatable automated suites
- large-scale checks
- environments without a display

## Selection Rules

```text
Local development → VISIBLE
Debugging         → VISIBLE
UI review         → VISIBLE
Interactive QA    → VISIBLE
SD3 verification → VISIBLE
CI/CD             → HEADLESS
Scheduled tests   → HEADLESS
No display        → HEADLESS
```

If the user explicitly requests visible execution, do not silently switch to headless mode.

If visible execution is impossible, report the limitation before using headless mode.

## Evidence

Both modes must produce verifiable evidence where appropriate.

Visible mode may use:

- screenshots
- video
- accessibility snapshots
- console logs
- test output

Headless mode may use:

- screenshots
- video
- accessibility snapshots
- console logs
- test output
- CI artifacts

Never claim that a human watched the browser when execution was headless.

## Security

Browser automation must protect credentials, tokens, cookies, personal information, private URLs, and confidential files. Never include secrets in screenshots, logs, or reports.

## Agent Compatibility

The standard applies equally to Claude Code and Codex. Runtime-specific browser commands belong in the corresponding runtime adapter.
