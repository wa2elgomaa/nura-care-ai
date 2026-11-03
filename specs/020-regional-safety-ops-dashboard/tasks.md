# Tasks: Regional Safety Ops Dashboard

**Input**: Design documents from `/specs/020-regional-safety-ops-dashboard/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because spec.md defines independent test criteria for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature module, contracts, and test scaffolding.

- [ ] T001 Create regional-safety-ops-dashboard service module scaffold in services/regional-safety-ops-dashboard-service/src/module/regional-safety-ops-dashboard.module.ts
- [ ] T002 Create regional-safety-ops-dashboard API controller scaffold in services/regional-safety-ops-dashboard-service/src/api/regional-safety-ops-dashboard.controller.ts
- [ ] T003 [P] Create regional-safety-ops-dashboard shared DTO and enum types in packages/shared-types/src/regional-safety-ops-dashboard/regional-safety-ops-dashboard.types.ts
- [ ] T004 [P] Create regional-safety-ops-dashboard feature configuration module in services/regional-safety-ops-dashboard-service/src/config/regional-safety-ops-dashboard.config.ts
- [ ] T005 [P] Create regional-safety-ops-dashboard test directories in tests/contract/regional-safety-ops-dashboard/, tests/integration/regional-safety-ops-dashboard/, and tests/e2e/regional-safety-ops-dashboard/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, policy, security, audit, and sync infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [ ] T006 Add RegionalCentreSnapshot, RegionalRiskBand, RegionalActionAssignment, TenantAccessScope, RegionalDashboardAuditEvent models in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for regional-safety-ops-dashboard domain models in packages/db/prisma/migrations/
- [ ] T008 [P] Implement RBAC and scope guard middleware for regional-safety-ops-dashboard routes in services/regional-safety-ops-dashboard-service/src/security/regional-safety-ops-dashboard-rbac.guard.ts
- [ ] T009 [P] Implement consent, residency, and non-diagnostic policy validator in services/regional-safety-ops-dashboard-service/src/domain/policy/regional-safety-ops-dashboard-policy-validator.service.ts
- [ ] T010 [P] Implement offline outbox and replay publisher for regional-safety-ops-dashboard events in packages/offline-sync/src/regional-safety-ops-dashboard/regional-safety-ops-dashboard.outbox.ts
- [ ] T011 [P] Implement immutable audit writer for regional-safety-ops-dashboard events in services/audit-service/src/regional-safety-ops-dashboard/regional-safety-ops-dashboard-audit-writer.service.ts
- [ ] T012 Implement deterministic regional-safety-ops-dashboard rules engine baseline in services/regional-safety-ops-dashboard-service/src/domain/rules/regional-safety-ops-dashboard-rules.service.ts
- [ ] T013 Implement Cloud Keycloak-only Regional Manager role enforcement policy in services/regional-ops-service/src/security/regional-manager-cloud-role.policy.ts
- [ ] T014 [P] Implement RBAC+ABAC tenant scope resolver for regional dashboard access in services/regional-ops-service/src/security/regional-abac-scope-resolver.service.ts

**Checkpoint**: Foundational baseline is complete; story work can proceed.

---

## Phase 3: User Story 1 - Cross-Centre Real-Time Oversight (Priority: P1) 🎯 MVP

**Goal**: Deliver cross-centre real-time oversight capabilities end-to-end.

**Independent Test**: Can be tested independently by opening the dashboard and confirming each managed

### Tests for User Story 1

- [ ] T015 [P] [US1] Add contract test for GET /api/regional/{regionCode}/snapshots in tests/contract/regional-safety-ops-dashboard/us1-regionalcentresnapshot.contract.spec.ts
- [ ] T016 [P] [US1] Add integration test for cross-centre real-time oversight flow in tests/integration/regional-safety-ops-dashboard/us1-tenantaccessscope.integration.spec.ts

### Implementation for User Story 1

- [ ] T017 [P] [US1] Create RegionalCentreSnapshot and TenantAccessScope repository layer in services/regional-safety-ops-dashboard-service/src/data/us1-regional-safety-ops-dashboard.repository.ts
- [ ] T018 [US1] Implement cross-centre real-time oversight application service in services/regional-safety-ops-dashboard-service/src/domain/us1/regional-safety-ops-dashboard-us1.service.ts
- [ ] T019 [US1] Implement GET /api/regional/{regionCode}/snapshots and GET /api/regional/{regionCode}/pickup-kpis routes in services/regional-safety-ops-dashboard-service/src/api/us1/regional-safety-ops-dashboard-us1.route.ts
- [ ] T020 [US1] Implement cross-centre real-time oversight role-layout screen in apps/mobile/src/role-layouts/regional-safety-ops-dashboard/us1-regional-safety-ops-dashboard.screen.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Incident and Compliance Triage (Priority: P2)

**Goal**: Deliver incident and compliance triage capabilities end-to-end.

**Independent Test**: Can be tested independently by reviewing centre rankings, incident summaries,

### Tests for User Story 2

- [ ] T021 [P] [US2] Add contract test for GET /api/regional/{regionCode}/centres/{centreId}/detail in tests/contract/regional-safety-ops-dashboard/us2-regionalriskband.contract.spec.ts
- [ ] T022 [P] [US2] Add integration test for incident and compliance triage flow in tests/integration/regional-safety-ops-dashboard/us2-regionaldashboardauditevent.integration.spec.ts

### Implementation for User Story 2

- [ ] T023 [P] [US2] Create RegionalRiskBand and RegionalDashboardAuditEvent repository layer in services/regional-safety-ops-dashboard-service/src/data/us2-regional-safety-ops-dashboard.repository.ts
- [ ] T024 [US2] Implement incident and compliance triage application service in services/regional-safety-ops-dashboard-service/src/domain/us2/regional-safety-ops-dashboard-us2.service.ts
- [ ] T025 [US2] Implement GET /api/regional/{regionCode}/centres/{centreId}/detail and GET /api/regional/{regionCode}/centres/{centreId}/detail routes in services/regional-safety-ops-dashboard-service/src/api/us2/regional-safety-ops-dashboard-us2.route.ts
- [ ] T026 [US2] Implement incident and compliance triage role-layout screen in apps/mobile/src/role-layouts/regional-safety-ops-dashboard/us2-regional-safety-ops-dashboard.screen.tsx

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Support Allocation and Follow-Through (Priority: P3)

**Goal**: Deliver support allocation and follow-through capabilities end-to-end.

**Independent Test**: Can be tested independently by creating support actions for flagged centres and

### Tests for User Story 3

- [ ] T027 [P] [US3] Add contract test for POST /api/regional/{regionCode}/actions in tests/contract/regional-safety-ops-dashboard/us3-regionalactionassignment.contract.spec.ts
- [ ] T028 [P] [US3] Add integration test for support allocation and follow-through flow in tests/integration/regional-safety-ops-dashboard/us3-regionalactionassignment.integration.spec.ts

### Implementation for User Story 3

- [ ] T029 [P] [US3] Create RegionalActionAssignment repository layer in services/regional-safety-ops-dashboard-service/src/data/us3-regional-safety-ops-dashboard.repository.ts
- [ ] T030 [US3] Implement support allocation and follow-through application service in services/regional-safety-ops-dashboard-service/src/domain/us3/regional-safety-ops-dashboard-us3.service.ts
- [ ] T031 [US3] Implement POST /api/regional/{regionCode}/actions and POST /api/regional/{regionCode}/actions routes in services/regional-safety-ops-dashboard-service/src/api/us3/regional-safety-ops-dashboard-us3.route.ts
- [ ] T032 [US3] Implement support allocation and follow-through role-layout screen in apps/mobile/src/role-layouts/regional-safety-ops-dashboard/us3-regional-safety-ops-dashboard.screen.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, governance validation, and operational readiness across stories.

- [ ] T033 [P] Add regional-safety-ops-dashboard performance and reliability metrics in services/regional-safety-ops-dashboard-service/src/observability/regional-safety-ops-dashboard.metrics.ts
- [ ] T034 Run regional-safety-ops-dashboard quickstart validation scenarios in specs/020-regional-safety-ops-dashboard/quickstart.md
- [ ] T035 [P] Add end-to-end cross-story regression suite in tests/e2e/regional-safety-ops-dashboard/regional-safety-ops-dashboard-workflow.e2e.spec.ts
- [ ] T036 Validate constitution gates (privacy, consent, phase sequencing, non-diagnostic) for regional-safety-ops-dashboard in specs/020-regional-safety-ops-dashboard/research.md

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
Task: "Add contract test for GET /api/regional/{regionCode}/snapshots in tests/contract/regional-safety-ops-dashboard/us1-regionalcentresnapshot.contract.spec.ts"
Task: "Add integration test for cross-centre real-time oversight flow in tests/integration/regional-safety-ops-dashboard/us1-tenantaccessscope.integration.spec.ts"
Task: "Create RegionalCentreSnapshot and TenantAccessScope repository layer in services/regional-safety-ops-dashboard-service/src/data/us1-regional-safety-ops-dashboard.repository.ts"
```

---

## Parallel Example: User Story 2

```bash
Task: "Add contract test for GET /api/regional/{regionCode}/centres/{centreId}/detail in tests/contract/regional-safety-ops-dashboard/us2-regionalriskband.contract.spec.ts"
Task: "Add integration test for incident and compliance triage flow in tests/integration/regional-safety-ops-dashboard/us2-regionaldashboardauditevent.integration.spec.ts"
Task: "Create RegionalRiskBand and RegionalDashboardAuditEvent repository layer in services/regional-safety-ops-dashboard-service/src/data/us2-regional-safety-ops-dashboard.repository.ts"
```

---

## Parallel Example: User Story 3

```bash
Task: "Add contract test for POST /api/regional/{regionCode}/actions in tests/contract/regional-safety-ops-dashboard/us3-regionalactionassignment.contract.spec.ts"
Task: "Add integration test for support allocation and follow-through flow in tests/integration/regional-safety-ops-dashboard/us3-regionalactionassignment.integration.spec.ts"
Task: "Create RegionalActionAssignment repository layer in services/regional-safety-ops-dashboard-service/src/data/us3-regional-safety-ops-dashboard.repository.ts"
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
