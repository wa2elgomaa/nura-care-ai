# Research: Edge Noise Spike Alerts

## Decision: pyAudioAnalysis for local anomaly features
- Decision: use pyAudioAnalysis to derive short-window acoustic features locally.
- Rationale: robust edge-friendly pipeline with interpretable metrics.
- Alternatives considered: cloud audio ML services (rejected).

## Decision: ephemeral rolling buffer only
- Decision: process audio in brief memory buffer and discard immediately.
- Rationale: enforces prohibition on continuous audio recording.
- Alternatives considered: temporary clip retention for debugging (rejected).

## Decision: room-profile threshold tuning
- Decision: maintain per-room anomaly profiles and debounce windows.
- Rationale: reduce noise-driven false alerts in high-activity areas.
- Alternatives considered: single global threshold (rejected).
