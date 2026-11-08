# Week 5 Implementation Plan: Behavioral Analytics

**Spec**: `specs/054-week5-behavioral-analytics/spec.md`  
**Duration**: 1 week (8 days)  
**Status**: 📋 Planning

---

## Overview

Build a behavioral analytics system that automatically tracks unknown persons, classifies activities, and generates daily behavior reports for each person.

**Key Features:**
1. Unknown person auto-creation with persistent IDs
2. Activity classification (11 classes: playing, eating, crying, etc.)
3. Daily behavior reports (time distribution, activities, interactions)
4. Manual linking of unknown persons to real identities

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│          Stream Processor Enhancement                │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Person Detection:                                   │
│    ↓                                                 │
│  Face Recognition:                                   │
│    ├─ Identified → Update location cache            │
│    └─ Unknown → AUTO-CREATE "Unknown Person N"      │
│                  ├─ Generate persistent ID           │
│                  ├─ Store face embedding             │
│                  └─ Track across cameras             │
│                                                      │
│  Activity Classification:                            │
│    ↓                                                 │
│  MobileNetV3 (11 classes):                           │
│    - playing, eating, crying, sitting                │
│    - running, standing, reading, sleeping            │
│    - interacting, alone, other                       │
│                                                      │
│  Store Detection Event:                              │
│    person_id, activity, timestamp, camera, bbox      │
│                                                      │
└──────────────────────────────────────────────────────┘
         ↓                                  ↓
┌──────────────────────────────────────────────────────┐
│         Analytics Service (NEW)                      │
│         nura-analytics                               │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Consumes: person_detections events                  │
│                                                      │
│  Daily Aggregation:                                  │
│    - Time per zone                                   │
│    - Activity breakdown                              │
│    - Social interactions                             │
│    - Movement patterns                               │
│    - Anomaly detection                               │
│                                                      │
│  Generates: Daily Behavior Reports                   │
│    - JSON format                                     │
│    - Stored in behavior_reports table                │
│    - Accessible via API                              │
│                                                      │
└──────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────┐
│         Admin API (Manual Linking)                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  GET /admin/unknown-persons                          │
│    - List all unlinked unknowns                      │
│    - Show face photo + detection history             │
│                                                      │
│  POST /api/persons/unknown/{id}/link                 │
│    - Link to existing person                         │
│    - Or create new enrollment                        │
│    - Merge all detections                            │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## Implementation Tasks

### Task 1: Unknown Person Auto-Creation (2 days) ✅ FIRST

**Why First**: Foundation for all other analytics

**Database Migration:**
Create `unknown_persons` table and update `person_detections`.

**Files:**
- `edge/postgres/migrations/010_unknown_persons_behavioral.sql` (NEW)

**Schema:**
```sql
-- Unknown persons table
CREATE TABLE IF NOT EXISTS unknown_persons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unknown_id VARCHAR(50) UNIQUE NOT NULL,  -- 'unknown_001', 'unknown_002', etc.
    face_embedding VECTOR(512) NOT NULL,
    first_seen TIMESTAMP NOT NULL DEFAULT NOW(),
    last_seen TIMESTAMP NOT NULL DEFAULT NOW(),
    detection_count INTEGER DEFAULT 1,
    sample_photo_url TEXT,
    linked_to_person_id VARCHAR(50),  -- NULL until manually linked
    linked_at TIMESTAMP,
    linked_by VARCHAR(100),
    notes TEXT,
    active BOOLEAN DEFAULT TRUE
);

-- person_detections table (if not exists)
CREATE TABLE IF NOT EXISTS person_detections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id VARCHAR(50) NOT NULL,  -- Can be 'unknown_001'
    camera_id VARCHAR(50) NOT NULL,
    detected_at TIMESTAMP NOT NULL DEFAULT NOW(),
    confidence FLOAT NOT NULL,
    bbox JSONB,  -- {x1, y1, x2, y2}
    activity VARCHAR(50),  -- 'playing', 'eating', etc.
    activity_confidence FLOAT,
    frame_url TEXT
);

-- activity_events table (aggregated activities)
CREATE TABLE IF NOT EXISTS activity_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id VARCHAR(50) NOT NULL,
    camera_id VARCHAR(50) NOT NULL,
    activity VARCHAR(50) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    duration_seconds INTEGER,
    confidence FLOAT
);

-- behavior_reports table (daily summaries)
CREATE TABLE IF NOT EXISTS behavior_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id VARCHAR(50) NOT NULL,
    report_date DATE NOT NULL,
    report_data JSONB NOT NULL,  -- Full JSON report
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(person_id, report_date)
);

-- Indexes
CREATE INDEX idx_unknown_persons_face ON unknown_persons 
    USING ivfflat (face_embedding vector_cosine_ops) WITH (lists = 50);
CREATE INDEX idx_person_detections_person_time ON person_detections (person_id, detected_at DESC);
CREATE INDEX idx_person_detections_activity ON person_detections (activity, detected_at DESC);
CREATE INDEX idx_activity_events_person_time ON activity_events (person_id, started_at DESC);
CREATE INDEX idx_behavior_reports_person_date ON behavior_reports (person_id, report_date DESC);
```

