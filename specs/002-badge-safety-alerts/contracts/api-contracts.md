# API Contracts: Badge Safety Alerts

## POST /api/safety-scans/evaluate
- Body: childToken, intentKind, intentPayload
- Response: result, reasonCode, guidance, scanEventId

## POST /api/safety-scans/{scanEventId}/escalate
- Body: severity, note
- Response: alertId, status

## POST /api/safety-alerts/{alertId}/resolve
- Body: resolutionNote
- Response: status, resolvedAt

## GET /api/safety-scans/history
- Query: childId, from, to, result

## GET /api/safety-alerts/open
- Query: siteId, severity
