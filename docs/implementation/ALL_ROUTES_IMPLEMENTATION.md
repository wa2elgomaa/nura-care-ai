# 🎯 All 4 Core Safety Routes - Complete Implementation Specs

**Status:** Ready for implementation  
**Total Timeline:** 6 weeks (3 weeks routes + 3 weeks testing/integration)  
**Team:** 2-3 engineers

---

## 📊 Implementation Overview

| Route | Current | Target | Effort | Priority |
|-------|---------|--------|--------|----------|
| Route 1: Incident Detection | 70% | 100% | 2 weeks | P0 |
| Route 2: Stranger Detection | 40% | 100% | 1 week | P0 |
| Route 3: Person Search | 50% | 100% | 1 week | P1 |
| Route 4: Behavioral Analytics | 50% | 100% | 2 weeks | P1 |

**Total:** 6 weeks parallel work (2-3 engineers)

---

## 🚨 Route 1: Incident Detection & Alert

**Detailed Spec:** See [ROUTE_1_IMPLEMENTATION.md](ROUTE_1_IMPLEMENTATION.md)

### Summary of Missing Components

1. **Enhanced Alert Payload** (3 days)
   - Add `persons_involved[]` with name, role, image
   - Add `evidence` with snapshot + video clip
   - Add `context` with environment data
   - Update database schema + migrations

2. **Video Evidence Clips** (3 days)
   - Frigate API integration for clip export
   - Background job to attach clips (30s delay)
   - Clip serving endpoints (`/api/alerts/{id}/clip.mp4`)
   - Email attachments with video links

3. **Safety Hazard Detector** (5 days)
   - Train MobileNetV3 model (knife, staircase, safe)
   - Achieve 80%+ accuracy
   - Integrate into hybrid router
   - Add to fast-path detectors

4. **WiFi Sensing Integration** (5 days - optional Phase 2)
   - RuView MQTT consumer service
   - Bathroom occupancy anomaly detection
   - After-hours movement alerts

### Key Files Created
```bash
# Backend
services/nura-alerts/src/models/alert.model.ts
services/nura-alerts/src/services/evidence.service.ts
services/nura-alerts/src/clients/frigate.client.ts

# VLM
services/nura-vlm/src/hybrid_router.py (updated)
services/nura-vlm/src/detectors/safety_detector.py

# Training
training/train_safety_detector.py

# Database
edge/postgres/migrations/006_enhanced_alerts.sql
```

---

## 👤 Route 2: Stranger Detection & Alert

**Status:** 40% → 100%  
**Effort:** 1 week  
**Priority:** P0

### Missing Components

#### 1. Stranger Detection Logic (2 days)

**File:** `services/nura-vlm/src/detectors/stranger_detector.py`

```python
class StrangerDetector:
    """Detect unknown persons in frame"""
    
    def __init__(self, face_identifier, enrollment_db):
        self.face_identifier = face_identifier
        self.enrollment_db = enrollment_db
        self.unknown_confidence_threshold = 0.6
        self.visitor_cache = {}  # Temporary visitors
    
    async def detect(
        self,
        frame: np.ndarray,
        person_tracks: List[PersonTrack],
        camera_id: str,
        timestamp: datetime
    ) -> List[StrangerDetection]:
        """Detect strangers in frame"""
        
        strangers = []
        
        for track in person_tracks:
            # Extract face
            face_roi = extract_face_roi(frame, track.bbox)
            if face_roi is None:
                continue
            
            # Try to identify
            person_id, confidence = await self.face_identifier.identify(face_roi)
            
            # Check if visitor (temporary enrollment)
            if person_id and await self.is_active_visitor(person_id, timestamp):
                continue  # Don't flag active visitors
            
            # Unknown person detected
            if person_id is None or confidence < self.unknown_confidence_threshold:
                strangers.append(StrangerDetection(
                    track_id=track.id,
                    face_image=encode_base64(face_roi),
                    bbox=track.bbox,
                    confidence=1.0 - (confidence if person_id else 0.0),
                    first_seen=timestamp,
                    camera_id=camera_id,
                    possible_match_id=person_id if confidence > 0.4 else None,
                    possible_match_name=await self.get_person_name(person_id) if person_id else None,
                    possible_match_confidence=confidence if person_id else 0.0
                ))
        
        return strangers
    
    async def is_active_visitor(self, person_id: str, timestamp: datetime) -> bool:
        """Check if person is an active visitor"""
        
        # Check cache first
        if person_id in self.visitor_cache:
            visitor = self.visitor_cache[person_id]
            return visitor['valid_from'] <= timestamp <= visitor['valid_until']
        
        # Query database
        visitor = await self.enrollment_db.get_visitor(person_id)
        if visitor:
            self.visitor_cache[person_id] = visitor
            return visitor['valid_from'] <= timestamp <= visitor['valid_until']
        
        return False
```

