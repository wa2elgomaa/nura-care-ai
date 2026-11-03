# API Contracts: Pickup Guardian Verification

## POST /api/pickup/verify
- Body: childId, method, methodPayload
- Response: verificationOutcome, allowedNextActions

## POST /api/pickup/handover
- Body: childId, verificationAttemptId
- Response: handoverDecision, handoverRef

## POST /api/pickup/alerts/{alertId}/ack
- Body: actorId, note

## GET /api/pickup/audit
- Query: childId, dateRange
- Response: attempts, handovers, alerts
