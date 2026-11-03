# Research: Verified Visitor Check-In

## Decision: Extend pickup core instead of rebuilding
- Decision: integrate with existing pickup verification module for QR/PIN/optional facial logic.
- Rationale: lower priority extension should maximize reuse and consistency.
- Alternatives considered: standalone visitor verifier service (rejected).

## Decision: Temporary credential lifecycle
- Decision: expiry-bounded visitor credentials with centre scope and one active session guard.
- Rationale: minimizes stale access risk.
- Alternatives considered: open-ended credentials (rejected).

## Decision: Occupancy reconciliation rules
- Decision: rules-driven stale session detection and resolution workflow.
- Rationale: keeps active roster accurate for safety operations.
- Alternatives considered: manual-only checkout tracking (rejected).
