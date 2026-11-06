# Phase 4B: Person Identification & Multi-Camera Tracking

**Status:** 📋 Planning  
**Dependencies:** Phase 4 (Person Tracking)  
**Estimated Duration:** 5-6 weeks

## Overview

Extends Phase 4's anonymous person tracking with **real identity linking** and **multi-camera handoff**.

### Key Features

1. **Person Identification**
   - Link tracked IDs to real names (e.g., "Person 1" → "Adam W.")
   - Face recognition (primary, 95%+ accuracy)
   - Appearance-based ReID (fallback, 70-85% accuracy)

2. **Multi-Camera Tracking**
   - Track individuals across camera boundaries
   - Automatic handoff detection
   - Complete movement timeline

3. **Named Alerting**
   - "Violence: Adam W. pushed Noah M." (instead of "Person 1 pushed Person 2")
   - Persons involved in incidents clearly identified

4. **Location Search**
   - "Where is Adam W.?" → "Camera 3, Zone A, last seen 2 minutes ago"
   - Historical movement patterns

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Phase 4B Components                                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. FaceIdentifier                                  │
│     - Face detection (YOLO-Face)                    │
│     - Face encoding (ArcFace/FaceNet)               │
│     - Match vs enrollment DB                        │
│                                                     │
│  2. AppearanceReID                                  │
│     - Appearance embeddings (OSNet)                 │
│     - Cross-camera matching                         │
│     - Temporal voting                               │
│                                                     │
│  3. GlobalIdentityManager                           │
│     - Maps: local_id → global_id → real_name        │
│     - Cross-camera ID merging                       │
│     - Persistent identity storage                   │
│                                                     │
│  4. MultiCameraTracker                              │
│     - Camera topology & adjacency                   │
│     - Handoff detection (exit/entry matching)       │
│     - Movement timeline reconstruction              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 4B.1: Face Enrollment & Identification (Week 1-2)
- [ ] Face enrollment UI
- [ ] Face database (PostgreSQL + pgvector)
- [ ] FaceIdentifier class
- [ ] Integration with PersonTracker

### Phase 4B.2: Appearance ReID (Week 3)
- [ ] OSNet model integration
- [ ] Appearance matcher
- [ ] Temporal voting logic

### Phase 4B.3: Global Identity Manager (Week 4)
- [ ] Database schema
- [ ] GlobalIdentityManager class
- [ ] Search API

### Phase 4B.4: Multi-Camera Handoff (Week 5)
- [ ] Camera topology configuration
- [ ] Handoff detection
- [ ] Movement timeline

## Technical Decisions

### Face Recognition Library
**Recommended:** InsightFace (ArcFace)
- State-of-the-art accuracy
- Fast inference (~30ms)
- Well-maintained

**Alternatives:**
- face_recognition (dlib, easier but slower)
- DeepFace (multiple models, heavier)

### ReID Model
**Recommended:** OSNet
- Lightweight (~50ms)
- Good accuracy for appearance matching
- PyTorch-based

### Database
**Recommended:** PostgreSQL + pgvector
- Vector similarity search
- Existing infrastructure
- ACID compliance

## Privacy Considerations

⚠️ **Face biometrics are sensitive data**

**Requirements:**
- ✅ Parental consent for enrollment
- ✅ Encrypted storage (embeddings, not raw images)
- ✅ Access control (authorized staff only)
- ✅ Data retention policy (delete after child leaves)
- ✅ GDPR/COPPA compliance

**Mitigation:**
- Store embeddings only (can't reconstruct faces)
- Opt-out option (appearance-only, lower accuracy)
- Data deletion on request

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Face recognition accuracy | >90% | Enrolled, good lighting |
| Appearance ReID accuracy | >70% | Fallback method |
| Identification latency | <100ms | Per person, per frame |
| Camera handoff delay | <2s | Detection of transition |
| Scale | 100 children, 10 cameras | Initial deployment |

## Use Cases

### UC1: Named Alerts
**Before:** "Violence detected: Person 1 pushed Person 2"  
**After:** "Violence detected: Adam W. (aggressor) pushed Noah M. (victim)"

### UC2: Location Search
**Query:** "Where is Adam W.?"  
**Response:** "Camera 3, Zone A, last seen 2 minutes ago" + live thumbnail

### UC3: Movement Tracking
**Timeline:** "Adam W.: Playground (9:00 AM) → Hallway (9:15 AM) → Classroom (9:20 AM)"

## Next Steps

1. **Review & approve** this specification
2. **Setup enrollment database**
3. **Choose face recognition library**
4. **Build enrollment UI**
5. **Implement FaceIdentifier**

## Related Documents

- [Phase 4B Detailed Spec](spec.md)
- [Phase 4 Person Tracking Spec](../040-phase4-person-tracking/spec.md)
- [Privacy & Compliance Guidelines](../../docs/privacy/README.md) *(to be created)*
