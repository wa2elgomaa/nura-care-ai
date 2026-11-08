# Week 6 Implementation Plan - Complete Strategy

**Date**: 2026-11-08  
**Decisions Made**: Face Service + Privacy Mode + RAG/Rules Integration  
**Timeline**: 2-3 weeks total

---

## Summary of Decisions

### 1. ✅ Create Dedicated nura-face Service
**Why**: Centralized face operations, better scalability, future-ready for custom models  
**Timeline**: Week 6-7 (parallel with other work)  
**Priority**: HIGH

### 2. ✅ Implement nura-perception (Privacy-First Mode)
**Why**: Privacy compliance, better tracking, env-variable switchable  
**Timeline**: Week 6 (1 week)  
**Priority**: HIGH

### 3. ✅ Integrate nura-rag + nura-rules (Option A)
**Why**: Compliance-based violations, regulation matching, audit trail  
**Timeline**: Week 6 (5-7 days)  
**Priority**: HIGH

---

## Three Parallel Tracks

### Track 1: RAG + Rules Integration (Option A)
**Owner**: Backend Team  
**Duration**: 5-7 days  
**Deliverable**: Compliance-based violation detection

**Tasks**:
1. Configure nura-rag service
2. Load policy documents (Ministry, State, School)
3. Configure nura-rules orchestrator
4. Implement threshold tracking
5. Integrate RAG matching
6. Update VLM event publishing
7. End-to-end testing

**Value**: 
- Rule-based compliance (not hard-coded)
- Match violations to regulations
- Custom school rules
- Audit trail for violations

---

### Track 2: nura-face Service Creation
**Owner**: AI/Vision Team  
**Duration**: 1-2 weeks  
**Deliverable**: Centralized face recognition API

**Tasks**:
1. Create service structure
2. Implement face enrollment API
3. Implement face recognition API
4. Implement search API
5. Migrate from nura-vlm
6. Update calling services
7. Testing

**Value**:
- Centralized face operations
- Better model management
- Scalable architecture
- Future: custom models, fine-tuning

---

### Track 3: nura-perception Implementation
**Owner**: Computer Vision Team  
**Duration**: 1 week  
**Deliverable**: Privacy-first detection mode

**Tasks**:
1. Complete YOLO detection loop
2. Integrate ByteTrack
3. Add MediaPipe pose estimation
4. NATS event publishing
5. Environment-based mode switching
6. Testing both modes

**Value**:
- Privacy-first option (frames never leave edge)
- Better tracking (ByteTrack)
- Better activity detection (MediaPipe)
- Env-switchable modes

---

## Detailed Timeline

### Week 6: Core Implementation

#### Days 1-2: RAG Setup + nura-face Foundation
**RAG Track**:
- ✅ Configure nura-rag service
- ✅ Load sample policy documents
- ✅ Test rule matching
- ✅ Verify embeddings working

**Face Track**:
- ✅ Create nura-face service structure
- ✅ Setup FastAPI + InsightFace
- ✅ Database schema for face embeddings
- ✅ Basic health endpoint

**Perception Track**:
- ✅ Review nura-perception skeleton
- ✅ Setup YOLO detection loop
- ✅ Basic person detection working

#### Days 3-4: Rules Engine + Face APIs
**RAG Track**:
- ✅ Configure nura-rules service
- ✅ Implement NATS subscriptions
- ✅ Implement threshold tracking
- ✅ Basic violation creation

**Face Track**:
- ✅ Implement enrollment API
- ✅ Implement recognition API
- ✅ Test face matching
- ✅ pgvector similarity search

**Perception Track**:
- ✅ Integrate ByteTrack
- ✅ Multi-object tracking working
- ✅ Test tracking accuracy

#### Days 5-6: Integration
**RAG Track**:
- ✅ Integrate RAG query in rules engine
- ✅ Update VLM event publishing
- ✅ End-to-end test
- ✅ Verify violation workflow

**Face Track**:
- ✅ Implement search API
- ✅ Unknown person handling
- ✅ Model management endpoints

