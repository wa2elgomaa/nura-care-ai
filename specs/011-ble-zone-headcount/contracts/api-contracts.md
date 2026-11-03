# API Contracts: BLE Zone Headcount

## POST /api/ble/gateway-events
- Body: gatewayId, observedBadges[], observedAt

## GET /api/occupancy/zones
- Response: current zone headcount, staff count, ratio status

## POST /api/occupancy/alerts/{alertId}/ack
- Body: actorId, note

## POST /api/panic/trigger
- Body: badgeId, triggeredAt
- Response: alertId, routedRecipients
