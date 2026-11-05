# NURA Positioning & Roadmap

## Current State (Q4 2026)

### ✅ What We've Built
- **Hybrid Fast-Path Architecture** - 300-500ms per frame
- **5 Specialized Detectors** - Violence, Distress, Body Language, Supervision, Pose
- **VLM Integration** - Context-aware validation
- **Video Analysis** - Frame-by-frame processing
- **Environment-Aware** - Configurable thresholds per location

### 📊 Performance Metrics
- **Speed:** 70% fast-path (<500ms), 30% VLM (20-30s)
- **Accuracy:** 100% on test images, 78% false positive reduction with tuning
- **Throughput:** ~2-3 FPS per camera (with VLM), ~30 FPS (fast-path only)

---

## Market Position

### Our Unique Value Proposition

**"VLM-powered contextual behavior detection for childcare safety"**

### Competitive Advantages
1. ✅ **VLM Integration** - Industry-first for childcare
2. ✅ **Hybrid Architecture** - Fast + Accurate
3. ✅ **Domain-Specific** - Purpose-built for childcare
4. ✅ **Self-Hosted** - Privacy-first
5. ✅ **Open Source** - Transparent & customizable

### Competitive Gaps
1. ✅ **Temporal Analysis** - NOW COMPLETE! (95.83% accuracy)
2. ❌ **Person Tracking** - No identity tracking
3. ❌ **Real-Time Streaming** - Batch video only
4. ❌ **Multi-Camera** - Single camera support

---

## Immediate Next Steps (Priority Order)

### Phase 3: Temporal Detection ✅ COMPLETE
**Completed:** 2026-11-05
**Status:** ✅ **Trained, integrated, and enabled**

**Completed Tasks:**
1. ✅ Integrated temporal detector into hybrid router
2. ✅ Added frame buffering (20-frame sequences)
3. ✅ Trained on violence-detection-dataset (240 balanced videos)
4. ✅ Enabled in production configuration
5. ✅ Added "sustained violence" scoring

**Results - EXCEEDED ALL TARGETS:**
- ✅ **95.83% accuracy** (target: 85%+)
- ✅ **0% false positives** on test set
- ✅ **8.3% false negatives** (target: <15%)
- ✅ F1-Score: 0.96 (both normal and violent classes)
- ✅ Model size: 1.2MB (lightweight)
- ⏳ Latency: ~300-500ms per sequence (estimated, needs benchmarking)

---

### Phase 4: Person Tracking
**Timeline:** 1 week
**Status:** Not started

**Tasks:**
1. Integrate DeepSORT or ByteTrack
2. Assign persistent IDs across frames
3. Link violations to individuals
4. Output incident timeline per person

**Success Criteria:**
- Track 5+ people simultaneously
- 90%+ ID consistency across frames
- "Child #3 involved in 2 incidents at 10:15 and 10:23"

---

### Phase 5: Real-Time Streaming
**Timeline:** 1 week
**Status:** Not started

**Tasks:**
1. RTSP/RTMP stream reader
2. Frame buffer management
3. Async detection pipeline
4. WebSocket for live alerts

**Success Criteria:**
- Process live stream at 2-5 FPS
- <2s alert latency
- Handle 4+ concurrent streams

---

## Technical Debt & Optimizations

### Performance Improvements (Ongoing)
- [ ] Replace HOG with Optical Flow (2x faster)
- [ ] GPU acceleration for YOLO
- [ ] Multi-threaded detection
- [ ] Reduce VLM validation to 10-15s

### Code Quality
- [ ] Add unit tests (detectors)
- [ ] Integration tests (hybrid router)
- [ ] Performance benchmarks
- [ ] CI/CD pipeline

---

## Long-Term Vision (6-12 months)

### System Integration
- Alert management (routing, escalation)
- Analytics dashboard (Grafana/custom)
- Multi-camera orchestration
- Integration with existing VMS (Frigate, etc.)

### Advanced AI
- Transformer-based temporal models
- Multimodal (audio + video)
- Predictive modeling (escalation detection)
- Fine-tuned VLM for childcare

### Deployment
- Edge deployment (Jetson, RPi)
- Cloud option (privacy-preserving)
- Mobile app (staff alerts)
- Parent portal (opt-in video access)

---

## Decision Matrix: What to Build vs Buy/Integrate

| Component | Build | Buy/Integrate | Rationale |
|-----------|-------|---------------|-----------|
| Behavior Detection | ✅ Build | | Our core IP |
| VLM Integration | ✅ Build | | Competitive advantage |
| Person Tracking | | ✅ Integrate (DeepSORT) | Commodity tech |
| Video Management | | ✅ Integrate (Frigate) | Not our focus |
| Camera Hardware | | ✅ Buy (standard IP cameras) | Hardware not software |
| Alert System | ✅ Build | | Domain-specific needs |
| Analytics | | ✅ Integrate (Grafana) | Standard dashboarding |
| Cloud Infra | | ✅ Use (Docker/K8s) | Standard DevOps |

---

## Success Metrics (3-Month Goals)

### Technical
- [ ] 90%+ accuracy on violence detection
- [ ] <500ms latency for 80% of frames
- [ ] Support 4+ concurrent cameras
- [ ] 95%+ uptime

### Product
- [ ] Pilot with 1-2 schools
- [ ] Process 100+ hours of video
- [ ] <5% false positive rate
- [ ] Positive feedback from staff

### Business
- [ ] Open source community (10+ contributors)
- [ ] Documentation complete
- [ ] Demo video
- [ ] Pricing model defined

