# Quickstart: Quarterly Interest Profile Validation

## Prerequisites
- Activity evidence events available
- Parent consent records configured

## Scenario 1: Descriptive profile generation
1. Run quarterly generation for a child.
2. Verify output is narrative-only with no scores or labels.

## Scenario 2: Comparison guardrails
1. Inject phrase with comparative wording.
2. Verify rule engine blocks publication.

## Scenario 3: Consent revocation
1. Revoke profile consent.
2. Verify future generation is blocked.
