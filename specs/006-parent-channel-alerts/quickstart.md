# Quickstart: Parent Channel Alerts Validation

## Prerequisites
- Guardian profiles and contact endpoints configured
- Event sources (daily report, billing reminder, urgent incidents) available

## Scenario 1: Preferred channel routine delivery
1. Set guardian preferred channel.
2. Trigger routine event.
3. Verify routed channel and delivery status.

## Scenario 2: Quiet-hours deferment
1. Configure quiet-hours window.
2. Trigger routine event during window.
3. Verify deferred status and release after window.

## Scenario 3: Urgent bypass and fallback
1. Trigger urgent event during quiet-hours.
2. Simulate preferred channel failure.
3. Verify fallback delivery attempts and audit trail.

## Scenario 4: Offline event capture
1. Disable network and generate routine event.
2. Reconnect and sync.
3. Verify dedupe-safe single delivery.
