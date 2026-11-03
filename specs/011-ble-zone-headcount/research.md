# Research: BLE Zone Headcount

## Decision: Room-level BLE architecture
- Decision: use per-room gateway topology with edge signal fusion for 1-3m room accuracy.
- Rationale: matches safety use-case and practical deployment envelope.
- Alternatives considered: camera-only headcount for this feature (rejected by scope).

## Decision: Tamper-resistant badges + panic channel
- Decision: mandate tamper-resistant child badges and separate staff panic badges.
- Rationale: improves safety confidence and incident response.
- Alternatives considered: standard commodity tags without tamper state (rejected).

## Decision: Offline occupancy ledger
- Decision: maintain local source-of-truth occupancy timeline and sync metadata to cloud.
- Rationale: preserves continuity during WAN outages.
- Alternatives considered: cloud-only occupancy state (rejected).
