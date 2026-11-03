# Quickstart: Teacher Pattern Insights Validation

## Prerequisites
- Observation events pipeline active
- Consent records present
- Clinical advisor account available

## Scenario 1: Rules-based flag creation
1. Run rule evaluation window.
2. Verify plain-language non-diagnostic flag generation.

## Scenario 2: Staff-only enforcement
1. Access flags as teacher/director and verify allowed.
2. Attempt parent access and verify denied.

## Scenario 3: No parent auto-send
1. Trigger new flag event.
2. Verify no parent notification artifacts are produced.

## Scenario 4: Clinical checklist gate
1. Disable advisor approval on threshold set.
2. Verify production activation is blocked.
