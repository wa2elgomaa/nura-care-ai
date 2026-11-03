# Tasks: Edge Noise Spike Alerts

**Input**: Design documents from `/specs/014-edge-noise-spike-alerts/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because spec.md defines independent test criteria for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature module, contracts, and test scaffolding.

- [ ] T001 Create edge-noise-spike-alerts service module scaffold in services/edge-noise-spike-alerts-service/src/module/edge-noise-spike-alerts.module.ts
- [ ] T002 Create edge-noise-spike-alerts API controller scaffold in services/edge-noise-spike-alerts-service/src/api/edge-noise-spike-alerts.controller.ts
- [ ] T003 [P] Create edge-noise-spike-alerts shared DTO and enum types in packages/shared-types/src/edge-noise-spike-alerts/edge-noise-spike-alerts.types.ts
- [ ] T004 [P] Create edge-noise-spike-alerts feature configuration module in services/edge-noise-spike-alerts-service/src/config/edge-noise-spike-alerts.config.ts
- [ ] T005 [P] Create edge-noise-spike-alerts test directories in tests/contract/edge-noise-spike-alerts/, tests/integration/edge-noise-spike-alerts/, and tests/e2e/edge-noise-spike-alerts/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, policy, security, audit, and sync infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [ ] T006 Add NoiseAnomalyEvent, NoiseThresholdPolicy, NoiseAlert, AudioRetentionGuardAudit, NoiseIncidentAudit models in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for edge-noise-spike-alerts domain models in packages/db/prisma/migrations/
- [ ] T008 [P] Implement RBAC and scope guard middleware for edge-noise-spike-alerts routes in services/edge-noise-spike-alerts-service/src/security/edge-noise-spike-alerts-rbac.guard.ts
- [ ] T009 [P] Implement consent, residency, and non-diagnostic policy validator in services/edge-noise-spike-alerts-service/src/domain/policy/edge-noise-spike-alerts-policy-validator.service.ts
- [ ] T010 [P] Implement offline outbox and replay publisher for edge-noise-spike-alerts events in packages/offline-sync/src/edge-noise-spike-alerts/edge-noise-spike-alerts.outbox.ts
- [ ] T011 [P] Implement immutable audit writer for edge-noise-spike-alerts events in services/audit-service/src/edge-noise-spike-alerts/edge-noise-spike-alerts-audit-writer.service.ts
- [ ] T012 Implement deterministic edge-noise-spike-alerts rules engine baseline in services/edge-noise-spike-alerts-service/src/domain/rules/edge-noise-spike-alerts-rules.service.ts

**Checkpoint**: Foundational baseline is complete; story work can proceed.

---

## Phase 3: User Story 1 - Immediate Loud Spike Alerting (Priority: P1) 🎯 MVP

**Goal**: Deliver immediate loud spike alerting capabilities end-to-end.

**Independent Test**: Can be tested independently by simulating loud spike events in monitored play

### Tests for User Story 1

- [ ] T013 [P] [US1] Add contract test for POST /api/noise/events in tests/contract/edge-noise-spike-alerts/us1-noiseanomalyevent.contract.spec.ts
- [ ] T014 [P] [US1] Add integration test for immediate loud spike alerting flow in tests/integration/edge-noise-spike-alerts/us1-audioretentionguardaudit.integration.spec.ts

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create NoiseAnomalyEvent and AudioRetentionGuardAudit repository layer in services/edge-noise-spike-alerts-service/src/data/us1-edge-noise-spike-alerts.repository.ts
- [ ] T016 [US1] Implement immediate loud spike alerting application service in services/edge-noise-spike-alerts-service/src/domain/us1/edge-noise-spike-alerts-us1.service.ts
- [ ] T017 [US1] Implement POST /api/noise/events and GET /api/noise/alerts routes in services/edge-noise-spike-alerts-service/src/api/us1/edge-noise-spike-alerts-us1.route.ts
- [ ] T018 [US1] Implement immediate loud spike alerting role-layout screen in apps/mobile/src/role-layouts/edge-noise-spike-alerts/us1-edge-noise-spike-alerts.screen.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Alert Acknowledgement and Escalation (Priority: P2)

**Goal**: Deliver alert acknowledgement and escalation capabilities end-to-end.

**Independent Test**: Can be tested independently by issuing alerts, confirming acknowledgement

### Tests for User Story 2

- [ ] T019 [P] [US2] Add contract test for POST /api/noise/alerts/{alertId}/ack in tests/contract/edge-noise-spike-alerts/us2-noisethresholdpolicy.contract.spec.ts
- [ ] T020 [P] [US2] Add integration test for alert acknowledgement and escalation flow in tests/integration/edge-noise-spike-alerts/us2-noiseincidentaudit.integration.spec.ts

### Implementation for User Story 2

- [ ] T021 [P] [US2] Create NoiseThresholdPolicy and NoiseIncidentAudit repository layer in services/edge-noise-spike-alerts-service/src/data/us2-edge-noise-spike-alerts.repository.ts
- [ ] T022 [US2] Implement alert acknowledgement and escalation application service in services/edge-noise-spike-alerts-service/src/domain/us2/edge-noise-spike-alerts-us2.service.ts
- [ ] T023 [US2] Implement POST /api/noise/alerts/{alertId}/ack and POST /api/noise/alerts/{alertId}/ack routes in services/edge-noise-spike-alerts-service/src/api/us2/edge-noise-spike-alerts-us2.route.ts
- [ ] T024 [US2] Implement alert acknowledgement and escalation role-layout screen in apps/mobile/src/role-layouts/edge-noise-spike-alerts/us2-edge-noise-spike-alerts.screen.tsx

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Incident Pattern Review (Priority: P3)

**Goal**: Deliver incident pattern review capabilities end-to-end.

**Independent Test**: Can be tested independently by reviewing historical incidents and verifying

### Tests for User Story 3

- [ ] T025 [P] [US3] Add contract test for POST /api/noise/alerts/{alertId}/resolve in tests/contract/edge-noise-spike-alerts/us3-noisealert.contract.spec.ts
- [ ] T026 [P] [US3] Add integration test for incident pattern review flow in tests/integration/edge-noise-spike-alerts/us3-noisealert.integration.spec.ts

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create NoiseAlert repository layer in services/edge-noise-spike-alerts-service/src/data/us3-edge-noise-spike-alerts.repository.ts
- [ ] T028 [US3] Implement incident pattern review application service in services/edge-noise-spike-alerts-service/src/domain/us3/edge-noise-spike-alerts-us3.service.ts
- [ ] T029 [US3] Implement POST /api/noise/alerts/{alertId}/resolve and POST /api/noise/alerts/{alertId}/resolve routes in services/edge-noise-spike-alerts-service/src/api/us3/edge-noise-spike-alerts-us3.route.ts
- [ ] T030 [US3] Implement incident pattern review role-layout screen in apps/mobile/src/role-layouts/edge-noise-spike-alerts/us3-edge-noise-spike-alerts.screen.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, governance validation, and operational readiness across stories.

- [ ] T031 [P] Add edge-noise-spike-alerts performance and reliability metrics in services/edge-noise-spike-alerts-service/src/observability/edge-noise-spike-alerts.metrics.ts
- [ ] T032 Run edge-noise-spike-alerts quickstart validation scenarios in specs/014-edge-noise-spike-alerts/quickstart.md
- [ ] T033 [P] Add end-to-end cross-story regression suite in tests/e2e/edge-noise-spike-alerts/edge-noise-spike-alerts-workflow.e2e.spec.ts
- [ ] T034 Validate constitution gates (privacy, consent, phase sequencing, non-diagnostic) for edge-noise-spike-alerts in specs/014-edge-noise-spike-alerts/research.md

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
Task: "Add contract test for POST /api/noise/events in tests/contract/edge-noise-spike-alerts/us1-noiseanomalyevent.contract.spec.ts"
Task: "Add integration test for immediate loud spike alerting flow in tests/integration/edge-noise-spike-alerts/us1-audioretentionguardaudit.integration.spec.ts"
Task: "Create NoiseAnomalyEvent and AudioRetentionGuardAudit repository layer in services/edge-noise-spike-alerts-service/src/data/us1-edge-noise-spike-alerts.repository.ts"
```

---

## Parallel Example: User Story 2

```bash
Task: "Add contract test for POST /api/noise/alerts/{alertId}/ack in tests/contract/edge-noise-spike-alerts/us2-noisethresholdpolicy.contract.spec.ts"
Task: "Add integration test for alert acknowledgement and escalation flow in tests/integration/edge-noise-spike-alerts/us2-noiseincidentaudit.integration.spec.ts"
Task: "Create NoiseThresholdPolicy and NoiseIncidentAudit repository layer in services/edge-noise-spike-alerts-service/src/data/us2-edge-noise-spike-alerts.repository.ts"
```

---

## Parallel Example: User Story 3

```bash
Task: "Add contract test for POST /api/noise/alerts/{alertId}/resolve in tests/contract/edge-noise-spike-alerts/us3-noisealert.contract.spec.ts"
Task: "Add integration test for incident pattern review flow in tests/integration/edge-noise-spike-alerts/us3-noisealert.integration.spec.ts"
Task: "Create NoiseAlert repository layer in services/edge-noise-spike-alerts-service/src/data/us3-edge-noise-spike-alerts.repository.ts"
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
