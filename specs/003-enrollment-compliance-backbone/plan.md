# Implementation Plan: Enrollment Compliance Backbone

**Branch**: `003-enrollment-compliance-backbone` | **Date**: 2026-07-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-enrollment-compliance-backbone/spec.md`

## Summary
Implement the canonical child compliance and consent workspace, and add identity provisioning integration so enrollment creates or updates parent accounts in Cloud Keycloak and triggers site-level Edge Keycloak sync.

## Technical Context

**Language/Version**: TypeScript 5.x

**Primary Dependencies**: Nx modules, NestJS enrollment and consent services, Prisma, event bus, Keycloak Admin API client

**Storage**: Regional PostgreSQL stores + encrypted local cache + provisioning outbox

**Testing**: Unit, contract, integration, offline sync, provisioning retry/idempotency tests, compliance E2E

**Target Platform**: Director/admin workflows + backend APIs

**Project Type**: Unified app + backend services in monorepo

**Performance Goals**: child profile retrieval <2s p95, provisioning trigger enqueue <5s p95

**Constraints**: No AI inference in this phase; explicit consent lifecycle; auditable provisioning and consent history

## Constitution Check

- Privacy and edge-first gate: PASS.
- Consent gate: PASS and foundational.
- Non-diagnostic gate: PASS.
- Phase gate: PASS.
- Architecture gate: PASS.
- Regulatory gate: PASS with retention and residency controls.

## Project Structure

```text
specs/003-enrollment-compliance-backbone/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api-contracts.md
└── tasks.md
```

## Technical Architecture

- `ChildComplianceProfile` remains the aggregate root for enrollment/compliance data.
- Consent service owns grant/deny/revoke state machine and emits immutable consent events.
- New identity-provisioning adapter calls Cloud Keycloak Admin API on enrollment create/update events.
- Provisioning workflow emits `ParentIdentitySyncRequested` events scoped by site for Edge Keycloak sync workers.
- Outbox pattern guarantees idempotent retries for Keycloak provisioning and sync trigger publication.

## Keycloak Integration Design

- Parent account upsert is executed against Cloud Keycloak using service credentials.
- Parent role/group mapping is derived from enrollment guardian relationship and site scope.
- Site-specific Edge Keycloak sync trigger is emitted only after successful Cloud Keycloak upsert.
- Failures are captured in provisioning audit events and retried with exponential backoff.

## Prisma Data Model Plan

- Existing profile, consent, and compliance entities remain.
- Add `IdentityProvisioningEvent(id, profileId, parentRef, cloudStatus, edgeSyncStatus, retryCount, lastError, at)`.
- Add `IdentityProvisioningAuditEvent(id, actorType, action, requestRef, responseCode, at)`.

## API Contracts Plan

See [contracts/api-contracts.md](./contracts/api-contracts.md).

## Dependencies

- Internal: identity/role service, audit service, edge sync orchestration service
- External: Cloud Keycloak Admin API
- Config: realm/client credentials, site-to-edge mapping, retry policy

## Testing Strategy

- Unit: consent transitions and provisioning payload mapping
- Contract: enrollment and consent APIs + provisioning callback contracts
- Integration: enrollment write -> Cloud Keycloak upsert -> Edge sync trigger
- Offline: local enrollment intake with deferred provisioning outbox replay
- Compliance: audit completeness for consent and provisioning events

## Post-Design Constitution Check

PASS after design:
- Consent-first handling preserved.
- Identity provisioning is auditable and role-scoped.
- Regional boundaries and retention controls remain enforced.
