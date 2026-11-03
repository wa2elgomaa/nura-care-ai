# API Contracts: Enrollment Compliance Backbone

## POST /api/compliance/children/{childId}/profiles
- Purpose: Create compliance profile

## GET /api/compliance/children/{childId}/profiles/current
- Purpose: Retrieve consolidated compliance workspace

## PUT /api/compliance/children/{childId}/documents/{documentId}
- Purpose: Upsert document metadata/status

## POST /api/compliance/children/{childId}/consents
- Body: consentType, decision, evidenceRef
- Purpose: Create consent lifecycle event and update current state

## GET /api/compliance/children/{childId}/consents/history
- Purpose: Retrieve consent timeline

## GET /api/compliance/reports/completeness
- Query: siteId, status
- Purpose: Cross-child completeness monitoring
