# Tasks: Attendance and Absence Flags

**Input**: Design documents from `/specs/004-attendance-absence-flags/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because spec.md defines independent test criteria for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature module, contracts, and test scaffolding.

- [ ] T001 Create attendance-absence-flags service module scaffold in services/attendance-absence-flags-service/src/module/attendance-absence-flags.module.ts
- [ ] T002 Create attendance-absence-flags API controller scaffold in services/attendance-absence-flags-service/src/api/attendance-absence-flags.controller.ts
- [ ] T003 [P] Create attendance-absence-flags shared DTO and enum types in packages/shared-types/src/attendance-absence-flags/attendance-absence-flags.types.ts
- [ ] T004 [P] Create attendance-absence-flags feature configuration module in services/attendance-absence-flags-service/src/config/attendance-absence-flags.config.ts
- [ ] T005 [P] Create attendance-absence-flags test directories in tests/contract/attendance-absence-flags/, tests/integration/attendance-absence-flags/, and tests/e2e/attendance-absence-flags/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, policy, security, audit, and sync infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [ ] T006 Add ChildDailyAttendance, AttendanceEvent, AbsenceReason, AbsenceThresholdPolicy, UnexplainedAbsenceFlag, FollowUpAction models in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for attendance-absence-flags domain models in packages/db/prisma/migrations/
- [ ] T008 [P] Implement RBAC and scope guard middleware for attendance-absence-flags routes in services/attendance-absence-flags-service/src/security/attendance-absence-flags-rbac.guard.ts
- [ ] T009 [P] Implement consent, residency, and non-diagnostic policy validator in services/attendance-absence-flags-service/src/domain/policy/attendance-absence-flags-policy-validator.service.ts
- [ ] T010 [P] Implement offline outbox and replay publisher for attendance-absence-flags events in packages/offline-sync/src/attendance-absence-flags/attendance-absence-flags.outbox.ts
- [ ] T011 [P] Implement immutable audit writer for attendance-absence-flags events in services/audit-service/src/attendance-absence-flags/attendance-absence-flags-audit-writer.service.ts
- [ ] T012 Implement deterministic attendance-absence-flags rules engine baseline in services/attendance-absence-flags-service/src/domain/rules/attendance-absence-flags-rules.service.ts

**Checkpoint**: Foundational baseline is complete; story work can proceed.

---

## Phase 3: User Story 1 - Flexible Daily Check-In/Out (Priority: P1) 🎯 MVP

**Goal**: Deliver flexible daily check-in/out capabilities end-to-end.

**Independent Test**: Can be tested independently by processing check-in and check-out events across

### Tests for User Story 1

- [ ] T013 [P] [US1] Add contract test for POST /api/attendance/events in tests/contract/attendance-absence-flags/us1-childdailyattendance.contract.spec.ts
- [ ] T014 [P] [US1] Add integration test for flexible daily check-in/out flow in tests/integration/attendance-absence-flags/us1-absencethresholdpolicy.integration.spec.ts

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create ChildDailyAttendance and AbsenceThresholdPolicy repository layer in services/attendance-absence-flags-service/src/data/us1-attendance-absence-flags.repository.ts
- [ ] T016 [US1] Implement flexible daily check-in/out application service in services/attendance-absence-flags-service/src/domain/us1/attendance-absence-flags-us1.service.ts
- [ ] T017 [US1] Implement POST /api/attendance/events and POST /api/attendance/unexplained-absences/{flagId}/follow-ups routes in services/attendance-absence-flags-service/src/api/us1/attendance-absence-flags-us1.route.ts
- [ ] T018 [US1] Implement flexible daily check-in/out role-layout screen in apps/mobile/src/role-layouts/attendance-absence-flags/us1-attendance-absence-flags.screen.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Auto-Flag Unexplained Absences (Priority: P2)

**Goal**: Deliver auto-flag unexplained absences capabilities end-to-end.

**Independent Test**: Can be tested independently by configuring thresholds, simulating missing

### Tests for User Story 2

- [ ] T019 [P] [US2] Add contract test for GET /api/attendance/roll in tests/contract/attendance-absence-flags/us2-attendanceevent.contract.spec.ts
- [ ] T020 [P] [US2] Add integration test for auto-flag unexplained absences flow in tests/integration/attendance-absence-flags/us2-unexplainedabsenceflag.integration.spec.ts

### Implementation for User Story 2

- [ ] T021 [P] [US2] Create AttendanceEvent and UnexplainedAbsenceFlag repository layer in services/attendance-absence-flags-service/src/data/us2-attendance-absence-flags.repository.ts
- [ ] T022 [US2] Implement auto-flag unexplained absences application service in services/attendance-absence-flags-service/src/domain/us2/attendance-absence-flags-us2.service.ts
- [ ] T023 [US2] Implement GET /api/attendance/roll and PUT /api/attendance/threshold-policies/{policyId} routes in services/attendance-absence-flags-service/src/api/us2/attendance-absence-flags-us2.route.ts
- [ ] T024 [US2] Implement auto-flag unexplained absences role-layout screen in apps/mobile/src/role-layouts/attendance-absence-flags/us2-attendance-absence-flags.screen.tsx

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Follow-Up and Ratio-Ready Roll (Priority: P3)

**Goal**: Deliver follow-up and ratio-ready roll capabilities end-to-end.

**Independent Test**: Can be tested independently by resolving flagged absences, recording outcomes,

### Tests for User Story 3

- [ ] T025 [P] [US3] Add contract test for GET /api/attendance/unexplained-absences in tests/contract/attendance-absence-flags/us3-absencereason.contract.spec.ts
- [ ] T026 [P] [US3] Add integration test for follow-up and ratio-ready roll flow in tests/integration/attendance-absence-flags/us3-followupaction.integration.spec.ts

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create AbsenceReason and FollowUpAction repository layer in services/attendance-absence-flags-service/src/data/us3-attendance-absence-flags.repository.ts
- [ ] T028 [US3] Implement follow-up and ratio-ready roll application service in services/attendance-absence-flags-service/src/domain/us3/attendance-absence-flags-us3.service.ts
- [ ] T029 [US3] Implement GET /api/attendance/unexplained-absences and GET /api/attendance/unexplained-absences routes in services/attendance-absence-flags-service/src/api/us3/attendance-absence-flags-us3.route.ts
- [ ] T030 [US3] Implement follow-up and ratio-ready roll role-layout screen in apps/mobile/src/role-layouts/attendance-absence-flags/us3-attendance-absence-flags.screen.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, governance validation, and operational readiness across stories.

- [ ] T031 [P] Add attendance-absence-flags performance and reliability metrics in services/attendance-absence-flags-service/src/observability/attendance-absence-flags.metrics.ts
- [ ] T032 Run attendance-absence-flags quickstart validation scenarios in specs/004-attendance-absence-flags/quickstart.md
- [ ] T033 [P] Add end-to-end cross-story regression suite in tests/e2e/attendance-absence-flags/attendance-absence-flags-workflow.e2e.spec.ts
- [ ] T034 Validate constitution gates (privacy, consent, phase sequencing, non-diagnostic) for attendance-absence-flags in specs/004-attendance-absence-flags/research.md

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
Task: "Add contract test for POST /api/attendance/events in tests/contract/attendance-absence-flags/us1-childdailyattendance.contract.spec.ts"
Task: "Add integration test for flexible daily check-in/out flow in tests/integration/attendance-absence-flags/us1-absencethresholdpolicy.integration.spec.ts"
Task: "Create ChildDailyAttendance and AbsenceThresholdPolicy repository layer in services/attendance-absence-flags-service/src/data/us1-attendance-absence-flags.repository.ts"
```

---

## Parallel Example: User Story 2

```bash
Task: "Add contract test for GET /api/attendance/roll in tests/contract/attendance-absence-flags/us2-attendanceevent.contract.spec.ts"
Task: "Add integration test for auto-flag unexplained absences flow in tests/integration/attendance-absence-flags/us2-unexplainedabsenceflag.integration.spec.ts"
Task: "Create AttendanceEvent and UnexplainedAbsenceFlag repository layer in services/attendance-absence-flags-service/src/data/us2-attendance-absence-flags.repository.ts"
```

---

## Parallel Example: User Story 3

```bash
Task: "Add contract test for GET /api/attendance/unexplained-absences in tests/contract/attendance-absence-flags/us3-absencereason.contract.spec.ts"
Task: "Add integration test for follow-up and ratio-ready roll flow in tests/integration/attendance-absence-flags/us3-followupaction.integration.spec.ts"
Task: "Create AbsenceReason and FollowUpAction repository layer in services/attendance-absence-flags-service/src/data/us3-attendance-absence-flags.repository.ts"
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
