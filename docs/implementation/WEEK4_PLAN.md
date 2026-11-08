# Week 4 Implementation Plan: Person Search & Locate

**Spec**: `specs/053-week4-person-search/spec.md`  
**Duration**: 1 week (4.5 days)  
**Status**: 📋 Planning

---

## Overview

Build a person search system that finds anyone across all cameras by name or photo, shows current location, and provides movement history.

**Key Features:**
1. Search by name (fuzzy matching) - <2s
2. Search by photo (face recognition) - <5s
3. Real-time location tracking (Redis cache)
4. 24-hour movement history

---

## Architecture

```
Search Request
  ↓
┌─────────────────────────────────────────┐
│         Person Search API               │
│         (VLM Service - Port 8001)       │
├─────────────────────────────────────────┤
│                                         │
│  1. Search by Name:                     │
│     - PostgreSQL fuzzy match (SIMILARITY)│
│     - enrolled_persons table            │
│                                         │
│  2. Search by Photo:                    │
│     - InsightFace face extraction       │
│     - pgvector similarity search        │
│     - enrolled_persons.face_embedding   │
│                                         │
│  3. Get Current Location:               │
│     - Redis cache (person_id → location)│
│     - 5-minute TTL                      │
│     - Fallback to person_detections     │
│                                         │
│  4. Movement History:                   │
│     - Query person_detections table     │
│     - Aggregate by camera/zone          │
│     - Last 24 hours                     │
│                                         │
└─────────────────────────────────────────┘
         ↓              ↓             ↓
   PostgreSQL       Redis        person_detections
   (enrolled)    (locations)      (history)
```

---

## Implementation Tasks

### Task 1: Add Redis to Stack (0.5 day) ✅ FIRST

**Why First**: All other tasks depend on Redis being available

**Files:**
- `compose.yaml` - Add Redis service
- `.env` - Add REDIS_URL

**Changes:**
```yaml
# compose.yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  command: redis-server --appendonly yes
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 5s
    timeout: 3s
    retries: 5
  networks:
    - nura-network

volumes:
  redis_data:
```

**Environment:**
```bash
# .env
REDIS_URL=redis://redis:6379
REDIS_LOCATION_TTL=300  # 5 minutes
```

**Testing:**
```bash
docker compose up -d redis
docker compose exec redis redis-cli ping
# Expected: PONG
```

---

### Task 2: Redis Location Cache Integration (1 day)

**Update Stream Processor** to cache locations when detecting persons.

**Files:**
- `services/nura-stream-processor/src/location-cache.service.ts` (NEW)
- `services/nura-stream-processor/src/stream-processor.service.ts` (UPDATE)

**Location Cache Service:**
```typescript
// location-cache.service.ts
import { Injectable } from '@nestjs/common';
import { Redis } from 'ioredis';

interface PersonLocation {
  person_id: string;
  camera_id: string;
  zone_name: string;
  last_seen: Date;
  confidence: number;
}

@Injectable()
export class LocationCacheService {
  private redis: Redis;
  private ttl: number;

  constructor() {
    this.redis = new Redis(process.env.REDIS_URL);
    this.ttl = parseInt(process.env.REDIS_LOCATION_TTL || '300');
  }

  async updateLocation(location: PersonLocation): Promise<void> {
    const key = `person:location:${location.person_id}`;
    await this.redis.setex(
      key,
      this.ttl,
      JSON.stringify(location)
    );
  }

  async getLocation(person_id: string): Promise<PersonLocation | null> {
    const key = `person:location:${person_id}`;
    const data = await this.redis.get(key);
    return data ? JSON.parse(data) : null;
  }

  async getAllLocations(): Promise<PersonLocation[]> {
    const keys = await this.redis.keys('person:location:*');
    const locations = await Promise.all(
      keys.map(key => this.redis.get(key))
    );
    return locations
      .filter(Boolean)
      .map(data => JSON.parse(data));
  }
}
```

**Update Stream Processor:**
```typescript
// After person identification
if (identified_person) {
  await this.locationCache.updateLocation({
    person_id: identified_person.person_id,
    camera_id: frame.camera_id,
    zone_name: frame.zone || 'unknown',
    last_seen: new Date(),
    confidence: identified_person.confidence
  });
}
```

---

### Task 3: Person Search API (2 days)

**Implement 3 search endpoints** in VLM service.

**Files:**
- `services/nura-vlm/src/person_search_api.py` (NEW)
- `services/nura-vlm/src/main.py` (UPDATE - register router)