**Perception Track**:
- ✅ Add MediaPipe pose estimation
- ✅ Activity classification from poses
- ✅ Fall detection
- ✅ NATS event publishing

#### Day 7: Testing & Documentation
**All Tracks**:
- ✅ End-to-end integration testing
- ✅ Performance benchmarking
- ✅ Documentation updates
- ✅ Demo preparation

---

### Week 7: Migration & Mode Switching

#### Days 1-2: Face Service Migration
- ✅ Update guardian_api to call nura-face
- ✅ Update visitor_api to call nura-face
- ✅ Update person_search_api to call nura-face
- ✅ Update stream-processor to call nura-face
- ✅ Migrate existing face embeddings
- ✅ Test all endpoints

#### Days 3-4: Perception Mode Switching
- ✅ Implement environment-based service selection
- ✅ Docker compose profiles (edge-box vs standard)
- ✅ Test ENABLE_EDGE_BOX=true mode
- ✅ Test ENABLE_EDGE_BOX=false mode
- ✅ Performance comparison

#### Days 5-7: Final Testing & Polish
- ✅ End-to-end testing all modes
- ✅ Performance optimization
- ✅ Documentation completion
- ✅ Deployment guides

---

## Architecture After Week 6-7

### Privacy Mode (ENABLE_EDGE_BOX=true):
```
Camera → Frigate → nura-perception
                        ↓
                   YOLO + ByteTrack
                   MediaPipe Pose
                        ↓
                   NATS Events (anonymous)
                        ↓
                   nura-rules
                        ↓
                   nura-rag (rule matching)
                        ↓
                   Violations
                        ↓
                   nura-alerts
```

### Standard Mode (ENABLE_EDGE_BOX=false):
```
Camera → Frigate → Stream Processor → VLM
                                        ↓
                                   Person Detection
                                        ↓
                                   nura-face ⬅️ NEW!
                                   (identification)
                                        ↓
                                   NATS Events (identified)
                                        ↓
                                   nura-rules
                                        ↓
                                   nura-rag (rule matching)
                                        ↓
                                   Violations + Analytics
                                        ↓
                                   nura-alerts
```

---

## Configuration Examples

### Privacy-First School:
```env
# .env
ENABLE_EDGE_BOX=true              # Use nura-perception
ENABLE_FACE_RECOGNITION=false     # No face tracking
ENABLE_VLM_ANALYSIS=false         # No scene understanding
ENABLE_RAG_RULES=true             # Still use rule matching
```

**Result**: 
- ✅ Privacy compliant (no frames leave edge)
- ✅ Rule-based violations
- ❌ No face identification
- ❌ No student analytics

---

### Standard School (Full Features):
```env
# .env
ENABLE_EDGE_BOX=false             # Use VLM-based detection
ENABLE_FACE_RECOGNITION=true      # Full face tracking
ENABLE_VLM_ANALYSIS=true          # Scene understanding
ENABLE_RAG_RULES=true             # Rule matching
```

**Result**:
- ✅ Full features
- ✅ Face recognition
- ✅ Student analytics
- ✅ Rule-based violations
- ✅ Scene understanding

---

### Hybrid School:
```env
# .env
ENABLE_EDGE_BOX=true              # Privacy-first continuous monitoring
ENABLE_FACE_RECOGNITION=true      # But enable face service
ENABLE_VLM_ANALYSIS=false         # No VLM for continuous
ENABLE_RAG_RULES=true             # Rule matching
FACE_SERVICE_MODE=checkin_only    # Only for check-in/out
```

**Result**:
- ✅ Privacy-first continuous monitoring
- ✅ Face recognition only at check-in/out
- ✅ Best of both worlds

---

## Expected Outcomes

### After Week 6:
1. ✅ **nura-rag** fully integrated with rules engine
2. ✅ **nura-rules** orchestrating violations
3. ✅ **nura-face** service created and working
4. ✅ **nura-perception** privacy mode implemented
5. ✅ Environment-based mode switching
6. ✅ Compliance-based violation detection

### Services Status:

