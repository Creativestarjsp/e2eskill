# SR Skills Developer

## Purpose

`sr-skills-developer` is a reusable engineering skill for designing, implementing, documenting, testing, reviewing, and maintaining high-quality AI-agent skills.

Use this skill when the task is to create a new skill, improve an existing skill, organize skill documentation, or make a skill reliable enough for repeated use by developers and coding agents.

## Core Principles

1. **Understand before changing**
   - Inspect the repository and existing skill structure before making changes.
   - Reuse established conventions where they exist.
   - Never invent repository structure when it can be inspected.

2. **Design for reliable execution**
   - A skill must tell an agent what to do, when to do it, and what good output looks like.
   - Prefer deterministic workflows over vague advice.
   - Separate required behavior from optional recommendations.

3. **Keep the skill focused**
   - One skill should have one clear job.
   - Avoid turning a skill into a general-purpose instruction dump.
   - Create supporting reference files when detailed material would make the main skill difficult to follow.

4. **Make quality verifiable**
   - Every important workflow should have observable completion criteria.
   - Include validation, testing, and review steps where appropriate.
   - Never claim an implementation is complete without verification.

5. **Document decisions**
   - Explain why the skill exists, what it covers, what it does not cover, and how users should invoke it.
   - Keep examples realistic and executable.

---

## Skill Development Workflow

When asked to build or modify a skill, follow this workflow.

### Phase 1 — Inspect

1. Identify the repository and target skill location.
2. Inspect existing skills, documentation, configuration, and conventions.
3. Look for duplicated functionality that should be reused.
4. Identify constraints from the host environment or agent platform.

### Phase 2 — Define

Write down:

- Skill name
- Problem solved
- Intended users/agents
- Trigger conditions
- Inputs
- Outputs
- Required tools or dependencies
- Non-goals
- Acceptance criteria

A good skill can answer these questions without ambiguity.

### Phase 3 — Design

Choose a structure appropriate to the skill.

Recommended baseline:

```text
skills/<skill-name>/
├── SKILL.md
├── README.md
├── examples/
│   └── example.md
└── references/
    └── reference.md
```

Do not create every file by default. Only add files that improve maintainability or usability.

### Phase 4 — Implement

Create the smallest complete implementation that satisfies the acceptance criteria.

Use:

- clear headings
- numbered workflows
- explicit inputs/outputs
- decision rules
- examples
- failure handling
- verification steps

Avoid:

- vague motivational language
- contradictory instructions
- repeated rules
- hidden assumptions
- unnecessary boilerplate

### Phase 5 — Validate

Review the skill as if another agent received it with no additional context.

Check:

- Can the agent tell when to use it?
- Can the agent follow the workflow without guessing?
- Are inputs and outputs clear?
- Are edge cases addressed?
- Are examples consistent with the instructions?
- Does the skill accidentally conflict with repository conventions?
- Is the documentation internally consistent?

### Phase 6 — Refine

Fix issues found during validation.

Prefer fewer, stronger instructions over a long list of weak ones.

### Phase 7 — Document

Every production-quality skill should explain:

- what it does
- when to use it
- when not to use it
- how it works
- expected inputs
- expected outputs
- examples
- validation expectations
- limitations

---

## Writing SKILL.md

`SKILL.md` is the operational source of truth.

A strong `SKILL.md` normally contains:

```markdown
# Skill Name

## Purpose

## When to Use

## When Not to Use

## Inputs

## Outputs

## Workflow

## Rules

## Validation

## Examples

## Limitations
```

### Instruction Quality

Use direct language.

Prefer:

> Inspect the existing skill before creating a new one.

Over:

> It may be a good idea to consider checking whether another skill already exists.

Use explicit actions:

- Inspect
- Compare
- Create
- Update
- Validate
- Test
- Document

Avoid ambiguous verbs such as:

- Handle
- Improve
- Optimize
- Consider
- Make better

unless the surrounding text defines exactly how.

