# Research: Edge Fall Stillness Alerts

## Decision: MediaPipe Pose baseline
- Decision: use MediaPipe Pose keypoints + rules for fall/stillness detection.
- Rationale: interpretable, edge-suitable, and constitution-aligned.
- Alternatives considered: custom deep model training (rejected by phase constraints).

## Decision: Two-stage alerting
- Decision: immediate alert plus escalation on no acknowledgment.
- Rationale: balances speed and operational accountability.
- Alternatives considered: alert-only without escalation (rejected).

## Decision: Policy-tunable thresholds
- Decision: expose room/program threshold profiles controlled by directors.
- Rationale: manages false-alert rate while preserving safety sensitivity.
- Alternatives considered: hardcoded global thresholds (rejected).
