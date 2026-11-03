# Research: Enrollment Compliance Backbone

## Decision 1: Separate consent state machine from document records
- Decision: Maintain dedicated consent lifecycle model linked to child profile.
- Rationale: Enables strict auditability and downstream enforcement.
- Alternatives considered: consent as flat fields on profile (rejected: weak history semantics).

## Decision 2: Canonical child compliance aggregate
- Decision: Use one profile root with typed subrecords.
- Rationale: Simplifies completeness checks and inspector reporting.
- Alternatives considered: many unrelated records only (rejected: fragmented view).

## Decision 3: Offline-first intake with ordered sync events
- Decision: Queue local changes and synchronize with version-based reconciliation.
- Rationale: Front-desk operations must continue during outages.
- Alternatives considered: online-only forms (rejected by continuity requirement).
