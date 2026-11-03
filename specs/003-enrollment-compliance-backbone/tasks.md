# Tasks: Enrollment Compliance Backbone

**Input**: Design documents from `/specs/003-enrollment-compliance-backbone/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because spec.md defines independent test criteria for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature module, contracts, and test scaffolding.

- [ ] T001 Create enrollment-compliance-backbone service module scaffold in services/enrollment-compliance-backbone-service/src/module/enrollment-compliance-backbone.module.ts
- [ ] T002 Create enrollment-compliance-backbone API controller scaffold in services/enrollment-compliance-backbone-service/src/api/enrollment-compliance-backbone.controller.ts
- [ ] T003 [P] Create enrollment-compliance-backbone shared DTO and enum types in packages/shared-types/src/enrollment-compliance-backbone/enrollment-compliance-backbone.types.ts
- [ ] T004 [P] Create enrollment-compliance-backbone feature configuration module in services/enrollment-compliance-backbone-service/src/config/enrollment-compliance-backbone.config.ts
- [ ] T005 [P] Create enrollment-compliance-backbone test directories in tests/contract/enrollment-compliance-backbone/, tests/integration/enrollment-compliance-backbone/, and tests/e2e/enrollment-compliance-backbone/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, policy, security, audit, and sync infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [ ] T006 Add ChildComplianceProfile, EnrollmentFormRecord, MedicalAllergyRecord, ImmunizationProofRecord, EmergencyContactRecord, ConsentRecord, ConsentAuditEvent, ComplianceAuditEvent models in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for enrollment-compliance-backbone domain models in packages/db/prisma/migrations/
- [ ] T008 [P] Implement RBAC and scope guard middleware for enrollment-compliance-backbone routes in services/enrollment-compliance-backbone-service/src/security/enrollment-compliance-backbone-rbac.guard.ts
- [ ] T009 [P] Implement consent, residency, and non-diagnostic policy validator in services/enrollment-compliance-backbone-service/src/domain/policy/enrollment-compliance-backbone-policy-validator.service.ts
- [ ] T010 [P] Implement offline outbox and replay publisher for enrollment-compliance-backbone events in packages/offline-sync/src/enrollment-compliance-backbone/enrollment-compliance-backbone.outbox.ts
- [ ] T011 [P] Implement immutable audit writer for enrollment-compliance-backbone events in services/audit-service/src/enrollment-compliance-backbone/enrollment-compliance-backbone-audit-writer.service.ts
- [ ] T012 Implement deterministic enrollment-compliance-backbone rules engine baseline in services/enrollment-compliance-backbone-service/src/domain/rules/enrollment-compliance-backbone-rules.service.ts
- [ ] T013 Implement Cloud Keycloak parent-account provisioning client in services/enrollment-service/src/integration/keycloak/cloud-keycloak-admin.client.ts
- [ ] T014 [P] Implement Edge Keycloak sync trigger publisher for site-scoped parent identities in services/enrollment-service/src/integration/keycloak/parent-identity-sync.publisher.ts

**Checkpoint**: Foundational baseline is complete; story work can proceed.

---

## Phase 3: User Story 1 - Create Complete Enrollment Record (Priority: P1) 🎯 MVP

**Goal**: Deliver create complete enrollment record capabilities end-to-end.

**Independent Test**: Can be tested independently by enrolling a child and verifying all required

### Tests for User Story 1

- [ ] T015 [P] [US1] Add contract test for POST /api/compliance/children/{childId}/profiles in tests/contract/enrollment-compliance-backbone/us1-childcomplianceprofile.contract.spec.ts
- [ ] T016 [P] [US1] Add integration test for create complete enrollment record flow in tests/integration/enrollment-compliance-backbone/us1-immunizationproofrecord.integration.spec.ts

### Implementation for User Story 1

- [ ] T017 [P] [US1] Create ChildComplianceProfile and ImmunizationProofRecord and ConsentAuditEvent repository layer in services/enrollment-compliance-backbone-service/src/data/us1-enrollment-compliance-backbone.repository.ts
- [ ] T018 [US1] Implement create complete enrollment record application service in services/enrollment-compliance-backbone-service/src/domain/us1/enrollment-compliance-backbone-us1.service.ts
- [ ] T019 [US1] Implement POST /api/compliance/children/{childId}/profiles and POST /api/compliance/children/{childId}/consents routes in services/enrollment-compliance-backbone-service/src/api/us1/enrollment-compliance-backbone-us1.route.ts
- [ ] T020 [US1] Implement create complete enrollment record role-layout screen in apps/mobile/src/role-layouts/enrollment-compliance-backbone/us1-enrollment-compliance-backbone.screen.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Manage Consent Lifecycle (Priority: P2)

**Goal**: Deliver manage consent lifecycle capabilities end-to-end.

**Independent Test**: Can be tested independently by recording consent decisions, changing consent

### Tests for User Story 2

- [ ] T021 [P] [US2] Add contract test for GET /api/compliance/children/{childId}/profiles/current in tests/contract/enrollment-compliance-backbone/us2-enrollmentformrecord.contract.spec.ts
- [ ] T022 [P] [US2] Add integration test for manage consent lifecycle flow in tests/integration/enrollment-compliance-backbone/us2-emergencycontactrecord.integration.spec.ts

### Implementation for User Story 2

- [ ] T023 [P] [US2] Create EnrollmentFormRecord and EmergencyContactRecord and ComplianceAuditEvent repository layer in services/enrollment-compliance-backbone-service/src/data/us2-enrollment-compliance-backbone.repository.ts
- [ ] T024 [US2] Implement manage consent lifecycle application service in services/enrollment-compliance-backbone-service/src/domain/us2/enrollment-compliance-backbone-us2.service.ts
- [ ] T025 [US2] Implement GET /api/compliance/children/{childId}/profiles/current and GET /api/compliance/children/{childId}/consents/history routes in services/enrollment-compliance-backbone-service/src/api/us2/enrollment-compliance-backbone-us2.route.ts
- [ ] T026 [US2] Implement manage consent lifecycle role-layout screen in apps/mobile/src/role-layouts/enrollment-compliance-backbone/us2-enrollment-compliance-backbone.screen.tsx

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Produce Audit-Ready Compliance Evidence (Priority: P3)

**Goal**: Deliver produce audit-ready compliance evidence capabilities end-to-end.

**Independent Test**: Can be tested independently by generating evidence outputs for selected child

### Tests for User Story 3

- [ ] T027 [P] [US3] Add contract test for PUT /api/compliance/children/{childId}/documents/{documentId} in tests/contract/enrollment-compliance-backbone/us3-medicalallergyrecord.contract.spec.ts
- [ ] T028 [P] [US3] Add integration test for produce audit-ready compliance evidence flow in tests/integration/enrollment-compliance-backbone/us3-consentrecord.integration.spec.ts

### Implementation for User Story 3

- [ ] T029 [P] [US3] Create MedicalAllergyRecord and ConsentRecord repository layer in services/enrollment-compliance-backbone-service/src/data/us3-enrollment-compliance-backbone.repository.ts
- [ ] T030 [US3] Implement produce audit-ready compliance evidence application service in services/enrollment-compliance-backbone-service/src/domain/us3/enrollment-compliance-backbone-us3.service.ts
- [ ] T031 [US3] Implement PUT /api/compliance/children/{childId}/documents/{documentId} and GET /api/compliance/reports/completeness routes in services/enrollment-compliance-backbone-service/src/api/us3/enrollment-compliance-backbone-us3.route.ts
- [ ] T032 [US3] Implement produce audit-ready compliance evidence role-layout screen in apps/mobile/src/role-layouts/enrollment-compliance-backbone/us3-enrollment-compliance-backbone.screen.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, governance validation, and operational readiness across stories.

- [ ] T033 [P] Add enrollment-compliance-backbone performance and reliability metrics in services/enrollment-compliance-backbone-service/src/observability/enrollment-compliance-backbone.metrics.ts
- [ ] T034 Run enrollment-compliance-backbone quickstart validation scenarios in specs/003-enrollment-compliance-backbone/quickstart.md
- [ ] T035 [P] Add end-to-end cross-story regression suite in tests/e2e/enrollment-compliance-backbone/enrollment-compliance-backbone-workflow.e2e.spec.ts
- [ ] T036 Validate constitution gates (privacy, consent, phase sequencing, non-diagnostic) for enrollment-compliance-backbone in specs/003-enrollment-compliance-backbone/research.md

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
Task: "Add contract test for POST /api/compliance/children/{childId}/profiles in tests/contract/enrollment-compliance-backbone/us1-childcomplianceprofile.contract.spec.ts"
Task: "Add integration test for create complete enrollment record flow in tests/integration/enrollment-compliance-backbone/us1-immunizationproofrecord.integration.spec.ts"
Task: "Create ChildComplianceProfile and ImmunizationProofRecord and ConsentAuditEvent repository layer in services/enrollment-compliance-backbone-service/src/data/us1-enrollment-compliance-backbone.repository.ts"
```

---

## Parallel Example: User Story 2

```bash
Task: "Add contract test for GET /api/compliance/children/{childId}/profiles/current in tests/contract/enrollment-compliance-backbone/us2-enrollmentformrecord.contract.spec.ts"
Task: "Add integration test for manage consent lifecycle flow in tests/integration/enrollment-compliance-backbone/us2-emergencycontactrecord.integration.spec.ts"
Task: "Create EnrollmentFormRecord and EmergencyContactRecord and ComplianceAuditEvent repository layer in services/enrollment-compliance-backbone-service/src/data/us2-enrollment-compliance-backbone.repository.ts"
```

---

## Parallel Example: User Story 3

```bash
Task: "Add contract test for PUT /api/compliance/children/{childId}/documents/{documentId} in tests/contract/enrollment-compliance-backbone/us3-medicalallergyrecord.contract.spec.ts"
Task: "Add integration test for produce audit-ready compliance evidence flow in tests/integration/enrollment-compliance-backbone/us3-consentrecord.integration.spec.ts"
Task: "Create MedicalAllergyRecord and ConsentRecord repository layer in services/enrollment-compliance-backbone-service/src/data/us3-enrollment-compliance-backbone.repository.ts"
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
