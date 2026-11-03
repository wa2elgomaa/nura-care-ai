# Quickstart: Edge Private Video Metadata Validation

## Prerequisites
- Edge Box provisioned with Coral TPU and camera connectivity
- Frigate, YOLO worker, CompreFace, policy enforcer, and sync agent running

## Scenario 1: Local-only inference
1. Generate camera activity.
2. Verify detection and matching run locally.
3. Confirm no raw media/embedding outbound traffic.

## Scenario 2: Egress policy enforcement
1. Inject payload containing disallowed field.
2. Verify publish is denied and audit logged.

## Scenario 3: Offline replay sync
1. Disconnect internet and generate events.
2. Reconnect internet.
3. Verify idempotent batch publish with no duplicate final records.
