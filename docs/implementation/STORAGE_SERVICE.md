# NURA Storage Service

**Service**: nura-storage  
**Port**: 3012  
**Purpose**: Centralized file storage for all services  
**Created**: 2026-11-08 (Week 2)

## Overview

The `nura-storage` service provides a centralized, backend-agnostic storage API for all file operations across the NURA system. All services interact with storage via HTTP API calls, making it easy to swap storage backends (local → S3 → GCS → Azure) without changing client code.

## Architecture

```
┌─────────────────┐     HTTP API      ┌──────────────────┐
│  nura-alerts    │ ───────────────>  │  nura-storage    │
│  (clips)        │                   │   (port 3012)    │
└─────────────────┘                   └──────────────────┘
                                              │
┌─────────────────┐     HTTP API              │
│ nura-stream     │ ───────────────>          │
│  (snapshots)    │                           │
└─────────────────┘                           ▼
                                      ┌──────────────────┐
┌─────────────────┐                   │  Storage Backend │
│  nura-vlm       │ ───────────────>  │                  │
│  (exports)      │     HTTP API      │  • Local FS      │
└─────────────────┘                   │  • AWS S3        │
                                      │  • Google GCS    │
                                      │  • Azure Blob    │
                                      └──────────────────┘
```

## Features

### Current (Week 2)
- ✅ Local filesystem backend
- ✅ HTTP REST API
- ✅ Multi-category storage (clips, snapshots, exports, temp)
- ✅ Stream and buffer uploads
- ✅ File metadata (size, created_at, path)
- ✅ File listing and deletion
- ✅ Storage statistics
- ✅ Docker volume persistence

### Future
- ⏳ AWS S3 backend
- ⏳ Google Cloud Storage backend
- ⏳ Azure Blob Storage backend
- ⏳ Authentication/authorization
- ⏳ File compression
- ⏳ CDN integration
- ⏳ Backup/restore

## API Endpoints

### Upload File (Multipart)
```http
POST /storage/upload/:category
Content-Type: multipart/form-data

Response:
{
  "success": true,
  "path": "/data/storage/clips/abc123_clip.mp4",
  "size": 2458624
}
```

### Upload File (JSON/Base64)
```http
POST /storage/upload-json
Content-Type: application/json

{
  "category": "clips",
  "filename": "test_clip.mp4",
  "data": "base64encodeddata..."
}

Response:
{
  "success": true,
  "path": "/data/storage/clips/test_clip.mp4",
  "size": 1024
}
```

### Download File
```http
GET /storage/download/:category/:filename

Response: Binary stream (video/mp4, image/jpeg, etc.)
```

### Get File Metadata
```http
GET /storage/metadata/:category/:filename

Response:
{
  "exists": true,
  "size": 2458624,
  "createdAt": "2026-11-08T10:30:00.000Z",
  "path": "/data/storage/clips/abc123_clip.mp4"
}
```

### Delete File
```http
DELETE /storage/:category/:filename

Response:
{
  "success": true,
  "message": "File clips/abc123_clip.mp4 deleted successfully"
}
```

### List Files
```http
GET /storage/list/:category

Response:
[
  "abc123_clip.mp4",
  "def456_clip.mp4",
  "xyz789_clip.mp4"
]
```

### Get Storage Statistics
```http
GET /storage/stats

Response:
{
  "totalSize": 125829120,
  "totalSizeFormatted": "120 MB",
  "fileCount": 42,
  "categories": {
    "clips": { "size": 104857600, "count": 35 },
    "snapshots": { "size": 20971520, "count": 7 },
    "exports": { "size": 0, "count": 0 },
    "temp": { "size": 0, "count": 0 }
  }
}
```

### Health Check
```http
GET /storage/health

Response:
{
  "status": "healthy",
  "service": "nura-storage",
  "timestamp": "2026-11-08T10:30:00.000Z"
}
```

## Storage Categories

| Category | Purpose | Retention | Used By |
|----------|---------|-----------|---------|
| `clips` | Video clips from Frigate | 30 days | nura-alerts |
| `snapshots` | Frame snapshots | 7 days | nura-stream-processor |
| `exports` | User-requested exports | 90 days | nura-vlm |
| `temp` | Temporary files | 1 day | All services |

## Client Usage

### TypeScript/NestJS
```typescript
import { StorageClient } from '../clients/storage.client';

// Upload a stream
const filepath = await this.storageClient.saveStream(
  stream, 
  'clips', 
  'alert123_clip.mp4'
);

// Upload a buffer
const filepath = await this.storageClient.saveBuffer(
  buffer, 
  'snapshots', 
  'frame_001.jpg'
);

// Get file metadata
const metadata = await this.storageClient.getMetadata('clips', 'alert123_clip.mp4');
console.log(`Size: ${metadata.size} bytes`);

// Download as stream
const stream = await this.storageClient.getStream('clips', 'alert123_clip.mp4');

// Delete file
await this.storageClient.delete('clips', 'alert123_clip.mp4');

// List files
const files = await this.storageClient.listFiles('clips');

// Get stats
const stats = await this.storageClient.getStats();
console.log(`Total storage: ${stats.totalSizeFormatted}`);
```

