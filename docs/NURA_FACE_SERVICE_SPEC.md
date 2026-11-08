# NURA Face Recognition Service - Specification

**Purpose**: Centralized face recognition service for all face-related operations  
**Status**: To Be Implemented  
**Priority**: High (Week 6)

---

## Why Separate Face Service?

### Current Problem:
- Face recognition logic scattered in nura-vlm
- Hard to optimize face operations independently
- Cannot scale face processing separately
- Model updates affect entire VLM service
- No dedicated GPU allocation for face tasks

### Benefits of Dedicated Service:

1. **Centralization**
   - Single API for all face operations
   - One place for model management
   - Consistent face recognition across all services

2. **Performance**
   - Dedicated GPU allocation
   - Optimized batch processing
   - Face-specific model caching
   - Can scale independently

3. **Model Management**
   - Easy model updates (InsightFace, custom models)
   - A/B testing of face models
   - Custom training on school data
   - Model versioning

4. **Reusability**
   - Guardian enrollment calls nura-face
   - Visitor enrollment calls nura-face
   - Stream processor calls nura-face
   - Person search calls nura-face
   - All use same API

5. **Future Capabilities**
   - Train custom models on school data
   - Fine-tune for childcare scenarios
   - Age estimation
   - Emotion detection (optional)
   - Mask detection

---

## Architecture

### Service Communication:
```
┌─────────────────────────────────────────────────────┐
│                  nura-face Service                  │
├─────────────────────────────────────────────────────┤
│  Face Enrollment  │  Face Recognition  │  Models    │
│  - Guardian       │  - Identify        │  - Buffalo │
│  - Visitor        │  - Match           │  - Custom  │
│  - Student        │  - Search          │  - Trained │
└─────────────────────────────────────────────────────┘
         ↑                    ↑                  ↑
         │                    │                  │
┌────────┴────────┐  ┌────────┴────────┐  ┌────┴─────┐
│  nura-vlm       │  │ stream-processor│  │ person   │
│  (Guardian API) │  │ (Identification)│  │ search   │
└─────────────────┘  └─────────────────┘  └──────────┘
```

### Data Flow:

**Enrollment Flow**:
```
Web UI → Guardian API (nura-vlm) → nura-face
                                      ↓
                                Face Embedding
                                      ↓
                              enrolled_persons DB
```

**Recognition Flow**:
```
Camera → Stream Processor → nura-face
                               ↓
                        Face Recognition
                               ↓
                     person_id (or unknown_NNN)
                               ↓
                       person_detections DB
```

---

## API Specification

### 1. Enrollment Endpoints

#### POST /api/face/enroll
Enroll a new face (guardian, visitor, student)

**Request**:
```json
{
  "person_id": "adam_w",
  "photo_base64": "base64_encoded_image",
  "person_type": "student|guardian|visitor"
}
```

**Response**:
```json
{
  "success": true,
  "person_id": "adam_w",
  "embedding_quality": 0.95,
  "face_detected": true,
  "embedding_id": "emb_123abc"
}
```

#### POST /api/face/enroll/batch
Enroll multiple faces for same person (improve accuracy)

**Request**:
```json
{
  "person_id": "adam_w",
  "photos": ["base64_1", "base64_2", "base64_3"]
}
```

---

### 2. Recognition Endpoints

#### POST /api/face/identify
Identify person from face crop

**Request**:
```json
{
  "photo_base64": "base64_encoded_face_crop",
  "threshold": 0.6,
  "top_k": 5
}
```

**Response**:
```json
{
  "identified": true,
  "person_id": "adam_w",
  "confidence": 0.87,
  "similarity": 0.89,
  "person_type": "student",
  "alternatives": [
    {"person_id": "emma_s", "confidence": 0.45}
  ]
}
```

#### POST /api/face/match
Match face against specific person

**Request**:
```json
{
  "photo_base64": "base64_encoded_image",
  "person_id": "adam_w"
}
```

**Response**:
```json
{
  "match": true,
  "similarity": 0.92,
  "confidence": 0.94
}
```

---

### 3. Search Endpoints

#### POST /api/face/search
Search across all enrolled faces

**Request**:
```json
{
  "photo_base64": "base64_encoded_image",
  "threshold": 0.6,
  "limit": 10,
  "person_types": ["student", "guardian"]
}
```

**Response**:
```json
{
  "results": [
    {
      "person_id": "adam_w",
      "similarity": 0.92,
      "person_type": "student",
      "full_name": "Adam Williams"
    }
  ],
  "query_time_ms": 45
}
```

---

### 4. Model Management

#### GET /api/face/models
List available models

**Response**:
```json
{
  "models": [
    {
      "name": "buffalo_l",
      "status": "active",
      "accuracy": 0.996,
      "speed_ms": 50
    },
    {
      "name": "custom_childcare_v1",
      "status": "available",
      "accuracy": 0.998,
      "speed_ms": 75
    }
  ]
}
```

#### POST /api/face/models/switch
Switch active model

**Request**:
```json
{
  "model_name": "custom_childcare_v1"
}
```

---

### 5. Unknown Person Handling

#### POST /api/face/unknown/create
Create unknown person entry

**Request**:
```json
{
  "embedding": [0.123, 0.456, ...],
  "photo_base64": "base64_encoded_image"
}
```

