# Phase 4B: Quick Start Guide

**Date:** 2026-11-06  
**Goal:** Get person identification system running

---

## Prerequisites

- ✅ PostgreSQL 16+ installed
- ✅ Python 3.10+ installed
- ✅ Phase 4 (Person Tracking) complete

---

## Step 1: Install Dependencies

```bash
cd packages/nura-detectors

# Install face recognition backend (choose one)

# Option A: InsightFace (RECOMMENDED - best accuracy)
pip install insightface onnxruntime

# Option B: face_recognition (easier, slower)
pip install face-recognition

# Database & vector search
pip install psycopg2-binary pgvector

# API server
cd ../../services/nura-vlm
pip install fastapi uvicorn python-multipart
```

---

## Step 2: Setup Database

```bash
# Connect to PostgreSQL
psql -U nura -d nura_db

# Run migration
\i services/nura-vlm/migrations/001_person_enrollment.sql

# Verify tables created
\dt

# Expected output:
#  enrolled_persons
#  person_sightings
#  person_actions
#  camera_topology
#  camera_handoffs

# Check pgvector extension
SELECT * FROM pg_extension WHERE extname = 'vector';
```

---

## Step 3: Start Enrollment API

```bash
cd services/nura-vlm

# Set environment variables
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=nura_db
export POSTGRES_USER=nura
export POSTGRES_PASSWORD='Pa$$w0rd!'
export FACE_RECOGNITION_BACKEND=insightface  # or face_recognition
export ENROLLMENT_API_PORT=8002

# Start API server
python3 src/enrollment_api.py

# Expected output:
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8002
```

---

## Step 4: Open Enrollment UI

```bash
# Open in browser
open http://localhost:8002/static/enrollment.html

# Or manually navigate to:
# http://localhost:8002/static/enrollment.html
```

---

## Step 5: Enroll Your First Person

### Using the UI:

1. **Fill in person details:**
   - Person ID: `adam_w`
   - Full Name: `Adam Williams`
   - Display Name: `Adam W.`
   - Age: `5`
   - Grade: `Kindergarten`
   - Classroom: `Room 3A`

2. **Upload 2-5 face photos:**
   - Different angles (frontal, left, right)
   - Good lighting
   - Clear, unobstructed face

3. **Check consent checkbox**

4. **Click "Enroll Person"**

### Using curl (API):

```bash
curl -X POST http://localhost:8002/api/persons/enroll \
  -F "person_id=adam_w" \
  -F "full_name=Adam Williams" \
  -F "display_name=Adam W." \
  -F "age_years=5" \
  -F "grade_level=Kindergarten" \
  -F "classroom=Room 3A" \
  -F "parental_consent=true" \
  -F "photos=@photo1.jpg" \
  -F "photos=@photo2.jpg" \
  -F "photos=@photo3.jpg"
```

---

## Step 6: Verify Enrollment

```bash
# List all enrolled persons
curl http://localhost:8002/api/persons

# Get specific person
curl http://localhost:8002/api/persons/adam_w

# Expected response:
# {
#   "person_id": "adam_w",
#   "full_name": "Adam Williams",
#   "display_name": "Adam W.",
#   "age_years": 5,
#   "grade_level": "Kindergarten",
#   "classroom": "Room 3A",
#   "parental_consent": true,
#   "active": true,
#   "enrolled_at": "2026-11-06T10:30:00"
# }
```

---

## Step 7: Test Face Identification

```python
# Create a test script
cat > test_identification.py << 'EOF'
from nura_detectors import FaceIdentifier
import cv2
import psycopg2

# Connect to database
db = psycopg2.connect(
    host="localhost",
    database="nura_db",
    user="nura",
    password="Pa$$w0rd!"
)

# Initialize identifier
identifier = FaceIdentifier(
    db_connection=db,
    backend="insightface",  # or "face_recognition"
    min_confidence=0.6
)

print(f"Enrolled persons: {identifier.get_enrollment_count()}")

# Load test image
test_img = cv2.imread("test_photo.jpg")

if test_img is not None:
    h, w = test_img.shape[:2]
    
    # Identify person (full image as person ROI)
    identity = identifier.identify(test_img, [0, 0, w, h])
    
    if identity:
        print(f"✓ Identified: {identity.display_name}")
        print(f"  Confidence: {identity.confidence:.2%}")
        print(f"  Method: {identity.method}")
    else:
        print("✗ No match found")
else:
    print("✗ Could not load test image")

db.close()
EOF

python3 test_identification.py
```

---

## Common Issues & Solutions

### Issue 1: pgvector extension not found
```sql
-- Install pgvector extension first
CREATE EXTENSION IF NOT EXISTS vector;
```

### Issue 2: InsightFace model download fails
```bash
# InsightFace downloads models on first use
# Ensure internet connection
# Models are cached in ~/.insightface/

# Alternatively, use face_recognition:
export FACE_RECOGNITION_BACKEND=face_recognition
```