**Unknown Person Handler (Stream Processor):**

Update stream processor to auto-create unknowns.

**Files:**
- `services/nura-stream-processor/src/unknown-person.service.ts` (NEW)
- `services/nura-stream-processor/src/stream-processor.service.ts` (UPDATE)

**Logic:**
```typescript
// unknown-person.service.ts
export class UnknownPersonService {
  async findOrCreateUnknown(faceEmbedding: number[]): Promise<string> {
    // 1. Search existing unknowns by face similarity
    const match = await this.findSimilarUnknown(faceEmbedding);
    
    if (match && match.similarity > 0.7) {
      // Same unknown person
      await this.updateLastSeen(match.unknown_id);
      return match.unknown_id;
    }
    
    // 2. New unknown - create entry
    const unknownId = await this.createNewUnknown(faceEmbedding);
    return unknownId;
  }
  
  private async createNewUnknown(faceEmbedding: number[]): Promise<string> {
    // Get next ID
    const count = await this.db.query(
      'SELECT COUNT(*) FROM unknown_persons'
    );
    const nextNum = count.rows[0].count + 1;
    const unknownId = `unknown_${String(nextNum).padStart(3, '0')}`;
    
    // Insert
    await this.db.query(`
      INSERT INTO unknown_persons (unknown_id, face_embedding)
      VALUES ($1, $2)
    `, [unknownId, faceEmbedding]);
    
    logger.info(`Created new unknown person: ${unknownId}`);
    return unknownId;
  }
}
```

---

### Task 2: Activity Classifier (3 days)

**Option A: Use Existing Model** (Recommended - 1 day)
Use pre-trained action recognition model.

**Option B: Train Custom Model** (3 days)
Train MobileNetV3 on ToddlerActions dataset.

**We'll use Option A for speed.**

**Activity Classes (11):**
1. playing
2. eating
3. crying
4. sitting
5. running
6. standing
7. reading
8. sleeping
9. interacting
10. alone
11. other

**Implementation:**

**Files:**
- `packages/nura-detectors/src/nura_detectors/activity_classifier.py` (NEW)

