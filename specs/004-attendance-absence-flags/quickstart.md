# Quickstart: Attendance and Absence Flags Validation

## Prerequisites
- Active child roster
- Teacher and director role accounts

## Scenario 1: Multi-method check-in/out
1. Check in three children via badge, QR, kiosk.
2. Check out one child.
3. Verify live roll and event history.

## Scenario 2: Auto-flag unexplained absence
1. Configure threshold policy.
2. Leave one expected child without check-in and no reason.
3. Verify unresolved flag is created after threshold.

## Scenario 3: Follow-up resolution
1. Open unresolved queue.
2. Add follow-up outcome.
3. Verify flag status changes and audit event persists.

## Scenario 4: Offline sync
1. Disconnect network and capture events.
2. Reconnect and sync.
3. Verify no duplicates and correct projected roll.
