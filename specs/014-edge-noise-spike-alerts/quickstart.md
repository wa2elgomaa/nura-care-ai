# Quickstart: Edge Noise Spike Alerts Validation

## Prerequisites
- Edge microphones calibrated by room
- pyAudioAnalysis worker running

## Scenario 1: Spike detection
1. Generate safe test spike in monitored area.
2. Verify immediate staff alert.

## Scenario 2: No audio retention
1. Run prolonged monitoring.
2. Verify no raw audio files are persisted/exported.

## Scenario 3: Offline continuity
1. Disconnect WAN.
2. Trigger noise spikes.
3. Verify local alerts continue and metadata syncs later.
