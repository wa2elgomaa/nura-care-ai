# Tasks: Staff Compliance Tracker

**Input**: Design documents from `/specs/001-staff-compliance-tracker/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because the specification defines independent test criteria per user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize compliance module scaffolding and shared contracts.

- [ ] T001 Create compliance service module scaffold in services/compliance-service/src/module/compliance.module.ts
- [ ] T002 Create compliance API controller scaffold in services/compliance-service/src/api/compliance.controller.ts
- [ ] T003 [P] Create compliance DTOs and enums in packages/shared-types/src/compliance/compliance.types.ts
- [ ] T004 [P] Create compliance feature configuration (warning windows and thresholds) in services/compliance-service/src/config/compliance.config.ts
- [ ] T005 [P] Create compliance test directories in tests/contract/compliance/, tests/integration/compliance/, and tests/e2e/compliance/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared persistence, policy, identity provisioning, and audit foundations required by all user stories.

**⚠️ CRITICAL**: No user story work starts until this phase is complete.

- [ ] T006 Add StaffMember, CredentialRecord, RoomRequirement, RoomAssignment, ComplianceAlert, ComplianceSnapshot, and ComplianceAuditEvent models in packages/db/prisma/schema.prisma
- [ ] T007 Add IdentityProvisioningEvent model for Cloud/Edge Keycloak sync tracking in packages/db/prisma/schema.prisma
- [ ] T008 Generate Prisma migration for compliance and identity provisioning models in packages/db/prisma/migrations/
- [ ] T009 [P] Implement director/admin RBAC guard for compliance routes in services/compliance-service/src/security/compliance-rbac.guard.ts
- [ ] T010 [P] Implement regional/site scope filter middleware in services/compliance-service/src/security/compliance-scope-filter.ts
- [ ] T011 [P] Implement immutable compliance audit writer in services/audit-service/src/compliance/compliance-audit-writer.service.ts
- [ ] T012 Configure Cloud Keycloak Admin API client for staff identity provisioning in services/compliance-service/src/integration/keycloak/cloud-keycloak-admin.client.ts
- [ ] T013 Implement staff provisioning outbox publisher for Edge Keycloak sync trigger events in services/compliance-service/src/integration/keycloak/staff-identity-sync.publisher.ts
- [ ] T014 [P] Implement Keycloak group/role mapper for staff role assignments in services/compliance-service/src/integration/keycloak/staff-role-mapper.service.ts
- [ ] T015 [P] Implement offline sync outbox for credential and room-policy updates in packages/offline-sync/src/compliance/compliance-updates.outbox.ts
- [ ] T016 [P] Implement retention and residency policy validator for snapshots and logs in services/compliance-service/src/domain/policy/compliance-retention-policy.service.ts
- [ ] T017 Implement deterministic credential status rules in services/compliance-service/src/domain/rules/credential-compliance-status.rules.ts
- [ ] T018 Implement deterministic room shortfall rules in services/compliance-service/src/domain/rules/room-coverage-shortfall.rules.ts

**Checkpoint**: Foundation complete; user stories can proceed.

---

## Phase 3: User Story 1 - Track Credential Expiry and Deadlines (Priority: P1) 🎯 MVP

**Goal**: Directors can track staff credential status, expiry windows, and overdue deadlines with audit-safe updates.

**Independent Test**: Seed mixed credential expiry dates and verify compliant/expiring/expired status plus expiring and overdue lists update correctly.

### Tests for User Story 1

- [ ] T019 [P] [US1] Add contract tests for GET /api/compliance/staff in tests/contract/compliance/get-staff-compliance.contract.spec.ts
- [ ] T020 [P] [US1] Add contract tests for PUT /api/compliance/staff/{staffId}/credentials/{credentialId} in tests/contract/compliance/put-credential-update.contract.spec.ts
- [ ] T021 [P] [US1] Add integration tests for credential status transitions and warning windows in tests/integration/compliance/credential-status.integration.spec.ts
- [ ] T022 [P] [US1] Add integration tests for staff create -> Cloud Keycloak upsert -> Edge sync trigger in tests/integration/compliance/staff-keycloak-provisioning.integration.spec.ts

### Implementation for User Story 1

- [ ] T023 [P] [US1] Implement staff and credential repositories in services/compliance-service/src/data/staff-member.repository.ts and services/compliance-service/src/data/credential-record.repository.ts
- [ ] T024 [US1] Implement credential update and recomputation service in services/compliance-service/src/domain/credentials/credential-update.service.ts
- [ ] T025 [US1] Implement staff compliance query service with expiring-window filtering in services/compliance-service/src/domain/credentials/staff-compliance-query.service.ts
- [ ] T026 [US1] Implement staff onboarding identity provisioning service in services/compliance-service/src/domain/identity/staff-identity-provisioning.service.ts
- [ ] T027 [US1] Implement GET /api/compliance/staff endpoint in services/compliance-service/src/api/staff/get-staff-compliance.route.ts
- [ ] T028 [US1] Implement PUT /api/compliance/staff/{staffId}/credentials/{credentialId} endpoint in services/compliance-service/src/api/staff/put-credential-update.route.ts
- [ ] T029 [US1] Implement director credential compliance screen in apps/mobile/src/role-layouts/director/compliance/StaffCredentialComplianceScreen.tsx

**Checkpoint**: US1 is independently functional and testable.

---

## Phase 4: User Story 2 - Monitor Ratio-Qualified Coverage by Room (Priority: P2)

**Goal**: Directors can detect room-level qualified-staff shortfalls before operations or audits are impacted.

**Independent Test**: Configure room thresholds and assignments, then verify each room shows required versus current qualified counts and exact shortfalls.

### Tests for User Story 2

- [ ] T030 [P] [US2] Add contract tests for GET /api/compliance/rooms/coverage in tests/contract/compliance/get-room-coverage.contract.spec.ts
- [ ] T031 [P] [US2] Add integration tests for assignment-driven room coverage recalculation in tests/integration/compliance/room-coverage-recalculation.integration.spec.ts

### Implementation for User Story 2

- [ ] T032 [P] [US2] Implement room requirement and assignment repositories in services/compliance-service/src/data/room-requirement.repository.ts and services/compliance-service/src/data/room-assignment.repository.ts
- [ ] T033 [US2] Implement room coverage projection service in services/compliance-service/src/domain/coverage/room-coverage-projection.service.ts
- [ ] T034 [US2] Implement room shortfall alert service in services/compliance-service/src/domain/coverage/room-shortfall-alert.service.ts
- [ ] T035 [US2] Implement GET /api/compliance/rooms/coverage endpoint in services/compliance-service/src/api/rooms/get-room-coverage.route.ts
- [ ] T036 [US2] Implement director room coverage screen in apps/mobile/src/role-layouts/director/compliance/RoomCoverageComplianceScreen.tsx

**Checkpoint**: US2 is independently functional and testable.

---

## Phase 5: User Story 3 - Produce Inspector-Ready Compliance Evidence (Priority: P3)

**Goal**: Directors can generate timestamped compliance evidence with immutable history for inspections.

**Independent Test**: Generate a snapshot from known test data and verify it includes credential statuses, deadlines, room coverage, and immutable audit references.

### Tests for User Story 3

- [ ] T037 [P] [US3] Add contract tests for POST /api/compliance/snapshots in tests/contract/compliance/post-compliance-snapshot.contract.spec.ts
- [ ] T038 [P] [US3] Add contract tests for GET /api/compliance/snapshots/{snapshotId} and GET /api/compliance/audit-events in tests/contract/compliance/get-snapshot-and-audit.contract.spec.ts
- [ ] T039 [P] [US3] Add integration tests for snapshot immutability and payload consistency in tests/integration/compliance/snapshot-audit.integration.spec.ts

### Implementation for User Story 3

- [ ] T040 [P] [US3] Implement compliance snapshot repository in services/compliance-service/src/data/compliance-snapshot.repository.ts
- [ ] T041 [US3] Implement snapshot generation service in services/compliance-service/src/domain/snapshots/compliance-snapshot-generation.service.ts
- [ ] T042 [US3] Implement snapshot query and payload-hash validation service in services/compliance-service/src/domain/snapshots/compliance-snapshot-query.service.ts
- [ ] T043 [US3] Implement POST /api/compliance/snapshots endpoint in services/compliance-service/src/api/snapshots/post-compliance-snapshot.route.ts
- [ ] T044 [US3] Implement GET /api/compliance/snapshots/{snapshotId} endpoint in services/compliance-service/src/api/snapshots/get-compliance-snapshot.route.ts
- [ ] T045 [US3] Implement GET /api/compliance/audit-events endpoint in services/compliance-service/src/api/audit/get-compliance-audit-events.route.ts
- [ ] T046 [US3] Implement director inspector evidence screen in apps/mobile/src/role-layouts/director/compliance/InspectorComplianceSnapshotScreen.tsx

**Checkpoint**: US3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate production readiness, performance, and constitution compliance across all stories.

- [ ] T047 [P] Add compliance dashboard and rule-engine performance metrics in services/compliance-service/src/observability/compliance-performance.metrics.ts
- [ ] T048 Run offline sync reconciliation and replay resilience tests in tests/integration/compliance/offline-sync-reconciliation.integration.spec.ts
- [ ] T049 [P] Add end-to-end director workflow test across credential, coverage, and snapshot flows in tests/e2e/compliance/director-compliance-workflow.e2e.spec.ts
- [ ] T050 Validate constitution gates and quickstart scenarios in specs/001-staff-compliance-tracker/quickstart.md
- [ ] T051 [P] Update compliance operator runbook with Keycloak provisioning failure handling in specs/001-staff-compliance-tracker/research.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories.
- **User Stories (Phase 3+)**: Depend on Foundational completion.
- **Polish (Phase 6)**: Depends on completion of targeted user stories.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational and delivers the MVP.
- **US2 (P2)**: Starts after Foundational and uses shared rules/audit infrastructure.
- **US3 (P3)**: Starts after Foundational and uses outputs from US1 and US2 for complete evidence generation.

### Within Each User Story

- Tests must fail before implementation.
- Repositories before services.
- Services before API routes.
- API routes before role-layout UI integration.

## Parallel Opportunities

- Setup: T003-T005 can run in parallel.
- Foundational: T009-T011 and T014-T016 can run in parallel after schema/migration tasks.
- US1: T019-T023 can run in parallel, then converge on T024-T029.
- US2: T030-T032 can run in parallel, then T033-T036.
- US3: T037-T040 can run in parallel, then T041-T046.
- Polish: T047, T049, and T051 can run in parallel.

---

## Parallel Example: User Story 1

```bash
Task: "Add contract tests for GET /api/compliance/staff in tests/contract/compliance/get-staff-compliance.contract.spec.ts"
Task: "Add contract tests for PUT /api/compliance/staff/{staffId}/credentials/{credentialId} in tests/contract/compliance/put-credential-update.contract.spec.ts"
Task: "Implement staff and credential repositories in services/compliance-service/src/data/staff-member.repository.ts and services/compliance-service/src/data/credential-record.repository.ts"
Task: "Add integration tests for staff create -> Cloud Keycloak upsert -> Edge sync trigger in tests/integration/compliance/staff-keycloak-provisioning.integration.spec.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate independent US1 acceptance criteria.
4. Demo/deploy credential-expiry MVP.

### Incremental Delivery

1. Deliver US1 and validate.
2. Deliver US2 and validate room shortfall logic.
3. Deliver US3 and validate inspector evidence outputs.
4. Complete Polish phase and execute quickstart validation.

### Parallel Team Strategy

1. Team completes Setup and Foundational together.
2. After Foundational:
   - Engineer A owns US1 API + domain logic.
   - Engineer B owns US2 room coverage pipeline.
   - Engineer C owns US3 snapshot/reporting workflow.
3. Integrate in Polish phase with full cross-story validation.