#### 2. Stranger Alert Type (1 day)

**File:** `services/nura-alerts/src/models/alert.model.ts`

```typescript
// Add to AlertType enum
enum AlertType {
  VIOLENCE = 'violence',
  DISTRESS = 'distress',
  SUPERVISION = 'supervision',
  BODY_LANGUAGE = 'body_language',
  STRANGER = 'stranger',           // NEW
  SAFETY_HAZARD = 'safety_hazard'
}

interface StrangerAlert extends Alert {
  type: 'stranger';
  stranger: {
    first_seen: string;
    last_seen: string;
    face_image_url: string;
    locations: Array<{
      camera_id: string;
      zone?: string;
      timestamp: string;
    }>;
    possible_matches?: Array<{
      person_id: string;
      name: string;
      confidence: number;
      reason: string;  // "Low confidence match" or "Similar appearance"
    }>;
  };
  suggested_action: string;  // "Check visitor log and verify identity"
}
```

#### 3. Visitor Management API (2 days)

**File:** `services/nura-vlm/src/enrollment_api.py`

```python
@app.post("/api/visitors/enroll")
async def enroll_visitor(
    name: str = Form(...),
    photo: UploadFile = File(...),
    valid_from: datetime = Form(...),
    valid_until: datetime = Form(...),
    purpose: str = Form(...),
    approved_by: str = Form(...)
):
    """Temporarily enroll a visitor"""
    
    # Read photo
    photo_bytes = await photo.read()
    photo_array = np.frombuffer(photo_bytes, np.uint8)
    image = cv2.imdecode(photo_array, cv2.IMREAD_COLOR)
    
    # Generate face encoding
    face_encoding = face_identifier.get_encoding(image)
    
    if face_encoding is None:
        raise HTTPException(400, "No face detected in photo")
    
    # Create visitor record
    visitor_id = str(uuid.uuid4())
    
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO visitors 
            (visitor_id, name, face_encoding, photo, valid_from, valid_until, purpose, approved_by, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
        """, visitor_id, name, face_encoding.tolist(), photo_bytes,
             valid_from, valid_until, purpose, approved_by)
    
    # Also add to persons table temporarily
    await conn.execute("""
        INSERT INTO persons (person_id, name, role, face_encoding, photo, is_visitor)
        VALUES ($1, $2, 'visitor', $3, $4, TRUE)
    """, visitor_id, f"Visitor: {name}", face_encoding.tolist(), photo_bytes)
    
    return {
        "visitor_id": visitor_id,
        "name": name,
        "valid_from": valid_from,
        "valid_until": valid_until,
        "message": "Visitor enrolled successfully"
    }

@app.post("/api/visitors/{visitor_id}/checkout")
async def checkout_visitor(visitor_id: str):
    """Mark visitor as checked out (expires enrollment early)"""
    
    async with db_pool.acquire() as conn:
        await conn.execute("""
            UPDATE visitors 
            SET valid_until = NOW()
            WHERE visitor_id = $1
        """, visitor_id)
        
        # Remove from persons table
        await conn.execute("""
            DELETE FROM persons WHERE person_id = $1
        """, visitor_id)
    
    return {"message": "Visitor checked out"}

# Background task to auto-expire visitors
async def cleanup_expired_visitors():
    """Remove expired visitors from persons table"""
    while True:
        async with db_pool.acquire() as conn:
            await conn.execute("""
                DELETE FROM persons 
                WHERE person_id IN (
                    SELECT visitor_id FROM visitors 
                    WHERE valid_until < NOW()
                )
            """)
        
        await asyncio.sleep(300)  # Every 5 minutes
```

#### 4. Stranger Alert Routing (1 day)

**File:** `services/nura-stream-processor/src/services/stranger-handler.ts`

