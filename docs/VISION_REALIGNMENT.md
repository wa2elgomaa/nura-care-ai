# NURA Vision Realignment Summary

**Date**: 2026-11-03  
**Status**: ✅ **COMPLETE - Architecture Realigned to Safety-First**

---

## What Changed

### ❌ Previous Focus (WRONG)
- **Phase 1**: Attendance tracking, billing, staff credentials (operational core)
- **Phase 2**: Edge deployment + safety features
- **Phase 3**: Behavioral intelligence

**Problem**: Safety monitoring was treated as a "Phase 2" feature, but it's actually **THE CORE PRODUCT**.

### ✅ New Focus (CORRECT)
- **Phase 1**: Camera violation detection with AI (safety monitoring)
- **Phase 2**: WiFi sensing for uncovered areas
- **Phase 3**: Fleet management + compliance reporting
- **Phase 4**: Monetization features (attendance, billing) - OPTIONAL

**Result**: Safety IS the product. Everything else is secondary.

---

## Core Product Definition

### What NURA Actually Is

> **"An AI-powered system that watches cameras 24/7, understands what's happening using Vision-Language Models, detects violations against school rules and regulations, and alerts administrators within 10 seconds — all while keeping video data completely on school servers."**

**Think**: Parlor (multimodal AI) + Frigate (local NVR) + RAG (rule knowledge)

---

## Architecture Changes

### Services Added

#### 1. ⭐ **nura-vlm** (NEW - CRITICAL)
**Purpose**: Vision-Language Model for scene understanding

**What it does**:
- Analyzes camera frames beyond object detection
- Answers questions: "Is there an adult? What are they doing? Is this safe?"
- Provides context for rule matching

**Technology**:
- Ollama + LLaVA 13B (or Moondream 2B for lightweight)
- FastAPI service
- Inference: <2 seconds per frame

**Why it's critical**: YOLO can detect "2 persons" but can't tell you if one is an adult supervising. VLM provides the **context** needed for safety monitoring.

#### 2. ⭐ **nura-wifi-sensing** (Phase 2)
**Purpose**: WiFi-based occupancy detection (RuView integration)

**What it does**:
- Detects presence in uncovered areas (bathrooms, changing rooms)
- No cameras, no images - just occupancy signals
- Alerts on anomalies (adult + child together >2 minutes)

**Technology**:
- RuView service (Rust + ESP32 firmware)
- 4-6 ESP32 nodes per site
- MQTT → NATS bridge

### Services Enhanced

#### **nura-rag** (Already exists, now properly defined)
**NEW Purpose**: RAG-based rule knowledge base

**What it does**:
- Load school policies (PDF upload)
- Load government regulations (per region: US, UAE, UK)
- Vector search (Qdrant) to match events to rule clauses
- Answer admin questions about regulations

**Example**:
```
Event: "child_alone_in_room for 45 seconds"
↓
RAG query: "What rules govern supervision?"
↓
Match: "State Regulation §45.1.2 - Children 0-5 must be within sight of staff"
↓
Alert: "CRITICAL - Supervision violation in Classroom 2"
```

#### **nura-rules** (Already exists, now properly defined)
**NEW Purpose**: Violation detection engine

**What it does**:
- Receives detection events from nura-perception
- Receives context analysis from nura-vlm
- Queries nura-rag for rule matches
- Generates violation alerts with evidence

**Flow**:
```
Detection → Context → Rule Match → Alert
```

#### **nura-notifier** (Already exists, now properly defined)
**NEW Purpose**: Real-time multi-channel alerts

**What it does**:
- Push notifications (ntfy) - <10s latency
- SMS for critical alerts
- Email summaries
- Dashboard real-time feed

**Example Alert**:
```
🚨 CRITICAL ALERT
Classroom 2: Children Unattended
2 children (ages 4-5) with no adult for 45 seconds
Rule: STATE-REG-45.1.2
Action: Send staff immediately
[View Evidence] (15-second clip, local only)
```

---

