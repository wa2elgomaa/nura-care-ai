# Research: Edge Offline Continuity

## Decision: Edge-first source of truth
- Decision: local event ledger is authoritative during outages.
- Rationale: safety operations must never depend on WAN.
- Alternatives considered: cloud-primary with local cache (rejected).

## Decision: Domain-specific outboxes
- Decision: maintain separate outboxes per domain with shared sync framework.
- Rationale: isolates failures and improves replay control.
- Alternatives considered: single global queue only (rejected).

## Decision: Deterministic reconciliation contracts
- Decision: use idempotency keys + ordered replay + conflict policies.
- Rationale: avoids duplicates and preserves audit integrity.
- Alternatives considered: best-effort merge without ids (rejected).