---

## Skill Naming

Use names that describe the capability.

Good:

- `api-reviewer`
- `database-migration`
- `react-native-ui`
- `sr-skills-developer`

Avoid:

- `helper`
- `smart-skill`
- `utils`
- `general`

Use lowercase kebab-case for directory names.

---

## Trigger Design

A skill should have clear trigger conditions.

Example:

```text
Use this skill when the user asks to:
- create a new skill
- refactor an existing skill
- improve skill documentation
- validate skill behavior
```

Avoid overly broad triggers that cause the skill to run for unrelated work.

---

## Input Design

Define the minimum information required to execute the skill.

Example:

```text
Required:
- target repository
- skill name
- desired behavior

Optional:
- reference implementation
- preferred framework
- test requirements
```

Never require information that can be reliably discovered from the repository.

---

## Output Design

Outputs should be concrete.

Examples:

- created or updated `SKILL.md`
- supporting documentation
- examples
- validation report
- test results
- known limitations

Avoid outputs such as "a better skill" without measurable criteria.

---

## Error Handling

A production skill must define what to do when assumptions fail.

Recommended pattern:

1. Detect the missing or conflicting information.
2. Inspect available sources.
3. Prefer repository evidence over assumptions.
4. Make the smallest safe decision.
5. Record the assumption when it materially affects the result.
6. Stop rather than fabricating facts when the missing information is critical.

---

## Security

Never embed:

- secrets
- API keys
- passwords
- private tokens
- credentials

Do not instruct agents to bypass repository permissions or security controls.

When a skill interacts with code or infrastructure, explicitly account for:

- secret handling
- input validation
- authorization
- dependency risk
- unsafe command execution

---

## Testing Strategy

Testing depends on the skill type.

### Documentation-only skill

Validate:

- Markdown structure
- headings
- links
- examples
- consistency
- formatting

### Code-generation skill

Validate:

- generated code compiles or type-checks
- relevant tests pass
- generated structure follows repository conventions
- examples are valid

### Workflow/agent skill

Validate:

- trigger conditions
- workflow order
- expected outputs
- failure handling
- tool assumptions

When tests are unavailable, perform a structured manual review and state the limitation.

---

## Example Development Prompt

Use this prompt when starting work on a skill:

```text
You are developing a production-quality agent skill.

Target skill: <skill-name>

First inspect:
- existing skill directories
- repository documentation
- related implementations
- repository conventions

Do not modify anything during inspection.

Then define:
- purpose
- trigger conditions
- inputs
- outputs
- non-goals
- acceptance criteria

Design the smallest maintainable structure.

Implement the skill and supporting documentation.

Validate the result as an independent agent would:
- verify instructions are unambiguous
- verify examples match the workflow
- verify no instructions conflict
- verify required files exist
- run available tests/checks

Report:
- files changed
- key decisions
- validation performed
- remaining limitations
```

---

## Example Review Prompt

```text
Review this skill as a senior skills engineer.

Inspect the actual files.

Evaluate:
1. clarity
2. trigger precision
3. workflow completeness
4. input/output definition
5. error handling
6. security
7. testability
8. documentation quality
9. maintainability
10. unnecessary complexity

Classify findings as:
- Critical
- High
- Medium
- Low

Fix Critical and High issues.
Then re-validate the skill.
```

---

## Definition of Done

A skill is complete when:

- its purpose is clear
- its trigger conditions are specific
- its workflow is executable
- its inputs and outputs are defined
- failure behavior is addressed
- security concerns are considered
- examples are consistent
- relevant validation has been performed
- documentation is understandable without hidden context
- the skill does not duplicate another existing skill without a clear reason

---

## Maintenance

Treat skills as maintained software.

When modifying a skill:

1. Read the current version first.
2. Preserve useful behavior unless intentionally changing it.
3. Update related examples and references.
4. Re-run applicable validation.
5. Document materially important changes.

Do not let examples drift away from the actual skill instructions.
