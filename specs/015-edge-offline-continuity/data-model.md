# Data Model: Edge Offline Continuity

## ConnectivitySession
- Fields: id, siteId, state, startedAt, endedAt, transitionReason

## LocalOperationRecord
- Fields: id, domain, operationType, payloadRef, createdAt, actorId, idempotencyKey

## DomainOutboxItem
- Fields: id, domain, operationRecordId, status, retryCount, nextRetryAt, lastErrorCode

## SyncCheckpoint
- Fields: id, domain, lastAckedSequence, lastSyncedAt, driftState

## ReconciliationDecision
- Fields: id, outboxItemId, decisionType, reasonCode, decidedAt

## OfflineAuditEvent
- Fields: id, domain, action, actorType, payloadJson, at
