# E2E Engineering Skill System

A runtime-neutral engineering system for AI-assisted software development. E2E combines reusable specialist skills with project context, rules, CodeBrain, SD1/SD2/SD3 orchestration, memory, guardrails, tools, verification, and runtime adapters.

## Core Architecture

```text
BRD / PRD
   ↓
Context + Rules
   ↓
CodeBrain context retrieval
   ↓
SD3 Supervisor
   ↓
SD2 Orchestrator
   ↓
SD1 Workers
   ↓
Specialist Skills
   ↓
Tools / Implementation
   ↓
Testing + Verification
   ↓
SD3 Approval
   ↓
Memory / Reports
```

## Existing Skills

Existing skills are preserved and remain the canonical domain layer:

| Skill | Purpose |
|---|---|
| `sr-skills-developer` | Design, document, validate, and maintain agent skills |
| `software-architect` | Architecture and technical decisions |
| `frontend-developer` | Frontend implementation and quality |
| `react-js-developer` | React web development |
| `react-native-cli-developer` | React Native CLI development |
| `expo-developer` | Expo development and EAS workflows |
| `backend-developer` | Backend services and business logic |
| `database-engineer` | Schema, migrations, queries, and integrity |
| `api-developer` | API contracts and endpoint implementation |
| `ui-ux-designer` | Product UX, interaction, and accessibility |
| `security-engineer` | Application security review |
| `qa-engineer` | Testing and quality assurance |
| `devops-engineer` | CI/CD, environments, deployment, and operations |
| `code-reviewer` | Independent engineering review |
| `agent-browser` | Browser automation and visible/headless verification |
| `seo-*` | SEO audit and specialist workflows |

See `skills/` for the full library.

## System Architecture Documents

- `E2E-PLAN.md` — master roadmap and phase status
- `BRD.md` — business source of truth for E2E
- `SD-AGENT-SYSTEM.md` — SD1/SD2/SD3 operating model
- `architecture/CONTEXT-AND-RULES.md` — context loading and rule precedence
- `architecture/CODEBRAIN.md` — repository intelligence architecture
- `architecture/SKILL-REGISTRY.md` — skill discovery and composition
- `architecture/HOOKS-AND-GUARDRAILS.md` — deterministic safety and lifecycle checks
- `architecture/MEMORY.md` — durable agent/project memory model
- `architecture/VERIFICATION.md` — evidence and verification model
- `architecture/RUNTIME-ADAPTERS.md` — Claude Code/Codex adapter boundary
- `architecture/DEVELOPER-EXPERIENCE.md` — CLI, status, reports, and observability
- `architecture/BENCHMARKS.md` — benchmark methodology
- `architecture/RELEASE-GATES.md` — production release gates

## Standards

The `standards/` directory defines how E2E skills and agents are authored, reviewed, scored, and verified. Runtime-specific behavior belongs in adapters rather than duplicated domain skills.

## Development Loop

```text
UNDERSTAND
→ INSPECT
→ DEFINE
→ DESIGN
→ IMPLEMENT
→ VALIDATE
→ REVIEW
→ VERIFY
→ DOCUMENT
```

## Key Principles

- Preserve and improve existing skills rather than replacing them casually.
- Keep shared engineering knowledge runtime-neutral.
- Use CodeBrain to reduce irrelevant context and support impact analysis.
- Keep SD1 execution, SD2 orchestration, and SD3 independent verification distinct.
- Require evidence for completion claims.
- Prefer deterministic guardrails for security and safety.
- Never store secrets in skills, memory, or generated project context.
- Escalate persistent or architectural failures instead of retrying forever.
