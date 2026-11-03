# Implementation Plan: Staff Compliance Tracker

**Branch**: `001-staff-compliance-tracker` | **Date**: 2026-07-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-staff-compliance-tracker/spec.md`

## Summary
Deliver a Phase 1 operational compliance module that tracks staff credential expiry, room-level ratio-qualified coverage, and inspector-ready compliance snapshots. Implement as offline-first operational workflows with local cache + eventual cloud sync, Prisma-backed data modeling, and role-scoped dashboards for directors/admins.

## Technical Context

**Language/Version**: TypeScript 5.x

**Primary Dependencies**: Nx workspace modules, NestJS backend services, React Native role view, Prisma ORM, event bus (NATS or RabbitMQ)

**Storage**: PostgreSQL (regionalized) + offline local cache on client

**Testing**: Vitest/Jest unit tests, contract tests, integration tests, offline sync tests, E2E role-flow tests

**Target Platform**: Mobile/tablet role app + NestJS APIs

**Project Type**: Unified app + backend services in monorepo

**Performance Goals**: Compliance dashboard load <2s p95, alert recomputation <30s p95 after updates

**Constraints**: No AI/biometrics/edge inference; offline-first behavior; auditable change history; role-based access

**Scale/Scope**: Multi-room centre operations, thousands of staff credential events per region

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Privacy and edge-first gate: PASS (no raw video/audio/biometric transfer).
- Consent gate: PASS (no biometric processing in this feature).
- Non-diagnostic gate: PASS (administrative compliance outputs only).
- Phase gate: PASS (Phase 1 core requirement).
- Architecture gate: PASS (TypeScript + Nx + NestJS + unified app preserved).
- Regulatory gate: PASS with staff-data retention/audit controls by region.
- Business gate: PASS (operational readiness feature; no HaaS conflict).

## Project Structure

### Documentation (this feature)

```text
specs/001-staff-compliance-tracker/
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
apps/
├── mobile/                  # role-based RN app
└── admin/                   # director/admin console surfaces

services/
├── compliance-service/      # staff credentials + room ratio checks
├── attendance-service/      # dependency for room assignment context
└── audit-service/           # immutable audit trails

packages/
├── db/                      # Prisma schema + migrations
├── shared-types/
└── offline-sync/

tests/
├── contract/
├── integration/
└── e2e/
```

**Structure Decision**: Web/mobile + backend modular architecture with a dedicated compliance service and shared Prisma models.

## Complexity Tracking

No constitution violations requiring exceptions.

## Technical Architecture

- Domain module: `compliance-service` owns credential records, room requirement policies, and compliance alerts.
- Query model: director dashboard queries read from normalized credential status + room coverage projections.
- Write model: credential updates and room policy edits append immutable audit events.
- Offline-first: staff/admin clients persist local updates; sync engine reconciles by version + server-authoritative timestamp.
- Integration points: attendance/room assignment events feed room coverage recalculation; alert outputs flow to notification channels.

## Prisma Data Model Plan

- `StaffMember(id, siteId, role, employmentStatus, createdAt, updatedAt)`
- `CredentialRecord(id, staffId, type, issueDate, renewalDate, verificationStatus, complianceStatus)`
- `RoomRequirement(id, siteId, roomId, requiredQualifiedCount, effectiveFrom, effectiveTo)`
- `RoomAssignment(id, staffId, roomId, shiftStart, shiftEnd, qualificationCountable)`
- `ComplianceAlert(id, siteId, category, severity, subjectRef, status, openedAt, resolvedAt)`
- `ComplianceSnapshot(id, siteId, generatedAt, generatedBy, payloadHash)`
- `ComplianceAuditEvent(id, actorId, entityType, entityId, action, beforeJson, afterJson, at)`

## API Contracts Plan

See [contracts/api-contracts.md](./contracts/api-contracts.md).

## Dependencies

- Internal: attendance room assignment feed, identity/role service, audit service
- External: none for AI/biometric/edge hardware
- Config: warning windows, room qualification thresholds, residency/retention policy

## Testing Strategy

- Unit: credential status calculations, expiry windows, room shortfall logic
- Contract: compliance API payload schema + status transitions
- Integration: attendance assignment ingest -> room compliance recalculation
- Offline: create/update credential records offline then sync merge validation
- E2E: director workflow from dashboard to inspector summary generation
- Compliance: audit event immutability and retention-policy enforcement tests

## Post-Design Constitution Check

PASS after design:
- No AI, biometrics, or edge hardware introduced.
- Offline-first and sync explicitly designed.
- Regulatory and retention checks mapped.
- Architecture constraints preserved.
