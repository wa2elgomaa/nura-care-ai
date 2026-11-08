# 🗺️ NURA AI - Next Phase Implementation Roadmap

**Date:** November 8, 2026  
**Current Phase:** Development Complete → Pre-Production  
**Target:** Production-Ready Safety-First System  
**Mission:** 4 Core Safety Routes BEFORE attendance/billing features

---

## 🎯 Strategic Overview

### Where We Are
- ✅ **Core AI Pipeline Working** - 4 detectors + VLM validation functional
- ✅ **Infrastructure Ready** - Docker services, database, messaging working
- ✅ **Demo Functional** - Can test individual videos/images
- ⚠️ **Route Gaps** - Need stranger detection, search, behavioral analytics
- ⚠️ **Production Gaps** - Security, monitoring, automation needed

### Where We're Going
**Next 8 Weeks:** Complete 4 core safety routes + production hardening

**Core Safety Routes (Priority):**
1. **Incident Detection & Alert** - Violence, distress, unsupervised, abuse, safety
2. **Stranger Detection & Alert** - Unknown faces flagged immediately
3. **Person Search & Locate** - Find anyone by name or image across cameras
4. **Behavioral Analysis & Reports** - Track behaviors, auto-create unknown persons

**Success Criteria:**
1. All 4 safety routes functional and accurate
2. System can be installed on school server in <1 hour
3. All data encrypted in transit and at rest
4. 24/7 monitoring and alerting operational
5. Automated backups and updates working
6. Complete documentation for ops team

> **See [CORE_SAFETY_ROUTES.md](CORE_SAFETY_ROUTES.md) for detailed route specifications**

---

## 📅 8-Week Roadmap

**Weeks 1-3:** Core Safety Routes Implementation  
**Weeks 4-5:** Security Hardening  
**Week 6:** Monitoring & Automation  
**Week 7:** Documentation & Testing  
**Week 8:** Pilot Preparation

---

### Week 1-2: Core Safety Routes (Phase 1)
**Goal:** Routes 1 & 2 functional (Incident + Stranger Detection)

#### Week 1: Enhanced Incident Detection
**Priority:** P0 - CRITICAL

**Tasks:**
1. **Enhanced Alert Payload** (3 days)
   ```bash
   # Include person names and images in alerts
   - Update alert model schema
   - Modify VLM response to include person IDs
   - Update alert service to fetch person data
   - Test alert flow with enrolled persons
   ```
   **Files:**
   - `services/nura-alerts/src/models/alert.model.ts`
   - `services/nura-vlm/src/hybrid_router.py`
   - `services/nura-stream-processor/src/services/frame-processor.ts`

2. **Safety Hazard Detector** (2 days setup + training)
   ```bash
   # Train knife/staircase detector
   cd training/
   python train_safety_detector.py \
     --dataset datasets/ToddlerActions \
     --classes "knife,staircase" \
     --model yolov8s \
     --epochs 50
   ```
   **Files:**
   - `training/train_safety_detector.py`
   - `services/nura-vlm/src/detectors/safety_detector.py`
   - `models/safety_hazard_detector.keras`

**Deliverable:**
- [ ] Person names appear in alerts
- [ ] Safety hazard detector trained and integrated

#### Week 2: Stranger Detection & Evidence
**Priority:** P0 - CRITICAL

**Tasks:**
1. **Stranger Detection Logic** (2 days)
   ```bash
   # Detect unknown faces and alert
   - Create stranger_detector.py
   - Integrate with hybrid router
   - Add confidence thresholding
   - Test with unknown faces
   ```
   **Files:**
   - `services/nura-vlm/src/detectors/stranger_detector.py`
   - `services/nura-vlm/src/hybrid_router.py`

2. **Stranger Alert Type** (1 day)
   ```bash
   # Add dedicated stranger alert
   - Update alert type enum
   - Add stranger alert payload
   - Configure routing rules
   - Test stranger alerts
   ```
   **Files:**
   - `services/nura-alerts/src/models/alert.model.ts`
   - `services/nura-stream-processor/src/services/stranger-handler.ts`

