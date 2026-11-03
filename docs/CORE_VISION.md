# NURA Core Vision - Camera-Based Violation Detection

**Updated**: 2026-11-03  
**Priority**: **PRIMARY PRODUCT FEATURE**

## Core Business Requirement

> **"Monitor children in classrooms 24/7 through cameras, detect violations based on school rules and government regulations, alert administrators immediately — all while keeping video data completely offline on school servers."**

## What NURA Actually Is

NURA is **NOT** an attendance/billing system.  
NURA **IS** a **real-time AI-powered safety monitoring system** that:

1. **Watches cameras continuously** in classrooms, playgrounds, hallways
2. **Understands context** using Vision-Language Models (VLMs)
3. **Matches events against rules** from school policies and government regulations (RAG)
4. **Alerts administrators** within seconds when violations occur
5. **Keeps all video/images local** — nothing leaves the school server

### Think: **Parlor (multimodal AI) + Frigate (local NVR) + RAG (rule knowledge base)**

---

## Core Features (Phase 1 - What We Build First)

### 1. Real-Time Camera Monitoring ✅ PRIMARY
**Like Parlor** - multimodal AI with vision + language understanding

- **Continuous detection** on all camera feeds (8-32 cameras per site)
- **Person detection** (YOLO) + **pose estimation** (MediaPipe)
- **Action recognition** using VLM (LLaVA, GPT-4V, or Claude Vision)
- **Scene understanding**: "Is this a child? Is an adult present? What are they doing?"

**Output**: Event stream with context
```json
{
  "timestamp": "2024-11-03T14:23:15Z",
  "camera": "classroom-2",
  "detection": "child_alone_in_room",
  "context": "Two children (ages 4-5) visible, no adult present, duration 45 seconds",
  "confidence": 0.89,
  "rule_match": "RULE-003: Children must be supervised by staff at all times"
}
```

### 2. Rule-Based Violation Detection ✅ PRIMARY
**RAG Knowledge Base** - school policies + government regulations

**Example Rules**:
- ❌ **Children alone without staff** (no adult detected for >30 seconds)
- ❌ **Physical contact violations** (inappropriate touching, restraint)
- ❌ **Restricted area access** (child in kitchen, storage, staff room)
- ❌ **Over-capacity rooms** (more children than allowed ratio)
- ❌ **Unauthorized persons** (unknown adult in classroom)
- ❌ **Falls/injuries** (child on ground, distress posture)
- ❌ **Doors/gates left open** (egress to parking lot, street)
- ❌ **Aggressive behavior** (hitting, pushing, throwing objects)

**Rule Sources**:
1. School's own handbook (uploaded PDFs)
2. Government childcare regulations (loaded per region: US, UAE, etc.)
3. Custom rules defined by administrators

### 3. WiFi Sensing for Uncovered Areas ✅ PRIMARY
**RuView Integration** - occupancy detection without cameras

For areas where cameras are **not allowed** (bathrooms, changing rooms):
- **Occupancy detection**: Is someone in the bathroom?
- **Duration tracking**: Has someone been there too long?
- **Anomaly detection**: Adult + child in bathroom together (flag for review)

**Privacy**: No images, no biometric data — only presence/absence signals.

### 4. Immediate Alert System ✅ PRIMARY
**Real-time notifications** to administrators and managers

**Alert Flow**:
```
Camera detects event 
  → VLM analyzes context 
  → Rule engine matches violation 
  → Alert sent within 10 seconds
```

**Alert Channels**:
- 🔔 **In-app push** (mobile app for admins)
- 📱 **SMS** (critical violations only)
- 📧 **Email** (daily summary)
- 🖥️ **Dashboard** (real-time feed on admin console)
- 📺 **Wall display** (optional: security office screen)

**Alert Content**:
- Rule violated + clause reference
- Camera location + timestamp
- 15-second clip (stored locally, access logged)
- Suggested action (from rule definition)

### 5. Audit Trail & Evidence Management ✅ PRIMARY
**Immutable log** of every alert, response, and rule change

