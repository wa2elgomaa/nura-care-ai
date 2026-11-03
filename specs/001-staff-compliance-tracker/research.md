# Research: Staff Compliance Tracker

## Decision 1: Use deterministic rule-based status evaluation
- Decision: Compute `compliant`, `expiring`, `expired` from renewal windows and room thresholds using deterministic rules.
- Rationale: Transparent, auditable behavior for inspections.
- Alternatives considered: Heuristic risk scoring (rejected: less explainable for audits).

## Decision 2: Event-backed audit history
- Decision: Persist immutable audit events for all credential and policy updates.
- Rationale: Required for regulator evidence and internal accountability.
- Alternatives considered: Last-write-only record history (rejected: insufficient audit traceability).

## Decision 3: Offline-first with conflict-aware sync
- Decision: Allow local updates and sync with server-authoritative reconciliation.
- Rationale: Supports operations during connectivity loss.
- Alternatives considered: Online-only updates (rejected: violates continuity constraint).
