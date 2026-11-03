# Implementation Plan: Billing Finance Automation

**Branch**: `005-billing-finance-automation` | **Date**: 2026-07-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-billing-finance-automation/spec.md`

## Summary
Implement end-to-end nursery finance operations: invoice generation, subsidy/voucher application, auto-payment lifecycle, and tax receipt issuance. Enforce strict domain isolation from video/vision services via Nx boundaries, and support offline-first operational entry with safe cloud reconciliation.

## Technical Context

**Language/Version**: TypeScript 5.x

**Primary Dependencies**: Nx modules, NestJS billing service, Prisma, payment integration adapter, React Native/admin finance views

**Storage**: PostgreSQL finance schema + local draft cache

**Testing**: Unit, contract, integration, reconciliation tests, E2E billing cycles

**Target Platform**: Director/admin finance roles

**Project Type**: Isolated billing domain service in monorepo

**Performance Goals**: cycle invoice generation for site <5m p95, payment posting <1m p95

**Constraints**: No AI/biometric/edge hardware; offline-first drafts; immutable financial audit trail; strict Nx isolation from video services

**Scale/Scope**: Monthly billing across families with multi-child accounts

## Constitution Check

- Privacy and edge-first gate: PASS (financial metadata only).
- Consent gate: PASS (payment consent/authorization only; biometric consent out of scope).
- Non-diagnostic gate: PASS.
- Phase gate: PASS (Phase 1 billing requirement).
- Architecture gate: PASS with explicit Nx boundary enforcement.
- Regulatory gate: PASS with retention/residency controls.
- Business gate: PASS (core commercial readiness).

## Project Structure

### Documentation (this feature)

```text
specs/005-billing-finance-automation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api-contracts.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
├── mobile/
└── admin/
services/
├── billing-service/            # isolated finance bounded context
├── subsidy-service/
├── payment-orchestration/
└── audit-service/
services/video-service/         # explicit no-import boundary target
packages/
├── db/
├── shared-types/
└── offline-sync/

tests/
├── contract/
├── integration/
└── e2e/
```

**Structure Decision**: Dedicated billing bounded context with enforced Nx tag boundaries (`domain:billing` cannot depend on `domain:video`).

## Complexity Tracking

No constitution violations requiring exceptions.

## Technical Architecture

- Invoice engine calculates recurring + one-off charges from enrollment/attendance billables.
- Subsidy/voucher pipeline applies eligibility-constrained reductions before payable total.
- Payment orchestration schedules auto-pay attempts and records outcomes.
- Receipt service issues tax receipts for successful settlements.
- Offline-first: draft edits and queued actions sync when online; settlement operations remain server-authoritative.

## Prisma Data Model Plan

- `FamilyBillingAccount(id, familyId, siteId, status, autopayEnabled)`
- `Invoice(id, accountId, periodStart, periodEnd, subtotal, discountTotal, totalDue, status)`
- `InvoiceLine(id, invoiceId, kind, description, quantity, unitAmount, amount)`
- `SubsidyAllocation(id, accountId, programCode, validFrom, validTo, amountRuleJson)`
- `VoucherApplication(id, invoiceId, voucherCode, appliedAmount, remainingBalance)`
- `PaymentTransaction(id, invoiceId, scheduledAt, attemptedAt, amount, status, failureCode)`
- `TaxReceipt(id, invoiceId, paymentId, receiptNumber, issuedAt)`
- `FinanceAuditEvent(id, actorId, entityType, entityId, action, payloadJson, at)`

## API Contracts Plan

See [contracts/api-contracts.md](./contracts/api-contracts.md).

## Dependencies

- Internal: enrollment + attendance billables, identity/roles, audit service
- External: payment gateway adapter (through bounded abstraction)
- Config: subsidy policy rules, voucher constraints, receipt numbering policy

## Testing Strategy

- Unit: invoice math, subsidy/voucher application, state transitions
- Contract: invoice/payment/receipt API payloads
- Integration: invoice generation -> payment posting -> receipt issuance
- Offline: draft invoice adjustments and sync conflict handling
- E2E: monthly billing cycle for multi-child family account
- Compliance: Nx boundary lint tests to prevent billing->video imports

## Post-Design Constitution Check

PASS after design:
- Billing domain isolated from video services with enforced boundaries.
- Offline-first operations preserved.
- No AI/biometric/edge hardware involvement.
