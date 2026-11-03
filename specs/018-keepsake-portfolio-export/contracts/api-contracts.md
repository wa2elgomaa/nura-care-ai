# API Contracts: Keepsake Portfolio Export

## POST /api/portfolio/exports
- Body: childId, dateRangeStart, dateRangeEnd, templateId
- Preconditions: parent authorized for child + active consent

## GET /api/portfolio/exports/{exportId}
- Response: status, bundleToken (if ready)

## POST /api/portfolio/exports/{exportId}/download
- Body: bundleToken
- Response: signedDownloadUrl

## POST /api/portfolio/consent
- Body: childId, parentId, consentState, sharePolicy
