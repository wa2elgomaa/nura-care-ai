# NURA Phase Rollout Plan (REVISED - Safety First)

**Version**: 2.0 - Safety-Focused  
**Updated**: 2026-11-03  
**Core Mission**: Real-time camera-based violation detection for child safety

---

## ⚠️ CRITICAL CHANGE: Safety Modules First

**Previous approach** ❌: Attendance/Billing → Edge deployment → Safety features  
**New approach** ✅: **Safety violation detection → WiFi sensing → Monetization features**

**Rationale**: Safety monitoring IS the product. Attendance/billing are nice-to-have monetization features that come later.

---

## Phase 1: Camera Violation Detection MVP (4-6 weeks) 🎯 **PRIMARY FOCUS**

**Objective**: Deploy real-time AI-powered safety monitoring in 2 pilot classrooms.

### Core Deliverables

#### 1. **Vision Pipeline** (Python Services)
- ✅ **nura-perception**: YOLO person detection + MediaPipe pose estimation
- ⭐ **nura-vlm**: Vision-Language Model for scene understanding (NEW)
  - Ollama + LLaVA 13B or Moondream 2B
  - Answers: "Is there an adult? What are they doing? Is this safe?"
  - Inference: <2 seconds per frame
  
#### 2. **Rule Engine & Knowledge Base** (TypeScript Services)
- ⭐ **nura-rag**: RAG-based rule knowledge base
  - Load school policies (PDF upload)
  - Load government regulations (per region: US, UAE, UK)
  - Qdrant vector search for rule matching
- ⭐ **nura-rules**: Violation detection engine
  - Event → Context → Rule matching → Alert
  - Configurable thresholds (e.g., "no adult for >30s")
  
#### 3. **Alert & Response System**
- ⭐ **nura-notifier**: Multi-channel alerts
  - Push notifications (ntfy) <10s latency
  - SMS for critical alerts
  - Email summaries
  - Dashboard real-time feed
- ⭐ **nura-ui**: Admin console
  - Live alert feed
  - Evidence viewer (local clips only)
  - Audit trail
  - Rule management

#### 4. **Infrastructure** (Already Exists)
- ✅ **Frigate NVR**: Local video storage + RTSP streaming
- ✅ **PostgreSQL**: Event storage with TimescaleDB
- ✅ **NATS JetStream**: Event bus
- ✅ **Keycloak**: Admin authentication

### Safety Rules for Phase 1 (6-8 rules)

| Priority | Rule | Detection Method | Trigger |
|----------|------|------------------|---------|
| **P0** | Children alone without staff | YOLO (no adult) + VLM confirmation | >30 seconds |
| **P0** | Child leaving designated area | YOLO tracking + zone boundaries | Immediate |
| **P0** | Fall/injury detection | MediaPipe (horizontal pose) | Immediate |
| **P1** | Restricted area access | YOLO + zone rules (kitchen, storage) | Immediate |
| **P1** | Room over capacity | YOLO person count | >5 minutes |
| **P1** | Door/gate left open | Object detection (open door) | >2 minutes |
| **P2** | Physical contact concern | VLM analysis (inappropriate touch) | Manual review |
| **P2** | Aggressive behavior | Pose + VLM (hitting, pushing) | Immediate |

**Rule Sources**:
- School's own supervision policies
- State/national childcare regulations
- Child protection guidelines

### Hardware Requirements

**Edge Box** (per site):
- Mini PC or workstation
- NVIDIA GPU (24GB VRAM recommended) or Coral TPU
- 32GB RAM
- 500GB SSD (local clips + models)
- Dual NIC (camera VLAN + server VLAN)

**Cameras**:
- 2-8 cameras per site (pilot)
- RTSP/ONVIF support
- 1080p minimum, 15 FPS
- Fixed mount (no auto-tracking)

### Success Criteria

- ✅ **Accuracy**: 90%+ correct alerts on seeded test events
- ✅ **Latency**: <10 seconds from violation to alert
- ✅ **Privacy**: Zero video data leaves school premises (network audit)
- ✅ **Usability**: Admins say alerts are actionable (end-of-pilot survey)
- ✅ **Reliability**: System runs 24/7 for 2 weeks without crashes

### Deliverables

1. Working system in 2 pilot classrooms
2. 6-8 rules active and tuned
3. Admin mobile app + web dashboard
4. Evidence management system
5. Audit trail and compliance reports
6. Pilot report with accuracy metrics

---

## Phase 2: WiFi Sensing + Advanced Detection (6-8 weeks)

**Objective**: Cover uncovered areas and add advanced behavioral detection.

### New Capabilities

#### 1. **WiFi Sensing** (RuView Integration)
- ⭐ **nura-wifi-sensing**: ESP32 + RuView service
  - 4-6 sensor nodes per site (bathrooms, changing rooms)
  - Occupancy detection without cameras
  - Duration tracking
  - Anomaly: adult + child together >2 minutes
  
#### 2. **Advanced Vision**
- **Multi-camera tracking**: Follow person across rooms
- **Face detection** (not recognition): Detect unknown faces
- **Aggressive behavior**: VLM + pose analysis
- **Audio anomalies**: Distress sounds (rolling buffer, not recorded)

#### 3. **Enhanced Rules**
- Bathroom occupancy anomalies (WiFi sensing)
- Multi-room unauthorized access
- After-hours intrusion detection
- Staff-to-child ratio violations (count accuracy)

### Hardware Additions

- 4-6 ESP32 nodes (WiFi sensing)
- Dedicated WiFi AP (sensor VLAN)
- Optional: USB microphone (audio anomaly detection)

### Success Criteria

- ✅ WiFi sensing accuracy >85% (occupancy/count)
- ✅ Multi-camera tracking follows person >90% of time
- ✅ Audio anomaly detection <10% false positives
- ✅ All Phase 1 rules still performing at 90%+ accuracy

