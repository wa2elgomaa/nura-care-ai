# Research: Billing Finance Automation

## Decision 1: Isolated billing bounded context
- Decision: Keep billing in a dedicated Nx domain with explicit import restrictions.
- Rationale: Protect finance reliability and constitutional architectural boundaries.
- Alternatives considered: shared mixed domain with video services (rejected: coupling risk).

## Decision 2: Server-authoritative payment settlement
- Decision: Payment settlement state changes only finalize on backend.
- Rationale: Prevents inconsistent client-side financial truth.
- Alternatives considered: client-trusted settlement state (rejected: audit risk).

## Decision 3: Immutable finance audit events
- Decision: Record every invoice/payment/receipt transition as append-only events.
- Rationale: Required for financial traceability and compliance.
- Alternatives considered: mutable status only logs (rejected: weak forensic value).
