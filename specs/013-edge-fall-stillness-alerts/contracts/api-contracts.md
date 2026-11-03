# API Contracts: Edge Fall Stillness Alerts

## POST /api/safety/fall-stillness/events
- Body: cameraRef, zoneRef, eventType, observedAt, confidenceBand

## POST /api/safety/alerts/{alertId}/ack
- Body: actorId, note

## POST /api/safety/alerts/{alertId}/resolve
- Body: actorId, outcome, note

## GET /api/safety/alerts
- Query: status, severity, from, to
- Response: alerts[]