---

## Phase 3: Fleet Management + Compliance (8-12 weeks)

**Objective**: Scale to 5-10 sites and add compliance reporting.

### New Capabilities

#### 1. **Multi-Site Management**
- Fleet dashboard (cloud)
- Centralized rule pack distribution
- Cross-site analytics
- Regional regulation packs (US, UAE, UK, EU)

#### 2. **Compliance & Reporting**
- Automated compliance reports (weekly, monthly)
- Inspector audit trail
- Evidence export for legal cases
- Incident trend analysis

#### 3. **Advanced Features**
- Staff face recognition (opt-in, for unauthorized person detection)
- Pickup verification (guardian face matching)
- Activity pattern analysis (developmental tracking, non-diagnostic)

### Success Criteria

- ✅ 5+ sites operational
- ✅ <1 hour incident response time (detection → resolution)
- ✅ Compliance reports pass inspector review
- ✅ Zero data breaches or privacy violations

---

## Phase 4: Monetization Features (Optional - 12+ weeks)

**Objective**: Add revenue-generating features beyond safety monitoring.

### Potential Additions

1. **Attendance Tracking** (reuse camera person detection)
2. **Billing Automation** (track child-hours)
3. **Staff Credential Tracking**
4. **Parent Portal** (pickup notifications, activity summaries)
5. **Bus Tracking** (GPS + geofencing)

**Note**: These features are **NOT** required for the core product. Safety monitoring alone is sufficient for product-market fit.

---

## Constraint Hierarchy (Updated)

When conflicts arise, resolve in this order:

1. **Safety and child protection** (core product value)
2. **Privacy and regulatory compliance** (COPPA, BIPA, GDPR-K)
3. **Phase sequencing** (safety → WiFi → scale → monetization)
4. **Technology stack and architecture** (Constitution mandates)
5. **Performance and scalability**

---

## Development Roadmap (Next 6 Weeks)

### Week 1: VLM Integration
- [ ] Set up Ollama + LLaVA 13B
- [ ] Create nura-vlm service (FastAPI)
- [ ] Test scene understanding prompts
- [ ] Benchmark inference speed (<2s target)

**Deliverable**: VLM service answering "Is there an adult in this room?"

### Week 2: RAG Implementation
- [ ] Load sample school policies into Qdrant
- [ ] Implement nura-rag service (NestJS)
- [ ] Test rule retrieval accuracy
- [ ] Create rule schema (YAML format)

**Deliverable**: RAG returns matching rules for "child alone in room"

### Week 3: Rule Engine
- [ ] Implement nura-rules service (NestJS)
- [ ] Connect detection → VLM → RAG → rules pipeline
- [ ] Add threshold logic (e.g., "no adult for >30s")
- [ ] Test 3 core rules end-to-end

**Deliverable**: Pipeline generates violation events

### Week 4: Alert System
- [ ] Implement nura-notifier (push + SMS)
- [ ] Build admin dashboard alert feed
- [ ] Add evidence clip viewer
- [ ] Test alert latency (<10s)

**Deliverable**: Admins receive push notifications within 10 seconds

### Week 5: Integration & Testing
- [ ] Deploy to dev edge box (with real GPU)
- [ ] Test with looped classroom footage
- [ ] Seed test violations
- [ ] Tune thresholds for accuracy

**Deliverable**: System runs 24/7 for 48 hours without crashes

### Week 6: Pilot Preparation
- [ ] Document installation procedure
- [ ] Create admin training materials
- [ ] Prepare pilot site (2 cameras)
- [ ] Deploy and validate

**Deliverable**: Pilot site operational, admins trained

---

## Open Source Component Integration Plan

### Immediate (Week 1-2)

| Component | Purpose | Integration Point |
|-----------|---------|------------------|
| **LLaVA / Moondream** | VLM scene understanding | nura-vlm service |
| **LangChain** | RAG framework | nura-rag service |
| **sentence-transformers** | Embeddings | nura-rag service |
| **Qdrant** | Vector database | Already in compose.yaml |

### Near-Term (Week 4-6)

| Component | Purpose | Integration Point |
|-----------|---------|------------------|
| **Parlor patterns** | Multimodal AI architecture | nura-vlm (inspiration) |
| **Ultralytics YOLO** | Already integrated | nura-perception |
| **MediaPipe** | Already integrated | nura-perception |
| **Frigate** | Already integrated | compose.yaml |

### Phase 2 (Week 8+)

| Component | Purpose | Integration Point |
|-----------|---------|------------------|
| **RuView** | WiFi sensing | nura-wifi-sensing (new service) |
| **ESP32 firmware** | Sensor nodes | Hardware deployment |
| **pyAudioAnalysis** | Audio anomaly detection | nura-perception (optional) |

---

## What We're NOT Building (Yet)

To stay focused on safety:

❌ **Attendance tracking** (Phase 4)  
❌ **Billing automation** (Phase 4)  
❌ **Staff credential tracking** (Phase 4)  
❌ **Medication logs** (Phase 4)  
❌ **Parent portal** (Phase 4)  
❌ **Bus tracking** (Phase 4)  

**These features are valuable but NOT part of the core safety product.**

---

## Amendment Policy

Changes to phase prioritization require:

1. Pull request with rationale
2. Approval from:
   - Product lead (market fit validation)
   - Engineering lead (technical feasibility)
   - Compliance lead (regulatory impact)
3. Update to Constitution if core principles change

---

**Version**: 2.0 - Safety-Focused  
**Ratified**: 2026-11-03  
**Next Review**: After Phase 1 pilot (Week 8)

---

**The mission is clear: Keep children safe by detecting violations in real-time, with zero privacy compromise.**
