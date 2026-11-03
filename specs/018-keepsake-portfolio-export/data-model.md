# Data Model: Keepsake Portfolio Export

## PortfolioAsset
- Fields: id, childId, assetType, storageRef, capturedAt, approvedForExport, metadataJson

## PortfolioConsentSnapshot
- Fields: id, childId, parentId, consentState, sharePolicy, capturedAt, validUntil

## PortfolioExportRequest
- Fields: id, childId, parentId, dateRangeStart, dateRangeEnd, status, requestedAt

## PortfolioExportBundle
- Fields: id, exportRequestId, bundleRef, tokenExpiresAt, downloadCount, generatedAt

## PortfolioExportAuditEvent
- Fields: id, exportRequestId, action, actorType, payloadJson, at
