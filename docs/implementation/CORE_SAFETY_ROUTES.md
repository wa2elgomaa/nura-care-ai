# 🎯 NURA AI - Core Safety Routes (Priority)

**Date:** November 8, 2026  
**Mission:** Safety-first monitoring system  
**Philosophy:** Attendance/billing comes AFTER safety is proven

---

## 🔥 Four Core Safety Routes

These are the **PRIMARY FOCUS** - everything else waits until these work perfectly.

---

## Route 1: Incident Detection & Alert 🚨

**Priority:** P0 - CRITICAL

### Flow
```
School Camera + WiFi Sensing
    ↓
Feed into System (Frigate + MQTT)
    ↓
AI Analysis (Fast-path + VLM validation)
    ↓ Detect:
    • Violence (hitting, pushing, fighting)
    • Distress (crying, injury, fear)
    • Unsupervised (no adult present)
    • Abuse (inappropriate contact)
    • Safety hazards (knife, stairs, dangerous areas)
    ↓
Alert with Context
    • Person name (if identified)
    • Person image (from enrollment or detection)
    • Confidence score
    • Video evidence (local clip)
    • Timestamp & location (camera/zone)
```

### Current Status

**✅ Working:**
- Camera ingestion (Frigate → MQTT)
- AI detection pipeline (4 fast-path detectors)
- VLM validation (qwen3-vl)
- Alert service (email working, SMS disabled)
- Person tracking (YOLOv8 + ByteTrack)
- Face identification (InsightFace)

**⚠️ Gaps:**
- WiFi sensing integration (RuView not connected)
- Abuse detection (needs training data)
- Safety hazard detector (knife/stairs - dataset ready, not trained)
- Person name in alerts (enrollment data exists but not in alert payload)
- Video evidence clips (Frigate has clips, not attached to alerts)

### Implementation Needed

#### 1. WiFi Sensing Integration (1 week)
```bash
# Add RuView service integration
services/nura-wifi-sensing/
  - Consume RuView MQTT events
  - Detect occupancy anomalies
  - Publish to NATS
  - Integrate with alert service

# Events to detect:
- Adult + child in bathroom >2 minutes
- After-hours movement
- Restricted area occupancy
```

**Files:**
- `services/nura-wifi-sensing/` (new service)
- `edge/ruview/` (configuration)
- `compose.yaml` (add ruview profile)

#### 2. Enhanced Alert Payload (3 days)
```bash
# Include person identity in alerts
{
  "alert_id": "...",
  "type": "distress",
  "confidence": 0.84,
  "timestamp": "...",
  "camera_id": "classroom_1",
  "zone": "play_area",
  
  # NEW: Person context
  "persons_involved": [
    {
      "person_id": "uuid",
      "name": "Jane Doe",           # From enrollment DB
      "role": "child",               # child, staff, unknown
      "image_url": "/api/persons/uuid/photo",
      "confidence": 0.95,            # Face recognition confidence
      "bbox": [x, y, w, h]           # Bounding box in frame
    }
  ],
  
  # NEW: Evidence
  "evidence": {
    "snapshot_url": "/api/alerts/uuid/snapshot.jpg",
    "clip_url": "/api/alerts/uuid/clip.mp4",  # 10s clip
    "duration_seconds": 10
  }
}
```

**Files:**
- `services/nura-alerts/src/models/alert.model.ts`
- `services/nura-stream-processor/src/services/frame-processor.ts`
- `services/nura-vlm/src/main.py` (include person IDs in response)

#### 3. Safety Hazard Detector (1 week)
```bash
# Train knife/staircase detector
cd training/
python train_safety_detector.py \
  --dataset datasets/ToddlerActions \
  --classes "knife,staircase" \
  --model yolov8s \
  --epochs 50

# Integrate into VLM service
services/nura-vlm/src/detectors/safety_detector.py
```

**Files:**
- `training/train_safety_detector.py`
- `services/nura-vlm/src/detectors/safety_detector.py`
- `models/safety_hazard_detector.keras`

#### 4. Video Evidence Clips (3 days)
```bash
# Extract and attach clips to alerts
- Query Frigate for clip (10s before/after event)
- Store clip reference in alert
- Serve via API endpoint
- Include in email/push notification
```

**Files:**
- `services/nura-alerts/src/services/evidence.service.ts`
- `services/nura-alerts/src/storage/` (clip storage)

---

## Route 2: Stranger Detection & Alert 👤

**Priority:** P0 - CRITICAL

