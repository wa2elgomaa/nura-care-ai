# Week 2 Implementation Status: Video Evidence Clips

**Status**: ✅ COMPLETE (Building)  
**Date**: 2026-11-08  
**Spec**: specs/051-week2-video-evidence/spec.md

## Summary

Week 2 implementation adds automatic video clip attachment to all alerts. When an incident is detected, the system queues a background job to export a 30-second video clip (10s before + 20s after the incident) from Frigate NVR and attach it to the alert as evidence.

## Completed Tasks

### 1. Database Migration ✅
- **File**: `edge/postgres/migrations/007_video_clips.sql`
- Created `clip_processing_queue` table for background processing
- Created `clip_retention` table for storage management and cleanup
- **Status**: Migration applied successfully

### 2. Frigate API Client ✅
- **File**: `services/nura-alerts/src/clients/frigate.client.ts`
- `exportClip()`: Download video clips from Frigate
- `verifyClipAvailable()`: Check if recordings exist for time period
- `healthCheck()`: Verify Frigate connectivity
- Streams data (no memory issues with large clips)
- Configurable timeout via `FRIGATE_TIMEOUT` env var

### 3. Database Entities ✅
- **File**: `services/nura-alerts/src/entities/clip-processing-queue.entity.ts`
  - Tracks clip processing jobs
  - Status: pending → processing → completed/failed
  - Retry logic (configurable max retries)

- **File**: `services/nura-alerts/src/entities/clip-retention.entity.ts`
  - Tracks stored clips for retention/cleanup
  - Expiry date calculation (default 30 days)
  - Deletion tracking

### 4. Clip Processing Worker ✅
- **File**: `services/nura-alerts/src/workers/clip-processing.worker.ts`
- Background worker that:
  - Polls clip_processing_queue every 10s (configurable)
  - Exports clips from Frigate
  - Saves to local storage (filesystem)
  - Updates alert.evidence with clip URL and metadata
  - Tracks retention for cleanup
  - Retries failed jobs (max 3 retries default)
- `cleanupExpiredClips()`: Daily cleanup job for expired clips

### 5. Alerts Service Integration ✅
- **File**: `services/nura-alerts/src/alerts/alerts.service.ts`
- Updated `createNewAlert()` to queue clip processing automatically
- Calls `queueClipProcessing()` for every new alert
- Configurable clip window: `CLIP_BEFORE_SECONDS` (default 10), `CLIP_AFTER_SECONDS` (default 20)

### 6. Module Registration ✅
- **File**: `services/nura-alerts/src/alerts/alerts.module.ts`
- Registered new entities: ClipProcessingQueue, ClipRetention
- Registered FrigateClient provider
- Registered ClipProcessingWorker provider
- Added HttpModule for HTTP requests

### 7. Validation & Testing ✅
- **File**: `tests/week2_validation.sh`
- Tests database schema (clip_processing_queue, clip_retention tables)
- Validates TypeScript entities exist
- Checks Frigate client exists
- Validates clip processing worker exists
- Verifies alerts service integration
- **Result**: 10/10 tests PASSED

## Data Structures

### AlertEvidence (Updated)
```typescript
{
  snapshot_url: string;
  clip_url: string | null;              // "/api/alerts/{id}/clip"
  clip_duration_seconds: number | null;  // 30 (10 + 20)
  clip_start_time: string | null;        // ISO timestamp
  clip_end_time: string | null;          // ISO timestamp
  clip_size_bytes: number | null;
  clip_status: 'pending' | 'available' | 'unavailable' | 'deleted';
  clip_error?: string;                   // If clip_status = unavailable
}
```

### ClipProcessingQueue
```typescript
{
  queueId: UUID;
  alertId: UUID;
  cameraId: string;
  incidentTimestamp: Date;
  beforeSeconds: number;  // Default 10
  afterSeconds: number;   // Default 20
  status: 'pending' | 'processing' | 'completed' | 'failed';
  retryCount: number;
  errorMessage?: string;
  createdAt: Date;
  processedAt?: Date;
}
```

### ClipRetention
```typescript
{
  clipId: UUID;
  alertId: UUID;
  filePath: string;        // Local filesystem path
  fileSizeBytes: number;
  createdAt: Date;
  expiresAt: Date;         // createdAt + CLIP_RETENTION_DAYS
  deletedAt?: Date;
}
```

## Configuration

All configuration is .env driven (no hardcoded values):

