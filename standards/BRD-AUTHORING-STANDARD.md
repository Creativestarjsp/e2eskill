# BRD Authoring Standard

## Purpose

This standard defines how Business Requirements Documents are created and maintained in projects using the E2E Skill system.

## BRD Principle

The BRD is the **business source of truth**.

It explains:

- why the initiative exists
- which business problem it addresses
- which business outcomes are required
- who the stakeholders and customers are
- what constraints and risks matter

It should not become a technical design document.

## BRD vs PRD

```text
BRD → Why does the business need this?
PRD → What should the product do?
Architecture → How should we build it?
```

## Required Sections

A production BRD should normally contain:

1. Document information
2. Executive summary
3. Business problem
4. Business opportunity
5. Current state
6. Proposed business solution
7. Business goals
8. Success metrics / KPIs
9. Stakeholders
10. Target customers / users
11. Business requirements
12. Business rules
13. Scope / out of scope
14. Constraints
15. Assumptions
16. Dependencies
17. Competitive / market context
18. Business model / revenue impact where relevant
19. Compliance and policy requirements
20. Risks
21. Business acceptance criteria
22. Traceability
23. Approval / sign-off

## Requirement Rules

Each business requirement should:

- have a stable identifier such as `BR-001`
- express a business need rather than an implementation detail
- be unambiguous
- be testable at the business level
- map to a business goal, problem, or stakeholder need

Avoid requirements such as:

> Use PostgreSQL for customer data.

Prefer:

> The business must retain customer records reliably and make them available to authorized product workflows.

Technical choices belong in architecture and technical design documents.

## Traceability

Where practical maintain this chain:

```text
Business Goal
 ↓
BR-###
 ↓
PRD Requirement
 ↓
Technical Requirement
 ↓
Implementation
 ↓
Verification
```

This allows SD3 to verify that delivered software still serves the original business objective.

## Quality Checks

Before a BRD moves to PRD planning, verify:

- business problem is specific
- proposed solution addresses the problem
- goals have measurable outcomes
- stakeholders are identified
- target users are clear
- requirements are traceable
- scope boundaries are explicit
- assumptions are visible
- risks have owners or mitigations
- acceptance criteria are defined
- technical implementation is not prematurely prescribed

## Change Management

When business requirements change:

1. Update the BRD.
2. Identify affected requirements.
3. Trace affected PRD requirements.
4. Re-evaluate architecture and implementation impact.
5. Update project planning.
6. Record material decisions.

Do not silently change business requirements through code or PRD edits.

## SD3 Review

SD3 should treat the BRD as the highest-level business intent when reviewing whether a project solves the intended problem.

A technically correct implementation that fails the approved business requirements should not be marked complete.
