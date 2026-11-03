# Quickstart: Edge Fall Stillness Alerts Validation

## Prerequisites
- MediaPipe Pose worker active on Edge Box
- Alert recipients configured by zone

## Scenario 1: Fall alert
1. Simulate safe fall test sequence.
2. Verify immediate alert delivery.

## Scenario 2: Stillness alert
1. Simulate prolonged stillness beyond threshold.
2. Verify alert and escalation if unacknowledged.

## Scenario 3: Offline continuity
1. Disconnect WAN.
2. Trigger alerts.
3. Verify local dispatch and later metadata sync.
