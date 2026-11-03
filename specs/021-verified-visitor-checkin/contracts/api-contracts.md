# API Contracts: Verified Visitor Check-In

## POST /api/visitor/checkin
- Body: visitorId, credentialInput, method (QR|PIN|FACE)
- Behavior: delegates verification to pickup core module
- Response: decision, reasonCode, sessionId?

## POST /api/visitor/checkout
- Body: sessionId
- Response: status, checkedOutAt

## POST /api/visitor/credentials
- Body: visitorId, validFrom, validUntil, centreId
- Access: director/front desk roles per policy

## GET /api/visitor/active-roster
- Query: centreId
- Response: activeVisitors[]

## POST /api/visitor/overrides
- Body: attemptId, reason
- Access: director role only