## Detection Pipeline (Complete Flow)

```
┌─────────────┐
│   Camera    │ (RTSP feed)
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│  Frigate NVR            │ (Local storage + restream)
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  nura-perception        │ ⭐ YOLO detects persons + MediaPipe pose
│  (Python/FastAPI)       │    Output: "2 children, 0 adults, 45 seconds"
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  nura-vlm               │ ⭐⭐ NEW - VLM analyzes context
│  (Python/FastAPI)       │    Query: "Is there an adult?"
│  Ollama + LLaVA         │    Output: "No adult visible, children unsupervised"
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  nura-rag               │ ⭐ RAG matches rule
│  (TypeScript/NestJS)    │    Query: "supervision violation"
│  Qdrant + embeddings    │    Match: "STATE-REG-45.1.2"
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  nura-rules             │ ⭐ Rule engine decides
│  (TypeScript/NestJS)    │    Threshold met? Yes (>30s without adult)
└──────┬──────────────────┘    Severity? CRITICAL
       │
       ▼
┌─────────────────────────┐
│  nura-notifier          │ ⭐ Alert sent (<10s total)
│  (TypeScript/NestJS)    │    Push → Admin phones
└──────┬──────────────────┘    Dashboard → Red banner
       │                       SMS → If unacknowledged 2min
       ▼
   Admins notified!
```

**Total Latency**: <10 seconds from violation to alert

---

## Safety Rules for Phase 1 (6-8 Rules)

| Priority | Rule | Detection | Trigger |
|----------|------|-----------|---------|
| **P0** | Children alone without staff | YOLO + VLM | >30s |
| **P0** | Child leaving designated area | YOLO tracking | Immediate |
| **P0** | Fall/injury detection | MediaPipe pose | Immediate |
| **P1** | Restricted area access | YOLO + zones | Immediate |
| **P1** | Room over capacity | YOLO count | >5 min |
| **P1** | Door/gate left open | Object detection | >2 min |
| **P2** | Physical contact concern | VLM analysis | Review |
| **P2** | Aggressive behavior | Pose + VLM | Immediate |

---

## Open Source Components Integration

### Immediate Use (Phase 1)

| Component | Source | Purpose |
|-----------|--------|---------|
| **Frigate NVR** | frigate.video | ✅ Already integrated |
| **Ultralytics YOLO** | ultralytics | ✅ Already integrated |
| **MediaPipe** | Google | ✅ Already integrated |
| **LLaVA / Moondream** | Ollama | ⭐ NEW - VLM for context |
| **Qdrant** | qdrant.tech | ✅ Already in compose |
| **LangChain** | LangChain | NEW - RAG framework |
| **sentence-transformers** | HuggingFace | NEW - Embeddings |

### Phase 2

| Component | Source | Purpose |
|-----------|--------|---------|
| **RuView** | github.com/ruvnet/ruview | WiFi sensing |
| **ESP32 firmware** | RuView project | Sensor nodes |
| **Parlor patterns** | github.com/fikrikarim/parlor | Multimodal AI inspiration |

---

## What We're NOT Building (Yet)

To stay focused on safety:

❌ Attendance tracking (Phase 4)  
❌ Billing automation (Phase 4)  
❌ Staff credential tracking (Phase 4)  
❌ Medication logs (Phase 4)  
❌ Parent portal (Phase 4)  
❌ Bus tracking (Phase 4)

**These are valuable but NOT part of the core safety product.**

---

## Updated Documentation

