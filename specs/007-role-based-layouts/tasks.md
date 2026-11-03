# Tasks: Role-Based Layouts

**Input**: Design documents from `/specs/007-role-based-layouts/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because the specification defines independent test criteria per user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize unified role-layout and identity integration scaffolding.

- [ ] T001 Create role-layout module scaffold in apps/mobile/src/role-layouts/index.ts
- [ ] T002 Create identity integration module scaffold in services/identity-service/src/module/identity.module.ts
- [ ] T003 [P] Create role-layout shared types in packages/shared-types/src/role-layouts/role-layout.types.ts
- [ ] T004 [P] Create OIDC client configuration module in apps/mobile/src/auth/oidc/oidc.config.ts
- [ ] T005 [P] Create role-layout test directories in tests/contract/role-layouts/, tests/integration/role-layouts/, and tests/e2e/role-layouts/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core auth, role policy, session, and audit foundations required across all user stories.

**⚠️ CRITICAL**: No user story work starts until this phase is complete.

- [ ] T006 Add UserRoleAssignment, RoleLayoutProfile, RoleContextSession, RoleAccessPolicy, OidcSessionEvent, and RoleEscalationAuditEvent models in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for role-layout and OIDC session models in packages/db/prisma/migrations/
- [ ] T008 Implement Cloud Keycloak OIDC provider client in services/identity-service/src/providers/keycloak/cloud-oidc.provider.ts
- [ ] T009 Implement Edge Keycloak issuer resolver for teacher/director sessions in services/identity-service/src/providers/keycloak/edge-issuer-resolver.service.ts
- [ ] T010 [P] Implement PKCE challenge/verifier utilities for web and mobile flows in apps/mobile/src/auth/oidc/pkce.util.ts
- [ ] T011 [P] Implement secure token storage and refresh scheduler in apps/mobile/src/auth/session/token-session.store.ts
- [ ] T012 [P] Implement Keycloak group/role to app-role mapper in services/identity-service/src/domain/roles/keycloak-role-mapper.service.ts
- [ ] T013 Implement deterministic role-priority policy engine in services/identity-service/src/domain/roles/role-priority-policy.service.ts
- [ ] T014 [P] Implement role-routing and role-switch audit writer in services/audit-service/src/identity/role-routing-audit-writer.service.ts
- [ ] T015 [P] Implement role-based navigation visibility guard middleware in apps/mobile/src/navigation/role-visibility.guard.ts

**Checkpoint**: Foundation complete; user stories can proceed.

---

## Phase 3: User Story 1 - Role-Driven Experience Selection (Priority: P1) 🎯 MVP

**Goal**: Authenticated users land in the correct role-specific layout in one app surface.

**Independent Test**: Authenticate as Parent, Teacher, Director, and Tablet users and verify each is routed to the correct initial layout within 2 seconds.

### Tests for User Story 1

- [ ] T016 [P] [US1] Add contract tests for GET /api/identity/me/roles in tests/contract/role-layouts/get-identity-roles.contract.spec.ts
- [ ] T017 [P] [US1] Add contract tests for GET /api/layouts/role/{role} in tests/contract/role-layouts/get-role-layout.contract.spec.ts
- [ ] T018 [P] [US1] Add integration tests for OIDC auth-code and PKCE login flows in tests/integration/role-layouts/oidc-login-flow.integration.spec.ts
- [ ] T019 [P] [US1] Add integration tests for Edge Keycloak issuer selection for teacher/director sessions in tests/integration/role-layouts/edge-issuer-selection.integration.spec.ts

### Implementation for User Story 1

- [ ] T020 [P] [US1] Implement role-layout profile repository in services/identity-service/src/data/role-layout-profile.repository.ts
- [ ] T021 [US1] Implement role-context bootstrap service from Keycloak claims in services/identity-service/src/domain/session/role-context-bootstrap.service.ts
- [ ] T022 [US1] Implement role entry router in apps/mobile/src/navigation/role-entry.router.ts
- [ ] T023 [US1] Implement Parent layout entry shell in apps/mobile/src/role-layouts/parent/ParentHomeLayout.tsx
- [ ] T024 [US1] Implement Teacher layout entry shell in apps/mobile/src/role-layouts/teacher/TeacherHomeLayout.tsx
- [ ] T025 [US1] Implement Director layout entry shell in apps/mobile/src/role-layouts/director/DirectorHomeLayout.tsx
- [ ] T026 [US1] Implement Tablet layout entry shell in apps/mobile/src/role-layouts/tablet/TabletHomeLayout.tsx

**Checkpoint**: US1 is independently functional and testable.

---

## Phase 4: User Story 2 - Unified Feature Behavior Across Roles (Priority: P2)

**Goal**: Shared workflows stay behaviorally consistent across roles while role permissions control visibility and actions.

**Independent Test**: Execute the same shared workflow under multiple roles and verify identical core outcomes with role-appropriate controls only.

### Tests for User Story 2

- [ ] T027 [P] [US2] Add contract tests for GET /api/access-policies/{role} in tests/contract/role-layouts/get-access-policy.contract.spec.ts
- [ ] T028 [P] [US2] Add integration tests for role-specific navigation visibility in tests/integration/role-layouts/role-visibility.integration.spec.ts
- [ ] T029 [P] [US2] Add integration tests for live role-assignment updates during active sessions in tests/integration/role-layouts/live-role-update.integration.spec.ts

### Implementation for User Story 2

- [ ] T030 [P] [US2] Implement role access-policy repository in services/identity-service/src/data/role-access-policy.repository.ts
- [ ] T031 [US2] Implement shared-workflow adapter layer with role wrappers in apps/mobile/src/workflows/shared/role-workflow.adapter.ts
- [ ] T032 [US2] Implement role-switch session update service in services/identity-service/src/domain/session/role-switch.service.ts
- [ ] T033 [US2] Implement POST /api/role-context/sessions endpoint in services/identity-service/src/api/session/post-role-context-session.route.ts
- [ ] T034 [US2] Implement POST /api/role-context/sessions/{sessionId}/switch endpoint in services/identity-service/src/api/session/post-role-context-switch.route.ts
- [ ] T035 [US2] Implement shared-tablet secure user-switch flow in apps/mobile/src/role-layouts/tablet/TabletUserSwitchFlow.tsx

**Checkpoint**: US2 is independently functional and testable.

---

## Phase 5: User Story 3 - Reduce Delivery Overhead with One App Surface (Priority: P3)

**Goal**: Consolidated release readiness proves one codebase can safely ship role variants with lower overhead.

**Independent Test**: Validate release checks demonstrate cross-role workflow parity and confirm one release artifact updates all role layouts.

### Tests for User Story 3

- [ ] T036 [P] [US3] Add E2E tests for cross-role regression matrix in tests/e2e/role-layouts/cross-role-regression-matrix.e2e.spec.ts
- [ ] T037 [P] [US3] Add integration tests for logout/session reset and cross-role cache clearing in tests/integration/role-layouts/session-reset-leakage.integration.spec.ts

### Implementation for User Story 3

- [ ] T038 [P] [US3] Implement consolidated release-readiness validator for role workflows in services/identity-service/src/quality/role-release-readiness.validator.ts
- [ ] T039 [US3] Implement role-targeted feature exposure service in services/identity-service/src/domain/flags/role-feature-exposure.service.ts
- [ ] T040 [US3] Implement role-routing operations dashboard for product/engineering visibility in apps/admin/src/operations/role-layouts/RoleDeliveryHealthDashboard.tsx
- [ ] T041 [US3] Implement role-layout parity metrics exporter in services/identity-service/src/observability/role-layout-parity.metrics.ts

**Checkpoint**: US3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Harden reliability, security, and governance checks across all stories.

- [ ] T042 [P] Add OIDC token refresh failure telemetry and alert thresholds in services/identity-service/src/observability/oidc-refresh-health.metrics.ts
- [ ] T043 Run quickstart validation scenarios for role routing, multi-role selection, and offline continuity in specs/007-role-based-layouts/quickstart.md
- [ ] T044 [P] Add security hardening checks for session isolation on shared tablet contexts in tests/e2e/role-layouts/tablet-session-isolation.e2e.spec.ts
- [ ] T045 Validate constitution gates for Keycloak OIDC, PKCE, role mapping, and non-diagnostic boundaries in specs/007-role-based-layouts/research.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories.
- **User Stories (Phase 3+)**: Depend on Foundational completion.
- **Polish (Phase 6)**: Depends on completion of targeted user stories.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational and delivers MVP role-driven entry.
- **US2 (P2)**: Starts after Foundational and extends shared workflow consistency.
- **US3 (P3)**: Starts after Foundational and adds release-overhead reduction controls.

### Within Each User Story

- Tests must fail before implementation.
- Data/policy repositories before session/layout services.
- Services before API routes.
- API routes before final UI integration and release checks.

## Parallel Opportunities

- Setup: T003-T005 can run in parallel.
- Foundational: T010-T012 and T014-T015 can run in parallel after schema and provider baseline.
- US1: T016-T020 can run in parallel, then converge on T021-T026.
- US2: T027-T030 can run in parallel, then T031-T035.
- US3: T036-T038 can run in parallel, then T039-T041.
- Polish: T042, T044, and T045 can run in parallel.

---

## Parallel Example: User Story 1

```bash
Task: "Add contract tests for GET /api/identity/me/roles in tests/contract/role-layouts/get-identity-roles.contract.spec.ts"
Task: "Add integration tests for OIDC auth-code and PKCE login flows in tests/integration/role-layouts/oidc-login-flow.integration.spec.ts"
Task: "Implement role-layout profile repository in services/identity-service/src/data/role-layout-profile.repository.ts"
Task: "Add integration tests for Edge Keycloak issuer selection for teacher/director sessions in tests/integration/role-layouts/edge-issuer-selection.integration.spec.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate role entry routing and OIDC/PKCE flow behavior.
4. Demo/deploy unified role-entry MVP.

### Incremental Delivery

1. Deliver US1 and validate.
2. Deliver US2 and validate shared workflow consistency.
3. Deliver US3 and validate release-readiness consolidation.
4. Complete Polish phase and run full quickstart scenarios.

### Parallel Team Strategy

1. Team completes Setup and Foundational together.
2. After Foundational:
   - Engineer A owns US1 routing and layout shells.
   - Engineer B owns US2 session switching and policy flows.
   - Engineer C owns US3 parity metrics and release validators.
3. Integrate with cross-role E2E and governance checks in Polish phase.
