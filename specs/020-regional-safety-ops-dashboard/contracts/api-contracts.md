# API Contracts: Regional Safety Ops Dashboard

## GET /api/regional/{regionCode}/snapshots
- Query: windowKey, orgId?, centreId?, riskLevel?
- Access: RBAC + ABAC scoped to requester tenant rights

## GET /api/regional/{regionCode}/centres/{centreId}/detail
- Response: anonymized aggregate metrics, action backlog, freshness markers

## POST /api/regional/{regionCode}/actions
- Body: centreId, ownerUserId, actionType, dueAt, note
- Access: regional director roles only

## GET /api/regional/{regionCode}/pickup-kpis
- Source: 010 pickup verification aggregates
- Response: approvedCount, deniedCount, unauthorizedAttemptRate, escalationLatencyP95
