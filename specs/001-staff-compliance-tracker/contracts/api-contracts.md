# API Contracts: Staff Compliance Tracker

## GET /api/compliance/staff
- Purpose: List staff compliance status for site
- Query: siteId, status, expiringWithinDays
- Response: staff[], paging

## PUT /api/compliance/staff/{staffId}/credentials/{credentialId}
- Purpose: Update credential dates/status
- Body: issueDate, renewalDate, verificationStatus
- Response: updated credential + recomputed complianceStatus

## GET /api/compliance/rooms/coverage
- Purpose: Room-level required vs current qualified counts
- Query: siteId, at
- Response: rooms[] with shortfall

## POST /api/compliance/snapshots
- Purpose: Generate inspector-ready summary
- Body: siteId
- Response: snapshotId, generatedAt

## GET /api/compliance/snapshots/{snapshotId}
- Purpose: Retrieve generated snapshot metadata/payload reference

## GET /api/compliance/audit-events
- Purpose: Query immutable change history