- Who saw what evidence, when
- How long it took to respond
- What action was taken
- Evidence clips stored locally with encryption
- Automatic deletion after retention period (configurable: 7-90 days)

---

## Architecture Alignment

### What We Have vs. What We Need

| Component | Current Status | Needed for Core Vision | Action |
|-----------|---------------|----------------------|--------|
| **Frigate NVR** | ✅ In compose.yaml | Local video storage | Keep |
| **YOLO Detection** | ✅ In nura-perception | Person detection | Keep |
| **MediaPipe Pose** | ✅ In nura-perception | Fall detection | Keep |
| **VLM Integration** | ❌ Missing | **Context understanding** | **ADD** |
| **RAG Knowledge Base** | ⚠️ Stub in nura-rag | **Rule matching** | **IMPLEMENT** |
| **Rule Engine** | ⚠️ Stub in nura-rules | **Violation detection** | **IMPLEMENT** |
| **Alert System** | ⚠️ Stub in nura-notifier | **Real-time alerts** | **IMPLEMENT** |
| **RuView Integration** | ❌ Missing | **WiFi sensing** | **ADD** |
| **Parlor-like VLM** | ❌ Missing | **Multimodal AI** | **ADD** |
| **Attendance/Billing** | ❌ Not needed yet | Phase 3 monetization | **DEFER** |

### Critical Missing Pieces

#### 1. **VLM Service (NEW)** - Vision-Language Model for Context
**Service**: `nura-vlm` (Python/FastAPI)

**Purpose**: Analyze camera frames and answer questions like:
- "Is there an adult in this room?"
- "What is this person doing?"
- "Is this appropriate physical contact?"
- "How many children are visible?"

**Technology Options**:
- **Ollama + LLaVA 13B** (local, free, 24GB VRAM)
- **GPT-4 Vision API** (cloud fallback, costs $0.01/image)
- **Claude 3.5 Vision** (cloud fallback, high quality)
- **Moondream 2B** (lightweight, 8GB VRAM, fast)

**Integration**:
```
Camera → Frigate → nura-perception (detects event) 
                      ↓
                   nura-vlm (analyzes context)
                      ↓
                   nura-rules (matches rule)
                      ↓
                   nura-notifier (sends alert)
```

#### 2. **Enhanced RAG Service** - Rule Knowledge Base
**Service**: `nura-rag` (TypeScript/NestJS, already exists but needs implementation)

**Purpose**:
- Load school policies (PDF upload)
- Load government regulations (per region)
- Index with embeddings (Qdrant)
- Match detected events to specific rule clauses
- Answer admin questions: "What does regulation XYZ say about supervision ratios?"

**Example Query**:
```typescript
const ruleMatch = await ragService.findViolation({
  event: "child_alone_in_room",
  context: "Two children ages 4-5, no adult present, duration 45 seconds",
  location: "classroom-2"
});

// Returns:
// {
//   rule_id: "RULE-003",
//   title: "Continuous Supervision Required",
//   clause: "Children ages 0-5 must be within sight and sound of staff at all times",
//   source: "State Childcare Regulation §45.1.2",
//   severity: "critical",
//   suggested_action: "Send staff to classroom immediately, document incident"
// }
```

#### 3. **RuView WiFi Sensing Integration** (NEW)
**Service**: `nura-wifi-sensing` (Rust/Python wrapper)

**Purpose**: Detect occupancy in uncovered areas (bathrooms, changing rooms)

**Hardware**: ESP32 nodes (4-6 per site) on isolated WiFi

**Events Published**:
```json
{
  "zone": "bathroom-staff",
  "occupancy": "occupied",
  "count": 2,
  "duration_seconds": 180,
  "anomaly": "adult_and_child_together"
}
```

**Rule Example**:
- "If bathroom occupied by adult + child for >2 minutes → Alert (potential abuse scenario)"

---

## Revised Phase Plan

### Phase 1: Camera Violation Detection MVP (4-6 weeks) ✅ **START HERE**

