# Research: Regional Safety Ops Dashboard

## Decision: Region-first tenancy architecture
- Decision: enforce separate US/EU/GCC data planes with strict tenant keys.
- Rationale: satisfies residency and isolation obligations.
- Alternatives considered: single global shared database (rejected).

## Decision: Aggregated metadata-only regional layer
- Decision: ingest centre summaries, not raw event payloads with identifying media artifacts.
- Rationale: reduces privacy risk and supports scale.
- Alternatives considered: direct centre-level detailed replication (rejected).

## Decision: Reuse pickup operational KPIs
- Decision: consume pickup verification aggregated metrics from existing module.
- Rationale: avoids duplicate logic and maintains one source of truth.
- Alternatives considered: re-implement pickup analytics in dashboard service (rejected).
