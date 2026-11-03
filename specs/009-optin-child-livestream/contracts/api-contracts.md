# API Contracts: Opt-In Child Livestream

## POST /api/livestream/sessions
- Body: childId
- Preconditions: parent role + active consent link
- Response: sessionId, streamToken (ephemeral)

## POST /api/livestream/sessions/{sessionId}/heartbeat
- Purpose: keepalive + consent revalidation

## POST /api/livestream/sessions/{sessionId}/stop
- Purpose: explicit termination

## GET /api/livestream/sessions/{sessionId}/status
- Response: activeCameraRef, handoffState, privacyState
