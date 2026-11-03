# API Contracts: Parent Channel Alerts

## PUT /api/parents/{guardianId}/notification-preferences
- Body: preferredChannel, quietHours, optInStates

## POST /api/notifications/events
- Body: childId, category, urgency, payload, dedupeKey
- Response: accepted, eventId

## GET /api/notifications/events/{eventId}/status
- Response: overallStatus, attempts[]

## POST /api/notifications/events/{eventId}/retry
- Purpose: manual retry for failed non-urgent notifications

## GET /api/notifications/deferred
- Query: releaseWindow
