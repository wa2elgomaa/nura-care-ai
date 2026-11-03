# NURA VLM Service

Vision-Language Model service for scene understanding and context analysis in childcare safety monitoring.

## Purpose

Analyzes camera frames to understand **context** beyond simple object detection:
- **Supervision checks**: Is an adult present?
- **Activity understanding**: What are the children doing?
- **Safety assessment**: Are there concerning behaviors or hazards?
- **Scene description**: Natural language explanation of what's happening

**Privacy**: Processes frames in real-time, no storage of images. Only text analysis results are saved.

## Technology Stack

- **FastAPI**: Async Python web framework
- **Ollama**: Local LLM runtime (supports VLMs)
- **LLaVA / Moondream**: Vision-Language Models
- **NATS**: Event publishing

## VLM Model Options

| Model | VRAM | Quality | Speed | Use Case |
|-------|------|---------|-------|----------|
| **LLaVA 13B** | 24GB | High | Slow (2-3s) | Production (NVIDIA GPU) |
| **LLaVA 7B** | 16GB | Medium | Medium (1-2s) | Balanced |
| **Moondream 2B** | 8GB | Good | Fast (<1s) | Edge devices, quick checks |

## Local Development

```bash
# Prerequisites: Ollama installed and running
# Install Ollama: https://ollama.ai/

# Pull VLM model (one-time)
ollama pull llava:13b  # or llava:7b, or moondream

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run service
uvicorn src.main:app --reload --port 8001

# Test endpoint
curl http://localhost:8001/health
```

## Docker Build

```bash
docker build -t nura/vlm:dev .
docker run -p 8001:8001 --env-file .env nura/vlm:dev
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NATS_URL` | `nats://nats:4222` | NATS server URL |
| `OLLAMA_URL` | `http://ollama:11434` | Ollama API endpoint |
| `VLM_MODEL` | `llava:13b` | VLM model to use |
| `VLM_TEMPERATURE` | `0.3` | Model temperature (lower = more consistent) |
| `VLM_MAX_TOKENS` | `500` | Max response length |
| `SITE_ID` | `dev-site-001` | Site identifier |
| `LOG_LEVEL` | `info` | Logging level |

## API Endpoints

### Health Check
```bash
GET /health
```

### Analyze Scene (Custom Prompt)
```bash
POST /analyze
{
  "image_base64": "<base64-encoded-image>",
  "prompt": "Is there an adult supervising?",
  "camera_id": "classroom-2",
  "timestamp": "2024-11-03T14:23:15Z"
}
```

**Response**:
```json
{
  "analysis": "Two children approximately ages 4-5 are sitting at a table. No adults visible in the frame...",
  "adults_detected": false,
  "children_count": 2,
  "safety_concern": true,
  "confidence": 0.89
}
```

### Quick Checks
```bash
POST /analyze/supervision
POST /analyze/count
POST /analyze/activity
POST /analyze/behavior
```

### Predefined Prompts
```bash
GET /prompts
```

## Integration with Detection Pipeline

```
Camera Frame
    ↓
nura-perception (YOLO detects persons)
    ↓
nura-vlm (analyzes context: "Is adult present?")
    ↓
nura-rules (matches violation: "No adult for 30s")
    ↓
nura-notifier (sends alert)
```

## Example VLM Prompts

### Supervision Check
```
"Analyze this classroom scene. Are there any adults present? 
How many children? Describe what you see."
```

### Behavior Analysis
```
"Look at the interactions between people in this image. 
Is there any concerning physical contact, aggression, or distress? 
Describe what's happening."
```

### Restricted Area
```
"Is this a restricted area like a kitchen, storage room, or staff area? 
Are there any children present where they shouldn't be?"
```

### Safety Hazard
```
"Identify any safety hazards in this scene: open doors, sharp objects, 
spills, unsecured furniture, or other dangers to children."
```

## Performance Optimization

### Model Selection
- **Development/Testing**: Use `moondream` (fast, lightweight)
- **Production**: Use `llava:13b` (accurate, requires GPU)
- **Balanced**: Use `llava:7b` (good middle ground)

### Frame Sampling
Don't analyze every frame:
- **Detection trigger**: Only analyze when YOLO detects an event
- **Time-based**: Analyze every 5-10 seconds for supervision checks
- **Change detection**: Analyze when scene changes significantly

### Batch Processing
For non-real-time analysis (e.g., nightly compliance review), batch process frames.

## Hardware Requirements

| Model | GPU | VRAM | Inference Time |
|-------|-----|------|----------------|
| LLaVA 13B | NVIDIA RTX 4090 | 24GB | ~2-3 seconds |
| LLaVA 7B | NVIDIA RTX 3080 | 16GB | ~1-2 seconds |
| Moondream 2B | NVIDIA GTX 1660 | 8GB | <1 second |

**Note**: CPU-only inference is possible but very slow (30+ seconds per frame).

## Next Steps

- [ ] Implement Ollama client integration
- [ ] Add image preprocessing (resize, normalize)
- [ ] Implement response parsing (extract structured fields)
- [ ] Add NATS event publishing
- [ ] Create prompt template library
- [ ] Add batch processing endpoint
- [ ] Write integration tests
- [ ] Add Prometheus metrics
- [ ] Benchmark inference speed on target hardware

## Example Use Cases

### Use Case 1: Unsupervised Children Alert
```
1. YOLO detects 2 persons (both children, no adults)
2. Wait 30 seconds to confirm
3. Send frame to VLM: "Are there any adults in this room?"
4. VLM responds: "No adults visible, two children present"
5. Rule engine: VIOLATION - "Children require adult supervision"
6. Alert sent to administrators
```

### Use Case 2: Restricted Area Access
```
1. YOLO detects person in "kitchen" zone
2. Send frame to VLM: "Is this person a child or adult? What are they doing?"
3. VLM responds: "This is a child, approximately 5 years old, reaching for objects on counter"
4. Rule engine: VIOLATION - "Children not allowed in kitchen"
5. Alert sent immediately
```

### Use Case 3: Fall Detection Verification
```
1. MediaPipe detects horizontal pose (potential fall)
2. Send frame to VLM: "Is this person injured or in distress? Describe what you see."
3. VLM responds: "A child is lying on the floor, appears to be reaching for a toy, no signs of distress"
4. Rule engine: False alarm - suppress alert
5. Log event for review
```

## Privacy & Compliance

- ✅ Images processed in-memory only (no disk storage)
- ✅ Only text analysis results saved to database
- ✅ All processing happens locally on edge box
- ✅ No images sent to external APIs (Ollama is local)
- ✅ Evidence clips stored separately with access logging

---

**Status**: Template ready - awaiting Ollama integration implementation
