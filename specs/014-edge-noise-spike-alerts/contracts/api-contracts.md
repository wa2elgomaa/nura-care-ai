# API Contracts: Edge Noise Spike Alerts

## POST /api/noise/events
- Body: zoneRef, peakDb, detectedAt, featureSummary
- Constraint: no raw audio payload accepted

## POST /api/noise/alerts/{alertId}/ack
- Body: actorId, note

## POST /api/noise/alerts/{alertId}/resolve
- Body: actorId, resolutionCode, note

## GET /api/noise/alerts
- Query: status, zoneRef, from, to
- Response: alerts[]
