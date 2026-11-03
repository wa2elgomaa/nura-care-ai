# API Contracts: Role-Based Layouts

## GET /api/identity/me/roles
- Response: roles[], priority order, effective statuses

## GET /api/layouts/role/{role}
- Response: navigationConfig, featureFlags, version

## POST /api/role-context/sessions
- Body: activeRole, sourceDevice
- Response: sessionId

## POST /api/role-context/sessions/{sessionId}/switch
- Body: toRole
- Response: updated session context

## GET /api/access-policies/{role}
- Response: resource-action policy set
