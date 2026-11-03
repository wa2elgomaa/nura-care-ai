# Data Model: Evacuation Live Rollcall

## EvacuationEvent
- Fields: id, siteId, triggerActorId, triggerAt, mode, status, closedAt

## RollcallSession
- Fields: id, evacuationEventId, teacherId, tabletId, startedAt, status

## AccountabilityState
- Fields: id, evacuationEventId, childId, state, lastEvidenceType, lastEvidenceAt, discrepancyCode

## BLEExitEvidence
- Fields: id, evacuationEventId, childBadgeId, gateId, observedAt, qualityBand

## QRFallbackEvidence
- Fields: id, evacuationEventId, childId, scannedBy, scannedAt, checkpointRef

## EvacuationAuditEvent
- Fields: id, evacuationEventId, action, actorType, payloadJson, at