```python
# activity_classifier.py
import cv2
import numpy as np
from typing import Tuple, Dict
import onnxruntime as ort

class ActivityClassifier:
    """
    Classifies person activities from video frames
    Uses MobileNetV3 or similar lightweight model
    """
    
    ACTIVITIES = [
        'playing', 'eating', 'crying', 'sitting', 'running',
        'standing', 'reading', 'sleeping', 'interacting', 'alone', 'other'
    ]
    
    def __init__(self, model_path: str = None):
        if model_path is None:
            # Use default pre-trained model
            model_path = '/app/models/activity_classifier.onnx'
        
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        
    def classify(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> Dict[str, float]:
        """
        Classify activity for person in bounding box
        
        Args:
            frame: Full frame image
            bbox: (x1, y1, x2, y2) bounding box
            
        Returns:
            {
                'activity': 'playing',
                'confidence': 0.87,
                'probabilities': {'playing': 0.87, 'running': 0.05, ...}
            }
        """
        # Crop person from frame
        x1, y1, x2, y2 = bbox
        person_crop = frame[y1:y2, x1:x2]
        
        # Preprocess
        input_tensor = self.preprocess(person_crop)
        
        # Inference
        outputs = self.session.run(None, {self.input_name: input_tensor})
        probabilities = outputs[0][0]  # [11,]
        
        # Get top prediction
        top_idx = np.argmax(probabilities)
        activity = self.ACTIVITIES[top_idx]
        confidence = float(probabilities[top_idx])
        
        # Build probabilities dict
        probs_dict = {
            act: float(prob) 
            for act, prob in zip(self.ACTIVITIES, probabilities)
        }
        
        return {
            'activity': activity,
            'confidence': confidence,
            'probabilities': probs_dict
        }
    
    def preprocess(self, crop: np.ndarray) -> np.ndarray:
        """Preprocess crop for model input"""
        # Resize to 224x224
        resized = cv2.resize(crop, (224, 224))
        
        # Normalize
        normalized = resized.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        normalized = (normalized - mean) / std
        
        # NCHW format
        tensor = np.transpose(normalized, (2, 0, 1))
        tensor = np.expand_dims(tensor, axis=0)
        
        return tensor
```

**For now, use a simple rule-based classifier:**

```python
class SimpleActivityClassifier:
    """
    Simple rule-based activity classifier
    Uses motion and pose to estimate activity
    """
    
    def classify(self, frame, bbox, prev_bbox=None):
        """
        Simple heuristic-based classification
        """
        # Calculate movement
        if prev_bbox:
            movement = self.calculate_movement(bbox, prev_bbox)
            
            if movement > 50:
                return {'activity': 'running', 'confidence': 0.7}
            elif movement > 10:
                return {'activity': 'playing', 'confidence': 0.6}
            else:
                return {'activity': 'sitting', 'confidence': 0.5}
        
        # Default
        return {'activity': 'other', 'confidence': 0.3}
```

---

### Task 3: Analytics Service (2 days)

**New Service: nura-analytics**

**Purpose:**
- Consume person_detections events
- Aggregate daily statistics
- Generate behavior reports

**Files:**
- `services/nura-analytics/` (NEW SERVICE)
- `services/nura-analytics/src/analytics.service.ts`
- `services/nura-analytics/src/report-generator.service.ts`
- `services/nura-analytics/Dockerfile`
- `services/nura-analytics/package.json`

**Analytics Service:**
```typescript
// analytics.service.ts
@Injectable()
export class AnalyticsService {
  async generateDailyReport(personId: string, date: Date): Promise<BehaviorReport> {
    const startOfDay = new Date(date);
    startOfDay.setHours(0, 0, 0, 0);
    
    const endOfDay = new Date(date);
    endOfDay.setHours(23, 59, 59, 999);
    
    // Get all detections for this person on this day
    const detections = await this.getDetections(personId, startOfDay, endOfDay);
    
    // Analyze
    const report = {
      person_id: personId,
      report_date: date,
      summary: {
        total_detections: detections.length,
        first_seen: detections[0]?.detected_at,
        last_seen: detections[detections.length - 1]?.detected_at,
        time_on_campus_minutes: this.calculateTimeOnCampus(detections)
      },
      zones: this.analyzeZones(detections),
      activities: this.analyzeActivities(detections),
      social: this.analyzeSocialInteractions(detections),
      anomalies: this.detectAnomalies(detections)
    };
    
    // Store report
    await this.storeReport(personId, date, report);
    
    return report;
  }
}
```

**Report API:**

**Files:**
- `services/nura-vlm/src/analytics_api.py` (NEW)