```typescript
export class StrangerHandler {
  async handleStrangerDetection(
    strangers: StrangerDetection[],
    cameraId: string,
    timestamp: Date
  ): Promise<void> {
    for (const stranger of strangers) {
      // Check if we already alerted for this stranger recently
      const recentAlert = await this.alertService.findRecentStrangerAlert(
        stranger.face_image,  // Use face similarity
        300  // Within last 5 minutes
      );
      
      if (recentAlert) {
        // Update existing alert with new sighting
        await this.alertService.addStrangerSighting(recentAlert.alert_id, {
          camera_id: cameraId,
          timestamp: timestamp,
          zone: await this.getZone(cameraId, stranger.bbox)
        });
        continue;
      }
      
      // Create new stranger alert
      await this.alertService.createAlert({
        type: 'stranger',
        severity: 'medium',
        confidence: stranger.confidence,
        camera_id: cameraId,
        timestamp: timestamp,
        stranger: {
          first_seen: timestamp.toISOString(),
          last_seen: timestamp.toISOString(),
          face_image_url: await this.saveStrangerImage(stranger.face_image),
          locations: [{
            camera_id: cameraId,
            timestamp: timestamp.toISOString()
          }],
          possible_matches: stranger.possible_match_id ? [{
            person_id: stranger.possible_match_id,
            name: stranger.possible_match_name,
            confidence: stranger.possible_match_confidence,
            reason: 'Low confidence match - verification needed'
          }] : []
        },
        suggested_action: stranger.possible_match_id
          ? `Possible match to ${stranger.possible_match_name} - verify identity`
          : 'Check visitor log and verify identity'
      });
    }
  }
}
```

### Database Migration

**File:** `edge/postgres/migrations/007_visitors.sql`

```sql
-- Visitors table
CREATE TABLE visitors (
    visitor_id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    face_encoding VECTOR(512),
    photo BYTEA,
    valid_from TIMESTAMP NOT NULL,
    valid_until TIMESTAMP NOT NULL,
    purpose TEXT,
    approved_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_visitors_valid ON visitors(valid_from, valid_until);

-- Add is_visitor flag to persons
ALTER TABLE persons ADD COLUMN is_visitor BOOLEAN DEFAULT FALSE;
```

### Testing
```bash
# Test stranger detection
python tests/test_stranger_detection.py

# Test visitor enrollment
curl -X POST http://localhost:8001/api/visitors/enroll \
  -F 'name=John Visitor' \
  -F 'photo=@visitor.jpg' \
  -F 'valid_from=2026-11-08T09:00:00Z' \
  -F 'valid_until=2026-11-08T17:00:00Z' \
  -F 'purpose=Parent meeting' \
  -F 'approved_by=principal'

# Verify no stranger alert for visitor
./demo.sh visitor_image.jpg
```

---

## 🔍 Route 3: Person Search & Locate

**Status:** 50% → 100%  
**Effort:** 1 week  
**Priority:** P1

### Missing Components

#### 1. Search API (2 days)

**File:** `services/nura-vlm/src/services/search.py`

```python
from typing import Optional, List, Dict
import numpy as np
from datetime import datetime, timedelta

class PersonSearchService:
    """Search for persons by name or image"""
    
    def __init__(self, db_pool, face_identifier, location_cache):
        self.db = db_pool
        self.face_identifier = face_identifier
        self.location_cache = location_cache
    
    async def search_by_name(self, query: str) -> List[Dict]:
        """Search persons by name (fuzzy match)"""
        
        async with self.db.acquire() as conn:
            # Fuzzy search using similarity
            results = await conn.fetch("""
                SELECT 
                    person_id,
                    name,
                    role,
                    photo,
                    SIMILARITY(name, $1) as match_score
                FROM persons
                WHERE SIMILARITY(name, $1) > 0.3
                ORDER BY match_score DESC
                LIMIT 10
            """, query)
            
            persons = []
            for row in results:
                # Get current location
                location = await self.location_cache.get_location(row['person_id'])
                
                persons.append({
                    'person_id': row['person_id'],
                    'name': row['name'],
                    'role': row['role'],
                    'match_score': row['match_score'],
                    'photo_url': f"/api/persons/{row['person_id']}/photo",
                    'current_location': location
                })
            
            return persons
    
    async def search_by_image(self, image: np.ndarray) -> Optional[Dict]:
        """Search for person by face image"""
        
        # Get face encoding from image
        encoding = self.face_identifier.get_encoding(image)
        
        if encoding is None:
            return None
        
        # Search in enrollment database
        person_id, confidence = await self.face_identifier.identify_from_encoding(encoding)
        
        if person_id is None:
            return None
        
        # Get person details
        async with self.db.acquire() as conn:
            person = await conn.fetchrow("""
                SELECT person_id, name, role
                FROM persons
                WHERE person_id = $1
            """, person_id)
            
            if not person:
                return None
            
            # Get current location
            location = await self.location_cache.get_location(person_id)
            
            return {
                'person_id': person['person_id'],
                'name': person['name'],
                'role': person['role'],
                'confidence': confidence,
                'photo_url': f"/api/persons/{person_id}/photo",
                'current_location': location
            }
```

