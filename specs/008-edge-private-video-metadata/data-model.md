# Data Model: Edge Private Video Metadata

## EdgeSiteNode
- Fields: id, siteCode, hardwareProfile, tpuStatus, tamperState, softwareVersion, lastHeartbeatAt

## CameraIngestSource
- Fields: id, siteNodeId, cameraRef, zoneRef, rtspEndpointHash, status, lastFrameAt

## LocalDetectionEvent
- Fields: id, siteNodeId, cameraRef, eventType, confidenceBand, occurredAt, localOnlyRef

## MetadataOutboxItem
- Fields: id, eventId, payloadJson, schemaVersion, dedupeKey, status, retryCount, nextRetryAt

## EgressPolicyRule
- Fields: id, ruleName, blockedFieldPattern, allowedSchemaVersion, enabled, updatedAt

## EgressAuditEvent
- Fields: id, outboxItemId, decision, reasonCode, actorType, at
