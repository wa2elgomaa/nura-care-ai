# Quickstart: Role-Based Layouts Validation

## Prerequisites
- Auth users for Parent, Teacher, Director, Tablet and one multi-role account

## Scenario 1: Role-specific entry routing
1. Sign in as each single-role account.
2. Verify routed layout and navigation.

## Scenario 2: Multi-role deterministic selection
1. Sign in as multi-role user.
2. Verify selected role follows priority matrix.
3. Switch role and verify session/audit updates.

## Scenario 3: Shared workflow consistency
1. Trigger one shared workflow visible to multiple roles.
2. Verify outcome parity with role-specific UI differences only.

## Scenario 4: Offline role continuity
1. Sign in and cache role context.
2. Restart app offline.
3. Verify safe startup in cached role and reconciliation on reconnect.
