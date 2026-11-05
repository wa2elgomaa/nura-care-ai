# NURA Pipeline Integration Test

Complete integration test guide for the safety violation detection pipeline.

## Prerequisites

1. **Docker Compose** running
2. **Ollama** with LLaVA model installed
3. **All services built**

## Quick Test

```bash
# Run the automated test suite
./test-pipeline.sh
```

## Manual Step-by-Step Test

### Step 1: Start All Services

```bash
# Start infrastructure + new services
docker compose --env-file .env --profile app --profile ai up -d \
  postgres nats ollama nura-vlm nura-rag nura-rules

# Check all services are running
docker compose ps
```

**Expected**: All services show "running" or "healthy"

### Step 2: Verify Service Health

```bash
# VLM Service
curl http://localhost:8001/health | jq '.'
# Expected: {"status": "healthy", "model_loaded": true}

# RAG Service  
curl http://localhost:3002/health | jq '.'
# Expected: {"status": "healthy"}

# Rules Engine
curl http://localhost:3003/health | jq '.'
# Expected: {"status": "healthy"}
```

### Step 3: Test RAG Rule Matching

```bash
curl -X POST http://localhost:3002/match \
  -H "Content-Type: application/json" \
  -d '{
    "event_context": "two children visible, no adult present for 45 seconds",
    "category": "supervision",
    "top_k": 3
  }' | jq '.matches[0]'
```

**Expected Output**:
```json
{
  "rule_id": "RULE-001",
  "title": "Continuous Adult Supervision Required",
  "severity": "critical",
  "similarity": 0.92,
  "query_time_ms": 45
}
```

**Success Criteria**:
- ✅ `rule_id` = "RULE-001"
- ✅ `similarity` > 0.7
- ✅ `query_time_ms` < 100

### Step 4: Test VLM Scene Analysis (Optional)

```bash
# Create test image
curl -o test_classroom.jpg "https://via.placeholder.com/640x480.jpg?text=Classroom+Test"

# Encode to base64
IMAGE_B64=$(base64 < test_classroom.jpg | tr -d '\n')

# Analyze
curl -X POST http://localhost:8001/analyze/supervision \
  -H "Content-Type: application/json" \
  -d "{\"image_base64\": \"$IMAGE_B64\", \"camera_id\": \"test-camera\"}" | jq '.'
```

**Expected**: VLM returns analysis with `adults_detected` and `children_count` fields

### Step 5: Test End-to-End Detection Event

```bash
# Publish detection event to NATS
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
```

**Expected Log Output**:
```
nura-rules | Received detection event: no_adults_detected from classroom-2
nura-rules | Started tracking event: classroom-2_no_adults_detected
nura-rules | (wait ~30 seconds)
nura-rules | Threshold met for classroom-2_no_adults_detected (30s), processing...
nura-rules | Rule matched: RULE-001 (similarity: 0.92)
nura-rules | 🚨 VIOLATION ALERT: RULE-001 - Continuous Adult Supervision Required (critical)
nura-rules | Stored violation: EVT-1730646225-abc123
nura-rules | ✓ Violation alert generated in 2350ms
```

### Step 6: Verify Violation Was Stored

```bash
# Check violations in database
curl http://localhost:3003/violations | jq '.[0]'
```

**Expected**:
```json
{
  "event_id": "EVT-1730646225-abc123",
  "rule_id": "RULE-001",
  "camera_id": "classroom-2",
  "severity": "critical",
  "status": "open",
  "context": "2 children visible, no adult present...",
  "evidence_clip_path": "/evidence/2024-11-03/classroom-2/14-23-30.mp4"
}
```

### Step 7: Test Violation Acknowledgment

```bash
# Acknowledge the violation
curl -X POST http://localhost:3003/violations/EVT-1730646225-abc123/acknowledge \
  -H "Content-Type: application/json" \
  -d '{"acknowledged_by": "admin@school.com"}'

# Verify status changed
curl http://localhost:3003/violations | jq '.[0] | {event_id, status, acknowledged_by}'
```

**Expected**: `status` = "acknowledged"

---

## Performance Benchmarks

| Component | Target | Command to Test |
|-----------|--------|-----------------|
| RAG Query | <100ms | `curl -w "%{time_total}\n" -X POST http://localhost:3002/match ...` |
| VLM Analysis | <2s | `curl -w "%{time_total}\n" -X POST http://localhost:8001/analyze ...` |
| E2E Pipeline | <10s | See logs from step 5 (excluding 30s threshold) |

---

## Troubleshooting

### Issue: Services not healthy

```bash
# Check logs
docker compose logs nura-vlm
docker compose logs nura-rag  
docker compose logs nura-rules

# Restart service
docker compose restart nura-vlm
```

### Issue: RAG returns no matches

```bash
# Check rules exist
curl http://localhost:3002/rules | jq '.[] | {rule_id, title}'

# Should show: RULE-001, RULE-002, RULE-003

# If empty, rules not loaded - check Postgres init
docker compose exec postgres psql -U nura -d nura -c "SELECT * FROM rules;"
```

### Issue: VLM "model not loaded"

```bash
# Check Ollama has model
docker compose exec ollama ollama list

# Should show: llava:13b (or qwen3-vl:8b-instruct or moondream)

# If missing, pull model
docker compose exec ollama ollama pull llava:13b
```

### Issue: Rules engine not receiving events

```bash
# Check NATS connection
docker compose logs nura-rules | grep NATS

# Expected: "📡 NATS connected: nats://nats:4222"

# Test NATS directly
docker run --rm --network nura_core_net natsio/nats-box nats pub test "hello"
```

---

## Success Criteria

✅ **All services healthy**  
✅ **RAG matches RULE-001 for supervision violation (similarity >0.7)**  
✅ **RAG query <100ms**  
✅ **VLM analysis completes (if tested)**  
✅ **Rules engine tracks events and creates violations**  
✅ **Violations stored in Postgres**  
✅ **Total processing time <10s (excluding threshold wait)**

---

## What This Proves

✅ **VLM → RAG → Rules pipeline is operational**  
✅ **pgvector semantic search works**  
✅ **NATS event bus is functioning**  
✅ **Threshold tracking logic works**  
✅ **Database integration complete**  
✅ **Ready for real camera integration**

---

**Next**: Connect to real Frigate camera streams and build nura-notifier!