**File:** `services/nura-vlm/src/enrollment_api.py`

```python
@app.get("/api/persons/search")
async def search_persons(name: str = Query(..., min_length=2)):
    """Search persons by name"""
    
    results = await search_service.search_by_name(name)
    
    return {
        "query": name,
        "results": results,
        "count": len(results)
    }

@app.post("/api/persons/search/by-image")
async def search_by_image(photo: UploadFile = File(...)):
    """Search for person by uploading their photo"""
    
    # Read and decode image
    photo_bytes = await photo.read()
    photo_array = np.frombuffer(photo_bytes, np.uint8)
    image = cv2.imdecode(photo_array, cv2.IMREAD_COLOR)
    
    # Search
    result = await search_service.search_by_image(image)
    
    if result is None:
        raise HTTPException(404, "No matching person found")
    
    return result
```

#### 2. Real-time Location Cache (1 day)

**File:** `services/nura-vlm/src/cache/location_cache.py`

```python
import redis
import json
from typing import Optional, Dict
from datetime import datetime

class PersonLocationCache:
    """Redis cache for real-time person locations"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url)
        self.ttl = 300  # 5 minutes
    
    def update_location(
        self,
        person_id: str,
        camera_id: str,
        zone: Optional[str],
        timestamp: datetime
    ):
        """Update person's current location"""
        
        key = f"location:{person_id}"
        
        data = {
            "camera_id": camera_id,
            "zone": zone,
            "timestamp": timestamp.isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.redis.setex(key, self.ttl, json.dumps(data))
    
    def get_location(self, person_id: str) -> Optional[Dict]:
        """Get person's current location"""
        
        key = f"location:{person_id}"
        data = self.redis.get(key)
        
        if data is None:
            return None
        
        location = json.loads(data)
        
        # Calculate how long ago
        updated_at = datetime.fromisoformat(location['updated_at'])
        seconds_ago = (datetime.now() - updated_at).total_seconds()
        
        return {
            "camera_id": location['camera_id'],
            "zone": location['zone'],
            "last_seen": location['timestamp'],
            "seconds_ago": int(seconds_ago),
            "status": "current" if seconds_ago < 60 else "recent"
        }
    
    def batch_update(self, locations: List[Dict]):
        """Bulk update locations"""
        
        pipe = self.redis.pipeline()
        
        for loc in locations:
            key = f"location:{loc['person_id']}"
            data = json.dumps({
                "camera_id": loc['camera_id'],
                "zone": loc.get('zone'),
                "timestamp": loc['timestamp'].isoformat(),
                "updated_at": datetime.now().isoformat()
            })
            pipe.setex(key, self.ttl, data)
        
        pipe.execute()
```

**Integration:** Update Stream Processor to update cache

```typescript
// File: services/nura-stream-processor/src/services/frame-processor.ts

async processFrame(frame: Frame): Promise<void> {
  // ... existing processing ...
  
  // Update location cache for all detected persons
  if (analysis.persons_detected.length > 0) {
    await this.locationCache.batchUpdate(
      analysis.persons_detected.map(p => ({
        person_id: p.person_id,
        camera_id: frame.camera_id,
        zone: this.getZone(frame.camera_id, p.bbox),
        timestamp: frame.timestamp
      }))
    );
  }
}
```

#### 3. Movement History API (1 day)

**File:** `services/nura-vlm/src/enrollment_api.py`

