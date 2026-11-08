# Week 6 - Parallel Tracks Kickoff Summary

**Date**: 2026-11-08  
**Status**: 🚀 **STARTED** - All 3 tracks in progress  
**Approach**: Parallel implementation

---

## What We've Completed So Far

### Track 1: RAG + Rules Integration
✅ **nura-rag ConfigService** - Enhanced with centralized config pattern  
✅ **Sample Policy Documents Script** - Ready to load 5 rules (Ministry, State, School)

**Files Created/Modified**:
- `services/nura-rag/src/config/config.service.ts` - Enhanced ConfigService
- `services/nura-rag/scripts/load-sample-rules.sh` - Script to load sample rules

**Next Steps for Track 1**:
```bash
# 1. Build and start nura-rag service
cd /Users/wgomaa/Work/PixelPlusOne/Nura\ Childcare\ AI/nura-care-source
docker compose build nura-rag
docker compose up -d nura-rag

# 2. Load sample policy documents
./services/nura-rag/scripts/load-sample-rules.sh http://localhost:3002

# 3. Test RAG matching
curl -X POST http://localhost:3002/match \
  -H "Content-Type: application/json" \
  -d '{
    "event_context": "two children visible, no adult present for 45 seconds",
    "category": "supervision",
    "top_k": 3
  }'

# 4. Configure nura-rules service (similar ConfigService pattern)
# 5. Implement threshold tracking
# 6. Integrate RAG query in rules engine
```

---

### Track 2: nura-face Service
**Status**: Ready to start

**Next Steps for Track 2**:
```bash
# 1. Create service structure
mkdir -p services/nura-face/src/{api,config,models}
cd services/nura-face

# 2. Create files:
# - requirements.txt (FastAPI, InsightFace, psycopg2)
# - src/main.py (FastAPI app)
# - src/config.py (Pydantic ConfigService)
# - src/face_service.py (InsightFace wrapper)
# - src/api/enrollment.py (Enrollment endpoints)
# - src/api/recognition.py (Recognition endpoints)
# - src/api/search.py (Search endpoints)
# - Dockerfile

# 3. Create database migration for face_embeddings table
# 4. Implement enrollment API
# 5. Implement recognition API
# 6. Test with sample images
```

**Recommended Structure**:
```
services/nura-face/
├── src/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Pydantic config
│   ├── face_service.py      # InsightFace wrapper
│   ├── api/
│   │   ├── enrollment.py    # POST /api/face/enroll
│   │   ├── recognition.py   # POST /api/face/identify
│   │   └── search.py        # POST /api/face/search
│   └── models/
│       └── face_models.py   # Database models
├── requirements.txt
├── Dockerfile
└── README.md
```

---

### Track 3: nura-perception
**Status**: Ready to start

**Next Steps for Track 3**:
```bash
# 1. Review existing skeleton
cd services/nura-perception

# 2. Complete main.py implementation:
# - YOLO detection loop
# - Frigate restream connection
# - Person detection
# - NATS event publishing

# 3. Add ByteTrack:
# - Install: pip install boxmot
# - Integrate multi-object tracking
# - Persistent tracking IDs

# 4. Add MediaPipe:
# - Install: pip install mediapipe
# - Pose estimation
# - Activity classification from poses
# - Fall detection

# 5. Create ConfigService (Python/Pydantic)
# 6. Test with live camera feed
```

**Key Files to Implement**:
```
services/nura-perception/src/
├── main.py              # FastAPI app + detection loop
├── config.py            # Pydantic config
├── detector.py          # YOLO detector
├── tracker.py           # ByteTrack wrapper
├── pose_estimator.py    # MediaPipe pose
├── activity_classifier.py # Pose → activity
└── nats_publisher.py    # Event publishing
```

---

## Parallel Work Distribution

### If Working Solo:
**Recommended Order** (interleave tasks to avoid context switching):

**Day 1-2**: 
- Morning: Track 1 (RAG service setup + test)
- Afternoon: Track 2 (nura-face structure + enrollment API)

**Day 3-4**:
- Morning: Track 1 (Rules engine config + threshold tracking)
- Afternoon: Track 3 (nura-perception YOLO loop)

**Day 5-6**:
- Morning: Track 2 (Face recognition + search APIs)
- Afternoon: Track 3 (ByteTrack + MediaPipe)

**Day 7**:
- Integration testing all tracks
- Documentation

### If Working with Team:
**Person A**: Track 1 (RAG + Rules) - Backend TypeScript
**Person B**: Track 2 (nura-face) - Python AI/Vision
**Person C**: Track 3 (nura-perception) - Python Computer Vision

---

## Environment Variables Needed

### Track 1 (RAG + Rules):
```env
# nura-rag
PORT=3002
EMBEDDING_MODEL=Xenova/all-MiniLM-L6-v2
SIMILARITY_THRESHOLD=0.7
SITE_ID=dev-site-001

# nura-rules
PORT=3003
NATS_URL=nats://nats:4222
RAG_SERVICE_URL=http://nura-rag:3002
VLM_SERVICE_URL=http://host.docker.internal:8001
SUPERVISION_THRESHOLD_SECONDS=30
```