### Flow
```
School Camera
    ↓
Feed into System
    ↓
Face Detection + Recognition
    ↓
Check against Enrollment DB
    ↓
If UNKNOWN face detected
    ↓
Alert: Stranger detected
    • Photo of stranger
    • Location (camera/zone)
    • Timestamp
    • Suggested action ("Check visitor log")
```

### Current Status

**✅ Working:**
- Face detection (InsightFace)
- Face recognition (95%+ accuracy)
- Enrollment database (PostgreSQL)
- Alert routing

**⚠️ Gaps:**
- Stranger detection logic (need to flag unknown faces)
- Stranger alert type (dedicated alert category)
- Visitor whitelist (temporary enrollment for visitors)
- Confidence threshold tuning (avoid false positives with poor angles)

### Implementation Needed

#### 1. Stranger Detection Logic (2 days)
```python
# In VLM service hybrid router
def check_for_strangers(self, frame, person_tracks):
    strangers = []
    
    for track in person_tracks:
        # Try to identify
        person_id, confidence = self.face_identifier.identify(track.face_roi)
        
        if person_id is None:
            # Unknown person
            strangers.append({
                "track_id": track.id,
                "bbox": track.bbox,
                "face_image": encode_base64(track.face_roi),
                "first_seen": track.timestamp,
                "last_seen": track.timestamp
            })
        elif confidence < 0.6:
            # Low confidence - might be stranger
            strangers.append({
                "track_id": track.id,
                "possible_match": person_id,
                "confidence": confidence,
                "face_image": encode_base64(track.face_roi),
                "status": "uncertain"
            })
    
    return strangers
```

**Files:**
- `services/nura-vlm/src/hybrid_router.py`
- `services/nura-vlm/src/detectors/stranger_detector.py` (new)

#### 2. Stranger Alert Type (1 day)
```typescript
// Add stranger alert type
enum AlertType {
  VIOLENCE = 'violence',
  DISTRESS = 'distress',
  SUPERVISION = 'supervision',
  STRANGER = 'stranger',        // NEW
  SAFETY_HAZARD = 'safety_hazard'
}

// Stranger alert payload
{
  "type": "stranger",
  "severity": "medium",
  "stranger": {
    "first_seen": "...",
    "last_seen": "...",
    "camera_id": "entrance",
    "zone": "lobby",
    "image_url": "/api/alerts/uuid/stranger.jpg",
    "possible_matches": [        // If low confidence
      {
        "person_id": "...",
        "name": "John Smith",
        "confidence": 0.55
      }
    ]
  },
  "suggested_action": "Check visitor log and verify identity"
}
```

**Files:**
- `services/nura-alerts/src/models/alert.model.ts`
- `services/nura-stream-processor/src/services/stranger-handler.ts`

#### 3. Visitor Management (3 days)
```bash
# Temporary enrollment for visitors
POST /api/visitors/enroll
{
  "name": "Parent - Jane Smith",
  "photo": "base64...",
  "valid_from": "2026-11-08T09:00:00Z",
  "valid_until": "2026-11-08T10:00:00Z",
  "purpose": "Parent-teacher meeting",
  "approved_by": "staff_member_id"
}

# Auto-expire after valid_until
# Don't trigger stranger alert during valid period
```

**Files:**
- `services/nura-vlm/src/enrollment_api.py` (add visitor endpoints)
- `edge/postgres/migrations/003_visitors.sql`

---

## Route 3: Person Search & Locate 🔍

**Priority:** P1 - IMPORTANT

### Flow
```
User Input: Search by name OR image
    ↓
Search Service
    ↓
Query enrollment DB + recent detections
    ↓
Find person across cameras (last 24 hours)
    ↓
Respond with:
    • Current location (camera/zone)
    • Last seen timestamp
    • Recent movement history
    • Photo from latest detection
```

### Current Status

**✅ Working:**
- Enrollment database
- Face recognition
- Person tracking (persistent IDs)
- Timeline tracking (person_detections table)

**⚠️ Gaps:**
- Search API endpoint (not implemented)
- Real-time location tracking (need current location cache)
- Movement history API (have data, no API)
- Search by image (face encoding search)

### Implementation Needed

#### 1. Search API (2 days)
```typescript
// Search by name
GET /api/persons/search?name=Jane%20Doe
Response:
{
  "person_id": "uuid",
  "name": "Jane Doe",
  "role": "child",
  "current_location": {
    "camera_id": "classroom_1",
    "zone": "play_area",
    "last_seen": "2026-11-08T14:23:15Z",
    "confidence": 0.92
  },
  "photo_url": "/api/persons/uuid/photo"
}

// Search by image (upload photo)
POST /api/persons/search/by-image
FormData: { photo: File }
Response: (same as above)
```

