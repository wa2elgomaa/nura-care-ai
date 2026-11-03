# API Contracts: Edge Offline Continuity

## POST /api/sync/{domain}/batch
- Body: operations[] with idempotencyKey and sequence
- Response: accepted[], rejected[], checkpoint

## GET /api/sync/{domain}/checkpoint
- Response: lastAckedSequence, driftState

## POST /api/offline/connectivity-events
- Body: siteId, state, transitionedAt, reason

## GET /api/offline/status
- Response: queueDepthByDomain, lastSyncAtByDomain, unresolvedConflicts