**Person Search API:**
```python
# person_search_api.py
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import redis
import json
import numpy as np

router = APIRouter(prefix="/api/persons", tags=["person-search"])

# Redis client
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"))

class PersonLocation(BaseModel):
    person_id: str
    full_name: str
    camera_id: str
    zone_name: str
    last_seen: datetime
    confidence: float

class MovementRecord(BaseModel):
    camera_id: str
    zone_name: str
    entered_at: datetime
    exited_at: Optional[datetime]
    duration_seconds: Optional[int]

# 1. Search by Name (Fuzzy)
@router.get("/search", response_model=List[PersonLocation])
async def search_by_name(name: str = Query(..., min_length=2)):
    """
    Search for persons by name (fuzzy matching)
    Returns current location from Redis or database
    """
    # PostgreSQL fuzzy search using pg_trgm extension
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT person_id, full_name, 
               SIMILARITY(full_name, %s) as score
        FROM enrolled_persons
        WHERE active = true
          AND SIMILARITY(full_name, %s) > 0.3
        ORDER BY score DESC
        LIMIT 10
    """, (name, name))
    
    results = []
    for person_id, full_name, score in cursor.fetchall():
        # Get location from Redis
        location_key = f"person:location:{person_id}"
        location_data = redis_client.get(location_key)
        
        if location_data:
            location = json.loads(location_data)
            results.append(PersonLocation(
                person_id=person_id,
                full_name=full_name,
                camera_id=location['camera_id'],
                zone_name=location['zone_name'],
                last_seen=location['last_seen'],
                confidence=location['confidence']
            ))
        else:
            # Fallback to database (last detection)
            cursor.execute("""
                SELECT camera_id, detected_at
                FROM person_detections
                WHERE person_id = %s
                ORDER BY detected_at DESC
                LIMIT 1
            """, (person_id,))
            
            row = cursor.fetchone()
            if row:
                results.append(PersonLocation(
                    person_id=person_id,
                    full_name=full_name,
                    camera_id=row[0],
                    zone_name='unknown',
                    last_seen=row[1],
                    confidence=0.0
                ))
    
    cursor.close()
    conn.close()
    return results

# 2. Search by Image
@router.post("/search/by-image", response_model=PersonLocation)
async def search_by_image(photo: UploadFile = File(...)):
    """
    Search for person by uploading their photo
    Uses face recognition to identify and return location
    """
    # Read image
    content = await photo.read()
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Extract face embedding
    import insightface
    face_model = insightface.app.FaceAnalysis(
        name='buffalo_l',
        providers=['CPUExecutionProvider']
    )
    face_model.prepare(ctx_id=0, det_size=(640, 640))
    
    faces = face_model.get(img)
    if not faces:
        raise HTTPException(status_code=400, detail="No face detected in image")
    
    query_embedding = faces[0].embedding  # 512D vector
    
    # Search in pgvector (enrolled_persons)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT person_id, full_name,
               1 - (face_embedding <=> %s::vector) as similarity
        FROM enrolled_persons
        WHERE active = true
          AND face_embedding IS NOT NULL
        ORDER BY face_embedding <=> %s::vector
        LIMIT 1
    """, (query_embedding.tolist(), query_embedding.tolist()))
    
    row = cursor.fetchone()
    if not row or row[2] < 0.6:  # Similarity threshold
        raise HTTPException(status_code=404, detail="Person not found")
    
    person_id, full_name, similarity = row
    
    # Get location
    location_key = f"person:location:{person_id}"
    location_data = redis_client.get(location_key)
    
    if location_data:
        location = json.loads(location_data)
        return PersonLocation(
            person_id=person_id,
            full_name=full_name,
            camera_id=location['camera_id'],
            zone_name=location['zone_name'],
            last_seen=location['last_seen'],
            confidence=float(similarity)
        )
    
    # Fallback
    cursor.execute("""
        SELECT camera_id, detected_at
        FROM person_detections
        WHERE person_id = %s
        ORDER BY detected_at DESC
        LIMIT 1
    """, (person_id,))
    
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Person not recently detected")
    
    return PersonLocation(
        person_id=person_id,
        full_name=full_name,
        camera_id=row[0],
        zone_name='unknown',
        last_seen=row[1],
        confidence=float(similarity)
    )

# 3. Movement History
@router.get("/{person_id}/movements", response_model=List[MovementRecord])
async def get_movement_history(
    person_id: str,
    from_time: Optional[datetime] = Query(None),
    to_time: Optional[datetime] = Query(None)
):
    """
    Get movement history for a person
    Shows camera/zone transitions over time
    """
    if not from_time:
        from_time = datetime.now() - timedelta(hours=24)
    if not to_time:
        to_time = datetime.now()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all detections in time range
    cursor.execute("""
        SELECT camera_id, detected_at, bbox
        FROM person_detections
        WHERE person_id = %s
          AND detected_at BETWEEN %s AND %s
        ORDER BY detected_at ASC
    """, (person_id, from_time, to_time))
    
    detections = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Aggregate into movements (same camera = one movement)
    movements = []
    current_camera = None
    current_entry = None
    
    for camera_id, detected_at, bbox in detections:
        if camera_id != current_camera:
            # New location
            if current_camera:
                # Close previous movement
                movements.append(MovementRecord(
                    camera_id=current_camera,
                    zone_name='unknown',  # TODO: Get from camera config
                    entered_at=current_entry,
                    exited_at=detected_at,
                    duration_seconds=int((detected_at - current_entry).total_seconds())
                ))
            
            current_camera = camera_id
            current_entry = detected_at
    
    # Close last movement
    if current_camera:
        movements.append(MovementRecord(
            camera_id=current_camera,
            zone_name='unknown',
            entered_at=current_entry,
            exited_at=None,  # Still there
            duration_seconds=None
        ))
    
    return movements
```

