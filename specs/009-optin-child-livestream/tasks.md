# Tasks: Opt-In Child Livestream

**Input**: Design documents from `/specs/009-optin-child-livestream/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because spec.md defines independent test criteria for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature module, contracts, and test scaffolding.

- [ ] T001 Create optin-child-livestream service module scaffold in services/optin-child-livestream-service/src/module/optin-child-livestream.module.ts
- [ ] T002 Create optin-child-livestream API controller scaffold in services/optin-child-livestream-service/src/api/optin-child-livestream.controller.ts
- [ ] T003 [P] Create optin-child-livestream shared DTO and enum types in packages/shared-types/src/optin-child-livestream/optin-child-livestream.types.ts
- [ ] T004 [P] Create optin-child-livestream feature configuration module in services/optin-child-livestream-service/src/config/optin-child-livestream.config.ts
- [ ] T005 [P] Create optin-child-livestream test directories in tests/contract/optin-child-livestream/, tests/integration/optin-child-livestream/, and tests/e2e/optin-child-livestream/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, policy, security, audit, and sync infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [ ] T006 Add ParentLivestreamSession, ChildTrackingContext, BlurEnforcementEvent, LivestreamConsentSnapshot, LivestreamAuditEvent models in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for optin-child-livestream domain models in packages/db/prisma/migrations/
- [ ] T008 [P] Implement RBAC and scope guard middleware for optin-child-livestream routes in services/optin-child-livestream-service/src/security/optin-child-livestream-rbac.guard.ts
- [ ] T009 [P] Implement consent, residency, and non-diagnostic policy validator in services/optin-child-livestream-service/src/domain/policy/optin-child-livestream-policy-validator.service.ts
- [ ] T010 [P] Implement offline outbox and replay publisher for optin-child-livestream events in packages/offline-sync/src/optin-child-livestream/optin-child-livestream.outbox.ts
- [ ] T011 [P] Implement immutable audit writer for optin-child-livestream events in services/audit-service/src/optin-child-livestream/optin-child-livestream-audit-writer.service.ts
- [ ] T012 Implement deterministic optin-child-livestream rules engine baseline in services/optin-child-livestream-service/src/domain/rules/optin-child-livestream-rules.service.ts

**Checkpoint**: Foundational baseline is complete; story work can proceed.

---

## Phase 3: User Story 1 - View Child-Only Live Feed (Priority: P1) 🎯 MVP

**Goal**: Deliver view child-only live feed capabilities end-to-end.

**Independent Test**: Can be tested independently by enabling access for an opted-in parent and

### Tests for User Story 1

- [ ] T013 [P] [US1] Add contract test for POST /api/livestream/sessions in tests/contract/optin-child-livestream/us1-parentlivestreamsession.contract.spec.ts
- [ ] T014 [P] [US1] Add integration test for view child-only live feed flow in tests/integration/optin-child-livestream/us1-livestreamconsentsnapshot.integration.spec.ts

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create ParentLivestreamSession and LivestreamConsentSnapshot repository layer in services/optin-child-livestream-service/src/data/us1-optin-child-livestream.repository.ts
- [ ] T016 [US1] Implement view child-only live feed application service in services/optin-child-livestream-service/src/domain/us1/optin-child-livestream-us1.service.ts
- [ ] T017 [US1] Implement POST /api/livestream/sessions and GET /api/livestream/sessions/{sessionId}/status routes in services/optin-child-livestream-service/src/api/us1/optin-child-livestream-us1.route.ts
- [ ] T018 [US1] Implement view child-only live feed role-layout screen in apps/mobile/src/role-layouts/optin-child-livestream/us1-optin-child-livestream.screen.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Follow Child Across Cameras (Priority: P2)

**Goal**: Deliver follow child across cameras capabilities end-to-end.

**Independent Test**: Can be tested independently by simulating child movement across camera zones and

### Tests for User Story 2

- [ ] T019 [P] [US2] Add contract test for POST /api/livestream/sessions/{sessionId}/heartbeat in tests/contract/optin-child-livestream/us2-childtrackingcontext.contract.spec.ts
- [ ] T020 [P] [US2] Add integration test for follow child across cameras flow in tests/integration/optin-child-livestream/us2-livestreamauditevent.integration.spec.ts

### Implementation for User Story 2

- [ ] T021 [P] [US2] Create ChildTrackingContext and LivestreamAuditEvent repository layer in services/optin-child-livestream-service/src/data/us2-optin-child-livestream.repository.ts
- [ ] T022 [US2] Implement follow child across cameras application service in services/optin-child-livestream-service/src/domain/us2/optin-child-livestream-us2.service.ts
- [ ] T023 [US2] Implement POST /api/livestream/sessions/{sessionId}/heartbeat and POST /api/livestream/sessions/{sessionId}/heartbeat routes in services/optin-child-livestream-service/src/api/us2/optin-child-livestream-us2.route.ts
- [ ] T024 [US2] Implement follow child across cameras role-layout screen in apps/mobile/src/role-layouts/optin-child-livestream/us2-optin-child-livestream.screen.tsx

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Enforce Consent and No-Storage Policy (Priority: P3)

**Goal**: Deliver enforce consent and no-storage policy capabilities end-to-end.

**Independent Test**: Can be tested independently by validating opt-in gating, access denials,

### Tests for User Story 3

- [ ] T025 [P] [US3] Add contract test for POST /api/livestream/sessions/{sessionId}/stop in tests/contract/optin-child-livestream/us3-blurenforcementevent.contract.spec.ts
- [ ] T026 [P] [US3] Add integration test for enforce consent and no-storage policy flow in tests/integration/optin-child-livestream/us3-blurenforcementevent.integration.spec.ts

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create BlurEnforcementEvent repository layer in services/optin-child-livestream-service/src/data/us3-optin-child-livestream.repository.ts
- [ ] T028 [US3] Implement enforce consent and no-storage policy application service in services/optin-child-livestream-service/src/domain/us3/optin-child-livestream-us3.service.ts
- [ ] T029 [US3] Implement POST /api/livestream/sessions/{sessionId}/stop and POST /api/livestream/sessions/{sessionId}/stop routes in services/optin-child-livestream-service/src/api/us3/optin-child-livestream-us3.route.ts
- [ ] T030 [US3] Implement enforce consent and no-storage policy role-layout screen in apps/mobile/src/role-layouts/optin-child-livestream/us3-optin-child-livestream.screen.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, governance validation, and operational readiness across stories.

- [ ] T031 [P] Add optin-child-livestream performance and reliability metrics in services/optin-child-livestream-service/src/observability/optin-child-livestream.metrics.ts
- [ ] T032 Run optin-child-livestream quickstart validation scenarios in specs/009-optin-child-livestream/quickstart.md
- [ ] T033 [P] Add end-to-end cross-story regression suite in tests/e2e/optin-child-livestream/optin-child-livestream-workflow.e2e.spec.ts
- [ ] T034 Validate constitution gates (privacy, consent, phase sequencing, non-diagnostic) for optin-child-livestream in specs/009-optin-child-livestream/research.md

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
Task: "Add contract test for POST /api/livestream/sessions in tests/contract/optin-child-livestream/us1-parentlivestreamsession.contract.spec.ts"
Task: "Add integration test for view child-only live feed flow in tests/integration/optin-child-livestream/us1-livestreamconsentsnapshot.integration.spec.ts"
Task: "Create ParentLivestreamSession and LivestreamConsentSnapshot repository layer in services/optin-child-livestream-service/src/data/us1-optin-child-livestream.repository.ts"
```

---

## Parallel Example: User Story 2

```bash
Task: "Add contract test for POST /api/livestream/sessions/{sessionId}/heartbeat in tests/contract/optin-child-livestream/us2-childtrackingcontext.contract.spec.ts"
Task: "Add integration test for follow child across cameras flow in tests/integration/optin-child-livestream/us2-livestreamauditevent.integration.spec.ts"
Task: "Create ChildTrackingContext and LivestreamAuditEvent repository layer in services/optin-child-livestream-service/src/data/us2-optin-child-livestream.repository.ts"
```

---

## Parallel Example: User Story 3

```bash
Task: "Add contract test for POST /api/livestream/sessions/{sessionId}/stop in tests/contract/optin-child-livestream/us3-blurenforcementevent.contract.spec.ts"
Task: "Add integration test for enforce consent and no-storage policy flow in tests/integration/optin-child-livestream/us3-blurenforcementevent.integration.spec.ts"
Task: "Create BlurEnforcementEvent repository layer in services/optin-child-livestream-service/src/data/us3-optin-child-livestream.repository.ts"
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