3. **Video Evidence Clips** (2 days)
   ```bash
   # Attach video clips to alerts
   - Query Frigate for clips
   - Store clip references
   - Serve via API
   - Include in notifications
   ```
   **Files:**
   - `services/nura-alerts/src/services/evidence.service.ts`
   - `services/nura-alerts/src/storage/` (clip storage)

**Deliverable:**
- [ ] Stranger detection working
- [ ] Video clips attached to alerts

**Week 1-2 Total:** 10 days, 1-2 engineers

---

### Week 3: Core Safety Routes (Phase 2)
**Goal:** Routes 3 & 4 functional (Search + Behavioral Analytics)

#### Tasks

1. **Person Search API** (2 days)
   ```bash
   # Search by name or image
   GET /api/persons/search?name=Jane
   POST /api/persons/search/by-image
   
   - Implement search endpoints
   - Add real-time location cache (Redis)
   - Test search accuracy
   ```
   **Files:**
   - `services/nura-vlm/src/enrollment_api.py`
   - `services/nura-vlm/src/services/search.py`
   - `services/nura-vlm/src/cache/location_cache.py`
   - `compose.yaml` (add Redis)

2. **Unknown Person Auto-Creation** (2 days)
   ```bash
   # Auto-create "Unknown Person N"
   - Detect unknown faces
   - Create enrollment record
   - Track as "Unknown Person N"
   - Allow manual linking later
   ```
   **Files:**
   - `services/nura-vlm/src/services/unknown_person_handler.py`
   - `edge/postgres/migrations/004_unknown_persons.sql`

3. **Movement History API** (1 day)
   ```bash
   # Track person movements
   GET /api/persons/{id}/movements
   
   - Query person_detections table
   - Aggregate by camera/zone
   - Return movement history
   ```
   **Files:**
   - `services/nura-vlm/src/enrollment_api.py`

**Deliverable:**
- [ ] Search by name working
- [ ] Search by image working
- [ ] Unknown persons auto-created
- [ ] Movement history API working

**Week 3 Total:** 5 days, 1 engineer

---

### Week 4-5: Security Hardening (CRITICAL PATH)
**Goal:** Make system safe for production deployment

#### Week 1: Authentication & Encryption
**Priority:** P0 - BLOCKING

**Tasks:**
1. **SSL/TLS Setup** (2 days)
   ```bash
   # Configure Caddy for auto-HTTPS
   - Update edge/caddy/Caddyfile for TLS
   - Add Let's Encrypt integration
   - Test certificate renewal
   - Force HTTPS redirect
   ```
   **Files:**
   - `edge/caddy/Caddyfile`
   - `compose.yaml` (expose 443)
   - `docs/SSL_SETUP.md`

2. **Secrets Management** (2 days)
   ```bash
   # Move from .env to Docker secrets
   - Create secrets/ directory structure
   - Update compose.yaml for secrets
   - Create setup-secrets.sh script
   - Rotate all default passwords
   ```
   **Files:**
   - `scripts/setup-secrets.sh`
   - `compose.yaml` (use secrets)
   - `.env.example` (update)

3. **API Authentication** (1 day)
   ```bash
   # Enable Keycloak for admin endpoints
   - Configure Keycloak realm
   - Add JWT middleware to services
   - Test authentication flow
   ```
   **Files:**
   - `services/*/src/middleware/auth.ts`
   - `edge/keycloak/realm-export.json`

**Deliverable:**
- [ ] All endpoints HTTPS only
- [ ] No plaintext passwords in config
- [ ] Authentication working on admin UI

#### Week 2: Audit & Network Security
**Priority:** P0 - BLOCKING

**Tasks:**
1. **Audit Logging** (2 days)
   ```bash
   # Add comprehensive audit trail
   - Create audit_log table
   - Add audit middleware to all services
   - Log all video/image access
   - Log all configuration changes
   ```
   **Files:**
   - `edge/postgres/migrations/002_audit_log.sql`
   - `services/*/src/middleware/audit.ts`
   - `services/*/src/utils/logger.py`

