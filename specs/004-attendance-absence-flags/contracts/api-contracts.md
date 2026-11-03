# API Contracts: Attendance and Absence Flags

## POST /api/attendance/events
- Body: childId, type(CHECK_IN|CHECK_OUT), method(BADGE|QR|KIOSK), occurredAt, clientEventId
- Response: accepted, projectedState

## GET /api/attendance/roll
- Query: roomId, at
- Response: onSiteCount, absentCount, childStates[]

## GET /api/attendance/unexplained-absences
- Query: siteId, status
- Response: flags[]

## POST /api/attendance/unexplained-absences/{flagId}/follow-ups
- Body: outcomeCode, note
- Response: updated flag status

## PUT /api/attendance/threshold-policies/{policyId}
- Body: cutoffLocalTime, graceMinutes, active
