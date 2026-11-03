# Data Model: Parent Channel Alerts

## GuardianNotificationProfile
- Fields: id, guardianId, preferredChannel, quietHoursJson, optInStatesJson

## NotificationEvent
- Fields: id, childId, category, urgency, payloadJson, createdAt, dedupeKey

## DeliveryAttempt
- Fields: id, eventId, channel, endpointRef, status, attemptedAt, failureCode

## DeferredQueueItem
- Fields: id, eventId, releaseAt, status
- State transitions: queued -> released -> delivered|failed

## UrgentRoutingRule
- Fields: id, category, bypassQuietHours, fallbackChainJson, active

## NotificationAuditEvent
- Fields: id, eventId, action, actorType, payloadJson, at
