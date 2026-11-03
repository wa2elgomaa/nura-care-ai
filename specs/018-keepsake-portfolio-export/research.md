# Research: Keepsake Portfolio Export

## Decision: Single-child scoped export contracts
- Decision: enforce export requests scoped to one authorized child per operation.
- Rationale: reduces privacy leakage risk.
- Alternatives considered: family-wide multi-child archive export (rejected).

## Decision: Deterministic curation rules
- Decision: curated portfolio assembled by explicit category/date rules only.
- Rationale: predictable content governance and easier auditing.
- Alternatives considered: ML auto-selection (rejected).

## Decision: Signed short-lived download tokens
- Decision: use one-time or short-TTL signed URLs with audit logging.
- Rationale: prevents uncontrolled redistribution from stale links.
- Alternatives considered: permanent links (rejected).
