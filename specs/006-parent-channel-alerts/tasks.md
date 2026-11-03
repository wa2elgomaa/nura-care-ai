# Tasks: Parent Channel Alerts

**Input**: Design documents from `/specs/006-parent-channel-alerts/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because spec.md defines independent test criteria for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature module, contracts, and test scaffolding.

- [ ] T001 Create parent-channel-alerts service module scaffold in services/parent-channel-alerts-service/src/module/parent-channel-alerts.module.ts
- [ ] T002 Create parent-channel-alerts API controller scaffold in services/parent-channel-alerts-service/src/api/parent-channel-alerts.controller.ts
- [ ] T003 [P] Create parent-channel-alerts shared DTO and enum types in packages/shared-types/src/parent-channel-alerts/parent-channel-alerts.types.ts
- [ ] T004 [P] Create parent-channel-alerts feature configuration module in services/parent-channel-alerts-service/src/config/parent-channel-alerts.config.ts
- [ ] T005 [P] Create parent-channel-alerts test directories in tests/contract/parent-channel-alerts/, tests/integration/parent-channel-alerts/, and tests/e2e/parent-channel-alerts/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, policy, security, audit, and sync infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [ ] T006 Add GuardianNotificationProfile, NotificationEvent, DeliveryAttempt, DeferredQueueItem, UrgentRoutingRule, NotificationAuditEvent models in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for parent-channel-alerts domain models in packages/db/prisma/migrations/
- [ ] T008 [P] Implement RBAC and scope guard middleware for parent-channel-alerts routes in services/parent-channel-alerts-service/src/security/parent-channel-alerts-rbac.guard.ts
- [ ] T009 [P] Implement consent, residency, and non-diagnostic policy validator in services/parent-channel-alerts-service/src/domain/policy/parent-channel-alerts-policy-validator.service.ts
- [ ] T010 [P] Implement offline outbox and replay publisher for parent-channel-alerts events in packages/offline-sync/src/parent-channel-alerts/parent-channel-alerts.outbox.ts
- [ ] T011 [P] Implement immutable audit writer for parent-channel-alerts events in services/audit-service/src/parent-channel-alerts/parent-channel-alerts-audit-writer.service.ts
- [ ] T012 Implement deterministic parent-channel-alerts rules engine baseline in services/parent-channel-alerts-service/src/domain/rules/parent-channel-alerts-rules.service.ts

**Checkpoint**: Foundational baseline is complete; story work can proceed.

---

## Phase 3: User Story 1 - Receive Notifications on Preferred Channel (Priority: P1) 🎯 MVP

**Goal**: Deliver receive notifications on preferred channel capabilities end-to-end.

**Independent Test**: Can be tested independently by setting each available preference and verifying

### Tests for User Story 1

- [ ] T013 [P] [US1] Add contract test for PUT /api/parents/{guardianId}/notification-preferences in tests/contract/parent-channel-alerts/us1-guardiannotificationprofile.contract.spec.ts
- [ ] T014 [P] [US1] Add integration test for receive notifications on preferred channel flow in tests/integration/parent-channel-alerts/us1-deferredqueueitem.integration.spec.ts

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create GuardianNotificationProfile and DeferredQueueItem repository layer in services/parent-channel-alerts-service/src/data/us1-parent-channel-alerts.repository.ts
- [ ] T016 [US1] Implement receive notifications on preferred channel application service in services/parent-channel-alerts-service/src/domain/us1/parent-channel-alerts-us1.service.ts
- [ ] T017 [US1] Implement PUT /api/parents/{guardianId}/notification-preferences and POST /api/notifications/events/{eventId}/retry routes in services/parent-channel-alerts-service/src/api/us1/parent-channel-alerts-us1.route.ts
- [ ] T018 [US1] Implement receive notifications on preferred channel role-layout screen in apps/mobile/src/role-layouts/parent-channel-alerts/us1-parent-channel-alerts.screen.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Respect Quiet Hours for Routine Messages (Priority: P2)

**Goal**: Deliver respect quiet hours for routine messages capabilities end-to-end.

**Independent Test**: Can be tested independently by scheduling routine messages during quiet hours and

### Tests for User Story 2

- [ ] T019 [P] [US2] Add contract test for POST /api/notifications/events in tests/contract/parent-channel-alerts/us2-notificationevent.contract.spec.ts
- [ ] T020 [P] [US2] Add integration test for respect quiet hours for routine messages flow in tests/integration/parent-channel-alerts/us2-urgentroutingrule.integration.spec.ts

### Implementation for User Story 2

- [ ] T021 [P] [US2] Create NotificationEvent and UrgentRoutingRule repository layer in services/parent-channel-alerts-service/src/data/us2-parent-channel-alerts.repository.ts
- [ ] T022 [US2] Implement respect quiet hours for routine messages application service in services/parent-channel-alerts-service/src/domain/us2/parent-channel-alerts-us2.service.ts
- [ ] T023 [US2] Implement POST /api/notifications/events and GET /api/notifications/deferred routes in services/parent-channel-alerts-service/src/api/us2/parent-channel-alerts-us2.route.ts
- [ ] T024 [US2] Implement respect quiet hours for routine messages role-layout screen in apps/mobile/src/role-layouts/parent-channel-alerts/us2-parent-channel-alerts.screen.tsx

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Deliver Urgent Alerts Immediately (Priority: P3)

**Goal**: Deliver deliver urgent alerts immediately capabilities end-to-end.

**Independent Test**: Can be tested independently by triggering urgent alert types and confirming

### Tests for User Story 3

- [ ] T025 [P] [US3] Add contract test for GET /api/notifications/events/{eventId}/status in tests/contract/parent-channel-alerts/us3-deliveryattempt.contract.spec.ts
- [ ] T026 [P] [US3] Add integration test for deliver urgent alerts immediately flow in tests/integration/parent-channel-alerts/us3-notificationauditevent.integration.spec.ts

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create DeliveryAttempt and NotificationAuditEvent repository layer in services/parent-channel-alerts-service/src/data/us3-parent-channel-alerts.repository.ts
- [ ] T028 [US3] Implement deliver urgent alerts immediately application service in services/parent-channel-alerts-service/src/domain/us3/parent-channel-alerts-us3.service.ts
- [ ] T029 [US3] Implement GET /api/notifications/events/{eventId}/status and GET /api/notifications/events/{eventId}/status routes in services/parent-channel-alerts-service/src/api/us3/parent-channel-alerts-us3.route.ts
- [ ] T030 [US3] Implement deliver urgent alerts immediately role-layout screen in apps/mobile/src/role-layouts/parent-channel-alerts/us3-parent-channel-alerts.screen.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, governance validation, and operational readiness across stories.

- [ ] T031 [P] Add parent-channel-alerts performance and reliability metrics in services/parent-channel-alerts-service/src/observability/parent-channel-alerts.metrics.ts
- [ ] T032 Run parent-channel-alerts quickstart validation scenarios in specs/006-parent-channel-alerts/quickstart.md
- [ ] T033 [P] Add end-to-end cross-story regression suite in tests/e2e/parent-channel-alerts/parent-channel-alerts-workflow.e2e.spec.ts
- [ ] T034 Validate constitution gates (privacy, consent, phase sequencing, non-diagnostic) for parent-channel-alerts in specs/006-parent-channel-alerts/research.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all stories.
- **User Story Phases (Phase 3+)**: Depend on Foundational completion.
- **Polish (Phase 6)**: Depends on completion of all target user stories.

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational; independently testable via stated acceptance criteria.
- **US2 (P2)**: Can start after Foundational; independently testable via stated acceptance criteria.
- **US3 (P3)**: Can start after Foundational; independently testable via stated acceptance criteria.

### Within Each User Story

- Contract/integration tests before implementation.
- Repository/data tasks before domain services.
- Domain services before API routes and UI integration.

## Parallel Opportunities

- All tasks marked `[P]` are parallelizable by design.
- Setup and Foundational `[P]` tasks can run in parallel after schema baseline is agreed.
- Within each user story, contract tests and repository creation can run in parallel.
- Different user stories can be staffed in parallel after Foundational completion.

## Parallel Example: User Story 1

```bash
Task: "Add contract test for PUT /api/parents/{guardianId}/notification-preferences in tests/contract/parent-channel-alerts/us1-guardiannotificationprofile.contract.spec.ts"
Task: "Add integration test for receive notifications on preferred channel flow in tests/integration/parent-channel-alerts/us1-deferredqueueitem.integration.spec.ts"
Task: "Create GuardianNotificationProfile and DeferredQueueItem repository layer in services/parent-channel-alerts-service/src/data/us1-parent-channel-alerts.repository.ts"
```

---

## Parallel Example: User Story 2

```bash
Task: "Add contract test for POST /api/notifications/events in tests/contract/parent-channel-alerts/us2-notificationevent.contract.spec.ts"
Task: "Add integration test for respect quiet hours for routine messages flow in tests/integration/parent-channel-alerts/us2-urgentroutingrule.integration.spec.ts"
Task: "Create NotificationEvent and UrgentRoutingRule repository layer in services/parent-channel-alerts-service/src/data/us2-parent-channel-alerts.repository.ts"
```

---

## Parallel Example: User Story 3

```bash
Task: "Add contract test for GET /api/notifications/events/{eventId}/status in tests/contract/parent-channel-alerts/us3-deliveryattempt.contract.spec.ts"
Task: "Add integration test for deliver urgent alerts immediately flow in tests/integration/parent-channel-alerts/us3-notificationauditevent.integration.spec.ts"
Task: "Create DeliveryAttempt and NotificationAuditEvent repository layer in services/parent-channel-alerts-service/src/data/us3-parent-channel-alerts.repository.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup).
2. Complete Phase 2 (Foundational).
3. Complete User Story 1 implementation and tests.
4. Validate User Story 1 independently before expanding scope.

### Incremental Delivery

1. Deliver US1 (MVP) and validate.
2. Deliver US2, validate independently, and integrate without regressing earlier stories.
3. Deliver US3, validate independently, and integrate without regressing earlier stories.
4. Complete Polish phase and rerun quickstart scenarios.

### Parallel Team Strategy

1. Team completes Setup and Foundational collaboratively.
2. After Foundational, assign user stories to separate engineers for parallel delivery.
3. Merge in Polish phase with E2E and governance validation.