2. **Network Segmentation** (1 day)
   ```bash
   # Enforce VLAN separation
   - Document network architecture
   - Update compose.yaml networks
   - Add firewall rules documentation
   ```
   **Files:**
   - `docs/NETWORK_ARCHITECTURE.md`
   - `scripts/configure-firewall.sh`

3. **Data Retention** (2 days)
   ```bash
   # Implement cleanup policies
   - Create cleanup service
   - Add configurable retention periods
   - Test cleanup without data loss
   ```
   **Files:**
   - `services/nura-cleanup/` (new service)
   - `scripts/cleanup-old-data.sh`

**Deliverable:**
- [ ] Complete audit trail working
- [ ] Network diagram with VLANs
- [ ] Data retention policies enforced

**Week 1-2 Total:** 10 days, 2 engineers

---

### Week 6: Monitoring & Automation
**Goal:** Make system observable and automated

#### Tasks

1. **Prometheus + Grafana** (2 days)
   ```bash
   # Add metrics collection
   - Add Prometheus to compose.yaml
   - Add Grafana dashboards
   - Instrument all services
   - Create ops dashboard
   ```
   **Files:**
   - `edge/prometheus/prometheus.yml`
   - `edge/grafana/dashboards/`
   - `compose.yaml` (add monitoring)
   - Services: Add `/metrics` endpoints

2. **Centralized Logging** (2 days)
   ```bash
   # Add Loki or ELK
   - Add Loki to compose.yaml
   - Configure log shipping
   - Create log dashboard
   - Test log search
   ```
   **Files:**
   - `edge/loki/loki-config.yml`
   - `edge/promtail/promtail-config.yml`
   - `compose.yaml` (add logging)

3. **Alerting** (1 day)
   ```bash
   # Configure ops alerts
   - Add Alertmanager
   - Configure alert rules
   - Test alert routing
   ```
   **Files:**
   - `edge/alertmanager/alertmanager.yml`
   - `edge/prometheus/alert-rules.yml`

**Deliverable:**
- [ ] Grafana dashboard live
- [ ] Centralized logging working
- [ ] Ops alerts configured

**Deliverable:**
- [ ] Grafana dashboard live
- [ ] Centralized logging working
- [ ] Ops alerts configured
- [ ] Installation script working
- [ ] Backup script automated
- [ ] Update mechanism safe

**Week 6 Total:** 5 days, 1 engineer

---

### Week 7: Documentation & Testing
**Goal:** Complete docs and validate system

#### Tasks

1. **Installation Script** (2 days)
   ```bash
   # Create one-command install
   ./install.sh
   
   Features:
   - Check system requirements
   - Install dependencies
   - Generate secrets
   - Configure services
   - Pull images
   - Start services
   - Run smoke tests
   ```
   **Files:**
   - `install.sh`
   - `scripts/check-requirements.sh`
   - `scripts/generate-secrets.sh`
   - `scripts/smoke-test.sh`

2. **Backup & Restore** (2 days)
   ```bash
   # Automated backup system
   ./backup.sh --to /mnt/backup
   ./restore.sh --from /mnt/backup/2026-11-08
   
   Features:
   - PostgreSQL dump
   - Configuration backup
   - Enrollment photos
   - Encryption
   - Verify backup integrity
   ```
   **Files:**
   - `scripts/backup.sh`
   - `scripts/restore.sh`
   - `docs/BACKUP_GUIDE.md`

3. **Update Script** (1 day)
   ```bash
   # Safe updates with rollback
   ./update.sh --version v1.2.0
   
   Features:
   - Pull new images
   - Run migrations
   - Rolling restart
   - Smoke test
   - Auto-rollback on failure
   ```
   **Files:**
   - `scripts/update.sh`
   - `scripts/rollback.sh`

