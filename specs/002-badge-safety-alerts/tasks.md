# Tasks: Badge Safety Alerts

**Input**: Design documents from `/specs/002-badge-safety-alerts/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because spec.md defines independent test criteria for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature module, contracts, and test scaffolding.

- [ ] T001 Create badge-safety-alerts service module scaffold in services/badge-safety-alerts-service/src/module/badge-safety-alerts.module.ts
- [ ] T002 Create badge-safety-alerts API controller scaffold in services/badge-safety-alerts-service/src/api/badge-safety-alerts.controller.ts
- [ ] T003 [P] Create badge-safety-alerts shared DTO and enum types in packages/shared-types/src/badge-safety-alerts/badge-safety-alerts.types.ts
- [ ] T004 [P] Create badge-safety-alerts feature configuration module in services/badge-safety-alerts-service/src/config/badge-safety-alerts.config.ts
- [ ] T005 [P] Create badge-safety-alerts test directories in tests/contract/badge-safety-alerts/, tests/integration/badge-safety-alerts/, and tests/e2e/badge-safety-alerts/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, policy, security, audit, and sync infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [ ] T006 Add ChildSafetyProfile, AllergyRecord, MedicationSchedule, ServiceIntent, SafetyScanEvent, SafetyAlert, SafetyResolutionNote models in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for badge-safety-alerts domain models in packages/db/prisma/migrations/
- [ ] T008 [P] Implement RBAC and scope guard middleware for badge-safety-alerts routes in services/badge-safety-alerts-service/src/security/badge-safety-alerts-rbac.guard.ts
- [ ] T009 [P] Implement consent, residency, and non-diagnostic policy validator in services/badge-safety-alerts-service/src/domain/policy/badge-safety-alerts-policy-validator.service.ts
- [ ] T010 [P] Implement offline outbox and replay publisher for badge-safety-alerts events in packages/offline-sync/src/badge-safety-alerts/badge-safety-alerts.outbox.ts
- [ ] T011 [P] Implement immutable audit writer for badge-safety-alerts events in services/audit-service/src/badge-safety-alerts/badge-safety-alerts-audit-writer.service.ts
- [ ] T012 Implement deterministic badge-safety-alerts rules engine baseline in services/badge-safety-alerts-service/src/domain/rules/badge-safety-alerts-rules.service.ts

**Checkpoint**: Foundational baseline is complete; story work can proceed.

---

## Phase 3: User Story 1 - Scan Child Before Serving (Priority: P1) 🎯 MVP

**Goal**: Deliver scan child before serving capabilities end-to-end.

**Independent Test**: Can be tested independently by scanning children with safe and unsafe profiles

### Tests for User Story 1

- [ ] T013 [P] [US1] Add contract test for POST /api/safety-scans/evaluate in tests/contract/badge-safety-alerts/us1-childsafetyprofile.contract.spec.ts
- [ ] T014 [P] [US1] Add integration test for scan child before serving flow in tests/integration/badge-safety-alerts/us1-serviceintent.integration.spec.ts

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create ChildSafetyProfile and ServiceIntent and SafetyResolutionNote repository layer in services/badge-safety-alerts-service/src/data/us1-badge-safety-alerts.repository.ts
- [ ] T016 [US1] Implement scan child before serving application service in services/badge-safety-alerts-service/src/domain/us1/badge-safety-alerts-us1.service.ts
- [ ] T017 [US1] Implement POST /api/safety-scans/evaluate and GET /api/safety-scans/history routes in services/badge-safety-alerts-service/src/api/us1/badge-safety-alerts-us1.route.ts
- [ ] T018 [US1] Implement scan child before serving role-layout screen in apps/mobile/src/role-layouts/badge-safety-alerts/us1-badge-safety-alerts.screen.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Capture Safety Decision Evidence (Priority: P2)

**Goal**: Deliver capture safety decision evidence capabilities end-to-end.

**Independent Test**: Can be tested independently by performing scans and verifying each scan outcome,

### Tests for User Story 2

- [ ] T019 [P] [US2] Add contract test for POST /api/safety-scans/{scanEventId}/escalate in tests/contract/badge-safety-alerts/us2-allergyrecord.contract.spec.ts
- [ ] T020 [P] [US2] Add integration test for capture safety decision evidence flow in tests/integration/badge-safety-alerts/us2-safetyscanevent.integration.spec.ts

### Implementation for User Story 2

- [ ] T021 [P] [US2] Create AllergyRecord and SafetyScanEvent repository layer in services/badge-safety-alerts-service/src/data/us2-badge-safety-alerts.repository.ts
- [ ] T022 [US2] Implement capture safety decision evidence application service in services/badge-safety-alerts-service/src/domain/us2/badge-safety-alerts-us2.service.ts
- [ ] T023 [US2] Implement POST /api/safety-scans/{scanEventId}/escalate and GET /api/safety-alerts/open routes in services/badge-safety-alerts-service/src/api/us2/badge-safety-alerts-us2.route.ts
- [ ] T024 [US2] Implement capture safety decision evidence role-layout screen in apps/mobile/src/role-layouts/badge-safety-alerts/us2-badge-safety-alerts.screen.tsx

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Escalate and Resolve Safety Alerts (Priority: P3)

**Goal**: Deliver escalate and resolve safety alerts capabilities end-to-end.

**Independent Test**: Can be tested independently by triggering alerts, escalating them, and verifying

### Tests for User Story 3

- [ ] T025 [P] [US3] Add contract test for POST /api/safety-alerts/{alertId}/resolve in tests/contract/badge-safety-alerts/us3-medicationschedule.contract.spec.ts
- [ ] T026 [P] [US3] Add integration test for escalate and resolve safety alerts flow in tests/integration/badge-safety-alerts/us3-safetyalert.integration.spec.ts

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create MedicationSchedule and SafetyAlert repository layer in services/badge-safety-alerts-service/src/data/us3-badge-safety-alerts.repository.ts
- [ ] T028 [US3] Implement escalate and resolve safety alerts application service in services/badge-safety-alerts-service/src/domain/us3/badge-safety-alerts-us3.service.ts
- [ ] T029 [US3] Implement POST /api/safety-alerts/{alertId}/resolve and POST /api/safety-alerts/{alertId}/resolve routes in services/badge-safety-alerts-service/src/api/us3/badge-safety-alerts-us3.route.ts
- [ ] T030 [US3] Implement escalate and resolve safety alerts role-layout screen in apps/mobile/src/role-layouts/badge-safety-alerts/us3-badge-safety-alerts.screen.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, governance validation, and operational readiness across stories.

- [ ] T031 [P] Add badge-safety-alerts performance and reliability metrics in services/badge-safety-alerts-service/src/observability/badge-safety-alerts.metrics.ts
- [ ] T032 Run badge-safety-alerts quickstart validation scenarios in specs/002-badge-safety-alerts/quickstart.md
- [ ] T033 [P] Add end-to-end cross-story regression suite in tests/e2e/badge-safety-alerts/badge-safety-alerts-workflow.e2e.spec.ts
- [ ] T034 Validate constitution gates (privacy, consent, phase sequencing, non-diagnostic) for badge-safety-alerts in specs/002-badge-safety-alerts/research.md

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
Task: "Add contract test for POST /api/safety-scans/evaluate in tests/contract/badge-safety-alerts/us1-childsafetyprofile.contract.spec.ts"
Task: "Add integration test for scan child before serving flow in tests/integration/badge-safety-alerts/us1-serviceintent.integration.spec.ts"
Task: "Create ChildSafetyProfile and ServiceIntent and SafetyResolutionNote repository layer in services/badge-safety-alerts-service/src/data/us1-badge-safety-alerts.repository.ts"
```

---

## Parallel Example: User Story 2

```bash
Task: "Add contract test for POST /api/safety-scans/{scanEventId}/escalate in tests/contract/badge-safety-alerts/us2-allergyrecord.contract.spec.ts"
Task: "Add integration test for capture safety decision evidence flow in tests/integration/badge-safety-alerts/us2-safetyscanevent.integration.spec.ts"
Task: "Create AllergyRecord and SafetyScanEvent repository layer in services/badge-safety-alerts-service/src/data/us2-badge-safety-alerts.repository.ts"
```

---

## Parallel Example: User Story 3

```bash
Task: "Add contract test for POST /api/safety-alerts/{alertId}/resolve in tests/contract/badge-safety-alerts/us3-medicationschedule.contract.spec.ts"
Task: "Add integration test for escalate and resolve safety alerts flow in tests/integration/badge-safety-alerts/us3-safetyalert.integration.spec.ts"
Task: "Create MedicationSchedule and SafetyAlert repository layer in services/badge-safety-alerts-service/src/data/us3-badge-safety-alerts.repository.ts"
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
