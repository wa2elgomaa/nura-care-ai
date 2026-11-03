# Data Model: Enrollment Compliance Backbone

## ChildComplianceProfile
- Fields: id, childId, status, completenessScore, createdAt, updatedAt
- Validation: one active profile per child

## EnrollmentFormRecord
- Fields: id, profileId, formType, status, submittedAt, reviewedAt

## MedicalAllergyRecord
- Fields: id, profileId, category, payloadJson, effectiveFrom, effectiveTo

## ImmunizationProofRecord
- Fields: id, profileId, proofType, status, validUntil

## EmergencyContactRecord
- Fields: id, profileId, name, relation, priority, phone, email
- Validation: priority unique within profile

## ConsentRecord
- Fields: id, profileId, consentType, currentState, grantedAt, revokedAt
- State transitions: unknown -> granted|denied; granted -> revoked; revoked -> granted

## ConsentAuditEvent
- Fields: id, consentRecordId, actorId, action, previousState, nextState, at

## ComplianceAuditEvent
- Fields: id, profileId, actorId, action, entityType, entityId, at
