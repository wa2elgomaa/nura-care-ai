# Tasks: BLE Zone Headcount

**Input**: Design documents from `/specs/011-ble-zone-headcount/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because spec.md defines independent test criteria for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature module, contracts, and test scaffolding.

- [ ] T001 Create ble-zone-headcount service module scaffold in services/ble-zone-headcount-service/src/module/ble-zone-headcount.module.ts
- [ ] T002 Create ble-zone-headcount API controller scaffold in services/ble-zone-headcount-service/src/api/ble-zone-headcount.controller.ts
- [ ] T003 [P] Create ble-zone-headcount shared DTO and enum types in packages/shared-types/src/ble-zone-headcount/ble-zone-headcount.types.ts
- [ ] T004 [P] Create ble-zone-headcount feature configuration module in services/ble-zone-headcount-service/src/config/ble-zone-headcount.config.ts
- [ ] T005 [P] Create ble-zone-headcount test directories in tests/contract/ble-zone-headcount/, tests/integration/ble-zone-headcount/, and tests/e2e/ble-zone-headcount/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, policy, security, audit, and sync infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [ ] T006 Add ChildBadgeAssignment, StaffPanicBadge, ZoneGateway, ZonePresenceState, RatioComplianceState, ZoneSafetyAlert models in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for ble-zone-headcount domain models in packages/db/prisma/migrations/
- [ ] T008 [P] Implement RBAC and scope guard middleware for ble-zone-headcount routes in services/ble-zone-headcount-service/src/security/ble-zone-headcount-rbac.guard.ts
- [ ] T009 [P] Implement consent, residency, and non-diagnostic policy validator in services/ble-zone-headcount-service/src/domain/policy/ble-zone-headcount-policy-validator.service.ts
- [ ] T010 [P] Implement offline outbox and replay publisher for ble-zone-headcount events in packages/offline-sync/src/ble-zone-headcount/ble-zone-headcount.outbox.ts
- [ ] T011 [P] Implement immutable audit writer for ble-zone-headcount events in services/audit-service/src/ble-zone-headcount/ble-zone-headcount-audit-writer.service.ts
- [ ] T012 Implement deterministic ble-zone-headcount rules engine baseline in services/ble-zone-headcount-service/src/domain/rules/ble-zone-headcount-rules.service.ts

**Checkpoint**: Foundational baseline is complete; story work can proceed.

---

## Phase 3: User Story 1 - Live Room Headcount from BLE Presence (Priority: P1) 🎯 MVP

**Goal**: Deliver live room headcount from ble presence capabilities end-to-end.

**Independent Test**: Can be tested independently by assigning badges, moving children between zones,

### Tests for User Story 1

- [ ] T013 [P] [US1] Add contract test for POST /api/ble/gateway-events in tests/contract/ble-zone-headcount/us1-childbadgeassignment.contract.spec.ts
- [ ] T014 [P] [US1] Add integration test for live room headcount from ble presence flow in tests/integration/ble-zone-headcount/us1-zonepresencestate.integration.spec.ts

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create ChildBadgeAssignment and ZonePresenceState repository layer in services/ble-zone-headcount-service/src/data/us1-ble-zone-headcount.repository.ts
- [ ] T016 [US1] Implement live room headcount from ble presence application service in services/ble-zone-headcount-service/src/domain/us1/ble-zone-headcount-us1.service.ts
- [ ] T017 [US1] Implement POST /api/ble/gateway-events and POST /api/panic/trigger routes in services/ble-zone-headcount-service/src/api/us1/ble-zone-headcount-us1.route.ts
- [ ] T018 [US1] Implement live room headcount from ble presence role-layout screen in apps/mobile/src/role-layouts/ble-zone-headcount/us1-ble-zone-headcount.screen.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Restricted Area Safety Alerts (Priority: P2)

**Goal**: Deliver restricted area safety alerts capabilities end-to-end.

**Independent Test**: Can be tested independently by defining restricted zones and simulating child

### Tests for User Story 2

- [ ] T019 [P] [US2] Add contract test for GET /api/occupancy/zones in tests/contract/ble-zone-headcount/us2-staffpanicbadge.contract.spec.ts
- [ ] T020 [P] [US2] Add integration test for restricted area safety alerts flow in tests/integration/ble-zone-headcount/us2-ratiocompliancestate.integration.spec.ts

### Implementation for User Story 2

- [ ] T021 [P] [US2] Create StaffPanicBadge and RatioComplianceState repository layer in services/ble-zone-headcount-service/src/data/us2-ble-zone-headcount.repository.ts
- [ ] T022 [US2] Implement restricted area safety alerts application service in services/ble-zone-headcount-service/src/domain/us2/ble-zone-headcount-us2.service.ts
- [ ] T023 [US2] Implement GET /api/occupancy/zones and GET /api/occupancy/zones routes in services/ble-zone-headcount-service/src/api/us2/ble-zone-headcount-us2.route.ts
- [ ] T024 [US2] Implement restricted area safety alerts role-layout screen in apps/mobile/src/role-layouts/ble-zone-headcount/us2-ble-zone-headcount.screen.tsx

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Automatic Staff-to-Child Ratio Verification (Priority: P3)

**Goal**: Deliver automatic staff-to-child ratio verification capabilities end-to-end.

**Independent Test**: Can be tested independently by adjusting room occupancy and staff assignments and

### Tests for User Story 3

- [ ] T025 [P] [US3] Add contract test for POST /api/occupancy/alerts/{alertId}/ack in tests/contract/ble-zone-headcount/us3-zonegateway.contract.spec.ts
- [ ] T026 [P] [US3] Add integration test for automatic staff-to-child ratio verification flow in tests/integration/ble-zone-headcount/us3-zonesafetyalert.integration.spec.ts

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create ZoneGateway and ZoneSafetyAlert repository layer in services/ble-zone-headcount-service/src/data/us3-ble-zone-headcount.repository.ts
- [ ] T028 [US3] Implement automatic staff-to-child ratio verification application service in services/ble-zone-headcount-service/src/domain/us3/ble-zone-headcount-us3.service.ts
- [ ] T029 [US3] Implement POST /api/occupancy/alerts/{alertId}/ack and POST /api/occupancy/alerts/{alertId}/ack routes in services/ble-zone-headcount-service/src/api/us3/ble-zone-headcount-us3.route.ts
- [ ] T030 [US3] Implement automatic staff-to-child ratio verification role-layout screen in apps/mobile/src/role-layouts/ble-zone-headcount/us3-ble-zone-headcount.screen.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, governance validation, and operational readiness across stories.

- [ ] T031 [P] Add ble-zone-headcount performance and reliability metrics in services/ble-zone-headcount-service/src/observability/ble-zone-headcount.metrics.ts
- [ ] T032 Run ble-zone-headcount quickstart validation scenarios in specs/011-ble-zone-headcount/quickstart.md
- [ ] T033 [P] Add end-to-end cross-story regression suite in tests/e2e/ble-zone-headcount/ble-zone-headcount-workflow.e2e.spec.ts
- [ ] T034 Validate constitution gates (privacy, consent, phase sequencing, non-diagnostic) for ble-zone-headcount in specs/011-ble-zone-headcount/research.md

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
Task: "Add contract test for POST /api/ble/gateway-events in tests/contract/ble-zone-headcount/us1-childbadgeassignment.contract.spec.ts"
Task: "Add integration test for live room headcount from ble presence flow in tests/integration/ble-zone-headcount/us1-zonepresencestate.integration.spec.ts"
Task: "Create ChildBadgeAssignment and ZonePresenceState repository layer in services/ble-zone-headcount-service/src/data/us1-ble-zone-headcount.repository.ts"
```

---

## Parallel Example: User Story 2

```bash
Task: "Add contract test for GET /api/occupancy/zones in tests/contract/ble-zone-headcount/us2-staffpanicbadge.contract.spec.ts"
Task: "Add integration test for restricted area safety alerts flow in tests/integration/ble-zone-headcount/us2-ratiocompliancestate.integration.spec.ts"
Task: "Create StaffPanicBadge and RatioComplianceState repository layer in services/ble-zone-headcount-service/src/data/us2-ble-zone-headcount.repository.ts"
```

---

## Parallel Example: User Story 3

```bash
Task: "Add contract test for POST /api/occupancy/alerts/{alertId}/ack in tests/contract/ble-zone-headcount/us3-zonegateway.contract.spec.ts"
Task: "Add integration test for automatic staff-to-child ratio verification flow in tests/integration/ble-zone-headcount/us3-zonesafetyalert.integration.spec.ts"
Task: "Create ZoneGateway and ZoneSafetyAlert repository layer in services/ble-zone-headcount-service/src/data/us3-ble-zone-headcount.repository.ts"
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
