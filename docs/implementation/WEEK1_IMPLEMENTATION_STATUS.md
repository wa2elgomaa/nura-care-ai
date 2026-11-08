# Week 1 Implementation Status: Enhanced Alerts with Person Identity

**Status**: ✅ COMPLETE  
**Date**: 2026-11-08  
**Spec**: specs/050-week1-enhanced-alerts/spec.md

## Summary

Week 1 implementation adds person identification and contextual information to all alerts. When an incident is detected, the system now captures who is involved, their roles, confidence levels, and environmental context.

## Completed Tasks

### 1. Database Migration ✅
- **File**: `edge/postgres/migrations/006_enhanced_alerts_fixed.sql`
- Added `persons_involved` JSONB column to alerts table
- Added `context` JSONB column to alerts table  
- Added `evidence` JSONB column to alerts table
- Created `alert_person_images` table for face image storage
- Applied `enrolled_persons` table migration (001_person_enrollment.sql)
- **Status**: Migration applied successfully, 5 sample persons enrolled

### 2. VLM Service Updates ✅
- **File**: `services/nura-vlm/src/hybrid_router.py`
- Updated `ViolationAlert` dataclass to include:
  - `persons_involved`: Array of person objects (not just IDs)
  - `context`: Detection method, scores, environment data
- Modified `_create_alert_from_fast_path()` to build full person objects:
  - `person_id`: Identified person ID or "unknown_{track_id}"
  - `name`: Full name from face recognition or "Person {ID}"
  - `role`: "child", "staff", "visitor", or "unknown"
  - `confidence`: Face recognition confidence (0.0-1.0)
  - `image_url`: (populated later by alert service)
  - `bbox`: Person bounding box [x1, y1, x2, y2]
  - `is_primary_subject`: Boolean (first person = primary)
- Modified `_create_alert_from_hybrid()` with same structure
- Added `_get_time_of_day()` helper for environment context
- Context includes:
  - `detection_method`: "fast_path", "hybrid", or "vlm"
  - `detector_scores`: Violence, distress, supervision, body_language scores
  - `vlm_analysis`: VLM response text (if hybrid)
  - `environment`: time_of_day, occupancy_count, adults_present, children_present

### 3. Alert Service Updates ✅
- **File**: `services/nura-alerts/src/entities/alert.entity.ts`
- Added `personsInvolved` JSONB field
- Added `context` JSONB field
- Added `evidence` JSONB field

- **File**: `services/nura-alerts/src/alerts/alerts.service.ts`
- Updated `createNewAlert()` to save new fields from violation payload
- Rebuilt and restarted service successfully

### 4. Validation & Testing ✅
- **File**: `tests/week1_validation.sh`
- Tests database schema (persons_involved, context, evidence columns)
- Validates environment variables (ENABLE_PERSON_TRACKING, ENABLE_FACE_IDENTIFICATION)
- Checks VLM service health
- Verifies detector files exist in packages/nura-detectors/
- Tests database connectivity
- Checks enrolled_persons table
- **Result**: 12/12 tests PASSED

- **File**: `tests/week1_integration_test.sh`
- End-to-end integration test
- Validates entire pipeline from VLM → Alert Service → Database
- **Result**: ALL TESTS PASSED

## Data Structures

### PersonInAlert
```typescript
{
  person_id: string;           // "adam_w" or "unknown_42"
  name: string;                // "Adam Williams" or "Person 42"
  role: string;                // "child", "staff", "visitor", "unknown"
  confidence: number;          // 0.0-1.0 (face recognition confidence)
  image_url: string;           // Face crop URL (populated by alert service)
  bbox: [number, number, number, number]; // [x1, y1, x2, y2]
  is_primary_subject: boolean; // true for primary subject
}
```

### AlertContext
```typescript
{
  detection_method: string;    // "fast_path", "hybrid", "vlm"
  detector_scores: {
    violence?: number;
    distress?: number;
    supervision?: number;
    body_language?: number;
  };
  vlm_analysis?: string;       // VLM response if hybrid/vlm
  environment: {
    time_of_day: string;       // "morning", "afternoon", "evening", "night"
    occupancy_count: number;   // Total people in frame
    adults_present: number;    // Adult count (TODO: implement)
    children_present: number;  // Child count
  };
}
```

## Configuration

All configuration is .env driven (no hardcoded values):

```bash
# Person Tracking
ENABLE_PERSON_TRACKING=true
PERSON_TRACKER_MODEL=n  # YOLOv8 nano (fastest)

# Face Identification
ENABLE_FACE_IDENTIFICATION=true
FACE_RECOGNITION_BACKEND=insightface
FACE_RECOGNITION_MIN_CONFIDENCE=0.6

# Database
DATABASE_URL=postgresql://nura:Pa$$w0rd!@localhost:5432/nura_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=nura_db
POSTGRES_USER=nura
POSTGRES_PASSWORD=Pa$$w0rd!
```

## Key Files Modified

1. `edge/postgres/migrations/006_enhanced_alerts_fixed.sql` - Database schema
2. `services/nura-vlm/src/hybrid_router.py` - Person object construction
3. `services/nura-alerts/src/entities/alert.entity.ts` - TypeScript entity
4. `services/nura-alerts/src/alerts/alerts.service.ts` - Save new fields
5. `tests/week1_validation.sh` - Validation tests
6. `tests/week1_integration_test.sh` - Integration tests

## Next Steps (Not Yet Implemented)

These are documented in the Week 1 spec but deferred for later:

1. **Email notifications with person images** (User Story 4)
   - Update email templates to include person names and photos
   - Inline images in email body
   - Red border for primary subject

2. **Face crop image storage**
   - Save face crops to `alert_person_images` table
   - Generate `image_url` for each person
   - Clean up old images

3. **Primary subject logic improvements**
   - Currently: first person = primary
   - TODO: Identify distressed child as primary in distress alerts
   - TODO: Identify aggressor as primary in violence alerts

4. **Adult/child classification**
   - Currently: all persons assumed to be children
   - TODO: Use person height or enrolled person data to classify adults

## Testing Instructions

Run validation tests:
```bash
./tests/week1_validation.sh
./tests/week1_integration_test.sh
```

Manual database check:
```bash
docker exec -it $(docker ps -q -f name=postgres) psql -U nura -d nura_db \
  -c "SELECT id, persons_involved, context FROM alerts ORDER BY first_detected DESC LIMIT 1;"
```

## Notes

- VLM and Ollama run **natively** (not in Docker) on this system
- VLM service runs on port 8001
- Alert service runs on port 3011
- Person tracking uses YOLOv8-nano + ByteTrack
- Face identification uses InsightFace with 95%+ accuracy
- 5 sample enrolled persons exist in database for testing
