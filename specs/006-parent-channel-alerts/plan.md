# Implementation Plan: Parent Channel Alerts

**Branch**: `006-parent-channel-alerts` | **Date**: 2026-07-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-parent-channel-alerts/spec.md`

## Summary
Deliver multi-channel parent communications (email/SMS/WhatsApp) with preference routing, quiet-hours deferment for routine messages, and immediate urgent alert bypass/fallback behavior. System must be offline-tolerant for event capture and deterministic in delivery/audit logging.

## Technical Context

**Language/Version**: TypeScript 5.x

**Primary Dependencies**: Nx modules, NestJS notification orchestration, React Native parent settings views, Prisma, queue/event bus

**Storage**: PostgreSQL + local cache for preference reads and pending message metadata

**Testing**: Unit, contract, integration, delivery simulation, offline sync tests, E2E messaging flows

**Target Platform**: Parent app surfaces + staff operational consoles

**Project Type**: Unified app + backend messaging orchestration

**Performance Goals**: urgent dispatch trigger <60s p95; routine defer/release accuracy >98%

**Constraints**: No AI/biometric/edge hardware; quiet-hours compliance; dedupe guarantees; offline-safe queueing

**Scale/Scope**: Multi-guardian, high-volume daily routine and urgent notifications

## Constitution Check

- Privacy and edge-first gate: PASS (notification metadata only).
- Consent gate: PASS (communication preference/opt-in lifecycle handled).
- Non-diagnostic gate: PASS.
- Phase gate: PASS (Phase 1 parent communication support).
- Architecture gate: PASS.
- Regulatory gate: PASS with residency and communication consent records.
- Business gate: PASS.

## Project Structure

### Documentation (this feature)

```text
specs/006-parent-channel-alerts/
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
├── notification-orchestration/
├── parent-preferences-service/
├── urgent-alert-router/
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

**Structure Decision**: Central notification orchestration with urgency-aware routing and per-guardian preference engine.

## Complexity Tracking

No constitution violations requiring exceptions.

## Technical Architecture

- Notification event ingestor tags each event with urgency and category.
- Preference resolver chooses channel endpoint and quiet-hours policy per guardian.
- Routine scheduler defers quiet-hours messages; urgent router bypasses deferment.
- Fallback chain retries urgent failures on alternate allowed channels.
- Offline-first behavior: local generation queues events for sync while preserving dedupe keys.

## Prisma Data Model Plan

- `GuardianNotificationProfile(id, guardianId, preferredChannel, quietHoursJson, optInStatesJson)`
- `NotificationEvent(id, childId, category, urgency, payloadJson, createdAt, dedupeKey)`
- `DeliveryAttempt(id, eventId, channel, endpointRef, status, attemptedAt, failureCode)`
- `DeferredQueueItem(id, eventId, releaseAt, status)`
- `UrgentRoutingRule(id, category, bypassQuietHours, fallbackChainJson, active)`
- `NotificationAuditEvent(id, eventId, action, actorType, payloadJson, at)`

## API Contracts Plan

See [contracts/api-contracts.md](./contracts/api-contracts.md).

## Dependencies

- Internal: attendance/billing/incident event sources, identity and guardian linkage, audit service
- External: channel adapters (email/SMS/WhatsApp abstractions)
- Config: quiet-hours defaults, urgent categories, fallback channel policy

## Testing Strategy

- Unit: preference resolution, urgency classification, quiet-hours window logic
- Contract: notification event and status APIs
- Integration: event source -> orchestration -> delivery/fallback
- Offline: queued events and dedupe on reconnect
- E2E: parent preference changes and urgent bypass behavior
- Compliance: consent state and residency logging checks

## Post-Design Constitution Check

PASS after design:
- No AI/biometric dependency.
- Offline-safe orchestration defined.
- Non-diagnostic messaging boundaries maintained.
