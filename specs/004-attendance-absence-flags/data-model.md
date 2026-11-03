# Data Model: Attendance and Absence Flags

## ChildDailyAttendance
- Fields: id, childId, dateLocal, currentState, lastEventAt, roomId

## AttendanceEvent
- Fields: id, childId, type, method, actorId, occurredAt, clientEventId
- Validation: unique clientEventId per site/day

## AbsenceReason
- Fields: id, childId, dateLocal, reasonCode, submittedBy, submittedAt

## AbsenceThresholdPolicy
- Fields: id, siteId, roomId, cutoffLocalTime, graceMinutes, active

## UnexplainedAbsenceFlag
- Fields: id, childId, dateLocal, status, openedAt, resolvedAt, ownerId
- State transitions: open -> in_progress -> resolved

## FollowUpAction
- Fields: id, flagId, actorId, outcomeCode, note, createdAt
