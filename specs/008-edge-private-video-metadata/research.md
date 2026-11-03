# Research: Edge Private Video Metadata

## Decision: Edge stack baseline
- Decision: Standardize on Frigate + YOLO + CompreFace accelerated by Coral TPU as mandatory site baseline.
- Rationale: Meets constitution requirement for local CV with practical operability.
- Alternatives considered: cloud CV processing (rejected by privacy constraints), custom model stack (deferred by phase sequencing).

## Decision: Strict egress contract
- Decision: Enforce schema allowlist + denylist checks before any outbound publish.
- Rationale: Prevents accidental raw video or embedding leakage.
- Alternatives considered: best-effort filtering after publish (rejected for risk).

## Decision: Offline outbox-first sync
- Decision: Queue approved metadata locally and replay idempotently when online.
- Rationale: Supports outage continuity and deterministic reconciliation.
- Alternatives considered: live-only publish (rejected for outage fragility).