**Goal**: Detect and alert on 6-8 core violations in 2 classrooms

**Deliverables**:
1. ✅ **nura-perception** (YOLO + MediaPipe) - person/pose detection
2. ⭐ **nura-vlm** (LLaVA or Moondream) - scene understanding
3. ⭐ **nura-rag** (Qdrant + embeddings) - rule knowledge base
4. ⭐ **nura-rules** (rule engine) - violation detection
5. ⭐ **nura-notifier** (push + SMS) - real-time alerts
6. ✅ **Frigate NVR** - local video storage
7. ✅ **Admin dashboard** (Next.js) - alert feed

**Rules for Pilot**:
- Children alone without staff (>30s)
- Child leaving designated area
- Person in restricted zone
- Room over capacity
- Fall/injury detection
- Door/gate left open

**Success Criteria**:
- ✅ 90% accuracy on critical alerts (pilot site validation)
- ✅ <10 second alert latency
- ✅ Zero video data leaks off-site (verified by network audit)
- ✅ Administrators say alerts are actionable

### Phase 2: WiFi Sensing + Advanced Rules (6-8 weeks)

**Adds**:
- RuView WiFi sensing integration
- Bathroom/changing room occupancy monitoring
- Aggressive behavior detection (VLM + pose)
- Unauthorized person detection (face matching against staff database)
- Multi-camera tracking (person follows across rooms)

### Phase 3: Monetization & Scaling (8-12 weeks)

**Adds**:
- Attendance tracking (reuse camera person detection)
- Billing automation (track child-hours from attendance)
- Staff credential tracking
- Multi-site fleet management
- Regional rule pack marketplace

---

## Technology Stack (Revised)

### Core AI/ML Pipeline

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Video Ingestion** | Frigate NVR | Local RTSP stream management |
| **Object Detection** | Ultralytics YOLO v8 | Person detection, bounding boxes |
| **Pose Estimation** | MediaPipe Pose | Fall detection, body posture |
| **Scene Understanding** | **LLaVA 13B / Moondream 2B** | **Context analysis** |
| **Rule Knowledge** | Qdrant + sentence-transformers | **RAG vector search** |
| **Rule Engine** | Custom (NestJS) | **Violation matching** |
| **WiFi Sensing** | **RuView (Rust + ESP32)** | **Uncovered area occupancy** |

### Infrastructure (No Changes)

- **Edge Box**: Docker Compose on mini PC (32GB RAM, NVIDIA GPU 24GB)
- **Database**: PostgreSQL + TimescaleDB + PostGIS
- **Event Bus**: NATS JetStream
- **Auth**: Keycloak (local + cloud sync)
- **Storage**: Local SSD (500GB+, clips + models)

---

## Open Source Components to Integrate

### 1. **Parlor** (Multimodal AI Framework)
**Repo**: https://github.com/fikrikarim/parlor  
**Language**: Python  
**What it does**: On-device real-time multimodal AI (vision + speech + text)

**How we use it**:
- Inspiration for VLM integration architecture
- Real-time frame analysis patterns
- Multimodal event correlation (visual + audio anomalies)

