# Tasks: Billing Finance Automation

**Input**: Design documents from `/specs/005-billing-finance-automation/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because spec.md defines independent test criteria for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature module, contracts, and test scaffolding.

- [ ] T001 Create billing-finance-automation service module scaffold in services/billing-finance-automation-service/src/module/billing-finance-automation.module.ts
- [ ] T002 Create billing-finance-automation API controller scaffold in services/billing-finance-automation-service/src/api/billing-finance-automation.controller.ts
- [ ] T003 [P] Create billing-finance-automation shared DTO and enum types in packages/shared-types/src/billing-finance-automation/billing-finance-automation.types.ts
- [ ] T004 [P] Create billing-finance-automation feature configuration module in services/billing-finance-automation-service/src/config/billing-finance-automation.config.ts
- [ ] T005 [P] Create billing-finance-automation test directories in tests/contract/billing-finance-automation/, tests/integration/billing-finance-automation/, and tests/e2e/billing-finance-automation/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, policy, security, audit, and sync infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [ ] T006 Add FamilyBillingAccount, Invoice, InvoiceLine, SubsidyAllocation, VoucherApplication, PaymentTransaction, TaxReceipt, FinanceAuditEvent models in packages/db/prisma/schema.prisma
- [ ] T007 Generate Prisma migration for billing-finance-automation domain models in packages/db/prisma/migrations/
- [ ] T008 [P] Implement RBAC and scope guard middleware for billing-finance-automation routes in services/billing-finance-automation-service/src/security/billing-finance-automation-rbac.guard.ts
- [ ] T009 [P] Implement consent, residency, and non-diagnostic policy validator in services/billing-finance-automation-service/src/domain/policy/billing-finance-automation-policy-validator.service.ts
- [ ] T010 [P] Implement offline outbox and replay publisher for billing-finance-automation events in packages/offline-sync/src/billing-finance-automation/billing-finance-automation.outbox.ts
- [ ] T011 [P] Implement immutable audit writer for billing-finance-automation events in services/audit-service/src/billing-finance-automation/billing-finance-automation-audit-writer.service.ts
- [ ] T012 Implement deterministic billing-finance-automation rules engine baseline in services/billing-finance-automation-service/src/domain/rules/billing-finance-automation-rules.service.ts

**Checkpoint**: Foundational baseline is complete; story work can proceed.

---

## Phase 3: User Story 1 - Generate Accurate Family Invoices (Priority: P1) 🎯 MVP

**Goal**: Deliver generate accurate family invoices capabilities end-to-end.

**Independent Test**: Can be tested independently by generating invoices for multiple families and

### Tests for User Story 1

- [ ] T013 [P] [US1] Add contract test for POST /api/billing/invoices/generate in tests/contract/billing-finance-automation/us1-familybillingaccount.contract.spec.ts
- [ ] T014 [P] [US1] Add integration test for generate accurate family invoices flow in tests/integration/billing-finance-automation/us1-subsidyallocation.integration.spec.ts

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create FamilyBillingAccount and SubsidyAllocation and TaxReceipt repository layer in services/billing-finance-automation-service/src/data/us1-billing-finance-automation.repository.ts
- [ ] T016 [US1] Implement generate accurate family invoices application service in services/billing-finance-automation-service/src/domain/us1/billing-finance-automation-us1.service.ts
- [ ] T017 [US1] Implement POST /api/billing/invoices/generate and POST /api/billing/payments/schedule routes in services/billing-finance-automation-service/src/api/us1/billing-finance-automation-us1.route.ts
- [ ] T018 [US1] Implement generate accurate family invoices role-layout screen in apps/mobile/src/role-layouts/billing-finance-automation/us1-billing-finance-automation.screen.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Apply Subsidies and Vouchers (Priority: P2)

**Goal**: Deliver apply subsidies and vouchers capabilities end-to-end.

**Independent Test**: Can be tested independently by applying different subsidy and voucher rules and

### Tests for User Story 2

- [ ] T019 [P] [US2] Add contract test for GET /api/billing/invoices in tests/contract/billing-finance-automation/us2-invoice.contract.spec.ts
- [ ] T020 [P] [US2] Add integration test for apply subsidies and vouchers flow in tests/integration/billing-finance-automation/us2-voucherapplication.integration.spec.ts

### Implementation for User Story 2

- [ ] T021 [P] [US2] Create Invoice and VoucherApplication and FinanceAuditEvent repository layer in services/billing-finance-automation-service/src/data/us2-billing-finance-automation.repository.ts
- [ ] T022 [US2] Implement apply subsidies and vouchers application service in services/billing-finance-automation-service/src/domain/us2/billing-finance-automation-us2.service.ts
- [ ] T023 [US2] Implement GET /api/billing/invoices and POST /api/billing/payments/{paymentId}/attempt routes in services/billing-finance-automation-service/src/api/us2/billing-finance-automation-us2.route.ts
- [ ] T024 [US2] Implement apply subsidies and vouchers role-layout screen in apps/mobile/src/role-layouts/billing-finance-automation/us2-billing-finance-automation.screen.tsx

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Auto-Pay and Tax Receipt Lifecycle (Priority: P3)

**Goal**: Deliver auto-pay and tax receipt lifecycle capabilities end-to-end.

**Independent Test**: Can be tested independently by running payment schedules, capturing payment

### Tests for User Story 3

- [ ] T025 [P] [US3] Add contract test for POST /api/billing/invoices/{invoiceId}/adjustments in tests/contract/billing-finance-automation/us3-invoiceline.contract.spec.ts
- [ ] T026 [P] [US3] Add integration test for auto-pay and tax receipt lifecycle flow in tests/integration/billing-finance-automation/us3-paymenttransaction.integration.spec.ts

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create InvoiceLine and PaymentTransaction repository layer in services/billing-finance-automation-service/src/data/us3-billing-finance-automation.repository.ts
- [ ] T028 [US3] Implement auto-pay and tax receipt lifecycle application service in services/billing-finance-automation-service/src/domain/us3/billing-finance-automation-us3.service.ts
- [ ] T029 [US3] Implement POST /api/billing/invoices/{invoiceId}/adjustments and POST /api/billing/receipts/issue routes in services/billing-finance-automation-service/src/api/us3/billing-finance-automation-us3.route.ts
- [ ] T030 [US3] Implement auto-pay and tax receipt lifecycle role-layout screen in apps/mobile/src/role-layouts/billing-finance-automation/us3-billing-finance-automation.screen.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, governance validation, and operational readiness across stories.

- [ ] T031 [P] Add billing-finance-automation performance and reliability metrics in services/billing-finance-automation-service/src/observability/billing-finance-automation.metrics.ts
- [ ] T032 Run billing-finance-automation quickstart validation scenarios in specs/005-billing-finance-automation/quickstart.md
- [ ] T033 [P] Add end-to-end cross-story regression suite in tests/e2e/billing-finance-automation/billing-finance-automation-workflow.e2e.spec.ts
- [ ] T034 Validate constitution gates (privacy, consent, phase sequencing, non-diagnostic) for billing-finance-automation in specs/005-billing-finance-automation/research.md

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
Task: "Add contract test for POST /api/billing/invoices/generate in tests/contract/billing-finance-automation/us1-familybillingaccount.contract.spec.ts"
Task: "Add integration test for generate accurate family invoices flow in tests/integration/billing-finance-automation/us1-subsidyallocation.integration.spec.ts"
Task: "Create FamilyBillingAccount and SubsidyAllocation and TaxReceipt repository layer in services/billing-finance-automation-service/src/data/us1-billing-finance-automation.repository.ts"
```

---

## Parallel Example: User Story 2

```bash
Task: "Add contract test for GET /api/billing/invoices in tests/contract/billing-finance-automation/us2-invoice.contract.spec.ts"
Task: "Add integration test for apply subsidies and vouchers flow in tests/integration/billing-finance-automation/us2-voucherapplication.integration.spec.ts"
Task: "Create Invoice and VoucherApplication and FinanceAuditEvent repository layer in services/billing-finance-automation-service/src/data/us2-billing-finance-automation.repository.ts"
```

---

## Parallel Example: User Story 3

```bash
Task: "Add contract test for POST /api/billing/invoices/{invoiceId}/adjustments in tests/contract/billing-finance-automation/us3-invoiceline.contract.spec.ts"
Task: "Add integration test for auto-pay and tax receipt lifecycle flow in tests/integration/billing-finance-automation/us3-paymenttransaction.integration.spec.ts"
Task: "Create InvoiceLine and PaymentTransaction repository layer in services/billing-finance-automation-service/src/data/us3-billing-finance-automation.repository.ts"
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
