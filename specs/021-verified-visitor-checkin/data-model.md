# Data Model: Verified Visitor Check-In

## VisitorProfile
- Fields: id, regionCode, organizationId, centreId, fullName, visitorType, status

## VisitorCredential
- Fields: id, visitorId, credentialType, codeRef, validFrom, validUntil, status

## VisitorVerificationAttempt
- Fields: id, visitorId, method, outcome, reasonCode, verifiedAt, operatorId

## VisitorSession
- Fields: id, visitorId, centreId, checkedInAt, checkedOutAt, status, staleFlag

## VisitorOverrideApproval
- Fields: id, attemptId, approvedBy, approvalReason, approvedAt

## VisitorAuditEvent
- Fields: id, sessionId, action, actorType, payloadJson, at
