# NURA Phase Rollout Plan

Mandatory delivery sequencing per Constitution, Section IV.

## Phase 1: Operational Core (MUST ship first)

**Objective**: Establish reliable revenue operations and foundational compliance capabilities before any AI/ML behavioral features.

**Deliverables**:
1. **Attendance Tracking**
   - Daily check-in/check-out with timestamp
   - Absence flagging and notifications
   - Ratio monitoring (staff-to-child)
   - Audit trail

2. **Billing Automation**
   - Automated invoice generation
   - Payment tracking
   - Overdue notifications
   - Financial reporting

3. **Staff Credential Tracker**
   - Certification expiration alerts
   - Background check tracking
   - Training completion monitoring
   - Compliance dashboard

4. **Medication Cross-Check**
   - Medication administration log
   - Parent authorization verification
   - Dosage/timing validation
   - Incident tracking

**Architecture Requirements**:
- NestJS microservices for business logic
- Prisma ORM with PostgreSQL
- Keycloak authentication (Cloud + Edge)
- React Native mobile apps (parent/teacher/director)
- Next.js admin console
- Offline-first edge operation

**Success Criteria**:
- [ ] All four operational services deployed to pilot site
- [ ] Daily staff usage tracked for 30 consecutive days
- [ ] Zero critical bugs in attendance/billing
- [ ] Staff adoption rate > 80%
- [ ] Parent engagement rate > 60%

**Gate**: Operational core shows daily staff usage in pilot cohort.

---

## Phase 2: Edge + Safety Pilots (Requires Phase 1 live)

**Objective**: Deploy edge computing infrastructure and non-behavioral safety capabilities.

**Deliverables**:
1. **Edge Box Rollout**
   - Docker Compose edge stack
   - Frigate NVR deployment
   - Network segmentation (LAN, camera, sensor VLANs)
   - Signed update mechanism
   - Offline continuity (attendance/alerts survive internet outage)

2. **Camera-Follow (Person Tracking)**
   - YOLO person detection (nura-perception service)
   - ByteTrack multi-object tracking
   - Privacy-preserving metadata only (no raw video to cloud)

3. **Fall Detection**
   - MediaPipe pose estimation (nura-perception service)
   - Horizontal pose detection
   - Alert threshold tuning
   - False-positive measurement

4. **BLE Zone Tracking**
   - ESPresense gateway deployment
   - Room-level occupancy counting
   - Zone-based headcount
   - Evacuation roll-call support

**Architecture Requirements**:
- Python services: nura-perception (FastAPI)
- NATS JetStream event bus
- TimescaleDB for time-series sensor data
- Hardware: Mini PC with Coral TPU or NVIDIA GPU
- BLE gateways (ESP32 + ESPresense firmware)

**Success Criteria**:
- [ ] Edge box deployed and operational at pilot site
- [ ] 24+ hour offline continuity test passed
- [ ] Fall detection false-positive rate < 5%
- [ ] Camera-follow tracks person for > 30 seconds continuously
- [ ] BLE zone tracking accuracy > 95%
- [ ] Zero raw video leaks to cloud (verified by egress audit)

**Gate**: Incident false-alert rate below 5%.

---

## Phase 3: Behavioral Intelligence (Requires clinical sign-off)

**Objective**: Introduce pattern-based behavioral insights (non-diagnostic) with strict safety boundaries.

**Deliverables**:
1. **Pattern Anomaly Detection**
   - Occupancy pattern deviations
   - Noise spike detection (nura-analytics service)
   - Activity timeline clustering
   - **Staff-facing only, no parent-facing automation**

2. **Interaction Flagging**
   - Proximity-based interaction detection
   - Rapid motion energy thresholds
   - Escalation alerts (non-diagnostic)
   - **No diagnosis labels or disorder names**

3. **Activity Interest Profiling**
   - Zone preference tracking
   - Activity duration patterns
   - Quarterly interest summaries
   - **Opt-in only, requires parental consent**

**Architecture Requirements**:
- Python service: nura-analytics (FastAPI + scikit-learn)
- Qdrant vector database for embeddings
- Ollama (optional) for VLM verification
- Rules-based explainability (no black-box ML yet)

**Privacy Requirements**:
- **Biometric opt-in**: Face recognition (pickup verification) requires explicit parental consent
- **Consent lifecycle**: auditable opt-in, opt-out, revocation events
- **Data retention**: 7-day default for face embeddings, configurable with consent
- **No automated parent messaging**: Behavioral labels remain staff-facing

**Success Criteria**:
- [ ] Clinical advisory board sign-off obtained
- [ ] Biometric opt-in rate measured in pilots
- [ ] If opt-in rate < 50%, consent UX redesigned before scale rollout
- [ ] Zero diagnostic labels in parent-facing outputs
- [ ] Alert rationale documented for compliance reviewers
- [ ] Production usage evidence collected (3+ months)

**Gate**: Biometric opt-in rate above 50%, or consent UX redesigned.

---

## Phase 4: Custom ML Models (Requires Phase 3 evidence)

**Objective**: Introduce fine-tuned, site-specific ML models for advanced behavioral insights.

**Deliverables**:
1. **Fine-Tuned YOLO Models**
   - Site-specific training data collection
   - Custom object detection (toys, activities)
   - Performance validation vs. base model

2. **Custom Audio Anomaly Models**
   - Rolling buffer audio analysis
   - Scream/distress detection (non-recorded)
   - Threshold tuning per room acoustics

3. **Behavioral Clustering**
   - Unsupervised activity pattern clustering
   - Interest profile refinement
   - Developmental milestone alignment (non-diagnostic)

**Architecture Requirements**:
- Model training pipeline (MLflow or similar)
- Model versioning and A/B testing
- Explainability tooling (SHAP, LIME)
- Clinical advisory oversight

**Approval Requirements**:
- Product stakeholder approval
- Engineering stakeholder approval
- Compliance stakeholder approval
- Clinical advisory board sign-off
- Production evidence from Phase 3 (3+ months)

**Success Criteria**:
- [ ] Custom model performance > base model on pilot data
- [ ] False-positive rate maintained < 5%
- [ ] Explainability docs approved by clinical advisory
- [ ] Regional data residency compliance (US, EU, GCC)
- [ ] Model rollback mechanism tested

**Gate**: Product, engineering, and compliance stakeholder approval.

---

## Constraint Hierarchy (All Decisions)

When conflicts arise, resolve in this order:

1. **Regulatory and privacy obligations** (COPPA, BIPA, GDPR-K)
2. **Phase sequencing obligations** (this document)
3. **Technology stack and architecture obligations** (Constitution Section V)
4. **Performance and scalability optimization**

---

## Amendment Policy

Changes to phase sequencing require:
1. Pull request with rationale and risk assessment
2. Approval from product, engineering, and compliance stakeholders
3. Legal review for child data handling changes
4. Update to this document and Constitution

---

**Version**: 1.0.0  
**Ratified**: 2026-11-03  
**Next Review**: Before Phase 2 kickoff
