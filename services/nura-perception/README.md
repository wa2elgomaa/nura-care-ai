# NURA Perception Service

Privacy-first computer vision perception pipeline for childcare safety monitoring.

## Purpose

Processes camera feeds locally on the edge box to detect:
- Person presence and tracking (YOLO + ByteTrack)
- Fall detection via pose estimation (MediaPipe)
- Camera-follow tracking for child-specific views
- **Privacy guarantee**: No raw video or face embeddings leave the edge box

## Technology Stack

- **FastAPI**: Async Python web framework
- **Ultralytics YOLO**: Real-time person/object detection
- **MediaPipe Pose**: Skeletal keypoint extraction
- **ByteTrack**: Multi-object tracking
- **NATS**: Event publishing

## Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run service
uvicorn src.main:app --reload --port 8000

# Run tests
pytest
```

## Docker Build

```bash
docker build -t nura/perception:dev .
docker run -p 8000:8000 --env-file .env nura/perception:dev
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NATS_URL` | `nats://nats:4222` | NATS server URL |
| `RTSP_BASE` | `rtsp://frigate:8554` | Frigate restream base URL |
| `FRIGATE_API` | `http://frigate:5000` | Frigate API endpoint |
| `DETECTION_CONFIDENCE` | `0.5` | YOLO detection confidence threshold |
| `FALL_THRESHOLD` | `0.7` | Fall detection confidence threshold |
| `SITE_ID` | `dev-site-001` | Site identifier for events |
| `LOG_LEVEL` | `info` | Logging level |

## API Endpoints

- `GET /health` - Health check
- `GET /` - Service info
- `POST /detect` - Manual frame detection (TODO)
- `GET /streams` - List active streams (TODO)
- `POST /streams/{camera_id}/start` - Start processing (TODO)
- `POST /streams/{camera_id}/stop` - Stop processing (TODO)
- `GET /metrics` - Prometheus metrics (TODO)

## Event Schema (NATS)

### Person Detected
```json
{
  "type": "person_detected",
  "site_id": "site-001",
  "camera_id": "cam-room3",
  "zone": "room3",
  "timestamp": 1699000000,
  "confidence": 0.92,
  "bbox": {"x": 100, "y": 150, "w": 80, "h": 120},
  "tracking_id": "track-123"
}
```

### Fall Detected
```json
{
  "type": "fall_detected",
  "site_id": "site-001",
  "camera_id": "cam-room3",
  "zone": "room3",
  "timestamp": 1699000000,
  "confidence": 0.88,
  "pose_state": "horizontal",
  "tracking_id": "track-123"
}
```

**Privacy Note**: No video frames, images, or face embeddings are included in events.

## Hardware Acceleration

### Coral TPU
```bash
# Install Edge TPU runtime
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install libedgetpu1-std python3-pycoral
```

### NVIDIA GPU
Use `compose.gpu.yaml` overlay for NVIDIA Container Toolkit support.

## Next Steps

- [ ] Implement YOLO detection loop
- [ ] Add MediaPipe pose estimation
- [ ] Integrate ByteTrack for tracking
- [ ] Add NATS event publishing
- [ ] Implement Frigate restream ingestion
- [ ] Add Prometheus metrics
- [ ] Write integration tests
