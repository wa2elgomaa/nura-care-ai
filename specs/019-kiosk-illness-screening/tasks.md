# Tasks: Kiosk Illness Screening

**Input**: Design documents from `/specs/019-kiosk-illness-screening/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because spec.md defines independent test criteria for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature module, contracts, and test scaffolding.

- [ ] T001 Create kiosk-illness-screening service module scaffold in services/kiosk-illness-screening-service/src/module/kiosk-illness-screening.module.ts
- [ ] T002 Create kiosk-illness-screening API controller scaffold in services/kiosk-illness-screening-service/src/api/kiosk-illness-screening.controller.ts
- [ ] T003 [P] Create kiosk-illness-screening shared DTO and enum types in packages/shared-types/src/kiosk-illness-screening/kiosk-illness-screening.types.ts
- [ ] T004 [P] Create kiosk-illness-screening feature configuration module in services/kiosk-illness-screening-service/src/config/kiosk-illness-screening.config.ts
- [ ] T005 [P] Create kiosk-illness-screening test directories in tests/contract/kiosk-illness-screening/, tests/integration/kiosk-illness-screening/, and tests/e2e/kiosk-illness-screening/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, policy, security, audit, and sync infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [ ] T006 Add ScreeningConsentSnapshot, KioskScreeningSession, ThermalReading, SymptomChecklistResponse, ScreeningOutcome, ScreeningAuditEvent models in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for kiosk-illness-screening domain models in packages/db/prisma/migrations/
- [ ] T008 [P] Implement RBAC and scope guard middleware for kiosk-illness-screening routes in services/kiosk-illness-screening-service/src/security/kiosk-illness-screening-rbac.guard.ts
- [ ] T009 [P] Implement consent, residency, and non-diagnostic policy validator in services/kiosk-illness-screening-service/src/domain/policy/kiosk-illness-screening-policy-validator.service.ts
- [ ] T010 [P] Implement offline outbox and replay publisher for kiosk-illness-screening events in packages/offline-sync/src/kiosk-illness-screening/kiosk-illness-screening.outbox.ts
- [ ] T011 [P] Implement immutable audit writer for kiosk-illness-screening events in services/audit-service/src/kiosk-illness-screening/kiosk-illness-screening-audit-writer.service.ts
- [ ] T012 Implement deterministic kiosk-illness-screening rules engine baseline in services/kiosk-illness-screening-service/src/domain/rules/kiosk-illness-screening-rules.service.ts

**Checkpoint**: Foundational baseline is complete; story work can proceed.

---

## Phase 3: User Story 1 - Fast Drop-Off Screening Capture (Priority: P1) 🎯 MVP

**Goal**: Deliver fast drop-off screening capture capabilities end-to-end.

**Independent Test**: Can be tested independently by running drop-off sessions and confirming

### Tests for User Story 1

- [ ] T013 [P] [US1] Add contract test for POST /api/kiosk/screening/start in tests/contract/kiosk-illness-screening/us1-screeningconsentsnapshot.contract.spec.ts
- [ ] T014 [P] [US1] Add integration test for fast drop-off screening capture flow in tests/integration/kiosk-illness-screening/us1-symptomchecklistresponse.integration.spec.ts

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create ScreeningConsentSnapshot and SymptomChecklistResponse repository layer in services/kiosk-illness-screening-service/src/data/us1-kiosk-illness-screening.repository.ts
- [ ] T016 [US1] Implement fast drop-off screening capture application service in services/kiosk-illness-screening-service/src/domain/us1/kiosk-illness-screening-us1.service.ts
- [ ] T017 [US1] Implement POST /api/kiosk/screening/start and POST /api/kiosk/screening/{sessionId}/evaluate routes in services/kiosk-illness-screening-service/src/api/us1/kiosk-illness-screening-us1.route.ts
- [ ] T018 [US1] Implement fast drop-off screening capture role-layout screen in apps/mobile/src/role-layouts/kiosk-illness-screening/us1-kiosk-illness-screening.screen.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Attendance and Absence Workflow Integration (Priority: P2)

**Goal**: Deliver attendance and absence workflow integration capabilities end-to-end.

**Independent Test**: Can be tested independently by verifying screening records automatically appear

### Tests for User Story 2

- [ ] T019 [P] [US2] Add contract test for POST /api/kiosk/screening/{sessionId}/thermal in tests/contract/kiosk-illness-screening/us2-kioskscreeningsession.contract.spec.ts
- [ ] T020 [P] [US2] Add integration test for attendance and absence workflow integration flow in tests/integration/kiosk-illness-screening/us2-screeningoutcome.integration.spec.ts

### Implementation for User Story 2

- [ ] T021 [P] [US2] Create KioskScreeningSession and ScreeningOutcome repository layer in services/kiosk-illness-screening-service/src/data/us2-kiosk-illness-screening.repository.ts
- [ ] T022 [US2] Implement attendance and absence workflow integration application service in services/kiosk-illness-screening-service/src/domain/us2/kiosk-illness-screening-us2.service.ts
- [ ] T023 [US2] Implement POST /api/kiosk/screening/{sessionId}/thermal and GET /api/kiosk/screening/{sessionId}/audit routes in services/kiosk-illness-screening-service/src/api/us2/kiosk-illness-screening-us2.route.ts
- [ ] T024 [US2] Implement attendance and absence workflow integration role-layout screen in apps/mobile/src/role-layouts/kiosk-illness-screening/us2-kiosk-illness-screening.screen.tsx

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Director Oversight and Auditability (Priority: P3)

**Goal**: Deliver director oversight and auditability capabilities end-to-end.

**Independent Test**: Can be tested independently by reviewing screening reports for completion,

### Tests for User Story 3

- [ ] T025 [P] [US3] Add contract test for POST /api/kiosk/screening/{sessionId}/symptoms in tests/contract/kiosk-illness-screening/us3-thermalreading.contract.spec.ts
- [ ] T026 [P] [US3] Add integration test for director oversight and auditability flow in tests/integration/kiosk-illness-screening/us3-screeningauditevent.integration.spec.ts

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create ThermalReading and ScreeningAuditEvent repository layer in services/kiosk-illness-screening-service/src/data/us3-kiosk-illness-screening.repository.ts
- [ ] T028 [US3] Implement director oversight and auditability application service in services/kiosk-illness-screening-service/src/domain/us3/kiosk-illness-screening-us3.service.ts
- [ ] T029 [US3] Implement POST /api/kiosk/screening/{sessionId}/symptoms and POST /api/kiosk/screening/{sessionId}/symptoms routes in services/kiosk-illness-screening-service/src/api/us3/kiosk-illness-screening-us3.route.ts
- [ ] T030 [US3] Implement director oversight and auditability role-layout screen in apps/mobile/src/role-layouts/kiosk-illness-screening/us3-kiosk-illness-screening.screen.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, governance validation, and operational readiness across stories.

- [ ] T031 [P] Add kiosk-illness-screening performance and reliability metrics in services/kiosk-illness-screening-service/src/observability/kiosk-illness-screening.metrics.ts
- [ ] T032 Run kiosk-illness-screening quickstart validation scenarios in specs/019-kiosk-illness-screening/quickstart.md
- [ ] T033 [P] Add end-to-end cross-story regression suite in tests/e2e/kiosk-illness-screening/kiosk-illness-screening-workflow.e2e.spec.ts
- [ ] T034 Validate constitution gates (privacy, consent, phase sequencing, non-diagnostic) for kiosk-illness-screening in specs/019-kiosk-illness-screening/research.md

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
Task: "Add contract test for POST /api/kiosk/screening/start in tests/contract/kiosk-illness-screening/us1-screeningconsentsnapshot.contract.spec.ts"
Task: "Add integration test for fast drop-off screening capture flow in tests/integration/kiosk-illness-screening/us1-symptomchecklistresponse.integration.spec.ts"
Task: "Create ScreeningConsentSnapshot and SymptomChecklistResponse repository layer in services/kiosk-illness-screening-service/src/data/us1-kiosk-illness-screening.repository.ts"
```

---

## Parallel Example: User Story 2

```bash
Task: "Add contract test for POST /api/kiosk/screening/{sessionId}/thermal in tests/contract/kiosk-illness-screening/us2-kioskscreeningsession.contract.spec.ts"
Task: "Add integration test for attendance and absence workflow integration flow in tests/integration/kiosk-illness-screening/us2-screeningoutcome.integration.spec.ts"
Task: "Create KioskScreeningSession and ScreeningOutcome repository layer in services/kiosk-illness-screening-service/src/data/us2-kiosk-illness-screening.repository.ts"
```

---

## Parallel Example: User Story 3

```bash
Task: "Add contract test for POST /api/kiosk/screening/{sessionId}/symptoms in tests/contract/kiosk-illness-screening/us3-thermalreading.contract.spec.ts"
Task: "Add integration test for director oversight and auditability flow in tests/integration/kiosk-illness-screening/us3-screeningauditevent.integration.spec.ts"
Task: "Create ThermalReading and ScreeningAuditEvent repository layer in services/kiosk-illness-screening-service/src/data/us3-kiosk-illness-screening.repository.ts"
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
