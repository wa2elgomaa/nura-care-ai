# Tasks: Evacuation Live Rollcall

**Input**: Design documents from `/specs/012-evacuation-live-rollcall/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because spec.md defines independent test criteria for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature module, contracts, and test scaffolding.

- [ ] T001 Create evacuation-live-rollcall service module scaffold in services/evacuation-live-rollcall-service/src/module/evacuation-live-rollcall.module.ts
- [ ] T002 Create evacuation-live-rollcall API controller scaffold in services/evacuation-live-rollcall-service/src/api/evacuation-live-rollcall.controller.ts
- [ ] T003 [P] Create evacuation-live-rollcall shared DTO and enum types in packages/shared-types/src/evacuation-live-rollcall/evacuation-live-rollcall.types.ts
- [ ] T004 [P] Create evacuation-live-rollcall feature configuration module in services/evacuation-live-rollcall-service/src/config/evacuation-live-rollcall.config.ts
- [ ] T005 [P] Create evacuation-live-rollcall test directories in tests/contract/evacuation-live-rollcall/, tests/integration/evacuation-live-rollcall/, and tests/e2e/evacuation-live-rollcall/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, policy, security, audit, and sync infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [ ] T006 Add EvacuationEvent, RollcallSession, AccountabilityState, BLEExitEvidence, QRFallbackEvidence, EvacuationAuditEvent models in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for evacuation-live-rollcall domain models in packages/db/prisma/migrations/
- [ ] T008 [P] Implement RBAC and scope guard middleware for evacuation-live-rollcall routes in services/evacuation-live-rollcall-service/src/security/evacuation-live-rollcall-rbac.guard.ts
- [ ] T009 [P] Implement consent, residency, and non-diagnostic policy validator in services/evacuation-live-rollcall-service/src/domain/policy/evacuation-live-rollcall-policy-validator.service.ts
- [ ] T010 [P] Implement offline outbox and replay publisher for evacuation-live-rollcall events in packages/offline-sync/src/evacuation-live-rollcall/evacuation-live-rollcall.outbox.ts
- [ ] T011 [P] Implement immutable audit writer for evacuation-live-rollcall events in services/audit-service/src/evacuation-live-rollcall/evacuation-live-rollcall-audit-writer.service.ts
- [ ] T012 Implement deterministic evacuation-live-rollcall rules engine baseline in services/evacuation-live-rollcall-service/src/domain/rules/evacuation-live-rollcall-rules.service.ts

**Checkpoint**: Foundational baseline is complete; story work can proceed.

---

## Phase 3: User Story 1 - One-Tap Evacuation Activation (Priority: P1) 🎯 MVP

**Goal**: Deliver one-tap evacuation activation capabilities end-to-end.

**Independent Test**: Can be tested independently by triggering evacuation mode and confirming all

### Tests for User Story 1

- [ ] T013 [P] [US1] Add contract test for POST /api/evacuation/events in tests/contract/evacuation-live-rollcall/us1-evacuationevent.contract.spec.ts
- [ ] T014 [P] [US1] Add integration test for one-tap evacuation activation flow in tests/integration/evacuation-live-rollcall/us1-bleexitevidence.integration.spec.ts

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create EvacuationEvent and BLEExitEvidence repository layer in services/evacuation-live-rollcall-service/src/data/us1-evacuation-live-rollcall.repository.ts
- [ ] T016 [US1] Implement one-tap evacuation activation application service in services/evacuation-live-rollcall-service/src/domain/us1/evacuation-live-rollcall-us1.service.ts
- [ ] T017 [US1] Implement POST /api/evacuation/events and POST /api/evacuation/events/{eventId}/evidence/qr routes in services/evacuation-live-rollcall-service/src/api/us1/evacuation-live-rollcall-us1.route.ts
- [ ] T018 [US1] Implement one-tap evacuation activation role-layout screen in apps/mobile/src/role-layouts/evacuation-live-rollcall/us1-evacuation-live-rollcall.screen.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Live Cross-Checked Accountability (Priority: P2)

**Goal**: Deliver live cross-checked accountability capabilities end-to-end.

**Independent Test**: Can be tested independently by simulating evacuation movement and verifying

### Tests for User Story 2

- [ ] T019 [P] [US2] Add contract test for POST /api/evacuation/events/{eventId}/rollcall in tests/contract/evacuation-live-rollcall/us2-rollcallsession.contract.spec.ts
- [ ] T020 [P] [US2] Add integration test for live cross-checked accountability flow in tests/integration/evacuation-live-rollcall/us2-qrfallbackevidence.integration.spec.ts

### Implementation for User Story 2

- [ ] T021 [P] [US2] Create RollcallSession and QRFallbackEvidence repository layer in services/evacuation-live-rollcall-service/src/data/us2-evacuation-live-rollcall.repository.ts
- [ ] T022 [US2] Implement live cross-checked accountability application service in services/evacuation-live-rollcall-service/src/domain/us2/evacuation-live-rollcall-us2.service.ts
- [ ] T023 [US2] Implement POST /api/evacuation/events/{eventId}/rollcall and GET /api/evacuation/events/{eventId}/status routes in services/evacuation-live-rollcall-service/src/api/us2/evacuation-live-rollcall-us2.route.ts
- [ ] T024 [US2] Implement live cross-checked accountability role-layout screen in apps/mobile/src/role-layouts/evacuation-live-rollcall/us2-evacuation-live-rollcall.screen.tsx

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Emergency Audit and Post-Event Review (Priority: P3)

**Goal**: Deliver emergency audit and post-event review capabilities end-to-end.

**Independent Test**: Can be tested independently by closing an evacuation event and reviewing

### Tests for User Story 3

- [ ] T025 [P] [US3] Add contract test for POST /api/evacuation/events/{eventId}/evidence/ble in tests/contract/evacuation-live-rollcall/us3-accountabilitystate.contract.spec.ts
- [ ] T026 [P] [US3] Add integration test for emergency audit and post-event review flow in tests/integration/evacuation-live-rollcall/us3-evacuationauditevent.integration.spec.ts

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create AccountabilityState and EvacuationAuditEvent repository layer in services/evacuation-live-rollcall-service/src/data/us3-evacuation-live-rollcall.repository.ts
- [ ] T028 [US3] Implement emergency audit and post-event review application service in services/evacuation-live-rollcall-service/src/domain/us3/evacuation-live-rollcall-us3.service.ts
- [ ] T029 [US3] Implement POST /api/evacuation/events/{eventId}/evidence/ble and POST /api/evacuation/events/{eventId}/insurer-hook-preview routes in services/evacuation-live-rollcall-service/src/api/us3/evacuation-live-rollcall-us3.route.ts
- [ ] T030 [US3] Implement emergency audit and post-event review role-layout screen in apps/mobile/src/role-layouts/evacuation-live-rollcall/us3-evacuation-live-rollcall.screen.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, governance validation, and operational readiness across stories.

- [ ] T031 [P] Add evacuation-live-rollcall performance and reliability metrics in services/evacuation-live-rollcall-service/src/observability/evacuation-live-rollcall.metrics.ts
- [ ] T032 Run evacuation-live-rollcall quickstart validation scenarios in specs/012-evacuation-live-rollcall/quickstart.md
- [ ] T033 [P] Add end-to-end cross-story regression suite in tests/e2e/evacuation-live-rollcall/evacuation-live-rollcall-workflow.e2e.spec.ts
- [ ] T034 Validate constitution gates (privacy, consent, phase sequencing, non-diagnostic) for evacuation-live-rollcall in specs/012-evacuation-live-rollcall/research.md

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
Task: "Add contract test for POST /api/evacuation/events in tests/contract/evacuation-live-rollcall/us1-evacuationevent.contract.spec.ts"
Task: "Add integration test for one-tap evacuation activation flow in tests/integration/evacuation-live-rollcall/us1-bleexitevidence.integration.spec.ts"
Task: "Create EvacuationEvent and BLEExitEvidence repository layer in services/evacuation-live-rollcall-service/src/data/us1-evacuation-live-rollcall.repository.ts"
```

---

## Parallel Example: User Story 2

```bash
Task: "Add contract test for POST /api/evacuation/events/{eventId}/rollcall in tests/contract/evacuation-live-rollcall/us2-rollcallsession.contract.spec.ts"
Task: "Add integration test for live cross-checked accountability flow in tests/integration/evacuation-live-rollcall/us2-qrfallbackevidence.integration.spec.ts"
Task: "Create RollcallSession and QRFallbackEvidence repository layer in services/evacuation-live-rollcall-service/src/data/us2-evacuation-live-rollcall.repository.ts"
```

---

## Parallel Example: User Story 3

```bash
Task: "Add contract test for POST /api/evacuation/events/{eventId}/evidence/ble in tests/contract/evacuation-live-rollcall/us3-accountabilitystate.contract.spec.ts"
Task: "Add integration test for emergency audit and post-event review flow in tests/integration/evacuation-live-rollcall/us3-evacuationauditevent.integration.spec.ts"
Task: "Create AccountabilityState and EvacuationAuditEvent repository layer in services/evacuation-live-rollcall-service/src/data/us3-evacuation-live-rollcall.repository.ts"
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
