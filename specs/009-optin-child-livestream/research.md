# Research: Opt-In Child Livestream

## Decision: Edge-rendered blur-before-delivery
- Decision: Apply blur on edge prior to any parent-visible frame output.
- Rationale: Eliminates risk of exposing other children in transit.
- Alternatives considered: client-side blur (rejected as untrusted).

## Decision: Consent hard-stop control
- Decision: Re-check consent at session start and on periodic heartbeat; revoke immediately on change.
- Rationale: Ensures lawful continuation at runtime.
- Alternatives considered: start-only consent check (rejected).

## Decision: Metadata-only synchronization
- Decision: Sync session and policy events only, never stream content.
- Rationale: Preserves privacy and retention constraints.
- Alternatives considered: clip snapshots for troubleshooting (rejected).
