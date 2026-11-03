# Quickstart: Staff Compliance Tracker Validation

## Prerequisites
- Phase 1 baseline modules available (identity, attendance assignments, audit)
- Local cache + sync enabled for test clients

## Scenario 1: Credential lifecycle
1. Create staff member and two credentials.
2. Set one to expiring window and one expired.
3. Confirm dashboard classification and alert generation.

## Scenario 2: Room coverage compliance
1. Configure room requirement.
2. Add assignments below required threshold.
3. Confirm shortfall flag appears and updates when staffing corrected.

## Scenario 3: Inspector snapshot
1. Generate snapshot.
2. Verify it includes credential and room compliance sections.
3. Verify immutable audit entries for all changes.

## Expected Outcomes
- Status calculations are accurate.
- Room shortfalls are deterministic.
- Snapshot generation is repeatable and auditable.
