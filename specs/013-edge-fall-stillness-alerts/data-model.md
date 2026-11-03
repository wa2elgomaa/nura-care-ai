# Data Model: Edge Fall Stillness Alerts

## PoseSafetyEvent
- Fields: id, siteId, cameraRef, eventType, confidenceBand, observedAt, zoneRef

## FallStillnessPolicy
- Fields: id, zoneRef, stillnessSeconds, fallAngleThreshold, escalationSeconds, version

## SafetyAlert
- Fields: id, eventId, severity, routedToJson, status, acknowledgedAt, resolvedAt

## AlertEscalation
- Fields: id, alertId, escalationLevel, triggeredAt, recipientsJson

## SafetyIncidentAudit
- Fields: id, alertId, action, actorType, payloadJson, at