**Deliverable:**
- [ ] `./install.sh` working end-to-end
- [ ] Daily backups automated
- [ ] Safe update mechanism

**Deliverable:**
- [ ] All 4 routes tested end-to-end
- [ ] Integration tests passing
- [ ] Load tests passing (10 cameras)
- [ ] Security audit complete
- [ ] All documentation complete

**Week 7 Total:** 5 days, 1 QA + 1 writer

---

### Week 8: Pilot Preparation & Final Testing
**Goal:** Ready for pilot school deployment

#### Tasks

1. **Deployment Documentation** (2 days)
   ```bash
   # Complete deployment guides
   - INSTALLATION_GUIDE.md
   - OPERATIONS_RUNBOOK.md
   - TROUBLESHOOTING.md
   - SECURITY_GUIDE.md
   ```
   **Content:**
   - Step-by-step installation
   - Common operations (restart, backup, update)
   - Troubleshooting decision trees
   - Security controls documentation

2. **Compliance Documentation** (2 days)
   ```bash
   # Legal and compliance
   - COMPLIANCE_CHECKLIST.md (GDPR)
   - PRIVACY_POLICY.md
   - PARENT_CONSENT_FORM.md
   - DATA_PROCESSING_AGREEMENT.md
   ```
   **Content:**
   - GDPR compliance checklist
   - Privacy policy template
   - Parent consent form template
   - DPA for schools

3. **Training Materials** (1 day)
   ```bash
   # Staff training
   - STAFF_TRAINING.md
   - ADMIN_GUIDE.md
   - PARENT_FAQ.md
   ```
   **Content:**
   - How to use the system
   - How to respond to alerts
   - Common questions from parents

**Deliverable:**
- [ ] Complete deployment docs
- [ ] Compliance checklist done
- [ ] Training materials ready

#### Tasks

1. **Route-Specific Testing** (2 days)
   ```bash
   # Test all 4 core safety routes
   
   Route 1: Incident Detection
   - Trigger violence, distress, supervision violations
   - Verify person names in alerts
   - Verify video evidence attached
   
   Route 2: Stranger Detection
   - Test with unknown faces
   - Verify immediate alerts
   - Test visitor whitelist
   
   Route 3: Person Search
   - Search by name (accuracy)
   - Search by image (accuracy)
   - Verify real-time location
   
   Route 4: Behavioral Analytics
   - Verify unknown person auto-creation
   - Check movement history
   - Validate activity detection
   ```
   **Files:**
   - `tests/routes/test_incident_detection.py`
   - `tests/routes/test_stranger_detection.py`
   - `tests/routes/test_person_search.py`
   - `tests/routes/test_behavioral_analytics.py`

2. **Load Testing** (1 day)
   ```bash
   # Stress test with pilot school load
   - 10 cameras simultaneously
   - 100+ persons enrolled
   - 50 alerts per day
   - 24/7 continuous operation
   ```
   **Files:**
   - `tests/load/test_multi_camera.py`
   - `tests/load/test_route_performance.py`

3. **Pilot Hardware Setup** (2 days)
   ```bash
   # Prepare pilot school hardware
   - Server configuration
   - Camera setup
   - Network configuration
   - Initial enrollment (staff photos)
   ```
   **Files:**
   - `docs/PILOT_SETUP_GUIDE.md`
   - `docs/HARDWARE_CHECKLIST.md`

**Deliverable:**
- [ ] All 4 routes tested and working
- [ ] Load tests passing
- [ ] Pilot hardware ready
- [ ] Ready for on-site deployment

**Week 8 Total:** 5 days, 1 engineer + 1 on-site tech

---

## 📊 Resource Requirements

### Team Composition (6 weeks)

| Role | Weeks | Allocation | Tasks |
|------|-------|-----------|--------|
| Backend Engineer | 2 weeks | 100% | Security, Auth, Audit |
| DevOps Engineer | 3 weeks | 100% | Monitoring, Deployment, Automation |
| Technical Writer | 1 week | 100% | Documentation, Compliance |
| QA Engineer | 1 week | 50% | Testing, Validation |
| Security Engineer | 1 week | 25% | Security Audit, Review |

