# Research: Attendance and Absence Flags

## Decision 1: Event-sourced attendance state
- Decision: Store immutable attendance events and project current state.
- Rationale: Supports auditability and robust replay/sync behavior.
- Alternatives considered: direct mutable state only (rejected: weak traceability).

## Decision 2: Policy-driven unexplained absence flags
- Decision: Generate flags from configurable threshold policies.
- Rationale: Allows site-specific operations while preserving deterministic behavior.
- Alternatives considered: fixed global threshold (rejected: inflexible).

## Decision 3: Idempotent offline sync
- Decision: Use clientEventId to prevent duplicate event application.
- Rationale: High-frequency drop-off workflows require robust dedupe.
- Alternatives considered: timestamp-only dedupe (rejected: collision risk).