**Register Router:**
```python
# main.py
from src.person_search_api import router as person_search_router
app.include_router(person_search_router)
```

---

### Task 4: Database Setup (0.5 day)

**Enable PostgreSQL Extensions** for fuzzy search.

**Files:**
- `edge/postgres/migrations/009_person_search_extensions.sql` (NEW)

**Migration:**
```sql
-- Enable fuzzy text search extension
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create index for fast fuzzy search
CREATE INDEX IF NOT EXISTS idx_enrolled_persons_name_trgm 
ON enrolled_persons USING gin (full_name gin_trgm_ops);

-- Index for person_detections queries
CREATE INDEX IF NOT EXISTS idx_person_detections_person_time
ON person_detections (person_id, detected_at DESC);

-- Index for fast vector search
CREATE INDEX IF NOT EXISTS idx_enrolled_persons_face_embedding
ON enrolled_persons USING ivfflat (face_embedding vector_cosine_ops)
WITH (lists = 100);
```

**Run Migration:**
```bash
docker exec -it $(docker ps -q -f name=postgres) psql -U nura -d nura_db \
  -f /docker-entrypoint-initdb.d/009_person_search_extensions.sql
```

---

## Testing Plan

### Test 1: Redis Setup
```bash
docker compose up -d redis
docker compose exec redis redis-cli ping
# Expected: PONG

# Set test data
docker compose exec redis redis-cli SET "test:key" "hello"
docker compose exec redis redis-cli GET "test:key"
# Expected: hello
```

### Test 2: Search by Name
```bash
# Fuzzy search
curl "http://localhost:8001/api/persons/search?name=jane" | jq

# Expected:
# [
#   {
#     "person_id": "student_jane_doe",
#     "full_name": "Jane Doe",
#     "camera_id": "classroom_1",
#     "zone_name": "classroom",
#     "last_seen": "2026-11-08T15:30:00",
#     "confidence": 0.95
#   }
# ]
```

### Test 3: Search by Image
```bash
curl -X POST http://localhost:8001/api/persons/search/by-image \
  -F 'photo=@test_face.jpg' | jq

# Expected: Same format as name search
```

### Test 4: Movement History
```bash
curl "http://localhost:8001/api/persons/student_jane_doe/movements?from=2026-11-08T08:00" | jq

# Expected:
# [
#   {
#     "camera_id": "entrance",
#     "zone_name": "entrance",
#     "entered_at": "2026-11-08T08:15:00",
#     "exited_at": "2026-11-08T08:17:00",
#     "duration_seconds": 120
#   },
#   {
#     "camera_id": "classroom_1",
#     "zone_name": "classroom",
#     "entered_at": "2026-11-08T08:17:00",
#     "exited_at": null,
#     "duration_seconds": null
#   }
# ]
```

### Test 5: Performance
```bash
# Name search <2s
time curl "http://localhost:8001/api/persons/search?name=john"

# Image search <5s
time curl -X POST http://localhost:8001/api/persons/search/by-image \
  -F 'photo=@face.jpg'
```

---

## Success Metrics

- [ ] Redis deployed and healthy
- [ ] Location cache updating in real-time
- [ ] Name search <2s response time
- [ ] Image search <5s response time
- [ ] Fuzzy matching works ("jan" finds "Jane")
- [ ] Movement history shows 24h complete data
- [ ] 90%+ location accuracy from Redis cache

---

## Dependencies

**Services:**
- PostgreSQL (✅ running)
- Redis (❌ need to add)
- VLM Service (✅ running on host)
- Stream Processor (✅ running)

**Extensions:**
- pg_trgm (fuzzy search)
- pgvector (✅ already enabled)

---

## Timeline

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Redis setup + Migration | Redis running, extensions enabled |
| 2 | Location cache in stream processor | Locations cached in Redis |
| 3-4 | Person search API | 3 endpoints working |
| 4.5 | Testing & optimization | All metrics met |

---

**Week 4 Ready to Start!**  
**Next Step**: Add Redis to compose.yaml
