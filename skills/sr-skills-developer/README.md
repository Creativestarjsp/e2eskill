# SR Skills Developer

A production-oriented skill for building reliable, maintainable, and well-documented AI-agent skills.

## What it provides

- Skill discovery and repository inspection workflow
- Clear trigger, input, output, and non-goal definitions
- Practical `SKILL.md` structure
- Implementation and validation workflow
- Error-handling and security guidance
- Testing strategy for documentation, code-generation, and workflow skills
- Reusable prompts for skill development and review
- Definition of done and maintenance guidance

## Directory

```text
skills/sr-skills-developer/
├── SKILL.md
└── README.md
```

## Usage

Use this skill when you are creating or improving an agent skill.

Recommended workflow:

1. Inspect existing skills and repository conventions.
2. Define the new skill's purpose and scope.
3. Design the smallest maintainable structure.
4. Implement `SKILL.md` and only necessary supporting files.
5. Validate instructions, examples, and workflow behavior.
6. Document limitations and maintenance expectations.

## Design Philosophy

The skill favors explicit, verifiable instructions over vague guidance. It treats skills as maintainable software: they should have a clear purpose, predictable execution path, validation criteria, and documentation that remains consistent with implementation.

## Quality Bar

A skill should not be considered complete merely because its Markdown file exists. It should be understandable and executable by an agent that did not participate in its creation.
