# Tasks: Verified Visitor Check-In

**Input**: Design documents from `/specs/021-verified-visitor-checkin/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the visitor-access extension scaffolding and shared contracts.

- [ ] T001 Create visitor access service module scaffold in services/visitor-access-service/src/module/visitor-access.module.ts
- [ ] T002 Create visitor access API controller scaffold in services/visitor-access-service/src/api/visitor-access.controller.ts
- [ ] T003 [P] Create shared visitor access DTO/type definitions in packages/shared-types/src/visitor-access.ts
- [ ] T004 [P] Add visitor access feature flags and env config keys in services/visitor-access-service/src/config/visitor-access.config.ts
- [ ] T005 [P] Create visitor access test folders and baseline files in tests/contract/visitor-access/ and tests/integration/visitor-access/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement core foundations required by all user stories.

**CRITICAL**: No user story implementation starts before this phase is complete.

- [ ] T006 Add visitor domain models to Prisma schema in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for visitor check-in entities in packages/db/prisma/migrations/
- [ ] T008 [P] Implement tenant isolation repository filters (regionCode + organizationId + centreId) in services/visitor-access-service/src/data/tenant-scope.repository.ts
- [ ] T009 [P] Implement RBAC/ABAC authorization guard for visitor endpoints in services/visitor-access-service/src/security/visitor-access.guard.ts
- [ ] T010 Implement pickup-core integration client for QR/PIN/optional FACE reuse in services/visitor-access-service/src/integration/pickup-core.client.ts
- [ ] T011 [P] Implement consent notice and optional biometric consent validator in services/visitor-access-service/src/domain/consent/visitor-consent.service.ts
- [ ] T012 [P] Implement immutable visitor audit logger in services/visitor-access-service/src/domain/audit/visitor-audit.service.ts
- [ ] T013 Implement offline outbox for visitor check-in/out events in packages/offline-sync/src/visitor-access.outbox.ts
- [ ] T014 Enforce constitution non-diagnostic language and reason-code taxonomy in services/visitor-access-service/src/domain/policy/visitor-language-policy.ts

**Checkpoint**: Foundation complete. User stories can now proceed.

---

## Phase 3: User Story 1 - Verified Visitor Entry (Priority: P1) 🎯 MVP

**Goal**: Verify visitors at entry using reused pickup-grade rules and create a valid check-in session.

**Independent Test**: Valid QR/PIN (and consented FACE path) produces approved check-in session; invalid credentials are denied with reason code and audit log.

### Tests for User Story 1

- [ ] T015 [P] [US1] Add contract tests for POST /api/visitor/checkin in tests/contract/visitor-access/checkin.contract.spec.ts
- [ ] T016 [P] [US1] Add integration test for pickup-core delegation flow in tests/integration/visitor-access/checkin-pickup-delegation.integration.spec.ts

### Implementation for User Story 1

- [ ] T017 [P] [US1] Implement visitor verification attempt repository in services/visitor-access-service/src/data/visitor-verification-attempt.repository.ts
- [ ] T018 [US1] Implement check-in application service delegating to pickup core in services/visitor-access-service/src/domain/checkin/visitor-checkin.service.ts
- [ ] T019 [US1] Implement POST /api/visitor/checkin endpoint in services/visitor-access-service/src/api/checkin/post-visitor-checkin.route.ts
- [ ] T020 [US1] Implement denied-attempt escalation trigger in services/visitor-access-service/src/domain/alerts/visitor-denial-escalation.service.ts
- [ ] T021 [US1] Implement front-desk check-in workflow UI in apps/mobile/src/role-layouts/frontdesk/visitor-checkin/VisitorCheckinScreen.tsx
- [ ] T022 [US1] Persist check-in decision and audit entries in services/visitor-access-service/src/domain/checkin/visitor-checkin-persistence.service.ts

**Checkpoint**: US1 is independently functional and testable.

---

## Phase 4: User Story 2 - Expiry-Based Visitor Credentials (Priority: P2)

**Goal**: Issue and enforce time-bounded visitor credentials with override policy controls.

**Independent Test**: Credential valid only inside authorized window; expired credentials always denied and logged; director override path is controlled and auditable.

### Tests for User Story 2

- [ ] T023 [P] [US2] Add contract tests for POST /api/visitor/credentials in tests/contract/visitor-access/credentials.contract.spec.ts
- [ ] T024 [P] [US2] Add integration tests for expiry and centre-mismatch rules in tests/integration/visitor-access/credential-validity.integration.spec.ts

### Implementation for User Story 2

- [ ] T025 [P] [US2] Implement visitor credential repository in services/visitor-access-service/src/data/visitor-credential.repository.ts
- [ ] T026 [US2] Implement credential issuance and lifecycle service in services/visitor-access-service/src/domain/credentials/visitor-credential.service.ts
- [ ] T027 [US2] Implement credential validity rules engine (V1, V2) in services/visitor-access-service/src/domain/policy/visitor-credential-rules.service.ts
- [ ] T028 [US2] Implement POST /api/visitor/credentials endpoint in services/visitor-access-service/src/api/credentials/post-visitor-credentials.route.ts
- [ ] T029 [US2] Implement override approval workflow endpoint POST /api/visitor/overrides in services/visitor-access-service/src/api/overrides/post-visitor-overrides.route.ts
- [ ] T030 [US2] Implement director credential management screen in apps/mobile/src/role-layouts/director/visitor-checkin/VisitorCredentialManagementScreen.tsx

**Checkpoint**: US2 is independently functional and testable.

---

## Phase 5: User Story 3 - Building-Wide Visitor Tracking and Audit (Priority: P3)

**Goal**: Provide active visitor roster, historical tracking, and stale-session reconciliation.

**Independent Test**: Active roster reflects current check-ins/check-outs, history filters return full lifecycle records, and stale active sessions are flagged by rule.

### Tests for User Story 3

- [ ] T031 [P] [US3] Add contract tests for GET /api/visitor/active-roster in tests/contract/visitor-access/active-roster.contract.spec.ts
- [ ] T032 [P] [US3] Add integration tests for stale-active-visitor rule (V4) in tests/integration/visitor-access/stale-session-reconciliation.integration.spec.ts

### Implementation for User Story 3

- [ ] T033 [P] [US3] Implement visitor session repository in services/visitor-access-service/src/data/visitor-session.repository.ts
- [ ] T034 [US3] Implement check-out application service and endpoint in services/visitor-access-service/src/api/checkout/post-visitor-checkout.route.ts
- [ ] T035 [US3] Implement active occupancy roster query service in services/visitor-access-service/src/domain/roster/visitor-active-roster.service.ts
- [ ] T036 [US3] Implement stale session reconciliation worker in services/visitor-access-service/src/domain/reconciliation/visitor-session-reconciliation.worker.ts
- [ ] T037 [US3] Implement visitor history query endpoint with tenant-scoped filters in services/visitor-access-service/src/api/history/get-visitor-history.route.ts
- [ ] T038 [US3] Implement director visitor roster and history UI in apps/mobile/src/role-layouts/director/visitor-checkin/VisitorRosterAndHistoryScreen.tsx

**Checkpoint**: US3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening across all user stories.

- [ ] T039 [P] Add performance and latency instrumentation for check-in and roster queries in services/visitor-access-service/src/observability/visitor-access.metrics.ts
- [ ] T040 Run security tests for cross-tenant and cross-centre access denial in tests/integration/visitor-access/tenant-boundary-security.integration.spec.ts
- [ ] T041 Validate constitution gates and compliance evidence checklist in specs/021-verified-visitor-checkin/quickstart.md
- [ ] T042 [P] Update operational documentation for visitor check-in extension and pickup-core reuse in specs/021-verified-visitor-checkin/research.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no prerequisites.
- Foundational (Phase 2) depends on Setup and blocks all user stories.
- User Stories (Phases 3-5) depend on Foundational completion.
- Polish (Phase 6) depends on target user stories being complete.

### User Story Dependencies

- US1 (P1) starts after Phase 2 and is the MVP.
- US2 (P2) starts after Phase 2 and builds on shared visitor entities; it can be developed in parallel with late US1 UI polish.
- US3 (P3) starts after Phase 2 and depends on check-in/check-out event availability from US1/US2.

### Within Each User Story

- Tests should be written before implementation and fail first.
- Repository/data tasks before service logic.
- Service logic before endpoint wiring.
- Endpoint wiring before UI integration.

## Parallel Opportunities

- Phase 1: T003, T004, T005 can run in parallel after T001/T002.
- Phase 2: T008, T009, T011, T012 can run in parallel after T006/T007.
- US1: T015/T016 and T017 can run in parallel; T021 can start after endpoint contract is stable.
- US2: T023/T024 and T025 can run in parallel.
- US3: T031/T032 and T033 can run in parallel.

## Parallel Example: User Story 1

```bash
# Parallel test tasks
Task T015: Contract tests for check-in endpoint
Task T016: Integration test for pickup-core delegation

# Parallel implementation tasks
Task T017: Verification attempt repository
Task T021: Front-desk check-in UI (after API payload contract is frozen)
```

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2.
2. Complete US1 tasks (T015-T022).
3. Validate independent check-in verification and denial/audit behavior.
4. Demo/deploy MVP.

### Incremental Delivery

1. Add US2 expiry credentials and override governance.
2. Validate independent credential lifecycle behavior.
3. Add US3 active roster/history and stale-session reconciliation.
4. Complete Polish and compliance validation.