**Total Effort:** ~7 person-weeks

### Infrastructure Costs (Development)

| Item | Cost | Notes |
|------|------|-------|
| Development Server | $0 | Use existing Mac M4 |
| Test Server (Cloud) | $200/month | DigitalOcean/AWS for testing |
| Monitoring (Grafana Cloud) | $0 | Free tier sufficient |
| SSL Certificates | $0 | Let's Encrypt |
| **Total** | **$200/month** | During development only |

---

## 🎯 Critical Path & Dependencies

### Critical Path (Must Complete in Order)
```
Week 1-2: Security
   ↓
Week 3: Monitoring  ← Required for production support
   ↓
Week 4: Automation ← Required for deployment
   ↓
Week 5: Documentation ← Required for ops
   ↓
Week 6: Testing ← Validates everything
   ↓
PILOT DEPLOYMENT
```

### Parallel Tracks (Can Work Simultaneously)

**Track A: Core Security (Week 1-2)**
- SSL/TLS
- Secrets Management
- API Authentication

**Track B: Operational Security (Week 2)**
- Audit Logging
- Network Segmentation
- Data Retention

**Track C: Observability (Week 3)**
- Prometheus + Grafana
- Centralized Logging
- Alerting

---

## 🚨 Risks & Mitigations

### High-Risk Items

1. **Risk:** SSL certificate renewal fails in production
   **Mitigation:** 
   - Test renewal in staging
   - Add monitoring for cert expiry
   - Document manual renewal process

2. **Risk:** Database migration fails during update
   **Mitigation:**
   - Test migrations in staging
   - Always backup before update
   - Have rollback script ready

3. **Risk:** False positive rate too high in production
   **Mitigation:**
   - Extensive field testing
   - Configurable thresholds per school
   - Easy rule disable mechanism

4. **Risk:** GPU driver incompatibility
   **Mitigation:**
   - Document tested configurations
   - Provide CPU fallback mode
   - Remote diagnostics tool

### Medium-Risk Items

5. **Risk:** Monitoring overhead impacts performance
   **Mitigation:**
   - Tune metric collection frequency
   - Use efficient logging
   - Monitor monitoring overhead

6. **Risk:** Backup storage fills up
   **Mitigation:**
   - Automated cleanup of old backups
   - Compression
   - External storage option

---

## 📈 Success Metrics (Week 6)

### Technical Metrics
- [ ] All services have health checks
- [ ] All services emit Prometheus metrics
- [ ] All logs centralized in Loki/ELK
- [ ] SSL A+ rating on SSL Labs
- [ ] <10s installation time for updates
- [ ] 100% backup success rate

### Security Metrics
- [ ] 0 critical vulnerabilities
- [ ] 0 high-severity vulnerabilities
- [ ] 100% audit trail coverage
- [ ] All secrets rotated
- [ ] All endpoints authenticated

### Documentation Metrics
- [ ] 100% API documented
- [ ] 100% runbook coverage
- [ ] 0 unanswered questions in pilot

---

## 🎬 Post-6-Week Plan

### Week 7-8: Pilot Deployment
**Goal:** Deploy to first test school

**Tasks:**
1. Install system at pilot school
2. Enroll staff and students
3. Configure cameras
4. Train school staff
5. Monitor for 2 weeks
6. Collect feedback

**Success Criteria:**
- System runs 24/7 without intervention
- <5 false alerts per day
- Staff can respond to alerts
- Parents comfortable with privacy

### Week 9-10: Optimization
**Goal:** Fix issues from pilot

**Tasks:**
1. Tune detection thresholds
2. Fix bugs discovered
3. Optimize performance
4. Improve documentation
5. Update training materials

### Week 11-12: Production Rollout
**Goal:** Deploy to production schools

**Tasks:**
1. Deploy to 3-5 schools
2. 24/7 monitoring
3. Support staff training
4. Collect metrics
5. Iterate based on feedback

