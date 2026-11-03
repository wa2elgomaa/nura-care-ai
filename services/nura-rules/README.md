# NURA Rules Engine

Violation detection orchestrator - connects the entire detection pipeline.

**Spec**: [specs/024-rules-engine-violation/spec.md](../../specs/024-rules-engine-violation/spec.md)

## Purpose

The **brain** of NURA's safety monitoring system:
1. Subscribes to detection events from nura-perception (YOLO)
2. Optionally receives VLM context analysis
3. Queries nura-rag to match rules
4. Evaluates thresholds (e.g., "no adult for >30s")
5. Generates violation alerts with evidence clips
6. Publishes alerts to nura-notifier (<10s total)

## Complete Detection Flow

```
Camera Frame
    ↓
Frigate (RTSP restream)
    ↓
nura-perception (YOLO: "2 children, 0 adults")
    ↓ NATS: nura.events.detection
nura-vlm (VLM: "No adult visible")
    ↓ NATS: nura.events.vlm_analysis
nura-rules (THIS SERVICE) ⭐
    ├─ Track event duration (30s threshold)
    ├─ Query nura-rag for rule match
    ├─ Evaluate: threshold met? → YES
    ├─ Create violation alert
    └─ Store in Postgres
    ↓ NATS: nura.alerts.violation
nura-notifier (Push to admins)
```

## Technology Stack

- **NestJS**: TypeScript microservices framework
- **NATS**: Event bus (subscribe + publish)
- **PostgreSQL**: Store violations
- **HTTP clients**: Query nura-rag and nura-vlm

## Local Development

```bash
cd services/nura-rules

# Install dependencies
npm install

# Build
npm run build

# Start (requires Postgres, NATS, nura-rag)
npm run start:dev

# Service available at http://localhost:3003
```

## Docker Deployment

```bash
# Build
docker compose build nura-rules

# Start with full pipeline
docker compose --env-file .env --profile app --profile ai up -d \
  postgres nats nura-rag nura-vlm nura-rules

# Check logs
docker compose logs -f nura-rules
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://nura:password@postgres:5432/nura` | Postgres |
| `NATS_URL` | `nats://nats:4222` | NATS server |
| `RAG_SERVICE_URL` | `http://nura-rag:3002` | RAG service |
| `VLM_SERVICE_URL` | `http://nura-vlm:8001` | VLM service |
| `SUPERVISION_THRESHOLD_SECONDS` | `30` | Seconds before alerting |
| `SITE_ID` | `dev-site-001` | Site identifier |
| `PORT` | `3003` | HTTP port |

## API Endpoints

### GET /health
Health check

### GET /violations
List recent violations:
```bash
curl http://localhost:3003/violations?limit=50
```

### POST /violations/:eventId/acknowledge
Acknowledge violation:
```bash
curl -X POST http://localhost:3003/violations/EVT-123/acknowledge \
  -H "Content-Type: application/json" \
  -d '{"acknowledged_by": "admin@school.com"}'
```

## NATS Event Topics

### Subscribed Topics (Input)
- `nura.events.detection` - Detection events from nura-perception
- `nura.events.vlm_analysis` - VLM analysis results

### Published Topics (Output)
- `nura.alerts.violation` - Violation alerts for nura-notifier

## Event Schemas

### Detection Event (Input)
```json
{
  "camera_id": "classroom-2",
  "timestamp": "2024-11-03T14:23:45Z",
  "event_type": "no_adults_detected",
  "persons_detected": 2,
  "adults_detected": 0,
  "children_detected": 2,
  "confidence": 0.94
}
```

### Violation Alert (Output)
```json
{
  "event_id": "EVT-1730646225-abc123",
  "rule_id": "RULE-001",
  "camera_id": "classroom-2",
  "site_id": "dev-site-001",
  "timestamp": "2024-11-03T14:23:45Z",
  "severity": "critical",
  "title": "Continuous Adult Supervision Required",
  "description": "Children ages 0-5 must be within sight and sound of staff. Duration: 45s",
  "context": "2 children visible, no adult present. VLM analysis: No adult visible in frame.",
  "evidence_clip_path": "/evidence/2024-11-03/classroom-2/14-23-30.mp4",
  "rule_source": "STATE-REG-45.1.2"
}
```

## Threshold Evaluation Logic

**Supervision Violation Example**:

1. **T=0s**: YOLO detects "2 children, 0 adults" → Start tracking
2. **T=15s**: Still no adults → Continue tracking
3. **T=30s**: Threshold met (>30s) → Query RAG
4. **T=31s**: RAG returns RULE-001 (supervision) → Create violation
5. **T=32s**: Store in DB + Publish alert
6. **Total: 32s** (includes RAG query ~100ms)

**If adult returns at T=25s**: Event cleared, no alert.

## Performance

| Metric | Target | Implementation |
|--------|--------|----------------|
| **Detection → Alert** | <10s | Event tracking + RAG query ~2s |
| **Threshold tracking** | 30s default | Configurable per rule |
| **RAG query** | <100ms | HTTP to nura-rag |
| **DB write** | <50ms | Postgres insert |

## Testing

### Simulate Detection Event
```bash
# Publish test event to NATS
docker run --rm --network nura_core_net natsio/nats-box \
  nats pub nura.events.detection '{
    "camera_id": "test-camera",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "event_type": "no_adults_detected",
    "children_detected": 2,
    "adults_detected": 0,
    "confidence": 0.95
  }'

# Check logs for processing
docker compose logs -f nura-rules

# Check violations were stored
curl http://localhost:3003/violations
```

## Database Schema

Violations stored in `violation_events` table (already created in [edge/postgres/init.sql](../../edge/postgres/init.sql)):

```sql
CREATE TABLE violation_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(100) UNIQUE NOT NULL,
    rule_id VARCHAR(50) REFERENCES rules(rule_id),
    camera_id VARCHAR(50),
    site_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    context TEXT,
    evidence_clip_path TEXT,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'open',
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Next Steps

- [ ] Test with simulated events
- [ ] Connect to nura-perception (YOLO events)
- [ ] Connect to nura-vlm (VLM analysis)
- [ ] Connect to nura-notifier (alert publishing)
- [ ] Add evidence clip management (Frigate integration)
- [ ] Test complete pipeline end-to-end

---

**Status**: ✅ Rules Engine Built and Ready to Test

**Spec Compliance**: Implements FR-001 through FR-007 from [024-rules-engine-violation](../../specs/024-rules-engine-violation/spec.md)
