# Testing Guide

## End-to-End Pipeline Test

### Prerequisites

**Native Services (Mac):**
1. Ollama must be running (VLM in Docker will connect to it):
   ```bash
   ollama serve
   ```

**Note**: VLM now runs in Docker by default. For native mode (faster Metal GPU inference), see [compose.override.yml](compose.override.yml).

### Run Complete Test

```bash
./scripts/test-end-to-end.sh
```

This script will:
1. ✅ Check prerequisites (Docker, videos, native services)
2. ✅ Start core infrastructure (PostgreSQL, NATS, MQTT)
3. ✅ Start Frigate with test video file
4. ✅ Verify VLM Service and Ollama are running
5. ✅ Start VLM Proxy (bridges Docker ↔ Native VLM)
6. ✅ Start Stream Processor and Alert Service
7. ✅ Run database migrations
8. ✅ Trigger manual test event and monitor logs

### Manual Testing

#### Test MQTT → Stream Processor → VLM Pipeline

```bash
# Publish test detection event
docker exec nura-mosquitto-1 mosquitto_pub -h localhost \
  -t 'frigate/classroom_test/person' \
  -m '{"before":{"id":"manual-test","camera":"classroom_test","label":"person","score":0.99},"after":{"id":"manual-test","camera":"classroom_test","label":"person","score":0.99}}'

# Monitor Stream Processor
docker logs -f nura-nura-stream-processor-1

# Monitor VLM Proxy
docker logs -f nura-vlm-proxy-1

# Monitor Alert Service
docker logs -f nura-nura-alerts-1
```

#### Test VLM Service Directly

```bash
# Health check
curl http://localhost:8001/health | jq .

# Test detection (with tiny 1x1 pixel test image)
curl -X POST http://localhost:8001/analyze/hybrid \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "camera_id": "test"
  }'
```

#### Check Alerts in Database

```bash
docker exec -it nura-postgres-1 psql -U nura -d nura_db \
  -c "SELECT id, camera, violation_type, severity, confidence, created_at FROM alerts ORDER BY created_at DESC LIMIT 10;"
```

## Known Limitations

### Frigate CPU Detection
- **Issue**: CPU-based person detection is slow and often misses detections
- **Workaround**: Manually trigger test events via MQTT (see above)
- **Production**: Use NVIDIA GPU acceleration for real-time detection

### First Request Timeout
- **Issue**: First VLM `/analyze/hybrid` request loads detection models (30-90s)
- **Effect**: May timeout and return 502 from proxy
- **Workaround**: Second request will work as models stay loaded
- **Fix**: Pre-warm models on VLM service startup

### Test Videos
Current test videos: `tests/videos/classroom_*.mp4`
- `classroom_6.mp4` - 53MB, best for testing (most activity)
- `classroom_7.mp4` - 53MB, alternative
- Others - Smaller files, may have less detectable people

## Architecture (Local Development)

```
┌─────────────────────────────────────────┐
│  Native Mac (Metal GPU)                 │
│  ┌──────────┐        ┌──────────┐       │
│  │ Ollama   │        │ VLM      │       │
│  │          │◄───────┤ Service  │       │
│  └──────────┘        └────┬─────┘       │
│                           │ :8001       │
│                      ┌────▼─────┐       │
│                      │ nginx    │       │
│                      │ proxy    │       │
│                      └────┬─────┘       │
└───────────────────────────┼─────────────┘
                            │ 192.168.176.1:8001
┌───────────────────────────▼─────────────┐
│  Docker (core_net)                      │
│  ┌──────────────┐    ┌──────────────┐  │
│  │ Frigate      │───▶│ MQTT         │  │
│  │ (video file) │    │ (Mosquitto)  │  │
│  └──────────────┘    └──────┬───────┘  │
│                             │           │
│  ┌──────────────┐    ┌──────▼───────┐  │
│  │ Stream       │◄───┤ NATS         │  │
│  │ Processor    │───▶│              │  │
│  └──────┬───────┘    └──────────────┘  │
│         │                               │
│         │ fetch frame                   │
│         ▼                               │
│  ┌──────────────┐                      │
│  │ Frigate      │                      │
│  │ API          │                      │
│  └──────────────┘                      │
│         │                               │
│         │ POST /analyze/hybrid          │
│         ▼                               │
│  [to nginx proxy above]                │
│                                         │
│  ┌──────────────┐                      │
│  │ Alert        │◄─── NATS             │
│  │ Service      │                      │
│  └──────┬───────┘                      │
│         │                               │
│         ▼                               │
│  ┌──────────────┐                      │
│  │ PostgreSQL   │                      │
│  └──────────────┘                      │
└──────────────────────────────────────────┘
```

## Troubleshooting

### Pipeline Not Triggering
1. Check VLM Service is running: `pgrep -f "python.*src.main"`
2. Check Ollama is running: `pgrep -f "ollama"`
3. Check VLM Proxy logs: `docker logs nura-vlm-proxy-1`
4. Manually trigger event (see Manual Testing above)

### 502 Bad Gateway
- First request to VLM loads models (30-90s)
- Check VLM service logs for errors
- Verify VLM is accessible: `curl http://localhost:8001/health`

### No Alerts Created
- Check Stream Processor logs: `docker logs nura-nura-stream-processor-1`
- Check Alert Service logs: `docker logs nura-nura-alerts-1`
- Verify NATS connection: `curl http://localhost:8222`

## Quick Health Check

```bash
# All services status
docker compose ps

# VLM Service
curl -s http://localhost:8001/health | jq .

# Stream Processor
curl -s http://localhost:3010/health

# Alert Service  
curl -s http://localhost:3011/health

# NATS Monitor
curl -s http://localhost:8222/varz | jq .
```