---

## 🛠️ Technical Debt to Address

### High Priority (This Phase)
- [ ] Fix distress ML model training (1.12% → 85%+ recall)
- [ ] Add database connection pooling
- [ ] Add request rate limiting
- [ ] Implement circuit breakers
- [ ] Add service mesh (optional)

### Medium Priority (Next Phase)
- [ ] Train safety hazard detector
- [ ] Train activity classifier
- [ ] Add multi-camera person tracking
- [ ] Improve VLM prompts
- [ ] Add audio distress detection

### Low Priority (Future)
- [ ] Multi-site management UI
- [ ] Mobile app for staff
- [ ] Parent notification preferences
- [ ] Advanced analytics dashboard
- [ ] Integration with school systems

---

## 📚 Deliverables Summary

### Week 1-2: Security
- [ ] SSL/TLS configured
- [ ] Secrets management system
- [ ] API authentication
- [ ] Audit logging
- [ ] Network segmentation docs
- [ ] Data retention policies

### Week 3: Monitoring
- [ ] Prometheus + Grafana dashboards
- [ ] Centralized logging (Loki)
- [ ] Alerting configured
- [ ] Ops runbook started

### Week 4: Automation
- [ ] `install.sh` script
- [ ] `backup.sh` script
- [ ] `update.sh` script
- [ ] Smoke test suite

### Week 5: Documentation
- [ ] Installation guide
- [ ] Operations runbook
- [ ] Troubleshooting guide
- [ ] Security guide
- [ ] Compliance checklist
- [ ] Training materials

### Week 6: Testing
- [ ] Integration tests passing
- [ ] Load tests passing
- [ ] Security audit complete
- [ ] Pilot checklist ready

---

## ✅ Definition of Done (Production-Ready)

System is "production-ready" when:

**Security:**
- [ ] All traffic encrypted (HTTPS)
- [ ] No secrets in config files
- [ ] All admin endpoints authenticated
- [ ] Complete audit trail
- [ ] Security audit passed

**Operations:**
- [ ] Monitoring dashboard live
- [ ] Centralized logging working
- [ ] Alerts configured
- [ ] Automated backups
- [ ] Update mechanism tested

**Deployment:**
- [ ] One-command installation
- [ ] Installation <1 hour
- [ ] Update <15 minutes
- [ ] Rollback <5 minutes

**Documentation:**
- [ ] Installation guide complete
- [ ] Ops runbook complete
- [ ] Troubleshooting guide complete
- [ ] Training materials ready
- [ ] Compliance docs ready

**Testing:**
- [ ] All integration tests pass
- [ ] Load tests pass (10 cameras)
- [ ] Security audit pass
- [ ] Pilot school ready

**Metrics:**
- [ ] 90%+ detection accuracy
- [ ] <10s alert latency
- [ ] 99.9% uptime
- [ ] <10% false positive rate

---

## 🎯 Immediate Next Steps (This Week)

### Monday-Tuesday
1. **Set up SSL/TLS**
   - Configure Caddy for HTTPS
   - Test with self-signed cert
   - Document Let's Encrypt setup

2. **Create secrets management**
   - Create `scripts/setup-secrets.sh`
   - Update `compose.yaml` for secrets
   - Test secret rotation

### Wednesday-Thursday
3. **Add audit logging**
   - Create audit_log table
   - Add audit middleware
   - Test audit trail

4. **Start monitoring setup**
   - Add Prometheus to compose
   - Create first dashboard
   - Test metrics collection

### Friday
5. **Documentation sprint**
   - Start INSTALLATION_GUIDE.md
   - Start SECURITY_GUIDE.md
   - Update STATUS.md

---

**Timeline:** 6 weeks to production-ready  
**Team:** 2-3 engineers + 1 writer  
**Budget:** ~$1,200 (cloud testing)  
**Risk:** Low (clear path, proven tech)  
**Go/No-Go Decision:** End of Week 6
