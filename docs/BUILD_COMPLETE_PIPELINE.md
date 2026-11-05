# Build & Test Complete NURA Detection Pipeline

Complete guide to build and test the **full safety violation detection pipeline**.

**Date**: 2026-11-03  
**Status**: ✅ All 3 Core Services Built

---

## 🎯 What We Built Today

### 1. **nura-vlm** (Vision-Language Model)
- **Purpose**: Scene understanding with context
- **Tech**: Python, FastAPI, Ollama + LLaVA
- **Spec**: [specs/022-vlm-scene-understanding/spec.md](specs/022-vlm-scene-understanding/spec.md)
- **Build Guide**: [BUILD_AND_TEST_VLM.md](BUILD_AND_TEST_VLM.md)

### 2. **nura-rag** (Rule Knowledge Base)
- **Purpose**: Match events to rules via semantic search
- **Tech**: TypeScript, NestJS, pgvector
- **Spec**: [specs/023-rag-rule-knowledge/spec.md](specs/023-rag-rule-knowledge/spec.md)
- **README**: [services/nura-rag/README.md](services/nura-rag/README.md)

### 3. **nura-rules** (Rules Engine)
- **Purpose**: Orchestrate detection → VLM → RAG → alerts
- **Tech**: TypeScript, NestJS, NATS
- **Spec**: [specs/024-rules-engine-violation/spec.md](specs/024-rules-engine-violation/spec.md)
- **README**: [services/nura-rules/README.md](services/nura-rules/README.md)

---

## 📊 Complete Detection Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPLETE FLOW                            │
└─────────────────────────────────────────────────────────────┘

Camera (RTSP feed)
    ↓
Frigate NVR (local storage + restream) ✅ Already exists
    ↓
nura-perception (YOLO: "2 children, 0 adults detected") ✅ Template exists
    ↓ NATS: nura.events.detection
nura-vlm (LLaVA: "No adult visible in frame") ⭐ BUILT TODAY
    ↓ HTTP response OR NATS: nura.events.vlm_analysis
nura-rules (Rules Engine: Track 30s threshold) ⭐ BUILT TODAY
    ↓ HTTP: POST /match
nura-rag (pgvector: "RULE-001 matched, 0.92 similarity") ⭐ BUILT TODAY
    ↓ Return to nura-rules
nura-rules (Create violation alert + store in Postgres)
    ↓ NATS: nura.alerts.violation
nura-notifier (Push notification <10s total) ⏳ Next
    ↓
📱 Administrator receives alert
```

**Services Built**: 3/5 core services (60% complete)  
**Remaining**: nura-notifier, nura-perception enhancements

---

## 🚀 Quick Start (All Services)

### Prerequisites

1. **Ollama** (for VLM)
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llava:13b  # or qwen3-vl:8b-instruct or moondream
```

2. **Docker Compose** (for everything else)
```bash
docker compose version  # Should be v2.x
```

3. **Environment Setup**
```bash
cp .env.example .env
# Edit .env: change all *_PASSWORD values
nano .env
```

4. **Signing Keys** (for updates)
```bash
mkdir -p secrets && chmod 700 secrets
openssl genpkey -algorithm ed25519 -out secrets/update_signing_key.pem
openssl pkey -in secrets/update_signing_key.pem -pubout -out secrets/update_signing_key.pub
chmod 600 secrets/update_signing_key.pem
```

---

## 🔧 Build All Services

### Step 1: Start Infrastructure
```bash
# Postgres, NATS, Mosquitto, Keycloak, Frigate
docker compose --env-file .env up -d

# Verify
docker compose ps
docker compose exec postgres psql -U nura -c '\l'
```

### Step 2: Start Ollama (AI Profile)
```bash
# Start Ollama container
docker compose --env-file .env --profile ai up -d ollama

# Pull VLM model
docker compose exec ollama ollama pull llava:13b

# Verify
docker compose exec ollama ollama list
```

### Step 3: Build & Start New Services
```bash
# Build all new services
docker compose build nura-vlm nura-rag nura-rules

# Start with app profile
docker compose --env-file .env --profile app --profile ai up -d \
  nura-vlm nura-rag nura-rules

# Check logs
docker compose logs -f nura-vlm nura-rag nura-rules
```

**Expected logs**:
```
nura-vlm     | ✓ Ollama connection successful
nura-vlm     | ✓ Available models: ['llava:13b']
nura-rag     | ✓ Postgres connected successfully
nura-rag     | ✓ Embedding model loaded successfully
nura-rules   | 🚀 NURA Rules Engine listening on port 3003
nura-rules   | 📡 NATS connected: nats://nats:4222
```

---

## ✅ Verify Each Service

### 1. VLM Service (Port 8001)
```bash
# Health check
curl http://localhost:8001/health | jq '.'

# Expected:
# {
#   "status": "healthy",
#   "version": "0.1.0",
#   "vlm_model": "llava:13b",
#   "model_loaded": true
# }
```

### 2. RAG Service (Port 3002)
```bash
# Health check
curl http://localhost:3002/health | jq '.'

# List sample rules
curl http://localhost:3002/rules | jq '.[] | {rule_id, title, severity}'

# Expected: RULE-001, RULE-002, RULE-003
```

### 3. Rules Engine (Port 3003)
```bash
# Health check
curl http://localhost:3003/health | jq '.'

# List violations (should be empty initially)
curl http://localhost:3003/violations | jq '.'
```

