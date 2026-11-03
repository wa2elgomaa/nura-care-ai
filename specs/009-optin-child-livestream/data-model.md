# Data Model: Opt-In Child Livestream

## ParentLivestreamSession
- Fields: id, parentId, childId, startedAt, endedAt, status, revokeReason

## ChildTrackingContext
- Fields: id, sessionId, activeCameraRef, handoffState, confidenceBand, updatedAt

## BlurEnforcementEvent
- Fields: id, sessionId, frameWindowRef, nonTargetCount, enforcementState, at

## LivestreamConsentSnapshot
- Fields: id, parentId, childId, consentVersion, validatedAt, validUntil

## LivestreamAuditEvent
- Fields: id, sessionId, action, actorType, payloadJson, at