```python
# analytics_api.py
@router.get("/api/analytics/reports/daily")
async def get_daily_report(
    person_id: str,
    date: str = Query(..., description="Date in YYYY-MM-DD format")
):
    """
    Get daily behavior report for a person
    
    Returns:
    - Time distribution by zone
    - Activity breakdown
    - Social interactions
    - Anomalies detected
    """
    report_date = datetime.strptime(date, '%Y-%m-%d').date()
    
    # Check if report exists
    report = await get_report_from_db(person_id, report_date)
    
    if not report:
        # Generate on-demand
        report = await generate_report(person_id, report_date)
    
    return report
```

---

### Task 4: Manual Linking UI/API (1 day)

**Admin API for linking unknowns**

**Files:**
- `services/nura-vlm/src/admin_api.py` (NEW or UPDATE)

```python
# admin_api.py
@router.get("/admin/unknown-persons")
async def list_unknown_persons(
    limit: int = 50,
    unlinked_only: bool = True
):
    """
    List unknown persons for manual linking
    """
    query = """
        SELECT 
            id, unknown_id, first_seen, last_seen, 
            detection_count, sample_photo_url,
            linked_to_person_id
        FROM unknown_persons
        WHERE active = true
    """
    
    if unlinked_only:
        query += " AND linked_to_person_id IS NULL"
    
    query += " ORDER BY last_seen DESC LIMIT %s"
    
    # Execute and return
    

@router.post("/api/persons/unknown/{unknown_id}/link")
async def link_unknown_person(
    unknown_id: str,
    link_to_person_id: str = None,
    create_new: bool = False,
    full_name: str = None
):
    """
    Link unknown person to existing or new enrollment
    
    Options:
    1. Link to existing: link_to_person_id="adam_w"
    2. Create new: create_new=true, full_name="John Doe"
    """
    if create_new:
        # Create new enrollment
        person_id = await create_enrollment(full_name, unknown_id)
    else:
        person_id = link_to_person_id
    
    # Update unknown_persons
    await db.execute("""
        UPDATE unknown_persons
        SET linked_to_person_id = %s,
            linked_at = NOW(),
            active = false
        WHERE unknown_id = %s
    """, (person_id, unknown_id))
    
    # Update all person_detections
    await db.execute("""
        UPDATE person_detections
        SET person_id = %s
        WHERE person_id = %s
    """, (person_id, unknown_id))
    
    return {"success": True, "linked_to": person_id}
```

---

## Testing Plan

### Test 1: Unknown Auto-Creation
```bash
# Simulate unknown detection
# (This will be automatic when stream processor sees unknown face)

# Check database
docker exec $(docker ps -q -f name=postgres) psql -U nura -d nura_db \
  -c "SELECT * FROM unknown_persons ORDER BY first_seen DESC LIMIT 5;"

# Expected: unknown_001, unknown_002, etc.
```

### Test 2: Activity Classification
```bash
# Add activity to detection
# (Automatic in stream processor)

# Check person_detections
docker exec $(docker ps -q -f name=postgres) psql -U nura -d nura_db \
  -c "SELECT person_id, activity, activity_confidence FROM person_detections ORDER BY detected_at DESC LIMIT 10;"
```

### Test 3: Daily Report
```bash
curl "http://localhost:8001/api/analytics/reports/daily?person_id=adam_w&date=2026-11-08" | jq
```

### Test 4: Manual Linking
```bash
# List unknowns
curl "http://localhost:8001/admin/unknown-persons" | jq

# Link unknown to person
curl -X POST "http://localhost:8001/api/persons/unknown/unknown_001/link" \
  -H "Content-Type: application/json" \
  -d '{"link_to_person_id":"adam_w"}'
```

---

## Timeline

| Day | Task | Deliverable |
|-----|------|-------------|
| 1-2 | Unknown person auto-creation | DB + handler working |
| 3-5 | Activity classifier | Simple classifier deployed |
| 6-7 | Analytics service | Daily reports generated |
| 8 | Manual linking API | Admin endpoints working |

---

## Success Metrics

- [ ] Unknown persons auto-created with persistent IDs
- [ ] Same unknown tracked across cameras
- [ ] Activities classified (rule-based for now)
- [ ] Daily behavior reports generated
- [ ] Manual linking functional

---

**Week 5 Ready to Start!**  
**Next Step**: Create unknown_persons database migration