### Track 2 (nura-face):
```env
NURA_FACE_PORT=8002
NURA_FACE_HOST=0.0.0.0
FACE_RECOGNITION_MODEL=buffalo_l
FACE_RECOGNITION_THRESHOLD=0.6
FACE_EMBEDDING_DIM=512
ENABLE_GPU=true
GPU_DEVICE_ID=0
FACE_PHOTOS_PATH=/data/face-photos
```

### Track 3 (nura-perception):
```env
PORT=8000
NATS_URL=nats://nats:4222
RTSP_BASE=rtsp://frigate:8554
FRIGATE_API=http://frigate:5000
DETECTION_CONFIDENCE=0.5
FALL_THRESHOLD=0.7
SITE_ID=dev-site-001
ENABLE_BYTETRACK=true
ENABLE_MEDIAPIPE=true
```

---

## Integration Points

### Track 1 → Track 2:
- Rules engine will eventually call face service (not immediate)

### Track 1 → Track 3:
- Rules engine subscribes to perception events
- **Critical**: Event schema must match

### Track 2 → Track 3:
- Both independent, no direct integration

### All Tracks → Main System:
```
Perception → NATS → Rules → RAG → Alerts
              ↓
         Face Service
```

---

## Testing Strategy

### Track 1 Testing:
```bash
# Test RAG matching
curl -X POST http://localhost:3002/match -d '{"event_context": "no adult with children"}'

# Test Rules engine
docker run --rm --network nura_network natsio/nats-box \
  nats pub nura.events.detection '{"adults_detected": 0, "children_detected": 2}'
```

### Track 2 Testing:
```bash
# Test face enrollment
curl -X POST http://localhost:8002/api/face/enroll \
  -F "person_id=test_001" \
  -F "photo=@test_face.jpg"

# Test face recognition
curl -X POST http://localhost:8002/api/face/identify \
  -F "photo=@unknown_face.jpg"
```

### Track 3 Testing:
```bash
# Test detection endpoint
curl -X POST http://localhost:8000/detect \
  -F "image=@test_frame.jpg"

# Monitor NATS events
docker run --rm --network nura_network natsio/nats-box \
  nats sub "nura.events.detection"
```

---

## Success Criteria

### Track 1 Complete When:
- ✅ RAG service running and matching rules
- ✅ 5 sample policies loaded
- ✅ Rules engine tracking thresholds
- ✅ Violations created with rule references
- ✅ End-to-end: Detection → Rules → RAG → Violation

### Track 2 Complete When:
- ✅ Face service running
- ✅ Enrollment API working
- ✅ Recognition API working
- ✅ Search API working
- ✅ pgvector similarity search functional
- ✅ Unknown person handling implemented

### Track 3 Complete When:
- ✅ YOLO detection loop running
- ✅ ByteTrack multi-object tracking working
- ✅ MediaPipe pose estimation functional
- ✅ Activity classification from poses
- ✅ NATS events publishing
- ✅ Fall detection working

---

## Current Status

| Track | Task | Status |
|-------|------|--------|
| **Track 1** | RAG ConfigService | ✅ Done |
| **Track 1** | Sample Rules Script | ✅ Done |
| **Track 1** | Load Policy Docs | 🔄 Next |
| **Track 1** | Rules Engine Config | ⏳ Pending |
| **Track 2** | Service Structure | ⏳ Pending |
| **Track 2** | Enrollment API | ⏳ Pending |
| **Track 2** | Recognition API | ⏳ Pending |
| **Track 3** | YOLO Loop | ⏳ Pending |
| **Track 3** | ByteTrack | ⏳ Pending |
| **Track 3** | MediaPipe | ⏳ Pending |

---

## Immediate Next Actions

### For Track 1 (Continue Now):
```bash
# Start RAG service
docker compose up -d nura-rag

# Load sample rules
./services/nura-rag/scripts/load-sample-rules.sh

# Test matching
curl -X POST http://localhost:3002/match \
  -H "Content-Type: application/json" \
  -d '{"event_context": "children alone no adult"}'
```

### For Track 2 (Start Next):
```bash
# Create service directory
mkdir -p services/nura-face/src/{api,config,models}

# Create requirements.txt
# Create main.py with FastAPI
# Create config.py with Pydantic
```

### For Track 3 (Start After Track 2 Setup):
```bash
# Review existing code
cd services/nura-perception

# Complete src/main.py
# Add YOLO detection loop
# Test with Frigate feed
```

---

## Questions to Resolve

1. **Database Migrations**: Do we run migrations for face_embeddings table now?
2. **Testing Data**: Do we have sample face images for testing nura-face?
3. **Camera Access**: Do we have live camera feed for testing nura-perception?
4. **Priority**: Should any track be prioritized over others?

---

## Ready to Continue?

**Current position**: Track 1 configured, ready to load sample rules

**Next immediate action**: Start nura-rag service and load policy documents

**Shall I continue with Track 1 to completion, or would you like me to set up all 3 tracks first?**