---

## 🧪 Test Complete Pipeline

### Test 1: RAG Rule Matching
```bash
# Test: Match "children alone" to supervision rule
curl -X POST http://localhost:3002/match \
  -H "Content-Type: application/json" \
  -d '{
    "event_context": "two children visible, no adult present for 45 seconds",
    "category": "supervision",
    "top_k": 3
  }' | jq '.matches[0]'

# Expected: RULE-001 with similarity >0.8
```

### Test 2: VLM Scene Analysis
```bash
# Create test image (or use real classroom photo)
curl -o test_classroom.jpg "https://via.placeholder.com/640x480.jpg?text=Classroom"

# Base64 encode
IMAGE_B64=$(base64 < test_classroom.jpg | tr -d '\n')

# Analyze
curl -X POST http://localhost:8001/analyze/supervision \
  -H "Content-Type: application/json" \
  -d "{\"image_base64\": \"$IMAGE_B64\"}" | jq '.'

# Expected: adults_detected: true/false, children_count: N
```

### Test 3: End-to-End Detection Event
```bash
# Simulate detection event via NATS
docker run --rm --network nura_core_net natsio/nats-box nats pub nura.events.detection '{
  "camera_id": "classroom-2",
  "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
  "event_type": "no_adults_detected",
  "children_detected": 2,
  "adults_detected": 0,
  "confidence": 0.95
}'

# Watch rules engine logs
docker compose logs -f nura-rules

# Expected output:
# Processing detection: no_adults_detected at classroom-2
# Started tracking event: classroom-2_no_adults_detected
# (wait 30 seconds)
# Threshold met for classroom-2_no_adults_detected (30s), processing...
# Rule matched: RULE-001 (similarity: 0.92)
# 🚨 VIOLATION ALERT: RULE-001 - Continuous Adult Supervision Required (critical)
# Stored violation: EVT-...
# ✓ Violation alert generated in 2350ms

# Check violations were stored
curl http://localhost:3003/violations | jq '.[0]'
```

---

## 🔍 Troubleshooting

### Issue: VLM service "Ollama connection failed"
```bash
# Check Ollama is running
docker compose ps ollama

# Check model is pulled
docker compose exec ollama ollama list

# Restart VLM service
docker compose restart nura-vlm
```

### Issue: RAG service "Embedding model not initialized"
```bash
# Check logs for errors
docker compose logs nura-rag | grep -i error

# Model downloads on first run (may take 1-2 minutes)
docker compose logs -f nura-rag

# Wait for: "✓ Embedding model loaded successfully"
```

### Issue: Rules engine "Failed to query RAG service"
```bash
# Verify RAG service is accessible
docker compose exec nura-rules curl http://nura-rag:3002/health

# Check network connectivity
docker network inspect nura_core_net

# Verify both services are on core_net
docker compose ps --format json | jq -r '.[] | select(.Service | test("nura-(rag|rules)")) | .Networks'
```

### Issue: "pgvector extension not found"
```bash
# Recreate Postgres with init script
docker compose down postgres
docker volume rm nura_pg_data  # ⚠️ DELETES ALL DATA
docker compose up -d postgres

# Verify pgvector installed
docker compose exec postgres psql -U nura -d nura -c '\dx'
# Should show: vector | ... | vector data type and ivfflat access method
```

---

## 📈 Performance Benchmarks

| Component | Target | How to Measure |
|-----------|--------|----------------|
| **VLM Analysis** | <2s | Time from /analyze request to response |
| **RAG Query** | <100ms | `query_time_ms` field in /match response |
| **Rules Engine** | <10s total | Detection event → Alert published |

```bash
# Benchmark RAG
time curl -X POST http://localhost:3002/match \
  -H "Content-Type: application/json" \
  -d '{"event_context": "children alone"}' | jq '.query_time_ms'

# Should be <100ms
```

---

## 🎯 Next Steps

### 1. Implement nura-notifier
- Push notifications (ntfy)
- SMS alerts (Twilio)
- Email (SMTP)

### 2. Connect nura-perception
- Publish YOLO events to NATS
- Add pose estimation (fall detection)
- Integrate with rules engine

### 3. Add Evidence Clips
- Frigate clip extraction
- 15-second clips before violation
- Secure storage with access logging

### 4. Build Admin Dashboard
- Real-time alert feed
- Evidence viewer
- Violation acknowledgment
- Rule management UI

---

## 📚 Documentation Index

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture
- **[CORE_VISION.md](docs/CORE_VISION.md)** - Product vision
- **[PHASES_REVISED.md](.speckit/PHASES_REVISED.md)** - Roadmap
- **[BUILD_AND_TEST_VLM.md](BUILD_AND_TEST_VLM.md)** - VLM service guide
- **[services/nura-rag/README.md](services/nura-rag/README.md)** - RAG service
- **[services/nura-rules/README.md](services/nura-rules/README.md)** - Rules engine

---

## 🎉 Status

**✅ Core detection pipeline is 60% complete and ready to test!**

**Built Today**:
1. ✅ nura-vlm (VLM scene understanding)
2. ✅ nura-rag (Rule knowledge base with pgvector)
3. ✅ nura-rules (Violation detection orchestrator)

**All with specs first** - following proper software development practices.

**Next session**: Build nura-notifier and complete the pipeline!
