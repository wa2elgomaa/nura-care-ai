# Quickstart: Kiosk Illness Screening Validation

## Prerequisites
- Thermal sensor connected and calibrated
- Symptom checklist and consent flow configured

## Scenario 1: Standard screening flow
1. Start kiosk session with active consent.
2. Capture thermal and checklist inputs.
3. Verify operational outcome and rationale code.

## Scenario 2: Non-diagnostic wording enforcement
1. Inspect output content.
2. Verify no diagnosis terms are present.

## Scenario 3: Consent-missing fallback
1. Start session without active consent.
2. Verify automated capture blocks and manual process route is shown.