### Python
```python
import requests

STORAGE_URL = "http://nura-storage:3012"

# Upload file
with open('video.mp4', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        f"{STORAGE_URL}/storage/upload/clips",
        files=files
    )
    print(response.json())

# Download file
response = requests.get(
    f"{STORAGE_URL}/storage/download/clips/alert123_clip.mp4",
    stream=True
)
with open('downloaded.mp4', 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)
```

## Configuration

Environment variables:

```bash
# Service
PORT=3012

# Backend
STORAGE_BACKEND=local  # local | s3 | gcs | azure
STORAGE_BASE_DIR=/data/storage

# AWS S3 (future)
AWS_S3_BUCKET=nura-storage
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# Google Cloud Storage (future)
GCS_BUCKET=nura-storage
GCS_PROJECT_ID=...
GCS_CREDENTIALS_PATH=/secrets/gcs-key.json

# Azure Blob Storage (future)
AZURE_STORAGE_ACCOUNT=nura
AZURE_STORAGE_CONTAINER=storage
AZURE_STORAGE_KEY=...
```

## Docker Setup

### Compose Definition
```yaml
nura-storage:
  build:
    context: ./services/nura-storage
  image: nura/storage:dev
  environment:
    PORT: "3012"
    STORAGE_BACKEND: local
    STORAGE_BASE_DIR: /data/storage
  volumes:
    - storage_data:/data/storage
  ports:
    - "3012:3012"
  networks:
    - core_net

volumes:
  storage_data:
```

### Start Service
```bash
docker compose build nura-storage
docker compose up -d nura-storage

# Check logs
docker compose logs nura-storage -f

# Check storage usage
curl http://localhost:3012/storage/stats | jq
```

## Storage Backend Implementation

The service uses a strategy pattern for backends:

```typescript
switch (this.backend) {
  case StorageBackend.LOCAL:
    return await this.saveStreamLocal(stream, filepath);
  case StorageBackend.S3:
    return await this.saveStreamS3(stream, filepath);
  case StorageBackend.GCS:
    return await this.saveStreamGCS(stream, filepath);
  case StorageBackend.AZURE:
    return await this.saveStreamAzure(stream, filepath);
}
```

To add a new backend:
1. Implement backend-specific methods in `storage.service.ts`
2. Add backend enum value
3. Configure via `STORAGE_BACKEND` env var
4. No client code changes needed!

## Performance Considerations

### Local Filesystem
- Fast read/write (no network overhead)
- Limited to single machine
- Storage limited by disk size
- Good for development and single-node deployments

### Cloud Storage (S3/GCS/Azure)
- Scalable (unlimited storage)
- Higher latency (network overhead)
- Pay per GB stored + transfer
- Good for production multi-node deployments
- Enables CDN distribution

## Monitoring

### Disk Usage
```bash
# Check Docker volume size
docker system df -v | grep storage_data

# Check from inside container
docker exec nura-nura-storage-1 df -h /data/storage

# Via API
curl http://localhost:3012/storage/stats | jq .totalSizeFormatted
```

### Cleanup
```bash
# Delete all temp files
curl -X DELETE http://localhost:3012/storage/temp/*

# Delete specific file
curl -X DELETE http://localhost:3012/storage/clips/old_clip.mp4
```

## Integration with Week 2

The nura-storage service was created during Week 2 implementation to support video clip storage. The clip processing worker in nura-alerts uses the StorageClient to save clips:

```typescript
// Before (direct filesystem)
const filepath = join(this.storageDir, filename);
await this.saveStream(stream, filepath);

// After (centralized storage service)
const filepath = await this.storageClient.saveStream(stream, 'clips', filename);
```

This separation of concerns makes the system more modular and cloud-ready.

## Files

**Service:**
- `services/nura-storage/src/storage.service.ts` - Core storage logic
- `services/nura-storage/src/storage.controller.ts` - HTTP API endpoints
- `services/nura-storage/src/app.module.ts` - NestJS module
- `services/nura-storage/src/main.ts` - Service entry point
- `services/nura-storage/Dockerfile` - Docker build config

**Client:**
- `services/nura-alerts/src/clients/storage.client.ts` - HTTP client for TypeScript services

**Configuration:**
- `compose.yaml` - Service definition + volume
- `.env` - Configuration variables

## Next Steps

- [ ] Implement S3 backend for production
- [ ] Add authentication (JWT tokens)
- [ ] Add file encryption at rest
- [ ] Add automatic compression for large files
- [ ] Add CDN integration for public files
- [ ] Add backup/restore functionality
- [ ] Add file versioning
- [ ] Add access logs and audit trail