**Files:**
- `services/nura-vlm/src/enrollment_api.py` (add search endpoints)
- `services/nura-vlm/src/services/search.py` (new)

#### 2. Real-time Location Cache (1 day)
```python
# Redis cache for current locations
class PersonLocationCache:
    def __init__(self):
        self.redis = Redis()
        self.ttl = 300  # 5 minutes
    
    def update_location(self, person_id, camera_id, zone, timestamp):
        """Update person's current location"""
        key = f"location:{person_id}"
        self.redis.setex(key, self.ttl, json.dumps({
            "camera_id": camera_id,
            "zone": zone,
            "timestamp": timestamp.isoformat()
        }))
    
    def get_location(self, person_id):
        """Get person's current location"""
        key = f"location:{person_id}"
        data = self.redis.get(key)
        return json.loads(data) if data else None
```

**Files:**
- `services/nura-vlm/src/cache/location_cache.py` (new)
- `compose.yaml` (add Redis service)

#### 3. Movement History API (1 day)
```typescript
// Get person's movement history
GET /api/persons/{id}/movements?from=2026-11-08T08:00&to=2026-11-08T16:00
Response:
{
  "person_id": "uuid",
  "name": "Jane Doe",
  "movements": [
    {
      "camera_id": "entrance",
      "zone": "lobby",
      "entered_at": "2026-11-08T08:05:23Z",
      "exited_at": "2026-11-08T08:06:45Z",
      "duration_seconds": 82
    },
    {
      "camera_id": "classroom_1",
      "zone": "play_area",
      "entered_at": "2026-11-08T08:07:12Z",
      "exited_at": "2026-11-08T12:30:05Z",
      "duration_seconds": 15773
    }
  ]
}
```

**Files:**
- `services/nura-vlm/src/enrollment_api.py` (add movements endpoint)
- Query existing `person_detections` table

---

## Route 4: Behavioral Analysis & Reports 📊

**Priority:** P1 - IMPORTANT

### Flow
```
School Camera
    ↓
Feed into System
    ↓
Person Detection (track all persons)
    ↓
If person identified → Link to enrollment
If person unknown → Create "Person N" with photo
    ↓
Analyze behaviors over time:
    • Time in each zone
    • Interactions (who with)
    • Activity patterns (active, passive, isolated)
    • Emotional states (happy, distressed, neutral)
    ↓
Generate Reports:
    • Daily summary per person
    • Weekly behavior trends
    • Anomaly detection (unusual patterns)
    • Social interaction graph
```

### Current Status

**✅ Working:**
- Person detection & tracking
- Face identification
- Timeline tracking
- Unknown person storage (creates records)

**⚠️ Gaps:**
- Behavior analysis logic (not implemented)
- Activity classification (dataset ready, not trained)
- Emotional state tracking (basic distress only)
- Report generation (no reporting service)
- Social interaction tracking (not implemented)
- Unknown person management UI (auto-creates but no UI to link)

### Implementation Needed

#### 1. Unknown Person Auto-Creation (2 days)
```python
def handle_unknown_person(self, face_roi, timestamp, camera_id, bbox):
    """Auto-create record for unknown person"""
    
    # Generate face encoding
    encoding = self.face_identifier.get_encoding(face_roi)
    
    # Check if we've seen this unknown before
    unknown_id = self._match_unknown_encoding(encoding)
    
    if unknown_id is None:
        # New unknown person
        unknown_id = self._create_unknown_person(
            face_image=face_roi,
            encoding=encoding,
            first_seen=timestamp,
            first_camera=camera_id
        )
    
    # Track this sighting
    self._record_detection(
        person_id=unknown_id,
        timestamp=timestamp,
        camera_id=camera_id,
        bbox=bbox
    )
    
    return unknown_id

def _create_unknown_person(self, face_image, encoding, first_seen, first_camera):
    """Create 'Person N' record"""
    # Count existing unknowns
    count = db.query("SELECT COUNT(*) FROM persons WHERE name LIKE 'Unknown Person%'")
    name = f"Unknown Person {count + 1}"
    
    person_id = db.insert_person(
        name=name,
        role="unknown",
        face_encoding=encoding,
        photo=face_image,
        first_seen=first_seen,
        first_camera=first_camera,
        needs_manual_linking=True  # Flag for admin
    )
    
    return person_id
```

