# Tasks: Quarterly Interest Profile

**Input**: Design documents from `/specs/016-quarterly-interest-profile/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because spec.md defines independent test criteria for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature module, contracts, and test scaffolding.

- [ ] T001 Create quarterly-interest-profile service module scaffold in services/quarterly-interest-profile-service/src/module/quarterly-interest-profile.module.ts
- [ ] T002 Create quarterly-interest-profile API controller scaffold in services/quarterly-interest-profile-service/src/api/quarterly-interest-profile.controller.ts
- [ ] T003 [P] Create quarterly-interest-profile shared DTO and enum types in packages/shared-types/src/quarterly-interest-profile/quarterly-interest-profile.types.ts
- [ ] T004 [P] Create quarterly-interest-profile feature configuration module in services/quarterly-interest-profile-service/src/config/quarterly-interest-profile.config.ts
- [ ] T005 [P] Create quarterly-interest-profile test directories in tests/contract/quarterly-interest-profile/, tests/integration/quarterly-interest-profile/, and tests/e2e/quarterly-interest-profile/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, policy, security, audit, and sync infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [ ] T006 Add ActivityEvidenceEvent, QuarterlyProfileDraft, ProfileConsentSnapshot, PhraseRuleViolation, ProfileAuditEvent models in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for quarterly-interest-profile domain models in packages/db/prisma/migrations/
- [ ] T008 [P] Implement RBAC and scope guard middleware for quarterly-interest-profile routes in services/quarterly-interest-profile-service/src/security/quarterly-interest-profile-rbac.guard.ts
- [ ] T009 [P] Implement consent, residency, and non-diagnostic policy validator in services/quarterly-interest-profile-service/src/domain/policy/quarterly-interest-profile-policy-validator.service.ts
- [ ] T010 [P] Implement offline outbox and replay publisher for quarterly-interest-profile events in packages/offline-sync/src/quarterly-interest-profile/quarterly-interest-profile.outbox.ts
- [ ] T011 [P] Implement immutable audit writer for quarterly-interest-profile events in services/audit-service/src/quarterly-interest-profile/quarterly-interest-profile-audit-writer.service.ts
- [ ] T012 Implement deterministic quarterly-interest-profile rules engine baseline in services/quarterly-interest-profile-service/src/domain/rules/quarterly-interest-profile-rules.service.ts

**Checkpoint**: Foundational baseline is complete; story work can proceed.

---

## Phase 3: User Story 1 - Parent Receives Quarterly Interest Summary (Priority: P1) 🎯 MVP

**Goal**: Deliver parent receives quarterly interest summary capabilities end-to-end.

**Independent Test**: Can be tested independently by generating a quarterly report for a child with

### Tests for User Story 1

- [ ] T013 [P] [US1] Add contract test for POST /api/interest-profiles/generate in tests/contract/quarterly-interest-profile/us1-activityevidenceevent.contract.spec.ts
- [ ] T014 [P] [US1] Add integration test for parent receives quarterly interest summary flow in tests/integration/quarterly-interest-profile/us1-phraseruleviolation.integration.spec.ts

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create ActivityEvidenceEvent and PhraseRuleViolation repository layer in services/quarterly-interest-profile-service/src/data/us1-quarterly-interest-profile.repository.ts
- [ ] T016 [US1] Implement parent receives quarterly interest summary application service in services/quarterly-interest-profile-service/src/domain/us1/quarterly-interest-profile-us1.service.ts
- [ ] T017 [US1] Implement POST /api/interest-profiles/generate and POST /api/interest-profiles/consent routes in services/quarterly-interest-profile-service/src/api/us1/quarterly-interest-profile-us1.route.ts
- [ ] T018 [US1] Implement parent receives quarterly interest summary role-layout screen in apps/mobile/src/role-layouts/quarterly-interest-profile/us1-quarterly-interest-profile.screen.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Home Support Guidance (Priority: P2)

**Goal**: Deliver home support guidance capabilities end-to-end.

**Independent Test**: Can be tested independently by verifying each interest theme includes

### Tests for User Story 2

- [ ] T019 [P] [US2] Add contract test for GET /api/interest-profiles/{draftId} in tests/contract/quarterly-interest-profile/us2-quarterlyprofiledraft.contract.spec.ts
- [ ] T020 [P] [US2] Add integration test for home support guidance flow in tests/integration/quarterly-interest-profile/us2-profileauditevent.integration.spec.ts

### Implementation for User Story 2

- [ ] T021 [P] [US2] Create QuarterlyProfileDraft and ProfileAuditEvent repository layer in services/quarterly-interest-profile-service/src/data/us2-quarterly-interest-profile.repository.ts
- [ ] T022 [US2] Implement home support guidance application service in services/quarterly-interest-profile-service/src/domain/us2/quarterly-interest-profile-us2.service.ts
- [ ] T023 [US2] Implement GET /api/interest-profiles/{draftId} and GET /api/interest-profiles/{draftId} routes in services/quarterly-interest-profile-service/src/api/us2/quarterly-interest-profile-us2.route.ts
- [ ] T024 [US2] Implement home support guidance role-layout screen in apps/mobile/src/role-layouts/quarterly-interest-profile/us2-quarterly-interest-profile.screen.tsx

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Parent Trust and Continuity Over Time (Priority: P3)

**Goal**: Deliver parent trust and continuity over time capabilities end-to-end.

**Independent Test**: Can be tested independently by generating multiple quarterly profiles and

### Tests for User Story 3

- [ ] T025 [P] [US3] Add contract test for POST /api/interest-profiles/{draftId}/publish in tests/contract/quarterly-interest-profile/us3-profileconsentsnapshot.contract.spec.ts
- [ ] T026 [P] [US3] Add integration test for parent trust and continuity over time flow in tests/integration/quarterly-interest-profile/us3-profileconsentsnapshot.integration.spec.ts

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create ProfileConsentSnapshot repository layer in services/quarterly-interest-profile-service/src/data/us3-quarterly-interest-profile.repository.ts
- [ ] T028 [US3] Implement parent trust and continuity over time application service in services/quarterly-interest-profile-service/src/domain/us3/quarterly-interest-profile-us3.service.ts
- [ ] T029 [US3] Implement POST /api/interest-profiles/{draftId}/publish and POST /api/interest-profiles/{draftId}/publish routes in services/quarterly-interest-profile-service/src/api/us3/quarterly-interest-profile-us3.route.ts
- [ ] T030 [US3] Implement parent trust and continuity over time role-layout screen in apps/mobile/src/role-layouts/quarterly-interest-profile/us3-quarterly-interest-profile.screen.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, governance validation, and operational readiness across stories.

- [ ] T031 [P] Add quarterly-interest-profile performance and reliability metrics in services/quarterly-interest-profile-service/src/observability/quarterly-interest-profile.metrics.ts
- [ ] T032 Run quarterly-interest-profile quickstart validation scenarios in specs/016-quarterly-interest-profile/quickstart.md
- [ ] T033 [P] Add end-to-end cross-story regression suite in tests/e2e/quarterly-interest-profile/quarterly-interest-profile-workflow.e2e.spec.ts
- [ ] T034 Validate constitution gates (privacy, consent, phase sequencing, non-diagnostic) for quarterly-interest-profile in specs/016-quarterly-interest-profile/research.md

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
Task: "Add contract test for POST /api/interest-profiles/generate in tests/contract/quarterly-interest-profile/us1-activityevidenceevent.contract.spec.ts"
Task: "Add integration test for parent receives quarterly interest summary flow in tests/integration/quarterly-interest-profile/us1-phraseruleviolation.integration.spec.ts"
Task: "Create ActivityEvidenceEvent and PhraseRuleViolation repository layer in services/quarterly-interest-profile-service/src/data/us1-quarterly-interest-profile.repository.ts"
```

---

## Parallel Example: User Story 2

```bash
Task: "Add contract test for GET /api/interest-profiles/{draftId} in tests/contract/quarterly-interest-profile/us2-quarterlyprofiledraft.contract.spec.ts"
Task: "Add integration test for home support guidance flow in tests/integration/quarterly-interest-profile/us2-profileauditevent.integration.spec.ts"
Task: "Create QuarterlyProfileDraft and ProfileAuditEvent repository layer in services/quarterly-interest-profile-service/src/data/us2-quarterly-interest-profile.repository.ts"
```

---

## Parallel Example: User Story 3

```bash
Task: "Add contract test for POST /api/interest-profiles/{draftId}/publish in tests/contract/quarterly-interest-profile/us3-profileconsentsnapshot.contract.spec.ts"
Task: "Add integration test for parent trust and continuity over time flow in tests/integration/quarterly-interest-profile/us3-profileconsentsnapshot.integration.spec.ts"
Task: "Create ProfileConsentSnapshot repository layer in services/quarterly-interest-profile-service/src/data/us3-quarterly-interest-profile.repository.ts"
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
