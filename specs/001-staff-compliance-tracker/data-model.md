# Data Model: Staff Compliance Tracker

## Entities

## StaffMember
- Fields: id, siteId, role, employmentStatus, createdAt, updatedAt
- Relationships: has many CredentialRecord, has many RoomAssignment
- Validation: employmentStatus required; role in allowed enum

## CredentialRecord
- Fields: id, staffId, type, issueDate, renewalDate, verificationStatus, complianceStatus
- Relationships: belongs to StaffMember
- Validation: renewalDate >= issueDate; type in {CPR_FIRST_AID, BACKGROUND_CHECK}
- State transitions: verificationStatus {pending -> verified -> revoked}; complianceStatus recomputed

## RoomRequirement
- Fields: id, siteId, roomId, requiredQualifiedCount, effectiveFrom, effectiveTo
- Validation: requiredQualifiedCount >= 0; non-overlapping active windows per room

## RoomAssignment
- Fields: id, staffId, roomId, shiftStart, shiftEnd, qualificationCountable
- Validation: shiftEnd > shiftStart

## ComplianceAlert
- Fields: id, siteId, category, severity, subjectRef, status, openedAt, resolvedAt
- State transitions: status {open -> acknowledged -> resolved}

## ComplianceSnapshot
- Fields: id, siteId, generatedAt, generatedBy, payloadHash

## ComplianceAuditEvent
- Fields: id, actorId, entityType, entityId, action, beforeJson, afterJson, at
- Validation: append-only
