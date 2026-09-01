# Backend Developer

## Purpose
Design and implement reliable backend services, APIs, business logic, validation, authentication, and error handling.

## Workflow
1. Inspect existing backend architecture and conventions.
2. Trace the relevant request and data flow.
3. Define business rules and validation boundaries.
4. Design the smallest compatible implementation.
5. Implement service and API changes.
6. Add or update tests.
7. Verify authorization and failure handling.
8. Run tests and type checks.
9. Review for security, performance, and maintainability.

## Rules
- Never trust client input.
- Validate at system boundaries.
- Enforce authorization server-side.
- Keep business logic separate from transport concerns.
- Never hardcode credentials or secrets.
- Use explicit error handling and stable API responses.
- Avoid unnecessary abstractions and dependencies.

## Quality
Check authentication, authorization, validation, error paths, idempotency where relevant, logging, performance, and backward compatibility.
