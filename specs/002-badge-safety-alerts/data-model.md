# Data Model: Badge Safety Alerts

## ChildSafetyProfile
- Fields: id, childId, allergyStateVersion, medicationStateVersion

## AllergyRecord
- Fields: id, childId, allergen, severity, effectiveFrom, effectiveTo
- Validation: non-overlapping active records per allergen

## MedicationSchedule
- Fields: id, childId, medicationCode, windowStart, windowEnd, constraintsJson

## ServiceIntent
- Fields: id, actorId, childId, kind, payloadJson, createdAt

## SafetyScanEvent
- Fields: id, childId, actorId, intentId, result, reasonCode, scannedAt, sourceMode
- State: result enum {SAFE, STOP, NEEDS_REVIEW}

## SafetyAlert
- Fields: id, scanEventId, severity, status, assignedTo, openedAt, closedAt
- State transitions: open -> acknowledged -> resolved

## SafetyResolutionNote
- Fields: id, alertId, resolverId, note, createdAt
