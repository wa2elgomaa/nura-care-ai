# Quickstart: Enrollment Compliance Backbone Validation

## Prerequisites
- Child identity records available
- Director/admin accounts with compliance permissions

## Scenario 1: Full profile creation
1. Create child compliance profile.
2. Add enrollment docs, medical/allergy records, immunization proof, emergency contacts.
3. Verify completeness state transitions from incomplete to complete.

## Scenario 2: Consent lifecycle (including biometric opt-in)
1. Record consent as denied/not provided.
2. Update to granted.
3. Revoke and verify immediate state update and history integrity.

## Scenario 3: Audit extraction
1. Modify multiple records.
2. Export audit timeline.
3. Validate actor, action, timestamp continuity.

## Scenario 4: Offline intake sync
1. Disable network and perform intake edits.
2. Reconnect and sync.
3. Verify no lost updates and deterministic merge behavior.
