# Quickstart: Regional Safety Ops Dashboard Validation

## Prerequisites
- Region-isolated data stores provisioned (US, EU, GCC)
- Centre aggregate feeds and pickup KPI feed active
- RBAC and tenant scopes configured

## Scenario 1: Region isolation
1. Sign in as US regional manager.
2. Verify only US scoped centres are visible.
3. Attempt EU query and verify denied.

## Scenario 2: Aggregated metadata-only assurance
1. Inspect dashboard payloads and persisted rows.
2. Verify no raw video/media/embedding fields present.

## Scenario 3: Pickup KPI integration
1. Trigger pickup unauthorized attempts at centre level.
2. Verify regional risk band updates via pickup aggregate feed.
