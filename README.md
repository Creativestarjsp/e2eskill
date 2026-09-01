# E2E Skill Library

A reusable collection of focused engineering skills and project templates for AI-assisted software development.

## Skills

| Skill | Purpose |
|---|---|
| `sr-skills-developer` | Design, document, validate, and maintain agent skills |
| `software-architect` | Architecture and technical decisions |
| `frontend-developer` | Frontend implementation and quality |
| `backend-developer` | Backend services and business logic |
| `database-engineer` | Schema, migrations, queries, and integrity |
| `api-developer` | API contracts and endpoint implementation |
| `ui-ux-designer` | Product UX, interaction, and accessibility |
| `security-engineer` | Application security review |
| `qa-engineer` | Testing and quality assurance |
| `devops-engineer` | CI/CD, environments, deployment, and operations |
| `code-reviewer` | Independent engineering review |

## Project Templates

- `CLAUDE.md` — repository-level agent instructions
- `templates/PRD.md` — product requirements
- `templates/ARCHITECTURE.md` — system architecture
- `templates/PROGRESS.md` — project state and validation

## Recommended Development Loop

```text
IDEA
  ↓
PRD
  ↓
ARCHITECTURE
  ↓
DATABASE / API
  ↓
UI / IMPLEMENTATION
  ↓
TEST
  ↓
SECURITY REVIEW
  ↓
CODE REVIEW
  ↓
DEPLOY
  ↓
PROGRESS UPDATE
```

## Claude Workflow

Start by asking Claude to inspect the repository and understand its current state. Do not begin with a request to build the entire application.

Recommended first prompt:

```text
Read CLAUDE.md and inspect the complete repository.

Do not modify anything yet.

Understand:
- product purpose
- current architecture
- technology stack
- frontend
- backend
- database
- APIs
- authentication
- completed features
- incomplete features
- known issues
- technical risks

Then recommend the next implementation milestone.
```

Use specialist skills for the appropriate part of the work and require verification before considering a feature complete.