**Adopt**:
- Frame sampling strategies (don't analyze every frame, sample intelligently)
- VLM prompt templates for scene understanding
- Local inference optimization (MLX for Apple Silicon, CUDA for NVIDIA)

### 2. **RuView** (WiFi Sensing)
**Repo**: https://github.com/ruvnet/ruview  
**Language**: Rust + TypeScript + ESP32 firmware  
**What it does**: Turn WiFi signals into spatial intelligence (presence, vital signs, pose)

**How we use it**:
- ESP32 firmware for WiFi sensing nodes
- Rust service for signal processing
- REST API for occupancy data
- MQTT bridge to NATS

**Integration**:
```
ESP32 nodes (sensor VLAN) 
  → RuView service (Rust) 
  → MQTT → nura-sensor-adapter 
  → NATS events → nura-rules
```

### 3. **LangChain** (RAG Framework)
**For**: nura-rag service  
**Use**: Document loading (PDFs), chunking, embeddings, vector search

### 4. **Ollama** (Local LLM Runtime)
**For**: nura-vlm service  
**Models**: LLaVA 13B (vision), Mistral 7B (text RAG)

### 5. **Additional Open Source Tools**

| Tool | Purpose | License |
|------|---------|---------|
| **OpenCV** | Image preprocessing | BSD |
| **scikit-learn** | Anomaly detection | BSD |
| **sentence-transformers** | Embeddings for RAG | Apache 2.0 |
| **Qdrant** | Vector database | Apache 2.0 |
| **go2rtc** | RTSP stream relay | MIT |
| **step-ca** | Device certificates | Apache 2.0 |

---

## Example: Full Detection Flow

### Scenario: Child Alone in Classroom

**1. Camera Feed** (continuous)
```
Frigate → RTSP stream → nura-perception
```

**2. Person Detection** (YOLO, 30 FPS)
```
Frame analysis:
- Person 1: child (bbox: [120, 200, 80, 150], confidence: 0.94)
- Person 2: child (bbox: [450, 210, 75, 145], confidence: 0.91)
- No adults detected
```

**3. Context Analysis** (VLM, triggered after 30s of no-adult state)
```
nura-vlm prompt:
"Analyze this classroom image. Are there any adults present? How many children? 
What are the children doing? Is the situation safe or concerning?"

LLaVA response:
"Two children approximately ages 4-5 sitting at a table. No adults visible in frame.
Children appear calm, engaged in coloring activity. Potential supervision concern."
```

**4. Rule Matching** (RAG)
```
nura-rag query:
"Children in room with no adult for 30+ seconds"

Match found:
- Rule: STATE-REG-45.1.2
- Title: "Continuous Direct Supervision"
- Clause: "Children ages 0-5 must be within sight of staff at all times"
- Severity: CRITICAL
```

**5. Alert Generated** (<10s total latency)
```json
{
  "alert_id": "ALR-2024-1103-0023",
  "timestamp": "2024-11-03T14:23:45Z",
  "camera": "classroom-2",
  "rule": "STATE-REG-45.1.2",
  "title": "Children Unattended",
  "description": "Two children (ages 4-5) in classroom with no adult supervision for 45 seconds",
  "severity": "critical",
  "evidence_clip": "/evidence/2024-11-03/classroom-2-142300.mp4",
  "suggested_action": "Send staff to Classroom 2 immediately"
}
```

**6. Notification** (multi-channel)
- 📱 Push to admin phones
- 🔔 Dashboard alert (red banner)
- 📺 Wall display flashes
- 📧 Email (if unacknowledged after 2 minutes)

**7. Response Logged**
```
14:24:15 - Alert acknowledged by Admin "Sarah K."
14:24:45 - Teacher "Emily R." arrived at classroom (camera confirmed)
14:25:00 - Alert resolved, incident logged
```

---

## Next Steps (Immediate)

### Week 1: VLM Integration
- [ ] Set up Ollama + LLaVA 13B on dev machine
- [ ] Create nura-vlm service (FastAPI)
- [ ] Test VLM prompts for scene understanding
- [ ] Benchmark inference speed (target: <2s per frame)

### Week 2: RAG Implementation
- [ ] Load sample school policy PDFs into Qdrant
- [ ] Implement RAG query in nura-rag
- [ ] Create rule matching API
- [ ] Test retrieval accuracy

### Week 3: Rule Engine
- [ ] Define rule schema (YAML or JSON)
- [ ] Implement nura-rules service (NestJS)
- [ ] Connect detection → VLM → RAG → rules pipeline
- [ ] Test end-to-end with sample violations

### Week 4: Alert System
- [ ] Implement push notifications (ntfy)
- [ ] Build admin dashboard alert feed
- [ ] Add evidence clip storage + access logging
- [ ] Test alert latency (<10s)

---

**This is the real NURA.** Let's build it.