### New Files Created
1. ✅ **docs/CORE_VISION.md** - Product vision and detection flow
2. ✅ **.speckit/PHASES_REVISED.md** - Safety-first phase plan
3. ✅ **services/nura-vlm/** - VLM service template
4. ✅ **VISION_REALIGNMENT.md** - This document

### Updated Files
1. ✅ **README.md** - Rewritten to focus on safety monitoring
2. ✅ **docs/ARCHITECTURE.md** - Still valid, VLM added
3. ✅ **compose.yaml** - Ready for nura-vlm service

---

## Development Roadmap (Next 6 Weeks)

### Week 1: VLM Integration ⏰ **START NOW**
- [ ] Install Ollama + LLaVA 13B locally
- [ ] Test VLM scene understanding
- [ ] Implement nura-vlm service
- [ ] Benchmark inference speed

**Goal**: VLM answers "Is there an adult in this room?"

### Week 2: RAG Implementation
- [ ] Load sample policies into Qdrant
- [ ] Implement rule matching in nura-rag
- [ ] Create rule schema (YAML)
- [ ] Test retrieval accuracy

**Goal**: RAG returns matching rules for violations

### Week 3: Rule Engine
- [ ] Implement nura-rules violation logic
- [ ] Connect detection → VLM → RAG → rules
- [ ] Add threshold logic (e.g., ">30s")
- [ ] Test 3 core rules end-to-end

**Goal**: Pipeline generates violation events

### Week 4: Alert System
- [ ] Implement push notifications
- [ ] Build dashboard alert feed
- [ ] Add evidence clip viewer
- [ ] Test <10s latency

**Goal**: Admins receive alerts within 10 seconds

### Week 5: Integration Testing
- [ ] Deploy to dev edge box (GPU)
- [ ] Test with real classroom footage
- [ ] Seed test violations
- [ ] Tune thresholds

**Goal**: 90% accuracy on test events

### Week 6: Pilot Preparation
- [ ] Document installation
- [ ] Train administrators
- [ ] Deploy to pilot site (2 cameras)
- [ ] Validate 24/7 operation

**Goal**: Pilot site operational

---

## Success Criteria (Phase 1)

| Metric | Target | How We Measure |
|--------|--------|----------------|
| **Accuracy** | 90%+ correct alerts | Seeded test events + pilot validation |
| **Latency** | <10 seconds | Violation → Alert timestamp |
| **Privacy** | Zero video leaks | Network audit (pcap analysis) |
| **Reliability** | 24/7 uptime | 2-week continuous operation |
| **Usability** | Admins say "actionable" | End-of-pilot survey |

---

## What This Means

### For Product
✅ **Clear value proposition**: "We keep your children safe"  
✅ **Focused roadmap**: Safety first, monetization later  
✅ **Real differentiation**: AI-powered real-time monitoring

### For Engineering
✅ **Clear architecture**: Detection → VLM → RAG → Rules → Alert  
✅ **Right tech stack**: Python for AI, TypeScript for business logic  
✅ **Incremental delivery**: Week-by-week milestones

### For Customers
✅ **Immediate value**: Safety monitoring from day 1  
✅ **Privacy guarantee**: All video stays on-premise  
✅ **Compliance**: Automated rule enforcement + audit trail

---

## Next Actions

### Immediate (This Week)
1. **Install Ollama** on dev machine
2. **Pull LLaVA model**: `ollama pull llava:13b`
3. **Test VLM locally** with sample classroom images
4. **Start nura-vlm implementation**

### This Month
1. Complete nura-vlm service
2. Implement nura-rag with sample rules
3. Build detection pipeline (perception → VLM → rules)
4. Deploy to dev edge box with GPU

### This Quarter
1. Pilot site deployment (2 classrooms)
2. 6-8 rules operational
3. Admins trained and using system
4. Pilot report with accuracy metrics

---

## Questions?

- **"What about attendance/billing?"** → Phase 4, optional monetization features
- **"Is this too complex?"** → No, this is what the market needs for safety
- **"Can we ship faster without VLM?"** → No, VLM is critical for context understanding
- **"What if Ollama is slow?"** → We have lightweight options (Moondream 2B)
- **"How do we make money?"** → Safety monitoring subscription + optional add-ons (Phase 4)

---

**Status**: ✅ Architecture realigned to safety-first vision  
**Ready**: Phase 1 development can start immediately  
**Next**: VLM integration (Week 1)

---

**The mission is clear: Keep children safe through AI-powered real-time monitoring, with zero privacy compromise.**
