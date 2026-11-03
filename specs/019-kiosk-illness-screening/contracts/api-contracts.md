# API Contracts: Kiosk Illness Screening

## POST /api/kiosk/screening/start
- Body: childId, kioskId
- Preconditions: active consent or manual override workflow

## POST /api/kiosk/screening/{sessionId}/thermal
- Body: valueCelsius, sensorId, qualityBand

## POST /api/kiosk/screening/{sessionId}/symptoms
- Body: responses[]

## POST /api/kiosk/screening/{sessionId}/evaluate
- Response: outcomeBucket, rationaleCode, nextAction

## GET /api/kiosk/screening/{sessionId}/audit
- Response: timeline[]
