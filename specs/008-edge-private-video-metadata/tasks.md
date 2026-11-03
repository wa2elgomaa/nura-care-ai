# Tasks: Edge Private Video Metadata

**Input**: Design documents from `/specs/008-edge-private-video-metadata/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because spec.md defines independent test criteria for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature module, contracts, and test scaffolding.

- [ ] T001 Create edge-private-video-metadata service module scaffold in services/edge-private-video-metadata-service/src/module/edge-private-video-metadata.module.ts
- [ ] T002 Create edge-private-video-metadata API controller scaffold in services/edge-private-video-metadata-service/src/api/edge-private-video-metadata.controller.ts
- [ ] T003 [P] Create edge-private-video-metadata shared DTO and enum types in packages/shared-types/src/edge-private-video-metadata/edge-private-video-metadata.types.ts
- [ ] T004 [P] Create edge-private-video-metadata feature configuration module in services/edge-private-video-metadata-service/src/config/edge-private-video-metadata.config.ts
- [ ] T005 [P] Create edge-private-video-metadata test directories in tests/contract/edge-private-video-metadata/, tests/integration/edge-private-video-metadata/, and tests/e2e/edge-private-video-metadata/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, policy, security, audit, and sync infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [ ] T006 Add EdgeSiteNode, CameraIngestSource, LocalDetectionEvent, MetadataOutboxItem, EgressPolicyRule, EgressAuditEvent models in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for edge-private-video-metadata domain models in packages/db/prisma/migrations/
- [ ] T008 [P] Implement RBAC and scope guard middleware for edge-private-video-metadata routes in services/edge-private-video-metadata-service/src/security/edge-private-video-metadata-rbac.guard.ts
- [ ] T009 [P] Implement consent, residency, and non-diagnostic policy validator in services/edge-private-video-metadata-service/src/domain/policy/edge-private-video-metadata-policy-validator.service.ts
- [ ] T010 [P] Implement offline outbox and replay publisher for edge-private-video-metadata events in packages/offline-sync/src/edge-private-video-metadata/edge-private-video-metadata.outbox.ts
- [ ] T011 [P] Implement immutable audit writer for edge-private-video-metadata events in services/audit-service/src/edge-private-video-metadata/edge-private-video-metadata-audit-writer.service.ts
- [ ] T012 Implement deterministic edge-private-video-metadata rules engine baseline in services/edge-private-video-metadata-service/src/domain/rules/edge-private-video-metadata-rules.service.ts

**Checkpoint**: Foundational baseline is complete; story work can proceed.

---

## Phase 3: User Story 1 - Site-Local Ingest and Detection (Priority: P1) 🎯 MVP

**Goal**: Deliver site-local ingest and detection capabilities end-to-end.

**Independent Test**: Can be tested independently by connecting site cameras to the edge server and

### Tests for User Story 1

- [ ] T013 [P] [US1] Add contract test for POST /api/edge/metadata/events in tests/contract/edge-private-video-metadata/us1-edgesitenode.contract.spec.ts
- [ ] T014 [P] [US1] Add integration test for site-local ingest and detection flow in tests/integration/edge-private-video-metadata/us1-metadataoutboxitem.integration.spec.ts

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create EdgeSiteNode and MetadataOutboxItem repository layer in services/edge-private-video-metadata-service/src/data/us1-edge-private-video-metadata.repository.ts
- [ ] T016 [US1] Implement site-local ingest and detection application service in services/edge-private-video-metadata-service/src/domain/us1/edge-private-video-metadata-us1.service.ts
- [ ] T017 [US1] Implement POST /api/edge/metadata/events and POST /api/edge/sites/{siteCode}/health routes in services/edge-private-video-metadata-service/src/api/us1/edge-private-video-metadata-us1.route.ts
- [ ] T018 [US1] Implement site-local ingest and detection role-layout screen in apps/mobile/src/role-layouts/edge-private-video-metadata/us1-edge-private-video-metadata.screen.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Anonymized Metadata Publication (Priority: P2)

**Goal**: Deliver anonymized metadata publication capabilities end-to-end.

**Independent Test**: Can be tested independently by inspecting cloud-bound payloads and confirming

### Tests for User Story 2

- [ ] T019 [P] [US2] Add contract test for POST /api/edge/metadata/batch in tests/contract/edge-private-video-metadata/us2-cameraingestsource.contract.spec.ts
- [ ] T020 [P] [US2] Add integration test for anonymized metadata publication flow in tests/integration/edge-private-video-metadata/us2-egresspolicyrule.integration.spec.ts

### Implementation for User Story 2

- [ ] T021 [P] [US2] Create CameraIngestSource and EgressPolicyRule repository layer in services/edge-private-video-metadata-service/src/data/us2-edge-private-video-metadata.repository.ts
- [ ] T022 [US2] Implement anonymized metadata publication application service in services/edge-private-video-metadata-service/src/domain/us2/edge-private-video-metadata-us2.service.ts
- [ ] T023 [US2] Implement POST /api/edge/metadata/batch and POST /api/edge/metadata/batch routes in services/edge-private-video-metadata-service/src/api/us2/edge-private-video-metadata-us2.route.ts
- [ ] T024 [US2] Implement anonymized metadata publication role-layout screen in apps/mobile/src/role-layouts/edge-private-video-metadata/us2-edge-private-video-metadata.screen.tsx

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Enforce Privacy Guardrails Across Sites (Priority: P3)

**Goal**: Deliver enforce privacy guardrails across sites capabilities end-to-end.

**Independent Test**: Can be tested independently by running policy checks and audit reviews across

### Tests for User Story 3

- [ ] T025 [P] [US3] Add contract test for GET /api/edge/sites/{siteCode}/egress-policy in tests/contract/edge-private-video-metadata/us3-localdetectionevent.contract.spec.ts
- [ ] T026 [P] [US3] Add integration test for enforce privacy guardrails across sites flow in tests/integration/edge-private-video-metadata/us3-egressauditevent.integration.spec.ts

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create LocalDetectionEvent and EgressAuditEvent repository layer in services/edge-private-video-metadata-service/src/data/us3-edge-private-video-metadata.repository.ts
- [ ] T028 [US3] Implement enforce privacy guardrails across sites application service in services/edge-private-video-metadata-service/src/domain/us3/edge-private-video-metadata-us3.service.ts
- [ ] T029 [US3] Implement GET /api/edge/sites/{siteCode}/egress-policy and GET /api/edge/sites/{siteCode}/egress-policy routes in services/edge-private-video-metadata-service/src/api/us3/edge-private-video-metadata-us3.route.ts
- [ ] T030 [US3] Implement enforce privacy guardrails across sites role-layout screen in apps/mobile/src/role-layouts/edge-private-video-metadata/us3-edge-private-video-metadata.screen.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, governance validation, and operational readiness across stories.

- [ ] T031 [P] Add edge-private-video-metadata performance and reliability metrics in services/edge-private-video-metadata-service/src/observability/edge-private-video-metadata.metrics.ts
- [ ] T032 Run edge-private-video-metadata quickstart validation scenarios in specs/008-edge-private-video-metadata/quickstart.md
- [ ] T033 [P] Add end-to-end cross-story regression suite in tests/e2e/edge-private-video-metadata/edge-private-video-metadata-workflow.e2e.spec.ts
- [ ] T034 Validate constitution gates (privacy, consent, phase sequencing, non-diagnostic) for edge-private-video-metadata in specs/008-edge-private-video-metadata/research.md

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
Task: "Add contract test for POST /api/edge/metadata/events in tests/contract/edge-private-video-metadata/us1-edgesitenode.contract.spec.ts"
Task: "Add integration test for site-local ingest and detection flow in tests/integration/edge-private-video-metadata/us1-metadataoutboxitem.integration.spec.ts"
Task: "Create EdgeSiteNode and MetadataOutboxItem repository layer in services/edge-private-video-metadata-service/src/data/us1-edge-private-video-metadata.repository.ts"
```

---

## Parallel Example: User Story 2

```bash
Task: "Add contract test for POST /api/edge/metadata/batch in tests/contract/edge-private-video-metadata/us2-cameraingestsource.contract.spec.ts"
Task: "Add integration test for anonymized metadata publication flow in tests/integration/edge-private-video-metadata/us2-egresspolicyrule.integration.spec.ts"
Task: "Create CameraIngestSource and EgressPolicyRule repository layer in services/edge-private-video-metadata-service/src/data/us2-edge-private-video-metadata.repository.ts"
```

---

## Parallel Example: User Story 3

```bash
Task: "Add contract test for GET /api/edge/sites/{siteCode}/egress-policy in tests/contract/edge-private-video-metadata/us3-localdetectionevent.contract.spec.ts"
Task: "Add integration test for enforce privacy guardrails across sites flow in tests/integration/edge-private-video-metadata/us3-egressauditevent.integration.spec.ts"
Task: "Create LocalDetectionEvent and EgressAuditEvent repository layer in services/edge-private-video-metadata-service/src/data/us3-edge-private-video-metadata.repository.ts"
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
