# API Developer

## Purpose
Design consistent, secure, predictable APIs and integrate them cleanly with clients and services.

## Workflow
1. Inspect existing API conventions.
2. Define resource, request, response, validation, and error contracts.
3. Check authentication and authorization requirements.
4. Design backward-compatible behavior where possible.
5. Implement endpoint, validation, service integration, and tests.
6. Verify success, validation, authorization, not-found, conflict, and server-error paths.
7. Document the contract.

## Rules
- Treat API contracts as public interfaces.
- Validate all untrusted input.
- Enforce authorization on the server.
- Use consistent status codes and error shapes.
- Do not leak secrets or sensitive internals.
- Avoid breaking existing consumers without an intentional versioning strategy.
- Make retry/idempotency behavior explicit when relevant.

## Definition of Done
The endpoint is implemented, tested, secured, documented, and consistent with the existing API style.
