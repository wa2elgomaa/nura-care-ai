# Data Model: Kiosk Illness Screening

## ScreeningConsentSnapshot
- Fields: id, childId, guardianId, consentState, capturedAt, validUntil

## KioskScreeningSession
- Fields: id, childId, kioskId, startedAt, completedAt, status

## ThermalReading
- Fields: id, sessionId, sensorId, valueCelsius, qualityBand, capturedAt

## SymptomChecklistResponse
- Fields: id, sessionId, symptomKey, responseValue, capturedAt

## ScreeningOutcome
- Fields: id, sessionId, outcomeBucket, rationaleCode, escalatedTo, decidedAt

## ScreeningAuditEvent
- Fields: id, sessionId, action, actorType, payloadJson, at
