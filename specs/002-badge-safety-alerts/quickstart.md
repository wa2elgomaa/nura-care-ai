# Quickstart: Badge Safety Alerts Validation

## Prerequisites
- Active child allergy + medication records from enrollment module
- Teacher role test account

## Scenario 1: Safe scan
1. Select child with no conflicts.
2. Submit snack intent and scan.
3. Verify SAFE result and event log.

## Scenario 2: Allergy conflict stop
1. Select child with matching allergen.
2. Submit snack intent and scan.
3. Verify STOP result and blocked action record.

## Scenario 3: Escalation and resolution
1. Trigger STOP event.
2. Escalate to supervisor.
3. Resolve with note and verify status transition.

## Scenario 4: Offline queue
1. Disable network.
2. Capture scan events.
3. Re-enable network and verify sync with no duplicates.