**Files:**
- `services/nura-vlm/src/services/unknown_person_handler.py` (new)
- `edge/postgres/migrations/004_unknown_persons.sql`

#### 2. Activity Classification (1 week)
```bash
# Train activity classifier
cd training/
python train_activity_classifier.py \
  --dataset datasets/ToddlerActions \
  --classes "playing,eating,drinking,sleeping,crying,smiling,yawning,running,walking,sitting,standing" \
  --model mobilenet_v3 \
  --epochs 50

# Integrate into VLM service
services/nura-vlm/src/detectors/activity_detector.py
```

**Files:**
- `training/train_activity_classifier.py`
- `services/nura-vlm/src/detectors/activity_detector.py`
- `models/activity_classifier.keras`

#### 3. Behavior Analysis Service (3 days)
```typescript
// New service for behavior analysis
services/nura-analytics/
  - Consume person_detections events
  - Aggregate by person/day
  - Detect patterns and anomalies
  - Generate daily/weekly reports

// Example report
{
  "person_id": "uuid",
  "name": "Jane Doe",
  "date": "2026-11-08",
  "summary": {
    "total_time_minutes": 480,
    "zones": {
      "play_area": 320,
      "classroom": 140,
      "outdoor": 20
    },
    "activities": {
      "playing": 280,
      "eating": 45,
      "sitting": 120,
      "running": 35
    },
    "emotional_states": {
      "happy": 420,
      "neutral": 55,
      "distressed": 5
    },
    "interactions": [
      {
        "with_person_id": "other_uuid",
        "with_name": "John Smith",
        "duration_minutes": 180,
        "interaction_type": "playing_together"
      }
    ],
    "anomalies": [
      {
        "type": "isolated",
        "description": "Spent 45 minutes alone (unusual)",
        "timestamp": "2026-11-08T10:30:00Z"
      }
    ]
  }
}
```

**Files:**
- `services/nura-analytics/` (new service)
- `edge/postgres/migrations/005_behavior_reports.sql`

#### 4. Manual Linking UI (2 days)
```typescript
// Admin UI: Unknown persons page
GET /admin/unknown-persons
Response:
{
  "unknown_persons": [
    {
      "person_id": "uuid",
      "name": "Unknown Person 1",
      "photo_url": "/api/persons/uuid/photo",
      "first_seen": "2026-11-08T08:30:00Z",
      "sightings_count": 12,
      "cameras": ["entrance", "classroom_1"],
      "suggested_matches": [  // Based on face similarity
        {
          "person_id": "uuid2",
          "name": "Jane Doe",
          "confidence": 0.55,
          "reason": "Low confidence match"
        }
      ]
    }
  ]
}

// Link unknown to known person
POST /api/persons/unknown/{unknown_id}/link
{
  "target_person_id": "uuid2",  // OR
  "new_person_data": {          // Create new enrollment
    "name": "New Person Name",
    "role": "child"
  }
}
```

**Files:**
- `services/nura-ui/src/pages/UnknownPersons.tsx` (new)
- `services/nura-vlm/src/enrollment_api.py` (add linking endpoints)

---

## 📊 Implementation Priority Matrix

### Phase 1: Core Detection (2 weeks)
**Goal:** All 4 routes have basic functionality

| Route | Task | Days | Priority |
|-------|------|------|----------|
| 1 | Enhanced alert payload (person names) | 3 | P0 |
| 1 | Safety hazard detector | 5 | P0 |
| 2 | Stranger detection logic | 2 | P0 |
| 2 | Stranger alert type | 1 | P0 |
| 3 | Search API (name search) | 2 | P1 |
| 4 | Unknown person auto-creation | 2 | P1 |

**Total:** 15 days (3 weeks with 1 engineer)

### Phase 2: Evidence & Context (1 week)
**Goal:** Rich context in alerts

| Route | Task | Days | Priority |
|-------|------|------|----------|
| 1 | Video evidence clips | 3 | P0 |
| 1 | WiFi sensing integration | 5 | P1 |
| 2 | Visitor management | 3 | P1 |

**Total:** 11 days (parallel work, 1 week with 2 engineers)

### Phase 3: Advanced Features (2 weeks)
**Goal:** Search, analytics, reporting

| Route | Task | Days | Priority |
|-------|------|------|----------|
| 3 | Real-time location cache | 1 | P1 |
| 3 | Movement history API | 1 | P1 |
| 3 | Search by image | 2 | P1 |
| 4 | Activity classification | 5 | P1 |
| 4 | Behavior analysis service | 3 | P1 |
| 4 | Manual linking UI | 2 | P1 |

