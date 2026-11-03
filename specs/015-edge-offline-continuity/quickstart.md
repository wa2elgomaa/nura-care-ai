# Quickstart: Edge Offline Continuity Validation

## Prerequisites
- Edge local bus and event ledger enabled
- Domain outboxes configured for all Phase 1 and Phase 2 services

## Scenario 1: Full offline operations
1. Disable internet for site.
2. Perform attendance, pickup, BLE, evacuation, fall/noise alert actions.
3. Verify all actions complete locally with audit records.

## Scenario 2: Recovery sync
1. Restore internet connectivity.
2. Verify per-domain queued operations replay successfully.
3. Confirm cloud checkpoints align with local sequences.

## Scenario 3: Flapping resilience
1. Simulate repeated connect/disconnect cycles.
2. Verify no duplicate finalized records and stable reconciliation.
