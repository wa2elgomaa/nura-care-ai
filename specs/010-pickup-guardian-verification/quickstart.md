# Quickstart: Pickup Guardian Verification Validation

## Prerequisites
- Guardian authorization roster loaded
- Consent records configured for biometric optional path

## Scenario 1: Authorized QR/PIN pickup
1. Verify with QR or PIN.
2. Complete handover.
3. Confirm audit record exists.

## Scenario 2: Optional local facial verification
1. Enable consented facial path.
2. Verify local match completes.
3. Confirm no embedding egress and retention expiry set.

## Scenario 3: Unauthorized attempt
1. Attempt pickup with unauthorized guardian.
2. Confirm block + immediate alert + escalation path.
