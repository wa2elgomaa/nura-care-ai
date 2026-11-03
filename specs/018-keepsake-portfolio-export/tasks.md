# Tasks: Keepsake Portfolio Export

**Input**: Design documents from `/specs/018-keepsake-portfolio-export/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because spec.md defines independent test criteria for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature module, contracts, and test scaffolding.

- [ ] T001 Create keepsake-portfolio-export service module scaffold in services/keepsake-portfolio-export-service/src/module/keepsake-portfolio-export.module.ts
- [ ] T002 Create keepsake-portfolio-export API controller scaffold in services/keepsake-portfolio-export-service/src/api/keepsake-portfolio-export.controller.ts
- [ ] T003 [P] Create keepsake-portfolio-export shared DTO and enum types in packages/shared-types/src/keepsake-portfolio-export/keepsake-portfolio-export.types.ts
- [ ] T004 [P] Create keepsake-portfolio-export feature configuration module in services/keepsake-portfolio-export-service/src/config/keepsake-portfolio-export.config.ts
- [ ] T005 [P] Create keepsake-portfolio-export test directories in tests/contract/keepsake-portfolio-export/, tests/integration/keepsake-portfolio-export/, and tests/e2e/keepsake-portfolio-export/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, policy, security, audit, and sync infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [ ] T006 Add PortfolioAsset, PortfolioConsentSnapshot, PortfolioExportRequest, PortfolioExportBundle, PortfolioExportAuditEvent models in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for keepsake-portfolio-export domain models in packages/db/prisma/migrations/
- [ ] T008 [P] Implement RBAC and scope guard middleware for keepsake-portfolio-export routes in services/keepsake-portfolio-export-service/src/security/keepsake-portfolio-export-rbac.guard.ts
- [ ] T009 [P] Implement consent, residency, and non-diagnostic policy validator in services/keepsake-portfolio-export-service/src/domain/policy/keepsake-portfolio-export-policy-validator.service.ts
- [ ] T010 [P] Implement offline outbox and replay publisher for keepsake-portfolio-export events in packages/offline-sync/src/keepsake-portfolio-export/keepsake-portfolio-export.outbox.ts
- [ ] T011 [P] Implement immutable audit writer for keepsake-portfolio-export events in services/audit-service/src/keepsake-portfolio-export/keepsake-portfolio-export-audit-writer.service.ts
- [ ] T012 Implement deterministic keepsake-portfolio-export rules engine baseline in services/keepsake-portfolio-export-service/src/domain/rules/keepsake-portfolio-export-rules.service.ts

**Checkpoint**: Foundational baseline is complete; story work can proceed.

---

## Phase 3: User Story 1 - Automatic Keepsake Curation (Priority: P1) 🎯 MVP

**Goal**: Deliver automatic keepsake curation capabilities end-to-end.

**Independent Test**: Can be tested independently by generating a portfolio for an eligible child and

### Tests for User Story 1

- [ ] T013 [P] [US1] Add contract test for POST /api/portfolio/exports in tests/contract/keepsake-portfolio-export/us1-portfolioasset.contract.spec.ts
- [ ] T014 [P] [US1] Add integration test for automatic keepsake curation flow in tests/integration/keepsake-portfolio-export/us1-portfolioexportbundle.integration.spec.ts

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create PortfolioAsset and PortfolioExportBundle repository layer in services/keepsake-portfolio-export-service/src/data/us1-keepsake-portfolio-export.repository.ts
- [ ] T016 [US1] Implement automatic keepsake curation application service in services/keepsake-portfolio-export-service/src/domain/us1/keepsake-portfolio-export-us1.service.ts
- [ ] T017 [US1] Implement POST /api/portfolio/exports and POST /api/portfolio/consent routes in services/keepsake-portfolio-export-service/src/api/us1/keepsake-portfolio-export-us1.route.ts
- [ ] T018 [US1] Implement automatic keepsake curation role-layout screen in apps/mobile/src/role-layouts/keepsake-portfolio-export/us1-keepsake-portfolio-export.screen.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Export and Long-Term Access (Priority: P2)

**Goal**: Deliver export and long-term access capabilities end-to-end.

**Independent Test**: Can be tested independently by exporting portfolios in supported formats and

### Tests for User Story 2

- [ ] T019 [P] [US2] Add contract test for GET /api/portfolio/exports/{exportId} in tests/contract/keepsake-portfolio-export/us2-portfolioconsentsnapshot.contract.spec.ts
- [ ] T020 [P] [US2] Add integration test for export and long-term access flow in tests/integration/keepsake-portfolio-export/us2-portfolioexportauditevent.integration.spec.ts

### Implementation for User Story 2

- [ ] T021 [P] [US2] Create PortfolioConsentSnapshot and PortfolioExportAuditEvent repository layer in services/keepsake-portfolio-export-service/src/data/us2-keepsake-portfolio-export.repository.ts
- [ ] T022 [US2] Implement export and long-term access application service in services/keepsake-portfolio-export-service/src/domain/us2/keepsake-portfolio-export-us2.service.ts
- [ ] T023 [US2] Implement GET /api/portfolio/exports/{exportId} and GET /api/portfolio/exports/{exportId} routes in services/keepsake-portfolio-export-service/src/api/us2/keepsake-portfolio-export-us2.route.ts
- [ ] T024 [US2] Implement export and long-term access role-layout screen in apps/mobile/src/role-layouts/keepsake-portfolio-export/us2-keepsake-portfolio-export.screen.tsx

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Optional Printed Photo-Book Upsell (Priority: P3)

**Goal**: Deliver optional printed photo-book upsell capabilities end-to-end.

**Independent Test**: Can be tested independently by initiating a print order from eligible portfolio

### Tests for User Story 3

- [ ] T025 [P] [US3] Add contract test for POST /api/portfolio/exports/{exportId}/download in tests/contract/keepsake-portfolio-export/us3-portfolioexportrequest.contract.spec.ts
- [ ] T026 [P] [US3] Add integration test for optional printed photo-book upsell flow in tests/integration/keepsake-portfolio-export/us3-portfolioexportrequest.integration.spec.ts

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create PortfolioExportRequest repository layer in services/keepsake-portfolio-export-service/src/data/us3-keepsake-portfolio-export.repository.ts
- [ ] T028 [US3] Implement optional printed photo-book upsell application service in services/keepsake-portfolio-export-service/src/domain/us3/keepsake-portfolio-export-us3.service.ts
- [ ] T029 [US3] Implement POST /api/portfolio/exports/{exportId}/download and POST /api/portfolio/exports/{exportId}/download routes in services/keepsake-portfolio-export-service/src/api/us3/keepsake-portfolio-export-us3.route.ts
- [ ] T030 [US3] Implement optional printed photo-book upsell role-layout screen in apps/mobile/src/role-layouts/keepsake-portfolio-export/us3-keepsake-portfolio-export.screen.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, governance validation, and operational readiness across stories.

- [ ] T031 [P] Add keepsake-portfolio-export performance and reliability metrics in services/keepsake-portfolio-export-service/src/observability/keepsake-portfolio-export.metrics.ts
- [ ] T032 Run keepsake-portfolio-export quickstart validation scenarios in specs/018-keepsake-portfolio-export/quickstart.md
- [ ] T033 [P] Add end-to-end cross-story regression suite in tests/e2e/keepsake-portfolio-export/keepsake-portfolio-export-workflow.e2e.spec.ts
- [ ] T034 Validate constitution gates (privacy, consent, phase sequencing, non-diagnostic) for keepsake-portfolio-export in specs/018-keepsake-portfolio-export/research.md

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
Task: "Add contract test for POST /api/portfolio/exports in tests/contract/keepsake-portfolio-export/us1-portfolioasset.contract.spec.ts"
Task: "Add integration test for automatic keepsake curation flow in tests/integration/keepsake-portfolio-export/us1-portfolioexportbundle.integration.spec.ts"
Task: "Create PortfolioAsset and PortfolioExportBundle repository layer in services/keepsake-portfolio-export-service/src/data/us1-keepsake-portfolio-export.repository.ts"
```

---

## Parallel Example: User Story 2

```bash
Task: "Add contract test for GET /api/portfolio/exports/{exportId} in tests/contract/keepsake-portfolio-export/us2-portfolioconsentsnapshot.contract.spec.ts"
Task: "Add integration test for export and long-term access flow in tests/integration/keepsake-portfolio-export/us2-portfolioexportauditevent.integration.spec.ts"
Task: "Create PortfolioConsentSnapshot and PortfolioExportAuditEvent repository layer in services/keepsake-portfolio-export-service/src/data/us2-keepsake-portfolio-export.repository.ts"
```

---

## Parallel Example: User Story 3

```bash
Task: "Add contract test for POST /api/portfolio/exports/{exportId}/download in tests/contract/keepsake-portfolio-export/us3-portfolioexportrequest.contract.spec.ts"
Task: "Add integration test for optional printed photo-book upsell flow in tests/integration/keepsake-portfolio-export/us3-portfolioexportrequest.integration.spec.ts"
Task: "Create PortfolioExportRequest repository layer in services/keepsake-portfolio-export-service/src/data/us3-keepsake-portfolio-export.repository.ts"
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
