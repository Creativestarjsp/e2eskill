# Database Abstraction Architecture

## Goal

Keep application/domain logic independent from database-specific persistence details when that boundary provides real value.

## Reference Architecture

```text
┌──────────────────────────────┐
│ API / UI / Application       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Domain / Application Services│
└──────────────┬───────────────┘
               │ depends on
               ▼
┌──────────────────────────────┐
│ Persistence Contract         │
│ repositories / capabilities  │
└──────────────┬───────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌──────────────┐  ┌──────────────┐
│ Mongoose     │  │ SQL / Other  │
│ Adapter      │  │ Adapter      │
└──────┬───────┘  └──────┬───────┘
       │                 │
       ▼                 ▼
   MongoDB          PostgreSQL/etc.
```

## Principles

1. **Use-case driven contracts** — expose operations the application actually needs instead of generic CRUD.
2. **Explicit capabilities** — transactions, optimistic concurrency, search, aggregation, geospatial queries, and other database-specific features must remain explicit when they affect correctness.
3. **Adapter ownership** — schemas, models, query syntax, driver errors, sessions, and database-specific serialization belong in adapters.
4. **No fake portability** — an abstraction must not erase guarantees that the application relies on.
5. **Operational visibility** — migrations, indexes, backups, and database deployment behavior remain explicit even when application code uses a repository interface.
6. **Contract + integration testing** — contract tests validate adapter conformance; real-database integration tests validate database semantics.

## When to Use

Use the abstraction when:

- domain logic is becoming coupled to persistence APIs
- multiple persistence implementations are a real requirement
- persistence needs a stable test seam
- vendor-specific code is spreading through services/controllers

Do not introduce it merely to make a simple application appear portable.

## Mongoose Example Boundary

```text
UserService
    |
    v
UserRepository
    |
    v
MongooseUserRepository
    |
    v
UserSchema / UserModel
    |
    v
MongoDB
```

The service should not import `mongoose`, construct `UserModel.find(...)`, or depend on Mongoose documents directly when this boundary is in use.

## E2E Skill Composition

- `database-engineer` — correctness, integrity, migrations, indexes, performance, recovery
- `database-abstraction` — persistence boundary and capability contracts
- `mongoose-developer` — MongoDB/Mongoose implementation
- `backend-developer` — service/application integration
- `qa-engineer` — contract and integration verification
- `security-engineer` — authorization and sensitive-data protection

## Verification Gate

A database abstraction is acceptable only when SD3 can verify:

- the boundary reduces real coupling
- domain/application code does not leak database-specific models
- capability semantics are explicit
- adapters are testable
- real database behavior is covered by integration evidence
- migrations and operational concerns remain visible
