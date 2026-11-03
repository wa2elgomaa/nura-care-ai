# Quickstart: Verified Visitor Check-In Validation

## Prerequisites
- Pickup verification core module operational
- Visitor credential issuance policy configured
- RBAC scopes assigned

## Scenario 1: Reused verification pathway
1. Check in visitor with QR/PIN.
2. Verify decision path delegates to pickup core.

## Scenario 2: Optional facial path
1. Enable explicit biometric consent for visitor.
2. Verify optional facial check uses local-only policy.

## Scenario 3: Expiry enforcement
1. Use expired visitor credential.
2. Verify denial with reason code and audit event.

## Scenario 4: Tenant/RBAC boundaries
1. Attempt cross-centre roster access without scope.
2. Verify access denied and audit captured.
