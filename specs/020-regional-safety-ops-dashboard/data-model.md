# Data Model: Regional Safety Ops Dashboard

## RegionalCentreSnapshot
- Fields: id, regionCode, organizationId, centreId, windowStart, windowEnd, ratioState, incidentBand, pickupRiskBand, freshnessState

## RegionalRiskBand
- Fields: id, snapshotId, ruleVersion, riskLevel, triggeredRulesJson, computedAt

## RegionalActionAssignment
- Fields: id, regionCode, centreId, ownerUserId, actionType, dueAt, status, createdAt

## TenantAccessScope
- Fields: id, userId, roleCode, regionCode, organizationScopeJson, centreScopeJson, active

## RegionalDashboardAuditEvent
- Fields: id, userId, regionCode, action, payloadJson, at
