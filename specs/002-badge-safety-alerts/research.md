# Research: Badge Safety Alerts

## Decision 1: Deterministic safety rules at point of care
- Decision: Use strict, explainable allergy and medication conflict checks.
- Rationale: Safety-critical flows require predictable outcomes.
- Alternatives considered: probabilistic risk scoring (rejected as non-transparent).

## Decision 2: Immediate stop + escalation workflow
- Decision: Block unsafe actions and create supervisor-escalatable alerts.
- Rationale: Prevent harm and ensure accountability.
- Alternatives considered: warning-only model (rejected due to bypass risk).

## Decision 3: Offline capture with stale-data guardrails
- Decision: Allow scan event capture offline, but mark decisions when source data freshness is degraded.
- Rationale: Maintain operations while preventing silent unsafe assumptions.
- Alternatives considered: fully disable offline scans (rejected due to operational disruption).