```python
@app.get("/api/persons/{person_id}/movements")
async def get_person_movements(
    person_id: str,
    from_time: Optional[datetime] = Query(None),
    to_time: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000)
):
    """Get person's movement history"""
    
    # Default to last 24 hours
    if from_time is None:
        from_time = datetime.now() - timedelta(hours=24)
    if to_time is None:
        to_time = datetime.now()
    
    async with db_pool.acquire() as conn:
        # Get raw detections
        detections = await conn.fetch("""
            SELECT camera_id, zone, timestamp, bbox
            FROM person_detections
            WHERE person_id = $1
              AND timestamp BETWEEN $2 AND $3
            ORDER BY timestamp ASC
            LIMIT $4
        """, person_id, from_time, to_time, limit)
        
        # Aggregate into movements (group consecutive detections in same zone)
        movements = []
        current_movement = None
        
        for det in detections:
            location_key = f"{det['camera_id']}:{det['zone']}"
            
            if current_movement is None or current_movement['location_key'] != location_key:
                # Start new movement
                if current_movement:
                    movements.append(current_movement)
                
                current_movement = {
                    'location_key': location_key,
                    'camera_id': det['camera_id'],
                    'zone': det['zone'],
                    'entered_at': det['timestamp'],
                    'exited_at': det['timestamp'],
                    'duration_seconds': 0
                }
            else:
                # Update current movement
                current_movement['exited_at'] = det['timestamp']
                current_movement['duration_seconds'] = (
                    det['timestamp'] - current_movement['entered_at']
                ).total_seconds()
        
        # Add last movement
        if current_movement:
            movements.append(current_movement)
        
        # Get person details
        person = await conn.fetchrow("""
            SELECT name, role FROM persons WHERE person_id = $1
        """, person_id)
        
        return {
            "person_id": person_id,
            "name": person['name'] if person else "Unknown",
            "role": person['role'] if person else "unknown",
            "from_time": from_time.isoformat(),
            "to_time": to_time.isoformat(),
            "movements": [
                {
                    "camera_id": m['camera_id'],
                    "zone": m['zone'],
                    "entered_at": m['entered_at'].isoformat(),
                    "exited_at": m['exited_at'].isoformat(),
                    "duration_seconds": int(m['duration_seconds'])
                }
                for m in movements
            ],
            "total_movements": len(movements)
        }
```

### Docker Compose Update

**File:** `compose.yaml`

```yaml
# Add Redis service
redis:
  <<: *common
  image: redis:7-alpine
  volumes:
    - redis_data:/data
  networks: [ core_net ]
  ports:
    - "6379:6379"

volumes:
  redis_data:  # Add to volumes section
```

### Testing
```bash
# Test search by name
curl "http://localhost:8001/api/persons/search?name=Jane"

# Test search by image
curl -X POST http://localhost:8001/api/persons/search/by-image \
  -F 'photo=@test_face.jpg'

# Test movement history
curl "http://localhost:8001/api/persons/uuid/movements?from_time=2026-11-08T08:00:00Z"

# Test real-time location
# 1. Detect person in frame
# 2. Query location cache
# 3. Verify location updated
```

---

## 📊 Route 4: Behavioral Analysis & Reports

**Status:** 50% → 100%  
**Effort:** 2 weeks  
**Priority:** P1

### Missing Components

#### 1. Unknown Person Auto-Creation (2 days)
See detailed spec in CORE_SAFETY_ROUTES.md

#### 2. Activity Classifier (1 week)
Train 11-class activity model using ToddlerActions dataset

#### 3. Behavior Analysis Service (3 days)
New service to aggregate detections and generate reports

#### 4. Manual Linking UI (2 days)
Admin interface to link unknown persons to enrollment

**Full specs available in separate document to keep this summary concise.**

---

## 📋 Implementation Timeline

### Week 1: Route 1 & 2 Foundation
**Days 1-3:** Enhanced alerts with person names
**Days 4-5:** Stranger detection logic

### Week 2: Route 1 & 2 Complete
**Days 1-3:** Video evidence clips
**Days 4-5:** Visitor management + safety detector training

### Week 3: Routes 3 & 4
**Days 1-2:** Person search API
**Days 3-4:** Unknown person auto-creation
**Day 5:** Movement history API

### Weeks 4-5: Activity Classifier & Analytics
**Days 1-5:** Train activity model
**Days 6-10:** Behavior analysis service

### Week 6: Integration & Testing
**Days 1-2:** Manual linking UI
**Days 3-5:** End-to-end testing all routes

---

## ✅ Acceptance Criteria (All Routes)

### Route 1
- [ ] Person names in 90%+ alerts
- [ ] Video clips attached 100%
- [ ] Safety hazards detected 80%+
- [ ] Alert latency <10s

### Route 2
- [ ] Strangers detected 95%+
- [ ] False positives <5%
- [ ] Visitor whitelist working
- [ ] Alert within 30s

### Route 3
- [ ] Name search <2s
- [ ] Image search <5s
- [ ] Location accuracy 90%+
- [ ] Movement history complete

### Route 4
- [ ] Unknown auto-creation 100%
- [ ] Activity classification 80%+
- [ ] Daily reports generated
- [ ] Manual linking functional

---

**Status:** All routes fully specified  
**Ready for:** Team assignment and implementation kickoff  
**Next Step:** Review specs and begin Week 1 implementation
