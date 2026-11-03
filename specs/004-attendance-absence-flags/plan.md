# Implementation Plan: Attendance and Absence Flags

**Branch**: `004-attendance-absence-flags` | **Date**: 2026-07-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-attendance-absence-flags/spec.md`

## Summary
Build a multi-input attendance capture system (badge, QR, kiosk) with automatic unexplained-absence flagging, follow-up tracking, and live ratio-ready rolls. Design remains offline-first and deterministic, with auditable follow-up history.

## Technical Context

**Language/Version**: TypeScript 5.x

**Primary Dependencies**: Nx modules, NestJS attendance service, React Native staff flows, Prisma, event bus

**Storage**: PostgreSQL + local offline cache

**Testing**: Unit, contract, integration, offline sync, E2E attendance/follow-up flows

**Target Platform**: Teacher/director role surfaces

**Project Type**: Unified app + backend services

**Performance Goals**: check-in state propagation <3s p95, threshold flag trigger <2m after breach

**Constraints**: No AI/biometrics required; offline-first; deterministic thresholding; auditable events

**Scale/Scope**: Daily high-volume attendance across classrooms

## Constitution Check

- Privacy and edge-first gate: PASS (operational metadata only).
- Consent gate: PASS (non-biometric attendance paths available and default).
- Non-diagnostic gate: PASS.
- Phase gate: PASS (Phase 1 core attendance requirement).
- Architecture gate: PASS.
- Regulatory gate: PASS with residency/retention controls.
- Business gate: PASS.

## Project Structure

### Documentation (this feature)

```text
specs/004-attendance-absence-flags/
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
├── attendance-service/
├── roster-service/
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

**Structure Decision**: Dedicated attendance service with threshold policy engine and follow-up queue integration.

## Complexity Tracking

No constitution violations requiring exceptions.

## Technical Architecture

- Event ingestion supports badge/QR/kiosk input adapters -> normalized attendance event.
- Attendance state projector computes per-child current status and classroom live roll.
- Threshold policy engine creates unexplained-absence flags for expected roster gaps.
- Follow-up workflow tracks outreach outcomes and resolves flags.
- Offline-first queue persists check-in/out locally and reconciles with idempotent sync keys.

## Prisma Data Model Plan

- `ChildDailyAttendance(id, childId, dateLocal, currentState, lastEventAt, roomId)`
- `AttendanceEvent(id, childId, type, method, actorId, occurredAt, clientEventId)`
- `AbsenceReason(id, childId, dateLocal, reasonCode, submittedBy, submittedAt)`
- `AbsenceThresholdPolicy(id, siteId, roomId, cutoffLocalTime, graceMinutes, active)`
- `UnexplainedAbsenceFlag(id, childId, dateLocal, status, openedAt, resolvedAt, ownerId)`
- `FollowUpAction(id, flagId, actorId, outcomeCode, note, createdAt)`

## API Contracts Plan

See [contracts/api-contracts.md](./contracts/api-contracts.md).

## Dependencies

- Internal: enrollment roster feed, parent notification channels, audit service
- External: none
- Config: threshold policies, dedupe intervals, follow-up SLA targets

## Testing Strategy

- Unit: event dedupe, threshold calculation, state projection
- Contract: attendance event ingestion + unresolved queue APIs
- Integration: absence flag generation and resolution lifecycle
- Offline: local check-in/out replay and duplicate prevention
- E2E: teacher arrival flows and director unresolved absence follow-up
- Compliance: audit retention and role-based visibility tests

## Post-Design Constitution Check

PASS after design:
- No AI or biometric dependency required.
- Offline-first continuity covered.
- Operational non-diagnostic outputs only.
