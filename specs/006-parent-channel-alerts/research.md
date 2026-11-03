# Research: Parent Channel Alerts

## Decision 1: Category-driven urgency model
- Decision: Categorize events as routine vs urgent with explicit policy table.
- Rationale: Deterministic quiet-hours behavior and safety bypass.
- Alternatives considered: content heuristic urgency (rejected as unpredictable).

## Decision 2: Per-guardian preference resolution
- Decision: Resolve channel and quiet-hours per guardian, not per family only.
- Rationale: Supports multi-guardian households with distinct preferences.
- Alternatives considered: single family preference (rejected for flexibility limits).

## Decision 3: Fallback delivery chain for urgent alerts
- Decision: Use configured fallback channels on urgent delivery failure.
- Rationale: Improves likelihood of critical alert receipt.
- Alternatives considered: no fallback (rejected for safety risk).
