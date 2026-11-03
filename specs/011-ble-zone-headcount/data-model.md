# Data Model: BLE Zone Headcount

## ChildBadgeAssignment
- Fields: id, childId, badgeId, tamperState, batteryState, assignedAt, status

## StaffPanicBadge
- Fields: id, staffId, badgeId, status, lastHeartbeatAt

## ZoneGateway
- Fields: id, siteId, zoneRef, firmwareVersion, healthState, lastSeenAt

## ZonePresenceState
- Fields: id, subjectType, subjectId, zoneRef, confidenceBand, lastObservedAt

## RatioComplianceState
- Fields: id, zoneRef, requiredRatioRule, staffCount, childCount, status, evaluatedAt

## ZoneSafetyAlert
- Fields: id, alertType, zoneRef, subjectId, severity, status, raisedAt, resolvedAt
