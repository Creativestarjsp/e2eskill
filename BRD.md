# Business Requirements Document (BRD)

## 1. Document Information

- **Project:** <Project Name>
- **Version:** 0.1
- **Status:** Draft
- **Owner:** <Business Owner>
- **Created:** <Date>
- **Last Updated:** <Date>

## 2. Executive Summary

Describe the business problem, opportunity, proposed direction, and expected business outcome in concise terms.

## 3. Business Problem

Describe the problem the organization or target customer currently experiences.

Include:

- who experiences the problem
- how frequently it occurs
- current impact
- current workaround
- cost or opportunity lost

## 4. Business Opportunity

Describe the opportunity created by solving the problem.

Consider:

- market opportunity
- customer value
- operational improvement
- revenue opportunity
- strategic advantage

## 5. Current State

Document how the process or product works today.

Include existing systems, workflows, manual processes, limitations, and known pain points.

## 6. Proposed Business Solution

Describe the proposed solution at a business level.

Do not prescribe technical implementation here. Explain what the business intends to achieve.

## 7. Business Goals

Define measurable goals.

| Goal | Measure | Target | Timeframe |
|---|---|---|---|
| <Goal> | <Metric> | <Target> | <Timeframe> |

## 8. Success Metrics / KPIs

Define how business success will be measured.

Examples:

- revenue
- activation
- retention
- conversion
- cost reduction
- time saved
- adoption
- customer satisfaction

## 9. Stakeholders

| Stakeholder | Role | Responsibility | Influence |
|---|---|---|---|
| <Name/Group> | <Role> | <Responsibility> | <High/Medium/Low> |

## 10. Target Customers / Users

Describe the business audience and major user groups.

For each group define:

- role
- problem
- desired outcome
- business importance

## 11. Business Requirements

Write requirements in business language.

Use stable identifiers:

```text
BR-001
BR-002
BR-003
```

Each requirement should be:

- necessary
- testable at the business level
- unambiguous
- traceable to a goal or problem

Example:

> **BR-001:** The business must be able to measure successful customer activation.

## 12. Business Rules

Document rules that must remain true regardless of implementation technology.

Examples:

- eligibility rules
- pricing rules
- approval rules
- account rules
- operational policies

## 13. Scope

### In Scope

List business capabilities included in this initiative.

### Out of Scope

Explicitly list capabilities that are not part of the initiative.

## 14. Constraints

Document known constraints such as:

- budget
- timeline
- staffing
- regulatory requirements
- existing contracts
- existing systems
- geographic limitations

## 15. Assumptions

List assumptions that materially affect the business case.

Every important assumption should be validated before final approval.

## 16. Dependencies

Document dependencies on:

- teams
- vendors
- partners
- data
- existing products
- legal/compliance decisions
- external systems

## 17. Competitive / Market Context

Summarize relevant competitors, alternatives, market expectations, and differentiation.

Do not turn this section into a detailed market research report unless required by the project.

## 18. Business Model / Revenue Impact

Describe the expected business model where relevant.

Include:

- pricing approach
- revenue source
- cost drivers
- expected financial impact
- monetization assumptions

## 19. Compliance and Policy Requirements

Document applicable business-level requirements involving:

- privacy
- legal obligations
- industry regulations
- contractual requirements
- internal policies

Technical implementation details belong in the appropriate technical documents.

## 20. Risks

| Risk | Probability | Impact | Mitigation | Owner |
|---|---|---|---|---|
| <Risk> | <H/M/L> | <H/M/L> | <Mitigation> | <Owner> |

## 21. Business Acceptance Criteria

Define what must be true for the business to accept the initiative.

Acceptance criteria should connect back to business requirements and measurable outcomes.

## 22. Traceability

Business requirements should flow into product and engineering requirements.

```text
Business Goal
    ↓
BR-001
    ↓
PRD Requirement
    ↓
Architecture / Technical Design
    ↓
Implementation
    ↓
Test / Verification
```

Maintain requirement identifiers when practical so SD2 and SD3 can trace implementation back to business intent.

## 23. Approval / Sign-off

| Stakeholder | Decision | Date | Notes |
|---|---|---|---|
| <Stakeholder> | <Approved/Pending/Rejected> | <Date> | <Notes> |

## 24. Relationship to Other Project Documents

The BRD is the business source of truth.

Recommended document hierarchy:

```text
BRD
 ↓
PRD
 ↓
ARCHITECTURE
 ↓
DATABASE / API / UI
 ↓
IMPLEMENTATION
 ↓
TESTING
 ↓
RELEASE
```

### BRD
Defines **why the business needs the initiative and what business outcome is required**.

### PRD
Defines **what the product must do to satisfy the business and user requirements**.

### Architecture
Defines **how the software should be designed and implemented**.

## 25. Definition of Done

A BRD is ready for downstream product planning when:

- the business problem is clear
- the opportunity is documented
- business goals are measurable
- stakeholders are identified
- target users are understood
- business requirements have identifiers
- scope and non-scope are explicit
- business rules are documented
- constraints and assumptions are known
- dependencies and risks are documented
- acceptance criteria are defined
- requirements can be traced into the PRD
