# Tasks: Pickup Guardian Verification

**Input**: Design documents from `/specs/010-pickup-guardian-verification/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because spec.md defines independent test criteria for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature module, contracts, and test scaffolding.

- [ ] T001 Create pickup-guardian-verification service module scaffold in services/pickup-guardian-verification-service/src/module/pickup-guardian-verification.module.ts
- [ ] T002 Create pickup-guardian-verification API controller scaffold in services/pickup-guardian-verification-service/src/api/pickup-guardian-verification.controller.ts
- [ ] T003 [P] Create pickup-guardian-verification shared DTO and enum types in packages/shared-types/src/pickup-guardian-verification/pickup-guardian-verification.types.ts
- [ ] T004 [P] Create pickup-guardian-verification feature configuration module in services/pickup-guardian-verification-service/src/config/pickup-guardian-verification.config.ts
- [ ] T005 [P] Create pickup-guardian-verification test directories in tests/contract/pickup-guardian-verification/, tests/integration/pickup-guardian-verification/, and tests/e2e/pickup-guardian-verification/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, policy, security, audit, and sync infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [ ] T006 Add GuardianAuthorizationRecord, PickupVerificationAttempt, PickupHandoverEvent, BiometricTemplateLocalRef, UnauthorizedPickupAlert models in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for pickup-guardian-verification domain models in packages/db/prisma/migrations/
- [ ] T008 [P] Implement RBAC and scope guard middleware for pickup-guardian-verification routes in services/pickup-guardian-verification-service/src/security/pickup-guardian-verification-rbac.guard.ts
- [ ] T009 [P] Implement consent, residency, and non-diagnostic policy validator in services/pickup-guardian-verification-service/src/domain/policy/pickup-guardian-verification-policy-validator.service.ts
- [ ] T010 [P] Implement offline outbox and replay publisher for pickup-guardian-verification events in packages/offline-sync/src/pickup-guardian-verification/pickup-guardian-verification.outbox.ts
- [ ] T011 [P] Implement immutable audit writer for pickup-guardian-verification events in services/audit-service/src/pickup-guardian-verification/pickup-guardian-verification-audit-writer.service.ts
- [ ] T012 Implement deterministic pickup-guardian-verification rules engine baseline in services/pickup-guardian-verification-service/src/domain/rules/pickup-guardian-verification-rules.service.ts

**Checkpoint**: Foundational baseline is complete; story work can proceed.

---

## Phase 3: User Story 1 - Verify Pickup Identity at Handover (Priority: P1) 🎯 MVP

**Goal**: Deliver verify pickup identity at handover capabilities end-to-end.

**Independent Test**: Can be tested independently by completing pickup with each approved method and

### Tests for User Story 1

- [ ] T013 [P] [US1] Add contract test for POST /api/pickup/verify in tests/contract/pickup-guardian-verification/us1-guardianauthorizationrecord.contract.spec.ts
- [ ] T014 [P] [US1] Add integration test for verify pickup identity at handover flow in tests/integration/pickup-guardian-verification/us1-biometrictemplatelocalref.integration.spec.ts

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create GuardianAuthorizationRecord and BiometricTemplateLocalRef repository layer in services/pickup-guardian-verification-service/src/data/us1-pickup-guardian-verification.repository.ts
- [ ] T016 [US1] Implement verify pickup identity at handover application service in services/pickup-guardian-verification-service/src/domain/us1/pickup-guardian-verification-us1.service.ts
- [ ] T017 [US1] Implement POST /api/pickup/verify and GET /api/pickup/audit routes in services/pickup-guardian-verification-service/src/api/us1/pickup-guardian-verification-us1.route.ts
- [ ] T018 [US1] Implement verify pickup identity at handover role-layout screen in apps/mobile/src/role-layouts/pickup-guardian-verification/us1-pickup-guardian-verification.screen.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Detect and Alert Unauthorized Attempts (Priority: P2)

**Goal**: Deliver detect and alert unauthorized attempts capabilities end-to-end.

**Independent Test**: Can be tested independently by simulating unauthorized pickup attempts and

### Tests for User Story 2

- [ ] T019 [P] [US2] Add contract test for POST /api/pickup/handover in tests/contract/pickup-guardian-verification/us2-pickupverificationattempt.contract.spec.ts
- [ ] T020 [P] [US2] Add integration test for detect and alert unauthorized attempts flow in tests/integration/pickup-guardian-verification/us2-unauthorizedpickupalert.integration.spec.ts

### Implementation for User Story 2

- [ ] T021 [P] [US2] Create PickupVerificationAttempt and UnauthorizedPickupAlert repository layer in services/pickup-guardian-verification-service/src/data/us2-pickup-guardian-verification.repository.ts
- [ ] T022 [US2] Implement detect and alert unauthorized attempts application service in services/pickup-guardian-verification-service/src/domain/us2/pickup-guardian-verification-us2.service.ts
- [ ] T023 [US2] Implement POST /api/pickup/handover and POST /api/pickup/handover routes in services/pickup-guardian-verification-service/src/api/us2/pickup-guardian-verification-us2.route.ts
- [ ] T024 [US2] Implement detect and alert unauthorized attempts role-layout screen in apps/mobile/src/role-layouts/pickup-guardian-verification/us2-pickup-guardian-verification.screen.tsx

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Maintain Full Pickup Audit Trail (Priority: P3)

**Goal**: Deliver maintain full pickup audit trail capabilities end-to-end.

**Independent Test**: Can be tested independently by reviewing recorded pickup events and confirming

### Tests for User Story 3

- [ ] T025 [P] [US3] Add contract test for POST /api/pickup/alerts/{alertId}/ack in tests/contract/pickup-guardian-verification/us3-pickuphandoverevent.contract.spec.ts
- [ ] T026 [P] [US3] Add integration test for maintain full pickup audit trail flow in tests/integration/pickup-guardian-verification/us3-pickuphandoverevent.integration.spec.ts

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create PickupHandoverEvent repository layer in services/pickup-guardian-verification-service/src/data/us3-pickup-guardian-verification.repository.ts
- [ ] T028 [US3] Implement maintain full pickup audit trail application service in services/pickup-guardian-verification-service/src/domain/us3/pickup-guardian-verification-us3.service.ts
- [ ] T029 [US3] Implement POST /api/pickup/alerts/{alertId}/ack and POST /api/pickup/alerts/{alertId}/ack routes in services/pickup-guardian-verification-service/src/api/us3/pickup-guardian-verification-us3.route.ts
- [ ] T030 [US3] Implement maintain full pickup audit trail role-layout screen in apps/mobile/src/role-layouts/pickup-guardian-verification/us3-pickup-guardian-verification.screen.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, governance validation, and operational readiness across stories.

- [ ] T031 [P] Add pickup-guardian-verification performance and reliability metrics in services/pickup-guardian-verification-service/src/observability/pickup-guardian-verification.metrics.ts
- [ ] T032 Run pickup-guardian-verification quickstart validation scenarios in specs/010-pickup-guardian-verification/quickstart.md
- [ ] T033 [P] Add end-to-end cross-story regression suite in tests/e2e/pickup-guardian-verification/pickup-guardian-verification-workflow.e2e.spec.ts
- [ ] T034 Validate constitution gates (privacy, consent, phase sequencing, non-diagnostic) for pickup-guardian-verification in specs/010-pickup-guardian-verification/research.md

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
Task: "Add contract test for POST /api/pickup/verify in tests/contract/pickup-guardian-verification/us1-guardianauthorizationrecord.contract.spec.ts"
Task: "Add integration test for verify pickup identity at handover flow in tests/integration/pickup-guardian-verification/us1-biometrictemplatelocalref.integration.spec.ts"
Task: "Create GuardianAuthorizationRecord and BiometricTemplateLocalRef repository layer in services/pickup-guardian-verification-service/src/data/us1-pickup-guardian-verification.repository.ts"
```

---

## Parallel Example: User Story 2

```bash
Task: "Add contract test for POST /api/pickup/handover in tests/contract/pickup-guardian-verification/us2-pickupverificationattempt.contract.spec.ts"
Task: "Add integration test for detect and alert unauthorized attempts flow in tests/integration/pickup-guardian-verification/us2-unauthorizedpickupalert.integration.spec.ts"
Task: "Create PickupVerificationAttempt and UnauthorizedPickupAlert repository layer in services/pickup-guardian-verification-service/src/data/us2-pickup-guardian-verification.repository.ts"
```

---

## Parallel Example: User Story 3

```bash
Task: "Add contract test for POST /api/pickup/alerts/{alertId}/ack in tests/contract/pickup-guardian-verification/us3-pickuphandoverevent.contract.spec.ts"
Task: "Add integration test for maintain full pickup audit trail flow in tests/integration/pickup-guardian-verification/us3-pickuphandoverevent.integration.spec.ts"
Task: "Create PickupHandoverEvent repository layer in services/pickup-guardian-verification-service/src/data/us3-pickup-guardian-verification.repository.ts"
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
