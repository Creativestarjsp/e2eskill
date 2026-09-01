# E2E Skill Engineering Rules

This repository is a reusable skill library for AI-assisted software development.

## Mission

Build skills that are focused, executable, verifiable, secure, and well documented.

## Before Changing Anything

1. Inspect the repository.
2. Read the relevant skill and documentation.
3. Reuse existing conventions.
4. Identify affected files.
5. Define the smallest safe change.

Never invent repository facts when they can be inspected.

## Skill Development Workflow

UNDERSTAND → INSPECT → DEFINE → DESIGN → IMPLEMENT → VALIDATE → REVIEW → DOCUMENT

## Engineering Rules

- Prefer simple solutions.
- Keep each skill focused on one capability.
- Avoid unnecessary duplication.
- Make instructions explicit and actionable.
- Define trigger conditions, inputs, outputs, failure handling, and completion criteria.
- Never embed secrets or credentials.
- Do not bypass security controls.
- Keep examples consistent with actual instructions.
- Validate changes before claiming completion.

## Project Skills

Use the most relevant specialist skill instead of forcing one skill to handle unrelated concerns.

Available specialist areas include:

- software architecture
- frontend development
- backend development
- database engineering
- API development
- UI/UX
- security
- QA/testing
- DevOps
- code review
- skill development

## Review Standard

When reviewing a skill or implementation, inspect the actual files and classify important findings as Critical, High, Medium, or Low.

Do not report speculation as fact.

## Completion

A change is complete only after relevant validation has been performed and documentation is synchronized.
