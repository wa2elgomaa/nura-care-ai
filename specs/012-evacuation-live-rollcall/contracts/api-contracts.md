# API Contracts: Evacuation Live Rollcall

## POST /api/evacuation/events
- Body: siteId, mode (drill|emergency)
- Response: evacuationEventId, startedAt

## POST /api/evacuation/events/{eventId}/rollcall
- Body: childId, state, teacherId

## POST /api/evacuation/events/{eventId}/evidence/ble
- Body: badgeId, gateId, observedAt

## POST /api/evacuation/events/{eventId}/evidence/qr
- Body: childId, scannedBy, scannedAt, checkpointRef

## GET /api/evacuation/events/{eventId}/status
- Response: accountedCount, unaccountedCount, discrepancies[]

## POST /api/evacuation/events/{eventId}/insurer-hook-preview
- Purpose: validate future insurer payload shape (metadata only)