**Total:** 14 days (2 weeks with 2 engineers)

---

## 🎯 Route-Specific Success Criteria

### Route 1: Incident Detection
- [ ] 90%+ detection accuracy across all incident types
- [ ] <10s from incident to alert
- [ ] Person name included in 80%+ of alerts
- [ ] Video evidence attached to 100% of alerts
- [ ] <10% false positive rate

### Route 2: Stranger Detection
- [ ] 95%+ stranger detection accuracy
- [ ] <5% false positive rate (don't flag enrolled persons)
- [ ] Visitor whitelist working (no alerts for approved visitors)
- [ ] Alert within 30s of stranger detection

### Route 3: Person Search
- [ ] Search by name finds person in <2s
- [ ] Search by image finds person in <5s
- [ ] Location accuracy 90%+ (person is where system says)
- [ ] Movement history accurate to camera transitions

### Route 4: Behavioral Reports
- [ ] Unknown persons auto-created 100% of time
- [ ] Activity classification 80%+ accuracy
- [ ] Daily reports generated for all persons
- [ ] Anomaly detection catches unusual patterns

---

## 🚀 Integration with Existing System

### What Already Works (Keep Using)

```bash
✅ Camera Ingestion
   Frigate → MQTT → Stream Processor

✅ AI Detection Pipeline
   Fast-path detectors (violence, distress, supervision, body language)
   VLM validation (qwen3-vl)

✅ Person Tracking
   YOLOv8n + ByteTrack (persistent IDs)

✅ Face Recognition
   InsightFace (95%+ accuracy)

✅ Alert Service
   Multi-channel routing (email, push, SMS)

✅ Database
   PostgreSQL with enrollment, detections, alerts
```

### What Needs Enhancement

```bash
⚠️ Alert Payload
   ADD: Person names, images, video evidence

⚠️ Detection Types
   ADD: Stranger, safety hazards

⚠️ Search Capability
   ADD: Search API, real-time location

⚠️ Analytics
   ADD: Behavior analysis, reporting

⚠️ Unknown Person Handling
   ADD: Auto-creation, manual linking UI
```

---

## 📋 Next Steps (This Week)

### Day 1-2: Enhanced Alerts
```bash
1. Update alert payload schema
   - Add persons_involved array
   - Add evidence object
   - Update TypeScript types

2. Modify VLM response
   - Include person IDs in detection
   - Include bounding boxes
   - Update hybrid_router.py

3. Test alert flow
   - Trigger test alert
   - Verify person name appears
   - Check email formatting
```

### Day 3-4: Stranger Detection
```bash
1. Add stranger detection logic
   - Create stranger_detector.py
   - Integrate with hybrid router
   - Add confidence thresholding

2. Add stranger alert type
   - Update alert model
   - Add alert routing
   - Test stranger alert

3. Test with unknown faces
   - Use test images
   - Verify alerts triggered
   - Check false positive rate
```

### Day 5: Safety Hazards
```bash
1. Start safety detector training
   - Prepare knife/staircase dataset
   - Configure training parameters
   - Start training (overnight)

2. Meanwhile: Documentation
   - Document new alert schema
   - Document stranger detection
   - Update API docs
```

---

## 💡 Key Design Decisions

### 1. Unknown Person Handling
**Decision:** Auto-create "Unknown Person N" immediately, allow manual linking later

**Rationale:**
- Don't lose tracking data while waiting for manual enrollment
- School can retroactively link unknown to real person
- Maintains timeline continuity

### 2. Stranger vs Unknown
**Decision:** "Stranger" = immediate alert, "Unknown" = just tracked

**Rationale:**
- Stranger detection is real-time security concern
- Unknown persons might be new students not yet enrolled
- Different severity levels

### 3. Video Evidence Storage
**Decision:** Store clips in Frigate, reference by URL in alerts

**Rationale:**
- Frigate already manages video storage
- Don't duplicate storage
- Clips auto-expire with Frigate retention policy

### 4. Real-time Location
**Decision:** Use Redis cache with 5-minute TTL

**Rationale:**
- Fast lookups for "where is person now"
- Auto-expires stale locations
- PostgreSQL has full history, Redis has current

---

**Status:** Core routes defined, ready for implementation  
**Timeline:** 6 weeks (3 phases: detection, evidence, analytics)  
**Focus:** Safety monitoring FIRST, other features later
