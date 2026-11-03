# API Contracts: Edge Private Video Metadata

## POST /api/edge/metadata/events
- Purpose: ingest approved anonymized metadata from Edge Box
- Body: siteCode, eventType, zoneRef, occurredAt, confidenceBand, dedupeKey, schemaVersion, payload
- Rules: reject payloads containing media blobs, frame URIs, or embedding fields

## POST /api/edge/metadata/batch
- Purpose: offline replay sync
- Body: items[] with per-item dedupeKey
- Response: accepted[], rejected[] with reasonCode

## GET /api/edge/sites/{siteCode}/egress-policy
- Purpose: fetch signed allowlist policy

## POST /api/edge/sites/{siteCode}/health
- Purpose: heartbeat, queue depth, tamper state, TPU health
