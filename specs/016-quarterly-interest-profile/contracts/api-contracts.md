# API Contracts: Quarterly Interest Profile

## POST /api/interest-profiles/generate
- Body: childId, quarterKey
- Preconditions: active opt-in consent
- Response: draftId, status

## GET /api/interest-profiles/{draftId}
- Response: descriptive narrative sections only (no scores)

## POST /api/interest-profiles/{draftId}/publish
- Preconditions: rules engine pass + advisor-approved phrase set active

## POST /api/interest-profiles/consent
- Body: childId, parentId, consentState, scope
