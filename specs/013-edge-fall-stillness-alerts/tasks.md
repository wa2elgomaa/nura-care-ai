# Tasks: Edge Fall Stillness Alerts

**Input**: Design documents from `/specs/013-edge-fall-stillness-alerts/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because spec.md defines independent test criteria for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature module, contracts, and test scaffolding.

- [ ] T001 Create edge-fall-stillness-alerts service module scaffold in services/edge-fall-stillness-alerts-service/src/module/edge-fall-stillness-alerts.module.ts
- [ ] T002 Create edge-fall-stillness-alerts API controller scaffold in services/edge-fall-stillness-alerts-service/src/api/edge-fall-stillness-alerts.controller.ts
- [ ] T003 [P] Create edge-fall-stillness-alerts shared DTO and enum types in packages/shared-types/src/edge-fall-stillness-alerts/edge-fall-stillness-alerts.types.ts
- [ ] T004 [P] Create edge-fall-stillness-alerts feature configuration module in services/edge-fall-stillness-alerts-service/src/config/edge-fall-stillness-alerts.config.ts
- [ ] T005 [P] Create edge-fall-stillness-alerts test directories in tests/contract/edge-fall-stillness-alerts/, tests/integration/edge-fall-stillness-alerts/, and tests/e2e/edge-fall-stillness-alerts/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, policy, security, audit, and sync infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [ ] T006 Add PoseSafetyEvent, FallStillnessPolicy, SafetyAlert, AlertEscalation, SafetyIncidentAudit models in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for edge-fall-stillness-alerts domain models in packages/db/prisma/migrations/
- [ ] T008 [P] Implement RBAC and scope guard middleware for edge-fall-stillness-alerts routes in services/edge-fall-stillness-alerts-service/src/security/edge-fall-stillness-alerts-rbac.guard.ts
- [ ] T009 [P] Implement consent, residency, and non-diagnostic policy validator in services/edge-fall-stillness-alerts-service/src/domain/policy/edge-fall-stillness-alerts-policy-validator.service.ts
- [ ] T010 [P] Implement offline outbox and replay publisher for edge-fall-stillness-alerts events in packages/offline-sync/src/edge-fall-stillness-alerts/edge-fall-stillness-alerts.outbox.ts
- [ ] T011 [P] Implement immutable audit writer for edge-fall-stillness-alerts events in services/audit-service/src/edge-fall-stillness-alerts/edge-fall-stillness-alerts-audit-writer.service.ts
- [ ] T012 Implement deterministic edge-fall-stillness-alerts rules engine baseline in services/edge-fall-stillness-alerts-service/src/domain/rules/edge-fall-stillness-alerts-rules.service.ts

**Checkpoint**: Foundational baseline is complete; story work can proceed.

---

## Phase 3: User Story 1 - Immediate Fall and Stillness Detection (Priority: P1) 🎯 MVP

**Goal**: Deliver immediate fall and stillness detection capabilities end-to-end.

**Independent Test**: Can be tested independently by simulating fall and stillness scenarios and

### Tests for User Story 1

- [ ] T013 [P] [US1] Add contract test for POST /api/safety/fall-stillness/events in tests/contract/edge-fall-stillness-alerts/us1-posesafetyevent.contract.spec.ts
- [ ] T014 [P] [US1] Add integration test for immediate fall and stillness detection flow in tests/integration/edge-fall-stillness-alerts/us1-alertescalation.integration.spec.ts

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create PoseSafetyEvent and AlertEscalation repository layer in services/edge-fall-stillness-alerts-service/src/data/us1-edge-fall-stillness-alerts.repository.ts
- [ ] T016 [US1] Implement immediate fall and stillness detection application service in services/edge-fall-stillness-alerts-service/src/domain/us1/edge-fall-stillness-alerts-us1.service.ts
- [ ] T017 [US1] Implement POST /api/safety/fall-stillness/events and GET /api/safety/alerts routes in services/edge-fall-stillness-alerts-service/src/api/us1/edge-fall-stillness-alerts-us1.route.ts
- [ ] T018 [US1] Implement immediate fall and stillness detection role-layout screen in apps/mobile/src/role-layouts/edge-fall-stillness-alerts/us1-edge-fall-stillness-alerts.screen.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Contextual Alert Routing and Acknowledgement (Priority: P2)

**Goal**: Deliver contextual alert routing and acknowledgement capabilities end-to-end.

**Independent Test**: Can be tested independently by issuing alerts, acknowledging from tablets, and

### Tests for User Story 2

- [ ] T019 [P] [US2] Add contract test for POST /api/safety/alerts/{alertId}/ack in tests/contract/edge-fall-stillness-alerts/us2-fallstillnesspolicy.contract.spec.ts
- [ ] T020 [P] [US2] Add integration test for contextual alert routing and acknowledgement flow in tests/integration/edge-fall-stillness-alerts/us2-safetyincidentaudit.integration.spec.ts

### Implementation for User Story 2

- [ ] T021 [P] [US2] Create FallStillnessPolicy and SafetyIncidentAudit repository layer in services/edge-fall-stillness-alerts-service/src/data/us2-edge-fall-stillness-alerts.repository.ts
- [ ] T022 [US2] Implement contextual alert routing and acknowledgement application service in services/edge-fall-stillness-alerts-service/src/domain/us2/edge-fall-stillness-alerts-us2.service.ts
- [ ] T023 [US2] Implement POST /api/safety/alerts/{alertId}/ack and POST /api/safety/alerts/{alertId}/ack routes in services/edge-fall-stillness-alerts-service/src/api/us2/edge-fall-stillness-alerts-us2.route.ts
- [ ] T024 [US2] Implement contextual alert routing and acknowledgement role-layout screen in apps/mobile/src/role-layouts/edge-fall-stillness-alerts/us2-edge-fall-stillness-alerts.screen.tsx

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Safety Incident Audit and Review (Priority: P3)

**Goal**: Deliver safety incident audit and review capabilities end-to-end.

**Independent Test**: Can be tested independently by reviewing completed alert incidents and confirming

### Tests for User Story 3

- [ ] T025 [P] [US3] Add contract test for POST /api/safety/alerts/{alertId}/resolve in tests/contract/edge-fall-stillness-alerts/us3-safetyalert.contract.spec.ts
- [ ] T026 [P] [US3] Add integration test for safety incident audit and review flow in tests/integration/edge-fall-stillness-alerts/us3-safetyalert.integration.spec.ts

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create SafetyAlert repository layer in services/edge-fall-stillness-alerts-service/src/data/us3-edge-fall-stillness-alerts.repository.ts
- [ ] T028 [US3] Implement safety incident audit and review application service in services/edge-fall-stillness-alerts-service/src/domain/us3/edge-fall-stillness-alerts-us3.service.ts
- [ ] T029 [US3] Implement POST /api/safety/alerts/{alertId}/resolve and POST /api/safety/alerts/{alertId}/resolve routes in services/edge-fall-stillness-alerts-service/src/api/us3/edge-fall-stillness-alerts-us3.route.ts
- [ ] T030 [US3] Implement safety incident audit and review role-layout screen in apps/mobile/src/role-layouts/edge-fall-stillness-alerts/us3-edge-fall-stillness-alerts.screen.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, governance validation, and operational readiness across stories.

- [ ] T031 [P] Add edge-fall-stillness-alerts performance and reliability metrics in services/edge-fall-stillness-alerts-service/src/observability/edge-fall-stillness-alerts.metrics.ts
- [ ] T032 Run edge-fall-stillness-alerts quickstart validation scenarios in specs/013-edge-fall-stillness-alerts/quickstart.md
- [ ] T033 [P] Add end-to-end cross-story regression suite in tests/e2e/edge-fall-stillness-alerts/edge-fall-stillness-alerts-workflow.e2e.spec.ts
- [ ] T034 Validate constitution gates (privacy, consent, phase sequencing, non-diagnostic) for edge-fall-stillness-alerts in specs/013-edge-fall-stillness-alerts/research.md

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
Task: "Add contract test for POST /api/safety/fall-stillness/events in tests/contract/edge-fall-stillness-alerts/us1-posesafetyevent.contract.spec.ts"
Task: "Add integration test for immediate fall and stillness detection flow in tests/integration/edge-fall-stillness-alerts/us1-alertescalation.integration.spec.ts"
Task: "Create PoseSafetyEvent and AlertEscalation repository layer in services/edge-fall-stillness-alerts-service/src/data/us1-edge-fall-stillness-alerts.repository.ts"
```

---

## Parallel Example: User Story 2

```bash
Task: "Add contract test for POST /api/safety/alerts/{alertId}/ack in tests/contract/edge-fall-stillness-alerts/us2-fallstillnesspolicy.contract.spec.ts"
Task: "Add integration test for contextual alert routing and acknowledgement flow in tests/integration/edge-fall-stillness-alerts/us2-safetyincidentaudit.integration.spec.ts"
Task: "Create FallStillnessPolicy and SafetyIncidentAudit repository layer in services/edge-fall-stillness-alerts-service/src/data/us2-edge-fall-stillness-alerts.repository.ts"
```

---

## Parallel Example: User Story 3

```bash
Task: "Add contract test for POST /api/safety/alerts/{alertId}/resolve in tests/contract/edge-fall-stillness-alerts/us3-safetyalert.contract.spec.ts"
Task: "Add integration test for safety incident audit and review flow in tests/integration/edge-fall-stillness-alerts/us3-safetyalert.integration.spec.ts"
Task: "Create SafetyAlert repository layer in services/edge-fall-stillness-alerts-service/src/data/us3-edge-fall-stillness-alerts.repository.ts"
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
