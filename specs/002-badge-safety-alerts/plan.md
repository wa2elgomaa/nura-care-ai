# Implementation Plan: Badge Safety Alerts

**Branch**: `002-badge-safety-alerts` | **Date**: 2026-07-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-badge-safety-alerts/spec.md`

## Summary
Build a point-of-care safety scan flow where badge/QR identity checks compare snack/medication intents against allergy and schedule metadata, return immediate go/stop outcomes, and create full operational audit trails with escalation handling.

## Technical Context

**Language/Version**: TypeScript 5.x

**Primary Dependencies**: Nx modules, NestJS APIs, React Native staff flows, Prisma, event bus

**Storage**: PostgreSQL + offline event cache

**Testing**: Unit, contract, integration, offline sync, E2E safety workflows

**Target Platform**: Teacher/tablet role views + backend safety APIs

**Project Type**: Unified app + backend domain services

**Performance Goals**: safety decision response <2s p95

**Constraints**: No AI inference; no new biometrics; deterministic safety rules; offline-capable capture

**Scale/Scope**: High-frequency daily scans at classroom level

## Constitution Check

- Privacy and edge-first gate: PASS (metadata only, no raw media transfer).
- Consent gate: PASS (operational safety metadata; consent state consumed from enrollment records).
- Non-diagnostic gate: PASS (go/stop operational alerts only).
- Phase gate: PASS (Phase 1 medication cross-check alignment).
- Architecture gate: PASS (Nx + NestJS + unified app).
- Regulatory gate: PASS with sensitive data controls and retention.
- Business gate: PASS.

## Project Structure

### Documentation (this feature)

```text
specs/002-badge-safety-alerts/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api-contracts.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/mobile/
services/
├── safety-scan-service/
├── medication-service/
├── notification-service/
└── audit-service/
packages/
├── db/
├── shared-types/
└── offline-sync/
tests/
├── contract/
├── integration/
└── e2e/
```

**Structure Decision**: Dedicated safety scan service with integrations to medication and notification modules.

## Complexity Tracking

No constitution violations requiring exceptions.

## Technical Architecture

- Scan endpoint accepts child identity token + service intent.
- Rule engine checks allergy/schedule conflicts from current metadata snapshot.
- Decision object (`SAFE`, `STOP`) returned immediately with rationale code.
- Stop events can be escalated to supervisor workflows and tracked to resolution.
- Offline-first: scan events queue locally; conflict logic uses last valid safety dataset + stale-data guard.

## Prisma Data Model Plan

- `ChildSafetyProfile(id, childId, allergyStateVersion, medicationStateVersion)`
- `AllergyRecord(id, childId, allergen, severity, effectiveFrom, effectiveTo)`
- `MedicationSchedule(id, childId, medicationCode, windowStart, windowEnd, constraintsJson)`
- `ServiceIntent(id, actorId, childId, kind, payloadJson, createdAt)`
- `SafetyScanEvent(id, childId, actorId, intentId, result, reasonCode, scannedAt, sourceMode)`
- `SafetyAlert(id, scanEventId, severity, status, assignedTo, openedAt, closedAt)`
- `SafetyResolutionNote(id, alertId, resolverId, note, createdAt)`

## API Contracts Plan

See [contracts/api-contracts.md](./contracts/api-contracts.md).

## Dependencies

- Internal: enrollment compliance records (allergy/consent), medication schedule service, notifications, audit
- External: none
- Config: dedupe window, escalation recipients, stale-data thresholds

## Testing Strategy

- Unit: allergy conflict rules, medication window checks, dedupe logic
- Contract: scan request/response schema and alert lifecycle
- Integration: scan -> alert escalation -> resolution workflow
- Offline: queued scan sync and stale data behavior
- E2E: teacher scan flows for safe vs blocked actions
- Compliance: immutable audit checks for blocked actions

## Post-Design Constitution Check

PASS after design:
- No AI/biometric/edge dependencies introduced.
- Offline continuity implemented.
- Non-diagnostic alerting preserved.
