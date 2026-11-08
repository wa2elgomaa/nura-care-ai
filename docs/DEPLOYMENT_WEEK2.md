# Week 2 Deployment Complete ✅

**Date**: 2026-11-08  
**Services Deployed**: nura-storage, nura-alerts (updated)  
**Status**: ✅ OPERATIONAL

## Deployed Services

### 1. nura-storage (NEW)
- **Port**: 3012
- **Status**: ✅ Running
- **Health**: http://localhost:3012/storage/health
- **Purpose**: Centralized file storage for all services
- **Backend**: Local filesystem (/data/storage)
- **Volume**: storage_data (Docker volume)

### 2. nura-alerts (UPDATED)
- **Port**: 3011  
- **Status**: ✅ Running
- **Updates**: 
  - Clip processing worker active
  - Storage client integrated
  - Clip queue operational

## Verification

### Storage Service
```bash
# Health check
curl http://localhost:3012/storage/health
✅ {"status":"healthy","service":"nura-storage","timestamp":"..."}

# Storage stats
curl http://localhost:3012/storage/stats
✅ {
  "totalSize": 0,
  "totalSizeFormatted": "0 Bytes",
  "fileCount": 0,
  "categories": {
    "clips": {"size": 0, "count": 0},
    "snapshots": {"size": 0, "count": 0},
    "exports": {"size": 0, "count": 0},
    "temp": {"size": 0, "count": 0}
  }
}
```

### Alerts Service
```bash
# Clip processing worker
docker compose logs nura-alerts | grep Worker
✅ 🎬 Clip processing worker started
✅ Poll interval: 10000ms
✅ Retention: 30 days
✅ Max retries: 3
```

### Database
```bash
# Clip tables exist
docker exec -it $(docker ps -q -f name=postgres) psql -U nura -d nura_db \
  -c "\dt clip*"
✅ clip_processing_queue
✅ clip_retention
```

## Integration Points

### Services Using Storage

| Service | Category | Purpose |
|---------|----------|---------|
| nura-alerts | clips | Video clips from Frigate |
| nura-vlm | enrollments | Person enrollment photos |
| nura-stream-processor | snapshots | Frame snapshots (future) |
| nura-vlm | exports | VLM analysis exports (future) |

### Client Libraries

**TypeScript/NestJS:**
```typescript
import { StorageClient } from '../clients/storage.client';
// HTTP client to nura-storage:3012
```

**Python:**
```python
from storage_client import get_storage_client
# HTTP client to nura-storage:3012
```

## Configuration

### Environment Variables (Already Set)
```bash
# Storage Service
STORAGE_SERVICE_URL=http://nura-storage:3012
STORAGE_BACKEND=local
STORAGE_BASE_DIR=/data/storage

# Clip Processing (nura-alerts)
CLIP_POLL_INTERVAL=10000
CLIP_BEFORE_SECONDS=10
CLIP_AFTER_SECONDS=20
CLIP_MAX_RETRIES=3
CLIP_RETENTION_DAYS=30

# Frigate Integration
FRIGATE_URL=http://frigate:5000
FRIGATE_TIMEOUT=60000
```

## Testing Week 2

### 1. Upload Test File
```bash
# Create test file
echo "test content" > test.txt

# Upload via storage service
curl -F "file=@test.txt" http://localhost:3012/storage/upload/temp

# Expected response:
{
  "success": true,
  "path": "/data/storage/temp/test.txt",
  "size": 13
}
```

### 2. Download Test File
```bash
curl http://localhost:3012/storage/download/temp/test.txt

# Expected: "test content"
```

### 3. List Files
```bash
curl http://localhost:3012/storage/list/temp

# Expected: ["test.txt"]
```

### 4. Delete Test File
```bash
curl -X DELETE http://localhost:3012/storage/temp/test.txt

# Expected:
{
  "success": true,
  "message": "File temp/test.txt deleted successfully"
}
```

### 5. Trigger Alert (Clip Processing)
```bash
# This will queue a clip processing job
./demo.sh crying

# Check clip queue
docker exec -it $(docker ps -q -f name=postgres) psql -U nura -d nura_db \
  -c "SELECT * FROM clip_processing_queue ORDER BY created_at DESC LIMIT 1;"

# Wait 30s for processing, then check storage
curl http://localhost:3012/storage/list/clips
```

## Service Logs

```bash
# Storage service
docker compose logs nura-storage -f

# Alerts service (clip worker)
docker compose logs nura-alerts -f | grep Clip

# All services
docker compose logs -f
```

## Docker Volumes

```bash
# Check storage volume
docker volume inspect nura_storage_data

# Check usage
docker system df -v | grep storage_data
```

## Next: Week 3

Now ready to implement **Week 3: WiFi Sensing + Stranger Detection**

Requirements:
- ✅ Storage service operational
- ✅ Alert service with clip processing
- ✅ Database migrations complete
- ✅ All configuration .env driven

### Week 3 Will Add:
1. RuView/ESP32 WiFi sensing integration
2. WiFi occupancy detection service
3. Stranger detection from camera feeds
4. Visitor management system
5. Dual data source architecture (Camera + WiFi)

---

**Week 2: ✅ COMPLETE & DEPLOYED**  
**Storage Service: ✅ OPERATIONAL**  
**Ready for Week 3!**
