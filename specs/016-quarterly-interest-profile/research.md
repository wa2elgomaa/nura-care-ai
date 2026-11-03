# Research: Quarterly Interest Profile

## Decision: Deterministic descriptive templates only
- Decision: Use deterministic narrative templates sourced from event evidence.
- Rationale: Enforces low-risk descriptive framing and avoids model hallucination.
- Alternatives considered: probabilistic scoring model (rejected).

## Decision: Internal metrics, external prose
- Decision: Keep counts internal for quality thresholds; never expose scores externally.
- Rationale: Supports consistency without violating no-score requirement.
- Alternatives considered: parent-facing numeric charts (rejected).

## Decision: Clinical language sign-off
- Decision: Require one-time clinical advisor review of phrase library prior to launch.
- Rationale: Reduces drift into diagnostic language.
- Alternatives considered: engineering-only review (rejected).
