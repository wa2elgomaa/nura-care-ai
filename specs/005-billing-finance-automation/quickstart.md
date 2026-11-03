# Quickstart: Billing Finance Automation Validation

## Prerequisites
- Active family accounts and fee plans
- Subsidy/voucher policies configured
- Payment adapter test sandbox available

## Scenario 1: Invoice generation
1. Run cycle invoice generation.
2. Verify recurring + one-off lines and totals.

## Scenario 2: Subsidy/voucher application
1. Apply subsidy and voucher.
2. Verify payable amount and utilization history.

## Scenario 3: Auto-payment + receipt
1. Schedule payment attempt.
2. Simulate success.
3. Verify invoice status update and tax receipt issuance.

## Scenario 4: Failure and correction
1. Simulate payment failure.
2. Retry or apply credit note.
3. Verify complete audit trail.

## Scenario 5: Boundary compliance
1. Run Nx boundary checks.
2. Verify billing modules have no dependency on video domain.
