# Research: Pickup Guardian Verification

## Decision: Multi-method verification with biometric optionality
- Decision: QR/PIN remain primary; facial match is optional and consent-gated.
- Rationale: Balances safety, legal compliance, and operational continuity.
- Alternatives considered: facial-only pickup (rejected).

## Decision: Local biometric lifecycle enforcement
- Decision: keep embeddings local and enforce default 7-day purge.
- Rationale: aligns with constitution and BIPA-sensitive handling.
- Alternatives considered: cloud backup of embeddings (rejected).

## Decision: Immediate unauthorized escalation
- Decision: issue high-priority alerts on any unauthorized attempt.
- Rationale: reduces unsafe handover risk.
- Alternatives considered: passive logging only (rejected).