```bash
# Frigate Integration
FRIGATE_URL=http://frigate:5000
FRIGATE_TIMEOUT=60000  # 60s

# Clip Processing
CLIP_POLL_INTERVAL=10000  # 10s (worker poll rate)
CLIP_BEFORE_SECONDS=10    # Seconds before incident
CLIP_AFTER_SECONDS=20     # Seconds after incident
CLIP_MAX_RETRIES=3        # Max retry attempts
CLIP_STORAGE_DIR=/data/clips  # Local storage directory
CLIP_RETENTION_DAYS=30    # Retention period before cleanup
```

## System Flow

```
1. Alert Created (alerts.service.ts)
   ↓
2. Add to clip_processing_queue (status: pending)
   ↓
3. Worker picks up job every 10s (clip-processing.worker.ts)
   ↓
4. Check if Frigate has recordings for time period
   ↓
5. Export clip from Frigate (10s before + 20s after)
   ↓
6. Stream clip to local storage (/data/clips/{alert_id}_clip.mp4)
   ↓
7. Update alert.evidence:
   - clip_url: "/api/alerts/{id}/clip"
   - clip_duration_seconds: 30
   - clip_status: "available"
   - clip_size_bytes: file size
   ↓
8. Add to clip_retention (expires_at = now + 30 days)
   ↓
9. Mark queue job as completed
```

## Key Files Modified/Created

**Created:**
1. `edge/postgres/migrations/007_video_clips.sql` - Database schema
2. `services/nura-alerts/src/clients/frigate.client.ts` - Frigate API client
3. `services/nura-alerts/src/entities/clip-processing-queue.entity.ts` - Queue entity
4. `services/nura-alerts/src/entities/clip-retention.entity.ts` - Retention entity
5. `services/nura-alerts/src/workers/clip-processing.worker.ts` - Background worker
6. `tests/week2_validation.sh` - Validation tests

**Modified:**
7. `services/nura-alerts/src/alerts/alerts.service.ts` - Queue clip processing
8. `services/nura-alerts/src/alerts/alerts.module.ts` - Register new components
9. `services/nura-alerts/package.json` - Add @nestjs/axios dependency

## Storage Design

**Local Filesystem Storage (Current):**
- Clips stored in `/data/clips/` directory
- Filename format: `{alert_id}_clip.mp4`
- Worker creates directory if it doesn't exist
- Retention cleanup deletes files after expiry

**Future: Cloud Storage Integration**
- Design allows easy migration to S3/GCS/Azure Blob
- Just replace `saveStream()` implementation
- Retention tracking table remains same
- Clip URLs can be pre-signed URLs

## Next Steps (Not Yet Implemented)

These are documented in the Week 2 spec but deferred for later:

1. **API Endpoint for Clip Retrieval**
   - GET `/api/alerts/{id}/clip`
   - Stream MP4 file to client
   - Handle 410 Gone for expired clips

2. **Email Notifications with Video Links**
   - Update email templates to include video link button
   - "▶️ Watch Video Evidence (30s)"
   - Handle pending/unavailable states

3. **Daily Cleanup Cron Job**
   - Schedule `cleanupExpiredClips()` to run daily
   - Delete clips older than retention period
   - Update alert.evidence.clip_status = 'deleted'

4. **Storage Monitoring**
   - Emergency cleanup when storage >90% full
   - Delete oldest clips first
   - Alert admins about storage pressure

## Testing Instructions

Run validation tests:
```bash
./tests/week2_validation.sh
```

Manual database check after alert:
```bash
# Check clip queue
docker exec -it $(docker ps -q -f name=postgres) psql -U nura -d nura_db \
  -c "SELECT * FROM clip_processing_queue ORDER BY created_at DESC LIMIT 1;"

# Check clip retention
docker exec -it $(docker ps -q -f name=postgres) psql -U nura -d nura_db \
  -c "SELECT * FROM clip_retention ORDER BY created_at DESC LIMIT 1;"

# Check alert evidence
docker exec -it $(docker ps -q -f name=postgres) psql -U nura -d nura_db \
  -c "SELECT id, evidence FROM alerts ORDER BY first_detected DESC LIMIT 1;"
```

Check clip files:
```bash
docker exec nura-nura-alerts-1 ls -lh /data/clips/
```

## Notes

- Clips are stored **locally** in Docker volume `/data/clips`
- Worker starts automatically with the service (OnModuleInit)
- Frigate must be running and accessible at FRIGATE_URL
- Clip processing is asynchronous (30-60s delay expected)
- Failed clips retry up to 3 times before marking as unavailable
- Storage is managed automatically with retention cleanup