### Issue 3: Face not detected in photos
- Ensure good lighting
- Face should be clearly visible (not obscured)
- Minimum face size: 40x40 pixels
- Try different angles

### Issue 4: Low identification confidence
- Enroll with more photos (3-5 recommended)
- Use high-quality photos
- Ensure consistent lighting between enrollment and identification
- Lower threshold: `min_confidence=0.5` (from 0.6)

### Issue 5: Database connection refused
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection details
psql -U nura -d nura_db -c "SELECT 1"
```

---

## API Endpoints Reference

### Enrollment
```bash
POST /api/persons/enroll
  - person_id (required)
  - full_name (required)
  - display_name (optional)
  - age_years (optional)
  - grade_level (optional)
  - classroom (optional)
  - parental_consent (default: false)
  - photos (2-5 files, required)
```

### List Persons
```bash
GET /api/persons?active_only=true&classroom=Room%203A
```

### Get Person
```bash
GET /api/persons/{person_id}
```

### Get Location
```bash
GET /api/persons/{person_id}/location
```

### Get Timeline
```bash
GET /api/persons/{person_id}/timeline?hours=24
```

### Update Person
```bash
PUT /api/persons/{person_id}
  - full_name
  - display_name
  - age_years
  - grade_level
  - classroom
```

### Update Consent
```bash
POST /api/persons/{person_id}/consent
{
  "parental_consent": true,
  "consent_document_url": "https://..."
}
```

### Delete Person
```bash
# Soft delete (deactivate)
DELETE /api/persons/{person_id}

# Permanent delete (GDPR right to be forgotten)
DELETE /api/persons/{person_id}?permanent=true
```

---

## Next Steps

### Integration with Hybrid Router

Update `hybrid_router.py`:

```python
# Add to __init__
self.face_identifier = None

# In _init_detectors()
if self.enable_person_tracking:
    from nura_detectors import FaceIdentifier
    
    self.face_identifier = FaceIdentifier(
        db_connection=self.get_db_connection(),
        backend=os.getenv("FACE_RECOGNITION_BACKEND", "insightface")
    )

# In analyze_frame()
if self.face_identifier and person_tracks:
    for track in person_tracks:
        identity = self.face_identifier.identify(frame, track['bbox'])
        
        if identity:
            track['identity'] = identity.person_id
            track['display_name'] = identity.display_name
            track['identity_confidence'] = identity.confidence
```

### Testing with Real Videos

```bash
# Test person tracking + identification
python3 tools/testing/test_person_tracking.py \
  --video classroom_video.mp4 \
  --enable-identification
```

---

## Configuration

Add to `.env`:

```bash
# Face Recognition
FACE_RECOGNITION_BACKEND=insightface  # or face_recognition
FACE_RECOGNITION_MIN_CONFIDENCE=0.6

# Enrollment API
ENROLLMENT_API_PORT=8002
UPLOAD_DIR=/tmp/nura_uploads

# Database (if different from main config)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=nura_db
POSTGRES_USER=nura
POSTGRES_PASSWORD=Pa$$w0rd!
```

---

## Performance Benchmarks

Expected performance (per person, per frame):

| Backend | Face Detection | Face Encoding | Total | Accuracy |
|---------|---------------|---------------|-------|----------|
| **InsightFace** | ~15ms | ~15ms | ~30ms | 95%+ |
| **face_recognition** | ~30ms | ~20ms | ~50ms | 85-90% |

With caching enabled: ~10-20ms per identification

---

## Security Checklist

- [ ] PostgreSQL password changed from default
- [ ] Encryption at rest enabled (database)
- [ ] HTTPS enabled (API)
- [ ] CORS restricted to trusted origins
- [ ] File upload size limits configured
- [ ] Rate limiting enabled (API endpoints)
- [ ] Audit logging configured
- [ ] Parental consent required
- [ ] Data retention policy defined

---

## Support

**Documentation:**
- Full spec: `specs/041-phase4b-person-identification/spec.md`
- Progress: `docs/phases/PHASE4B_PROGRESS.md`

**Troubleshooting:**
- Check logs: API server console output
- Database logs: `/var/log/postgresql/`
- Test API health: `curl http://localhost:8002/health`

**Common Commands:**
```bash
# Check enrolled persons
psql -U nura -d nura_db -c "SELECT person_id, full_name, active FROM enrolled_persons"

# Check sightings
psql -U nura -d nura_db -c "SELECT global_id, camera_id, timestamp FROM person_sightings ORDER BY timestamp DESC LIMIT 10"

# Clear test data
psql -U nura -d nura_db -c "DELETE FROM enrolled_persons WHERE person_id LIKE 'test_%'"
```

---

## Success Indicators

✅ Database tables created  
✅ API server running on port 8002  
✅ Enrollment UI accessible  
✅ Successfully enrolled at least 1 person  
✅ Face identification working (>60% confidence)  
✅ Location queries returning data

**You're ready to proceed with integration!** 🎉
