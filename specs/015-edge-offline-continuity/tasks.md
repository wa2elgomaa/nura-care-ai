# Tasks: Edge Offline Continuity

**Input**: Design documents from `/specs/015-edge-offline-continuity/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because the specification defines independent test criteria per user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize edge continuity scaffolding and test harnesses.

- [ ] T001 Create edge continuity module scaffold in services/edge-continuity-service/src/module/edge-continuity.module.ts
- [ ] T002 Create offline status API scaffold in services/edge-continuity-service/src/api/offline-status.controller.ts
- [ ] T003 [P] Create shared offline-sync DTOs and queue state enums in packages/shared-types/src/offline/offline-sync.types.ts
- [ ] T004 [P] Create edge continuity configuration module (sync cadence, retries, queue limits) in services/edge-continuity-service/src/config/edge-continuity.config.ts
- [ ] T005 [P] Create outage resilience test directories in tests/contract/offline/, tests/integration/offline/, tests/e2e/offline/, and tests/chaos/offline/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build durable local ledger, sync framework, and Keycloak fallback infrastructure for all stories.

**⚠️ CRITICAL**: No user story work starts until this phase is complete.

- [ ] T006 Add ConnectivitySession, LocalOperationRecord, DomainOutboxItem, SyncCheckpoint, ReconciliationDecision, OfflineAuditEvent, OfflineAuthAttempt, and IdentityReplicaCheckpoint models in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for offline continuity and auth fallback models in packages/db/prisma/migrations/
- [ ] T008 Implement local append-only operations ledger repository in services/edge-continuity-service/src/data/local-operations-ledger.repository.ts
- [ ] T009 Implement per-domain outbox repository and state machine in services/edge-continuity-service/src/data/domain-outbox.repository.ts
- [ ] T010 [P] Implement connectivity state monitor and transition publisher in services/edge-continuity-service/src/domain/connectivity/connectivity-monitor.service.ts
- [ ] T011 [P] Implement idempotency-key generator and replay ordering utility in packages/offline-sync/src/replay/idempotency-ordering.util.ts
- [ ] T012 Configure Edge Keycloak container runtime manifests in infra/edge/keycloak/edge-keycloak-compose.yml
- [ ] T013 Implement Cloud Keycloak to Edge replica sync adapter in services/edge-continuity-service/src/integration/keycloak/identity-replica-sync.service.ts
- [ ] T014 [P] Implement offline auth attempt logger and cloud replay publisher in services/edge-continuity-service/src/integration/keycloak/offline-auth-attempt.publisher.ts
- [ ] T015 Enforce parent cloud-only authentication policy in services/identity-service/src/domain/session/parent-cloud-auth-policy.service.ts
- [ ] T016 [P] Implement role-based access guard for offline status and sync diagnostics in services/edge-continuity-service/src/security/offline-visibility-rbac.guard.ts

**Checkpoint**: Foundation complete; user stories can proceed.

---

## Phase 3: User Story 1 - Core Operations During Outage (Priority: P1) 🎯 MVP

**Goal**: Attendance, pickup verification, and local alerts remain operational during WAN outages with staff authentication continuity.

**Independent Test**: Disable internet and verify staff can complete attendance, pickup, and local alert workflows with local confirmation and audit records.

### Tests for User Story 1

- [ ] T017 [P] [US1] Add integration tests for offline attendance capture and local visibility in tests/integration/offline/offline-attendance.integration.spec.ts
- [ ] T018 [P] [US1] Add integration tests for offline pickup verification and local confirmations in tests/integration/offline/offline-pickup.integration.spec.ts
- [ ] T019 [P] [US1] Add integration tests for Edge Keycloak local auth fallback for teacher/director in tests/integration/offline/edge-keycloak-auth-fallback.integration.spec.ts
- [ ] T020 [P] [US1] Add integration tests that parent login is rejected when cloud is unreachable in tests/integration/offline/parent-cloud-only-auth.integration.spec.ts

### Implementation for User Story 1

- [ ] T021 [P] [US1] Implement offline attendance command handler in services/attendance-service/src/offline/offline-attendance.command-handler.ts
- [ ] T022 [P] [US1] Implement offline pickup verification command handler in services/pickup-service/src/offline/offline-pickup.command-handler.ts
- [ ] T023 [P] [US1] Implement offline local alert command handler in services/safety-service/src/offline/offline-alert.command-handler.ts
- [ ] T024 [US1] Implement offline operation recorder service in services/edge-continuity-service/src/domain/operations/offline-operation-recorder.service.ts
- [ ] T025 [US1] Implement Edge Keycloak credential validation gateway for staff roles in services/identity-service/src/providers/keycloak/edge-offline-auth.gateway.ts
- [ ] T026 [US1] Implement local audit event writer for outage operations in services/audit-service/src/offline/offline-operation-audit-writer.service.ts

**Checkpoint**: US1 is independently functional and testable.

---

## Phase 4: User Story 2 - Reliable Queue and Recovery Sync (Priority: P2)

**Goal**: Outage-period operations synchronize automatically and safely when connectivity returns.

**Independent Test**: Create operations offline, restore connectivity, and verify ordered/idempotent replay with no duplicate finalized records.

### Tests for User Story 2

- [ ] T027 [P] [US2] Add contract tests for POST /api/sync/{domain}/batch in tests/contract/offline/post-sync-batch.contract.spec.ts
- [ ] T028 [P] [US2] Add contract tests for GET /api/sync/{domain}/checkpoint in tests/contract/offline/get-sync-checkpoint.contract.spec.ts
- [ ] T029 [P] [US2] Add integration tests for reconnect-triggered replay and checkpoint advancement in tests/integration/offline/reconnect-replay.integration.spec.ts
- [ ] T030 [P] [US2] Add chaos tests for connectivity flapping and duplicate replay prevention in tests/chaos/offline/connectivity-flap-replay.chaos.spec.ts

### Implementation for User Story 2

- [ ] T031 [P] [US2] Implement sync batch ingestion service with idempotent replay in services/edge-continuity-service/src/domain/sync/sync-batch-ingestion.service.ts
- [ ] T032 [US2] Implement connectivity-restored replay orchestrator in services/edge-continuity-service/src/domain/sync/reconnect-replay-orchestrator.service.ts
- [ ] T033 [US2] Implement reconciliation decision engine for conflicting offline actions in services/edge-continuity-service/src/domain/reconciliation/reconciliation-decision.engine.ts
- [ ] T034 [US2] Implement POST /api/sync/{domain}/batch endpoint in services/edge-continuity-service/src/api/sync/post-sync-batch.route.ts
- [ ] T035 [US2] Implement GET /api/sync/{domain}/checkpoint endpoint in services/edge-continuity-service/src/api/sync/get-sync-checkpoint.route.ts

**Checkpoint**: US2 is independently functional and testable.

---

## Phase 5: User Story 3 - Director Visibility and Audit Confidence (Priority: P3)

**Goal**: Directors can monitor offline state, queue backlog, and sync outcomes with complete audit confidence.

**Independent Test**: During outage and after recovery, verify dashboard shows state transitions, queue depth, sync outcomes, and unresolved exceptions.

### Tests for User Story 3

- [ ] T036 [P] [US3] Add contract tests for POST /api/offline/connectivity-events and GET /api/offline/status in tests/contract/offline/offline-status.contract.spec.ts
- [ ] T037 [P] [US3] Add integration tests for offline status timeline and unresolved exception visibility in tests/integration/offline/offline-status-visibility.integration.spec.ts
- [ ] T038 [P] [US3] Add E2E tests for director outage-to-recovery dashboard journey in tests/e2e/offline/director-outage-recovery.e2e.spec.ts

### Implementation for User Story 3

- [ ] T039 [P] [US3] Implement offline status projection service in services/edge-continuity-service/src/domain/status/offline-status-projection.service.ts
- [ ] T040 [US3] Implement sync exception workflow service for manual review paths in services/edge-continuity-service/src/domain/exceptions/sync-exception-workflow.service.ts
- [ ] T041 [US3] Implement POST /api/offline/connectivity-events endpoint in services/edge-continuity-service/src/api/offline/post-connectivity-event.route.ts
- [ ] T042 [US3] Implement GET /api/offline/status endpoint in services/edge-continuity-service/src/api/offline/get-offline-status.route.ts
- [ ] T043 [US3] Implement director offline continuity dashboard in apps/admin/src/operations/offline/OfflineContinuityDashboard.tsx

**Checkpoint**: US3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Harden outage resilience, observability, and governance validation.

- [ ] T044 [P] Add sync freshness and backlog SLO telemetry in services/edge-continuity-service/src/observability/offline-sync-health.metrics.ts
- [ ] T045 Run full quickstart outage drills including WAN disable/reconnect replay validation in specs/015-edge-offline-continuity/quickstart.md
- [ ] T046 [P] Add chaos test for prolonged outage and local queue pressure handling in tests/chaos/offline/prolonged-outage-queue-pressure.chaos.spec.ts
- [ ] T047 Validate constitution gates for edge-first continuity, Keycloak fallback, and parent cloud-only auth in specs/015-edge-offline-continuity/research.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories.
- **User Stories (Phase 3+)**: Depend on Foundational completion.
- **Polish (Phase 6)**: Depends on completion of targeted user stories.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational and delivers outage-safe core operations (MVP).
- **US2 (P2)**: Starts after Foundational and adds reliable queue replay/recovery.
- **US3 (P3)**: Starts after Foundational and adds visibility/audit confidence workflows.

### Within Each User Story

- Tests must fail before implementation.
- Repositories and low-level utilities before orchestrators.
- Domain services before API routes.
- API routes before director-facing dashboard integration.

## Parallel Opportunities

- Setup: T003-T005 can run in parallel.
- Foundational: T010-T014 and T016 can run in parallel after schema/migration baseline.
- US1: T017-T023 can run in parallel, then converge on T024-T026.
- US2: T027-T031 can run in parallel, then T032-T035.
- US3: T036-T039 can run in parallel, then T040-T043.
- Polish: T044, T046, and T047 can run in parallel.

---

## Parallel Example: User Story 2

```bash
Task: "Add contract tests for POST /api/sync/{domain}/batch in tests/contract/offline/post-sync-batch.contract.spec.ts"
Task: "Add integration tests for reconnect-triggered replay and checkpoint advancement in tests/integration/offline/reconnect-replay.integration.spec.ts"
Task: "Implement sync batch ingestion service with idempotent replay in services/edge-continuity-service/src/domain/sync/sync-batch-ingestion.service.ts"
Task: "Add chaos tests for connectivity flapping and duplicate replay prevention in tests/chaos/offline/connectivity-flap-replay.chaos.spec.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate outage continuity for attendance, pickup, and alerts.
4. Demo/deploy outage-safe operations MVP.

### Incremental Delivery

1. Deliver US1 and validate.
2. Deliver US2 and validate replay/reconciliation.
3. Deliver US3 and validate director visibility and audit outcomes.
4. Complete Polish phase and run full outage quickstart drills.

### Parallel Team Strategy

1. Team completes Setup and Foundational together.
2. After Foundational:
   - Engineer A owns US1 offline operation handlers.
   - Engineer B owns US2 sync and reconciliation engine.
   - Engineer C owns US3 status dashboard and exception workflows.
3. Integrate via chaos/E2E validation in Polish phase.
