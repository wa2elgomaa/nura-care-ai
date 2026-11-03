# Implementation Plan: Role-Based Layouts

**Branch**: `007-role-based-layouts` | **Date**: 2026-07-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/007-role-based-layouts/spec.md`

## Summary
Implement the single React Native role-based app shell using Keycloak OIDC authentication, with authorization code flow + PKCE for mobile/web and role mapping sourced from Keycloak groups/roles. Teacher and Director sessions use Edge Keycloak as token issuer for offline continuity.

## Technical Context

**Language/Version**: TypeScript 5.x

**Primary Dependencies**: React Native + NativeWind, Nx modules, NestJS identity and role policy services, Keycloak OIDC clients, Prisma, offline session store

**Storage**: PostgreSQL for role policy metadata + encrypted device cache for active session and claims

**Testing**: Unit, contract, integration, OIDC flow tests, role-matrix E2E, offline session tests

**Target Platform**: Unified mobile/tablet/web role-based app surfaces

**Project Type**: Single app codebase with role-variant presentation and shared workflows

**Performance Goals**: role routing after auth <2s p95; token refresh completion <1.5s p95

**Constraints**: Single codebase only; no app forks; OIDC mandatory; offline-safe staff authentication

## Constitution Check

- Privacy and edge-first gate: PASS.
- Consent gate: PASS (permission and role routing only).
- Non-diagnostic gate: PASS.
- Phase gate: PASS.
- Architecture gate: PASS and CRITICAL.
- Regulatory gate: PASS with role access and escalation audit logging.

## Project Structure

```text
specs/007-role-based-layouts/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api-contracts.md
└── tasks.md
```

## Technical Architecture

- App shell initiates OIDC login via Keycloak authorization code flow with PKCE.
- Role router maps Keycloak groups/roles into app role contexts (parent, teacher, director, regional manager).
- Teacher and director tokens are issued by Edge Keycloak when site is offline or edge-routed.
- Parent and regional manager sessions are cloud-routed through Cloud Keycloak.
- Token refresh is automatic and auditable, with session fallback rules by role class.

## Keycloak Identity Flow

- Web flow: OIDC authorization code redirect with PKCE.
- Mobile flow: system browser/AppAuth PKCE flow with secure token storage.
- Role claims source: Keycloak realm roles and group mappings only.
- Edge Keycloak acts as issuer for site staff roles and uses synchronized user/role replica.

## Prisma Data Model Plan

- Existing role entities remain: `UserRoleAssignment`, `RoleLayoutProfile`, `RoleContextSession`, `RoleAccessPolicy`.
- Add `OidcSessionEvent(id, userId, issuer, flowType, refreshOutcome, at)`.
- Add `RoleEscalationAuditEvent(id, actorId, subjectUserId, fromRole, toRole, reasonCode, at)`.

## API Contracts Plan

See [contracts/api-contracts.md](./contracts/api-contracts.md).

## Dependencies

- Internal: role policy service, audit service, edge sync service
- External: Cloud Keycloak, Edge Keycloak
- Config: realm clients, PKCE policy, role-mapping table, token TTL/refresh settings

## Testing Strategy

- Unit: role mapping transforms and role-priority selection
- Contract: identity/session endpoints and role claims payloads
- Integration: OIDC login -> claim mapping -> routed layout initialization
- Offline: Edge Keycloak issuer path for teacher/director sessions
- Security: token refresh and session-isolation leakage checks

## Post-Design Constitution Check

PASS after design:
- Keycloak OIDC and PKCE mandated for authentication.
- Role mapping centralized through Keycloak groups/roles.
- Offline continuity maintained via Edge Keycloak issuer path for staff.
