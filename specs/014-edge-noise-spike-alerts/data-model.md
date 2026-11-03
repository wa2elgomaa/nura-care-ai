# Data Model: Edge Noise Spike Alerts

## NoiseAnomalyEvent
- Fields: id, siteId, zoneRef, peakDb, featureSummaryJson, detectedAt, confidenceBand

## NoiseThresholdPolicy
- Fields: id, zoneRef, peakThresholdDb, sustainedWindowMs, debounceMs, version

## NoiseAlert
- Fields: id, eventId, severity, status, acknowledgedAt, resolvedAt, routedToJson

## AudioRetentionGuardAudit
- Fields: id, guardAction, result, reasonCode, at

## NoiseIncidentAudit
- Fields: id, alertId, action, actorType, payloadJson, at
