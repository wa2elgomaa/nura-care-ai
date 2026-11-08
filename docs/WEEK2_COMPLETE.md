# Week 2 Implementation Complete ✅

**Date**: 2026-11-08  
**Status**: Complete with Storage Service  

## Summary

Week 2 adds automatic video clip attachment to all alerts + centralized storage service for all file operations.

## What Was Implemented

### 1. Video Evidence Clips
- Automatic 30s clip generation (10s before + 20s after incident)
- Frigate NVR integration via API
- Background worker for async clip processing
- Retention management (30 days default)
- Database tracking (clip_processing_queue, clip_retention)

### 2. Centralized Storage Service (NEW!)
- **nura-storage** microservice (port 3012)
- HTTP REST API for all file operations
- Backend-agnostic (local → S3/GCS/Azure later)
- Categories: clips, snapshots, exports, temp
- Storage stats and monitoring

## Services Modified/Created

### Created:
1. **nura-storage** - New storage microservice
   - `services/nura-storage/` (complete service)
   - Port 3012
   - Local filesystem backend (cloud-ready)

2. **Database Migrations:**
   - `edge/postgres/migrations/007_video_clips.sql`

3. **New Components in nura-alerts:**
   - `clients/frigate.client.ts` - Frigate API integration
   - `clients/storage.client.ts` - Storage service client
   - `entities/clip-processing-queue.entity.ts`
   - `entities/clip-retention.entity.ts`
   - `workers/clip-processing.worker.ts`

### Modified:
1. `compose.yaml` - Added nura-storage service + storage_data volume
2. `services/nura-alerts/` - Integrated clip processing
3. `.env` - Added clip configuration variables

## Architecture

```
Alert Created
  ↓
Queue Clip Job (clip_processing_queue)
  ↓
Background Worker (every 10s)
  ↓
Export Clip from Frigate (HTTP API)
  ↓
Save to Storage Service (HTTP POST to nura-storage:3012)
  ↓
Storage Service → Local Filesystem (/data/storage/clips/)
  ↓
Update Alert Evidence (clip_url, clip_status, metadata)
  ↓
Track Retention (expires_at = now + 30 days)
```

## Key Features

**Video Clips:**
- 30s duration (configurable)
- Async processing (no alert delay)
- Retry logic (max 3 attempts)
- Graceful failures (mark as unavailable)
- Automatic expiry cleanup

**Storage Service:**
- RESTful HTTP API
- Upload (multipart or base64)
- Download (stream)
- Delete, List, Metadata
- Storage statistics
- Easy to swap backends (S3/GCS/Azure)

## Configuration (.env)

```bash
# Frigate Integration
FRIGATE_URL=http://frigate:5000
FRIGATE_TIMEOUT=60000

# Clip Processing
CLIP_POLL_INTERVAL=10000  # Worker poll rate
CLIP_BEFORE_SECONDS=10
CLIP_AFTER_SECONDS=20
CLIP_MAX_RETRIES=3
CLIP_RETENTION_DAYS=30

# Storage Service
STORAGE_SERVICE_URL=http://nura-storage:3012
STORAGE_BACKEND=local
STORAGE_BASE_DIR=/data/storage
```

## API Examples

### Storage Service
```bash
# Upload file
curl -F "file=@video.mp4" http://localhost:3012/storage/upload/clips

# Download file
curl http://localhost:3012/storage/download/clips/abc123_clip.mp4 -o clip.mp4

# Get metadata
curl http://localhost:3012/storage/metadata/clips/abc123_clip.mp4

# Get stats
curl http://localhost:3012/storage/stats

# List files
curl http://localhost:3012/storage/list/clips
```

## Testing

### Build & Start
```bash
# Build both services
docker compose build nura-storage nura-alerts

# Start services
docker compose up -d nura-storage nura-alerts

# Check logs
docker compose logs nura-storage -f
docker compose logs nura-alerts -f
```

### Validation
```bash
# Run Week 2 tests
./tests/week2_validation.sh

# Check storage service health
curl http://localhost:3012/storage/health

# Trigger test alert (will queue clip processing)
./demo.sh crying

# Check clip queue (wait 10s for processing)
docker exec -it $(docker ps -q -f name=postgres) psql -U nura -d nura_db \
  -c "SELECT * FROM clip_processing_queue ORDER BY created_at DESC LIMIT 1;"

# Check storage
curl http://localhost:3012/storage/stats | jq
curl http://localhost:3012/storage/list/clips
```

## File Structure

```
services/
├── nura-storage/              # NEW: Centralized storage service
│   ├── src/
│   │   ├── storage.service.ts    # Core storage logic
│   │   ├── storage.controller.ts # HTTP API
│   │   ├── app.module.ts
│   │   └── main.ts
│   ├── Dockerfile
│   ├── package.json
│   └── tsconfig.json
│
└── nura-alerts/
    ├── src/
    │   ├── clients/
    │   │   ├── frigate.client.ts   # NEW: Frigate integration
    │   │   └── storage.client.ts   # NEW: Storage HTTP client
    │   ├── entities/
    │   │   ├── clip-processing-queue.entity.ts  # NEW
    │   │   └── clip-retention.entity.ts         # NEW
    │   ├── workers/
    │   │   └── clip-processing.worker.ts        # NEW
    │   └── ...
    └── ...

edge/postgres/migrations/
└── 007_video_clips.sql        # NEW: Clip tables

docs/implementation/
├── WEEK2_IMPLEMENTATION_STATUS.md
└── STORAGE_SERVICE.md         # NEW: Storage service docs
```

## Next Steps

### Immediate (Optional)
- [ ] Add API endpoint to serve clips: GET /api/alerts/:id/clip
- [ ] Update email templates with video links
- [ ] Implement daily cleanup cron job
- [ ] Add storage monitoring alerts

### Week 3
Ready to proceed to **Week 3: WiFi Sensing + Stranger Detection**
- Dual data sources (Camera + WiFi)
- RuView/ESP32 integration
- Visitor management
- Unknown person alerts

## Benefits of Storage Service

1. **Separation of Concerns**: File storage is decoupled from business logic
2. **Backend Flexibility**: Swap local → S3/GCS/Azure without code changes
3. **Centralized Management**: All services use same storage API
4. **Monitoring**: Single place to track storage usage
5. **Scalability**: Easy to scale storage independently
6. **Cost Optimization**: Can implement compression, deduplication, tiering

## Notes

- Storage service runs on port 3012
- All file operations go through HTTP API (no direct filesystem access)
- Docker volume `storage_data` persists files
- Local backend is production-ready for single-node deployments
- Cloud backends (S3/GCS/Azure) ready to implement when needed
- All configuration is .env driven (no hardcoded values)

---

**Week 2 Status: ✅ COMPLETE**  
**Storage Service: ✅ OPERATIONAL**  
**Ready for Week 3!**
