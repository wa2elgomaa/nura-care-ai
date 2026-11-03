# Research: Evacuation Live Rollcall

## Decision: BLE primary with QR fallback
- Decision: use BLE gate events as primary evidence and QR scans as mandatory fallback.
- Rationale: preserves accountability when RF coverage degrades.
- Alternatives considered: BLE-only architecture (rejected).

## Decision: Insurer integration seam now
- Decision: define insurer-ready event contract in Phase 2 even if adapter remains disabled.
- Rationale: supports future underwriting partnerships without core redesign.
- Alternatives considered: defer insurer hooks entirely (rejected).

## Decision: Local command authority
- Decision: evacuation trigger and state machine must execute locally first.
- Rationale: internet outages cannot block emergency workflows.
- Alternatives considered: cloud-triggered orchestration (rejected).
