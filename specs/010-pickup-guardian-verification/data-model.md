# Data Model: Pickup Guardian Verification

## GuardianAuthorizationRecord
- Fields: id, childId, guardianId, allowedMethodsJson, status, effectiveFrom, effectiveTo

## PickupVerificationAttempt
- Fields: id, childId, method, outcome, reasonCode, operatorId, attemptedAt

## PickupHandoverEvent
- Fields: id, childId, finalDecision, approvedGuardianId, completedAt, handoverRef

## BiometricTemplateLocalRef
- Fields: id, guardianId, localTemplateRef, createdAt, expiresAt, purgeStatus

## UnauthorizedPickupAlert
- Fields: id, childId, severity, attemptId, status, raisedAt, resolvedAt
