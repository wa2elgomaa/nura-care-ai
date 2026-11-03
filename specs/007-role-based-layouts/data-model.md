# Data Model: Role-Based Layouts

## UserRoleAssignment
- Fields: id, userId, role, priority, status, effectiveFrom, effectiveTo

## RoleLayoutProfile
- Fields: id, role, navigationConfigJson, featureFlagsJson, version

## RoleContextSession
- Fields: id, userId, activeRole, startedAt, endedAt, sourceDevice

## RoleAccessPolicy
- Fields: id, role, resource, action, effect, version

## RoleRoutingAuditEvent
- Fields: id, userId, selectedRole, reasonCode, at

## RoleSwitchAuditEvent
- Fields: id, sessionId, fromRole, toRole, actorId, at
