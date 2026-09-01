# E2E Memory Architecture

## Memory Layers

```text
Project Memory       durable project facts and conventions
Decision Memory      architecture/product decisions and rationale
Task Memory          current task state and unresolved items
Failure Memory       verified failure patterns and remediation
Agent Memory         scoped reusable execution knowledge
```

## Memory Record

```yaml
id: MEM-0001
type: decision | fact | failure | pattern
scope: project | subsystem | task | agent
summary: "..."
evidence: []
source: "..."
confidence: verified | probable | unknown
created_at: "..."
expires_at: null
supersedes: null
```

## Rules

1. Store durable, reusable information rather than transcripts.
2. Preserve provenance for important facts.
3. Never store secrets, credentials, tokens, or unnecessary personal data.
4. A new verified decision may supersede an older decision; do not silently rewrite history.
5. Low-confidence memories must be labeled and should not be treated as requirements.
6. Task-local memories should expire when the task is complete unless deliberately promoted.

## Retrieval

Memory retrieval should be relevance- and scope-aware. Prefer verified project decisions and current source-of-truth documents over stale memories.