**Response**:
```json
{
  "unknown_id": "unknown_001",
  "similar_to": null
}
```

#### POST /api/face/unknown/link
Link unknown to known person

**Request**:
```json
{
  "unknown_id": "unknown_001",
  "person_id": "adam_w"
}
```

---

## Technology Stack

### Core:
- **Framework**: FastAPI (Python) - async, high performance
- **Face Recognition**: InsightFace (Buffalo_L model)
- **Face Detection**: SCRFD (from InsightFace)
- **GPU**: ONNX Runtime (CPU/CUDA/TensorRT)
- **Database**: PostgreSQL (store embeddings with pgvector)

### Models:
- **Primary**: Buffalo_L (512-dim embeddings, 99.6% accuracy)
- **Alternative**: Buffalo_S (256-dim, faster, 99.3% accuracy)
- **Custom**: Fine-tuned on childcare data (future)

### Dependencies:
```python
insightface==0.7.3
onnxruntime==1.16.3  # or onnxruntime-gpu
opencv-python-headless==4.9.0.80
fastapi==0.109.0
uvicorn==0.27.0
psycopg2-binary==2.9.9
numpy==1.26.3
```

---

## Database Schema

### Face Embeddings Table:
```sql
CREATE TABLE face_embeddings (
    id SERIAL PRIMARY KEY,
    person_id VARCHAR(50) NOT NULL,
    embedding vector(512),  -- pgvector
    embedding_quality FLOAT,
    photo_path TEXT,
    model_name VARCHAR(50) DEFAULT 'buffalo_l',
    created_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (person_id) REFERENCES enrolled_persons(person_id)
);

-- Vector similarity index
CREATE INDEX face_embeddings_vector_idx
ON face_embeddings USING ivfflat (embedding vector_cosine_ops);
```

---

## Performance Requirements

| Metric | Target | Implementation |
|--------|--------|----------------|
| **Enrollment** | <500ms | InsightFace + GPU |
| **Recognition** | <100ms | pgvector similarity |
| **Search (1000 faces)** | <100ms | Indexed vector search |
| **Batch processing** | 10 faces/sec | Batch inference |
| **GPU memory** | <2GB | Buffalo_L model |

---

## Configuration

### Environment Variables:
```env
# Service
NURA_FACE_PORT=8002
NURA_FACE_HOST=0.0.0.0

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=nura_db
POSTGRES_USER=nura
POSTGRES_PASSWORD=SecurePassword

# Face Recognition
FACE_RECOGNITION_MODEL=buffalo_l
FACE_RECOGNITION_THRESHOLD=0.6
FACE_EMBEDDING_DIM=512
FACE_DETECTION_SIZE=640

# GPU
ENABLE_GPU=true
GPU_DEVICE_ID=0

# Storage
FACE_PHOTOS_PATH=/data/face-photos
```

---

## Migration from nura-vlm

### Current Face Code in nura-vlm:
```
services/nura-vlm/src/
├── guardian_api.py    # Has face enrollment
├── visitor_api.py     # Has face enrollment
├── person_search_api.py # Has face search
└── (Face recognition scattered)
```

### Migration Steps:

1. **Create nura-face service**
2. **Move face logic** from VLM APIs to nura-face
3. **Update APIs** to call nura-face instead
4. **Migrate embeddings** from enrolled_persons to face_embeddings table
5. **Test end-to-end**

### Updated Flow:

**Before** (current):
```python
# In guardian_api.py
face_app = FaceAnalysis(...)  # Local face recognition
face_app.get(image)           # Direct face processing
```

**After** (with nura-face):
```python
# In guardian_api.py
response = requests.post(
    f"{NURA_FACE_URL}/api/face/enroll",
    json={"person_id": person_id, "photo_base64": photo}
)
```

---

## Advantages Summary

### 1. **Separation of Concerns**
- VLM service → Scene understanding only
- Face service → Face operations only
- Stream processor → Orchestration only

### 2. **Performance**
- Dedicated GPU for face tasks
- Independent scaling
- Batch processing optimization

### 3. **Maintainability**
- Single place for face logic
- Easy to update models
- Consistent API across all consumers

### 4. **Future-Ready**
- Custom model training
- A/B testing of models
- Age/emotion detection
- Advanced face analytics

---

## Implementation Timeline

### Week 6: Core Service (3-4 days)
- Day 1: Create service structure + basic API
- Day 2: Face enrollment + recognition
- Day 3: Unknown person handling
- Day 4: Integration testing

### Week 7: Migration (2-3 days)
- Day 1: Update guardian/visitor APIs
- Day 2: Update stream processor
- Day 3: Migrate existing embeddings
- Day 4: End-to-end testing

### Week 8: Enhancements (Optional)
- Model management API
- Batch processing
- Custom model training pipeline
- Performance optimization

---

## Decision

**Recommendation**: ✅ **YES - Create dedicated nura-face service**

**Why**:
1. Better architecture (separation of concerns)
2. Easier to scale and optimize
3. Future-ready for custom models
4. Consistent API for all face operations
5. Industry standard approach (microservices)

**Next Steps**:
1. Approve specification
2. Create service skeleton
3. Implement core APIs
4. Migrate from nura-vlm
5. Test and deploy
