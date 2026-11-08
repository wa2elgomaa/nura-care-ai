# Feature Specification: Week 6 - Security Hardening

**Feature Branch**: `055-week6-security-hardening`
**Created**: 2026-11-08
**Sprint**: Week 6 of 8

## Overview
Harden system for production: SSL/TLS, secrets management, authentication, audit logging, data retention.

## User Stories

### Story 1 - HTTPS Everywhere (P0)
All traffic encrypted with SSL/TLS.

**Acceptance**:
- Caddy configured for auto-HTTPS
- All HTTP redirects to HTTPS
- SSL Labs A+ rating

### Story 2 - Secrets Management (P0)
No passwords in config files.

**Acceptance**:
- Docker secrets or Vault
- All passwords rotated
- .env.example has placeholders only

### Story 3 - API Authentication (P0)
All admin endpoints require authentication.

**Acceptance**:
- Keycloak integration
- JWT tokens
- Role-based access (admin, staff, parent)

### Story 4 - Audit Logging (P1)
Complete audit trail of all actions.

**Acceptance**:
- Log all video/image access
- Log all configuration changes
- Log all alert actions
- Tamper-proof logs

### Story 5 - Data Retention (P1)
Auto-delete old data per policy.

**Acceptance**:
- Configurable retention (default 30 days)
- Auto-cleanup job
- Clips/snapshots deleted
- Database records anonymized

## Implementation

### Task 1: SSL/TLS Setup (1 day)
- Configure Caddy Caddyfile
- Let's Encrypt or self-signed certs
- Force HTTPS redirect

### Task 2: Secrets Management (1 day)
- scripts/setup-secrets.sh
- Docker secrets in compose.yaml
- Migrate all passwords

### Task 3: Authentication (2 days)
- Keycloak realm configuration
- JWT middleware in all services
- Role-based access control

### Task 4: Audit Logging (1 day)
- Audit middleware
- Database: audit_log table
- Log rotation

### Task 5: Data Retention (1 day)
- Cleanup service
- Configurable policies
- Test cleanup

## Testing
```bash
# Test HTTPS
curl https://nura.school.local
# Expect: 200 OK, valid cert

# Test authentication
curl http://localhost:3011/api/alerts
# Expect: 401 Unauthorized

# Test audit log
# Trigger action, check audit_log table

# Test cleanup
# Create old data, run cleanup, verify deleted
```

## Success Metrics
- [ ] SSL Labs A+ rating
- [ ] 0 passwords in git
- [ ] 100% endpoints authenticated
- [ ] Complete audit trail
- [ ] Retention policies enforced

**Duration:** 1 week  
**Next:** Week 7
