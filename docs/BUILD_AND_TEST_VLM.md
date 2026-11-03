# Build and Test VLM Service

Complete guide to build and test the NURA VLM (Vision-Language Model) service.

**Spec**: [specs/022-vlm-scene-understanding/spec.md](specs/022-vlm-scene-understanding/spec.md)

---

## Prerequisites

### 1. Install Ollama (Local LLM Runtime)

**macOS / Linux**:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows**:
Download from https://ollama.ai/download

**Verify installation**:
```bash
ollama --version
```

### 2. Pull VLM Model

Choose one based on your hardware:

**Option A: LLaVA 13B** (High quality, 24GB VRAM required)
```bash
ollama pull llava:13b
```

**Option B: LLaVA 7B** (Medium quality, 16GB VRAM)
```bash
ollama pull llava:7b
```

**Option C: Moondream 2B** (Lightweight, 8GB VRAM, fastest)
```bash
ollama pull moondream
```

**Verify model is loaded**:
```bash
ollama list
```

---

## Local Development (Without Docker)

### 1. Start Ollama Server
```bash
# Ollama runs in background automatically after install
# Check it's running:
curl http://localhost:11434/api/tags
```

### 2. Setup Python Environment
```bash
cd services/nura-vlm

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run VLM Service
```bash
# Set environment variables
export OLLAMA_URL=http://localhost:11434
export VLM_MODEL=llava:13b  # or llava:7b or moondream

# Run service
uvicorn src.main:app --reload --port 8001

# Service will be available at http://localhost:8001
```

### 4. Test VLM Service
```bash
# In another terminal, test health check
curl http://localhost:8001/health | jq '.'

# Expected response:
# {
#   "status": "healthy",
#   "version": "0.1.0",
#   "vlm_model": "llava:13b",
#   "model_loaded": true
# }
```

### 5. Test with Sample Image

**Create a test image** (or use any classroom photo):
```bash
# Download a sample classroom image
curl -o test_classroom.jpg "https://via.placeholder.com/640x480.jpg?text=Classroom+Test"
```

**Test supervision check**:
```bash
# Base64 encode image
IMAGE_B64=$(base64 < test_classroom.jpg | tr -d '\n')

# Send to VLM
curl -X POST http://localhost:8001/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "'$IMAGE_B64'",
    "prompt": "Is there an adult supervising the children in this classroom?",
    "camera_id": "test-camera"
  }' | jq '.'
```

**Expected response**:
```json
{
  "analysis": "The image shows...",
  "adults_detected": true,
  "children_count": 2,
  "safety_concern": false,
  "confidence": 0.85
}
```

---

## Docker Deployment

### 1. Update .env File
```bash
# Add to .env
VLM_MODEL=llava:13b  # or llava:7b or moondream
VLM_TEMPERATURE=0.3
VLM_MAX_TOKENS=500
```

### 2. Start Ollama in Docker
```bash
# Start Ollama with AI profile
docker compose --env-file .env --profile ai up -d ollama

# Pull model inside container
docker compose exec ollama ollama pull llava:13b

# Verify
docker compose exec ollama ollama list
```

### 3. Build and Start VLM Service
```bash
# Build VLM service
docker compose --env-file .env build nura-vlm

# Start with app profile
docker compose --env-file .env --profile app --profile ai up -d nura-vlm

# Check logs
docker compose logs -f nura-vlm

# Should see:
# ✓ Ollama connection successful
# ✓ Available models: ['llava:13b']
# VLM service started successfully
```

### 4. Test VLM Service (Docker)
```bash
# Health check
curl http://localhost:8001/health | jq '.'

# Or use test script
cd services/nura-vlm
./test_vlm.sh test_classroom.jpg
```

---

## Full Stack Test (Perception → VLM Pipeline)

### 1. Start Complete Stack
```bash
docker compose --env-file .env \
  --profile app \
  --profile sim \
  --profile ai \
  up -d

# Verify all services running
docker compose ps
```

### 2. Test Pipeline
```python
# Python script to test full pipeline
import requests
import base64

# 1. Get frame from Frigate
frigate_url = "http://localhost:5000/api/events"
# ... (get latest event image)

# 2. Send to nura-perception (YOLO detection)
perception_url = "http://localhost:8000/detect"
# ... (get person detections)

# 3. If no adults detected, send to VLM for verification
vlm_url = "http://localhost:8001/analyze/supervision"
response = requests.post(vlm_url, json={
    "image_base64": base64.b64encode(image_bytes).decode(),
    "camera_id": "classroom-2"
})

result = response.json()
if not result["adults_detected"]:
    print("ALERT: Children unsupervised!")
    # Trigger alert via nura-rules
```

---

## Performance Benchmarking

### 1. Latency Test
```bash
# Install hey (HTTP load testing)
go install github.com/rakyll/hey@latest

# Benchmark VLM latency
hey -n 10 -c 1 -m POST \
  -H "Content-Type: application/json" \
  -D test_request.json \
  http://localhost:8001/analyze

# Target: <2000ms per request (SC-003)
```

### 2. Throughput Test
```bash
# Test 30 frames/minute sustained (SC-004)
hey -z 2m -c 2 -m POST \
  -H "Content-Type: application/json" \
  -D test_request.json \
  http://localhost:8001/analyze
```

### 3. Memory Monitoring
```bash
# Monitor GPU VRAM usage
watch -n 1 nvidia-smi

# Monitor container memory
docker stats nura-vlm ollama
```

---

## Accuracy Testing

### 1. Create Test Dataset
```bash
mkdir -p test_images
# Add labeled images:
# - with_adult_01.jpg (adult present)
# - without_adult_01.jpg (no adult)
# - 3_children_01.jpg (count = 3)
# etc.
```

### 2. Run Accuracy Tests
```bash
cd services/nura-vlm

# Run accuracy test script
python tests/test_accuracy.py

# Expected output:
# Supervision Detection Accuracy: 92%
# Child Counting Accuracy (±1): 87%
```

---

## Troubleshooting

### Issue: "Ollama connection failed"
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
docker compose restart ollama

# Check logs
docker compose logs ollama
```

### Issue: "Model llava:13b not found"
```bash
# Pull model
docker compose exec ollama ollama pull llava:13b

# Or use docker compose exec interactively
docker compose exec -it ollama bash
ollama pull llava:13b
```

### Issue: "VLM inference too slow (>2s)"
```bash
# Option 1: Use faster model
export VLM_MODEL=moondream
docker compose restart nura-vlm

# Option 2: Check GPU utilization
nvidia-smi
# If GPU not used, check NVIDIA Container Toolkit install

# Option 3: Reduce max_tokens
export VLM_MAX_TOKENS=300
docker compose restart nura-vlm
```

### Issue: "CUDA out of memory"
```bash
# Ollama using too much VRAM
# Switch to smaller model
docker compose exec ollama ollama pull llava:7b
# Update VLM_MODEL in .env
```

---

## Next Steps

1. ✅ VLM service operational
2. ⏳ Create RAG service (rule knowledge base)
3. ⏳ Implement rules engine (violation detection)
4. ⏳ Connect pipeline: Perception → VLM → Rules → Notifier
5. ⏳ Deploy to pilot site

---

## API Documentation

Once service is running, visit:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

---

**Status**: ✅ VLM Service Built and Ready to Test

**Spec Compliance**: Implements FR-001 through FR-012 from [022-vlm-scene-understanding](specs/022-vlm-scene-understanding/spec.md)