| Service | Before | After Week 6-7 |
|---------|--------|----------------|
| nura-face | ❌ Empty | ✅ Full service |
| nura-perception | 🟡 Skeleton | ✅ Production ready |
| nura-rag | 🟡 Not integrated | ✅ Integrated |
| nura-rules | 🟡 Not integrated | ✅ Integrated |
| nura-vlm | ✅ Working | ✅ Refactored (face → nura-face) |
| nura-stream-processor | ✅ Working | ✅ Updated (calls nura-face) |

---

## Testing Strategy

### Unit Tests:
- [ ] nura-face: enrollment, recognition, search
- [ ] nura-perception: detection, tracking, pose
- [ ] nura-rag: rule matching, embeddings
- [ ] nura-rules: threshold tracking, violation creation

### Integration Tests:
- [ ] Face enrollment → Recognition flow
- [ ] Detection → RAG → Violation flow
- [ ] Privacy mode end-to-end
- [ ] Standard mode end-to-end
- [ ] Mode switching

### Performance Tests:
- [ ] Face recognition latency (<100ms)
- [ ] Perception detection FPS (>15 fps)
- [ ] RAG matching latency (<100ms)
- [ ] Violation creation latency (<200ms)

---

## Documentation Deliverables

### Created:
1. ✅ `NURA_FACE_SERVICE_SPEC.md` - Face service specification
2. ✅ `NURA_PERCEPTION_ANALYSIS.md` - Privacy mode analysis
3. ✅ `WEEK6_RAG_RULES_INTEGRATION.md` - RAG/Rules integration plan
4. ✅ `WEEK6_IMPLEMENTATION_PLAN.md` - This document

### To Create:
- [ ] Face Service API Documentation
- [ ] Perception Mode User Guide
- [ ] RAG/Rules Configuration Guide
- [ ] Mode Switching Documentation
- [ ] Deployment Guide (privacy vs standard)

---

## Success Criteria

### Week 6 Complete When:
1. ✅ RAG + Rules integrated and working
2. ✅ Policy documents loaded and matching
3. ✅ Violations stored with rule references
4. ✅ nura-face service created
5. ✅ Face APIs working
6. ✅ nura-perception privacy mode working
7. ✅ Mode switching functional

### Week 7 Complete When:
1. ✅ All services migrated to nura-face
2. ✅ Environment-based switching tested
3. ✅ Both modes (privacy + standard) working
4. ✅ Performance benchmarks met
5. ✅ Documentation complete
6. ✅ Ready for production deployment

---

## Next Immediate Actions

### This Week (Starting Now):

**Day 1-2** (Today + Tomorrow):
1. 🚀 Start Track 1: Configure nura-rag
2. 🚀 Start Track 2: Create nura-face skeleton
3. 🚀 Start Track 3: Setup nura-perception YOLO loop

**Day 3-4**:
1. 🚀 RAG rule loading + testing
2. 🚀 Face enrollment API
3. 🚀 ByteTrack integration

**Day 5-6**:
1. 🚀 Rules engine threshold tracking
2. 🚀 Face recognition API
3. 🚀 MediaPipe pose estimation

**Day 7**:
1. 🚀 End-to-end testing
2. 🚀 Documentation
3. 🚀 Demo preparation

---

## Questions to Resolve

1. **Resource Allocation**: Which team works on which track?
2. **Priority Order**: Should any track start before others?
3. **Testing Strategy**: Unit tests as we go, or end-to-end at Week 7?
4. **Policy Documents**: Do we have Ministry/State regulations ready to load?
5. **Deployment**: Test on staging first, or directly to production?

---

## Recommendation

**Approach**: **Parallel Implementation** (all 3 tracks simultaneously)

**Why**:
- Tracks are independent (minimal conflicts)
- Faster time to completion (2 weeks vs 4-5 weeks sequential)
- Can test integration sooner
- Team members can work on different tracks

**Risk Mitigation**:
- Daily standups to sync progress
- Integration testing at end of Week 6
- Buffer time in Week 7 for issues

**Ready to proceed?** 🚀
