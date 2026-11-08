# Week 6: RAG + Rules Integration Plan

**Purpose**: Integrate nura-rag and nura-rules for compliance-based violation detection  
**Timeline**: Week 6 (5-7 days)  
**Priority**: Option A (as chosen)

---

## Understanding the Purpose

### nura-rag: Policy Knowledge Base
**Purpose**: Store and match school safety guidelines and government regulations

**Content**:
- 📄 Ministry of Education safety regulations
- 📄 School-specific safety policies
- 📄 Fire code requirements
- 📄 Health department guidelines
- 📄 State childcare regulations

**Example Rules**:
```
RULE-001: Continuous Adult Supervision Required
Source: STATE-REG-45.1.2
Clause: "Children ages zero through five years must be within 
         sight and sound of qualified child care staff at all times"
Category: supervision
Severity: critical

RULE-002: Maximum Room Capacity
Source: FIRE-CODE-12.4
Clause: "Classroom capacity must not exceed 1 child per 35 square feet"
Category: capacity
Severity: high

RULE-003: Restricted Area Access  
Source: HEALTH-CODE-8.2
Clause: "Children must not access kitchen, storage, or mechanical rooms"
Category: restricted_area
Severity: high
```

**How It Works**:
```
Detection Event: "Two children visible, no adult present for 45 seconds"
    ↓
Query RAG with semantic similarity
    ↓
RAG Returns: RULE-001 (similarity: 0.92)
    ↓
"This violates STATE-REG-45.1.2: Continuous Adult Supervision Required"
```

---

### nura-rules: Violation Orchestrator
**Purpose**: Monitor events, track durations, and trigger violations

**Capabilities**:
1. **Track event duration**: "No adult for >30 seconds"
2. **Query RAG**: Match event to regulations
3. **Create violations**: Store in database with evidence
4. **Publish alerts**: Send to notification system

**Example Flow**:
```
T=0s:  YOLO detects "2 children, 0 adults"
         ↓
       Start tracking (supervision violation)
         ↓
T=15s: Still no adults → Continue tracking
         ↓
T=30s: Threshold exceeded!
         ↓
       Query nura-rag: "no adult present with children"
         ↓
       RAG returns: RULE-001 (Continuous Supervision)
         ↓
       Create violation with evidence
         ↓
T=32s: Publish alert to nura-alerts
```

**Custom School Rules** (Added by School Admin):
```
CUSTOM-001: Playground Supervision Ratio
Source: SCHOOL-POLICY-2024
Clause: "1 staff member required per 8 children on playground"
Category: supervision
Severity: high
Threshold: 15 seconds  # Custom threshold
```

---

## Current vs Future Architecture

### Current Flow (Week 1-5):
```
Camera → Stream Processor → VLM
                              ↓
                         Hybrid Router
                         (detect violations)
                              ↓
                         Direct Alert
                         (no rule matching)
                              ↓
                         nura-alerts
```

**Problems**:
- ❌ No rule matching to regulations
- ❌ No threshold tracking (duration-based violations)
- ❌ Violations not stored in database
- ❌ No compliance reporting
- ❌ Hard-coded violation logic

---

### Future Flow (Week 6):
```
Camera → Stream Processor → VLM
                              ↓
                         Person Detection
                         Scene Analysis
                              ↓
                         NATS Event
                         (detection.person)
                              ↓
                       nura-rules ⬅️ NEW!
                       (orchestrator)
                         ├─ Track duration
                         ├─ Check thresholds
                         ├─ Query nura-rag ⬅️ NEW!
                         ├─ Match to regulations
                         ├─ Create violation
                         └─ Store in DB
                              ↓
                         NATS Event
                         (alert.violation)
                              ↓
                         nura-alerts
                         (route to channels)
```

**Benefits**:
- ✅ Rule-based compliance (not hard-coded)
- ✅ Duration tracking (">30s no adult")
- ✅ Violation database (audit trail)
- ✅ Compliance reporting (show regulation violations)
- ✅ Custom school rules (admin can add)

---

## Integration Tasks

### Phase 1: RAG Service Setup (1-2 days)

#### Task 1.1: Configure RAG Service
```bash
# services/nura-rag/.env
DATABASE_URL=postgresql://nura:password@postgres:5432/nura_db
EMBEDDING_MODEL=Xenova/all-MiniLM-L6-v2
SIMILARITY_THRESHOLD=0.7
PORT=3002
```

#### Task 1.2: Load Policy Documents
```bash
# Load sample rules
curl -X POST http://localhost:3002/rules -H "Content-Type: application/json" -d '{
  "rule_id": "STATE-REG-45.1.2",
  "title": "Continuous Adult Supervision Required",
  "description": "Children ages 0-5 must be within sight and sound of staff",
  "clause": "Children ages zero through five years must be within sight and sound of qualified child care staff at all times during the hours of operation",
  "source": "STATE-REG-45.1.2",
  "severity": "critical",
  "category": "supervision",
  "enabled": true
}'

# Load fire code rule
curl -X POST http://localhost:3002/rules -H "Content-Type: application/json" -d '{
  "rule_id": "FIRE-CODE-12.4",
  "title": "Maximum Room Capacity",
  "description": "Classroom capacity must not exceed 1 child per 35 square feet",
  "clause": "The maximum number of children permitted in any room must not exceed one child per thirty-five square feet of usable floor space",
  "source": "FIRE-CODE-12.4",
  "severity": "high",
  "category": "capacity",
  "enabled": true
}'

# Load restricted area rule
curl -X POST http://localhost:3002/rules -H "Content-Type: application/json" -d '{
  "rule_id": "HEALTH-CODE-8.2",
  "title": "Restricted Area Access",
  "description": "Children must not access kitchen, storage, or mechanical rooms",
  "clause": "Children shall not be permitted in kitchen areas, storage rooms, mechanical rooms, or other areas that present safety hazards",
  "source": "HEALTH-CODE-8.2",
  "severity": "high",
  "category": "restricted_area",
  "enabled": true
}'
```

#### Task 1.3: Test RAG Matching
```bash
# Test supervision violation matching
curl -X POST http://localhost:3002/match -H "Content-Type: application/json" -d '{
  "event_context": "two children visible, no adult present for 45 seconds",
  "category": "supervision",
  "top_k": 3
}'

# Expected response:
{
  "matches": [
    {
      "rule_id": "STATE-REG-45.1.2",
      "title": "Continuous Adult Supervision Required",
      "severity": "critical",
      "similarity": 0.92,
      "source": "STATE-REG-45.1.2"
    }
  ]
}
```

---

### Phase 2: Rules Engine Setup (2-3 days)

#### Task 2.1: Configure Rules Service
```bash
# services/nura-rules/.env
DATABASE_URL=postgresql://nura:password@postgres:5432/nura_db
NATS_URL=nats://nats:4222
RAG_SERVICE_URL=http://nura-rag:3002
VLM_SERVICE_URL=http://host.docker.internal:8001
SUPERVISION_THRESHOLD_SECONDS=30
PORT=3003
```

#### Task 2.2: Update NATS Event Subscriptions
**Current**: VLM publishes directly to `violations.detected`  
**New**: VLM publishes to `nura.events.detection` → Rules listens

**File**: `services/nura-rules/src/rules.service.ts`
```typescript
async subscribeToEvents() {
  // Subscribe to detection events
  const detectionSub = this.nats.subscribe('nura.events.detection');
  
  for await (const msg of detectionSub) {
    const event = this.jc.decode(msg.data);
    await this.processDetectionEvent(event);
  }
}

async processDetectionEvent(event: DetectionEvent) {
  // Track supervision violations
  if (event.adults_detected === 0 && event.children_detected > 0) {
    await this.trackSupervisionViolation(event);
  }
  
  // Track capacity violations
  if (event.persons_detected > this.getCapacityLimit(event.camera_id)) {
    await this.trackCapacityViolation(event);
  }
  
  // Track restricted area violations
  if (this.isRestrictedArea(event.zone) && event.children_detected > 0) {
    await this.trackRestrictedAreaViolation(event);
  }
}
```

#### Task 2.3: Implement Threshold Tracking
```typescript
// Track ongoing supervision violations
private supervisionTracking = new Map<string, {
  start_time: Date,
  camera_id: string,
  children_count: number
}>();

async trackSupervisionViolation(event: DetectionEvent) {
  const key = event.camera_id;
  
  if (!this.supervisionTracking.has(key)) {
    // Start tracking
    this.supervisionTracking.set(key, {
      start_time: new Date(),
      camera_id: event.camera_id,
      children_count: event.children_detected
    });
  } else {
    // Check duration
    const tracking = this.supervisionTracking.get(key);
    const duration = Date.now() - tracking.start_time.getTime();
    
    if (duration > this.SUPERVISION_THRESHOLD_SECONDS * 1000) {
      // Threshold exceeded - create violation
      await this.createViolation({
        camera_id: event.camera_id,
        event_type: 'no_adult_supervision',
        duration_seconds: Math.floor(duration / 1000),
        children_count: tracking.children_count
      });
      
      // Clear tracking
      this.supervisionTracking.delete(key);
    }
  }
}

// Clear tracking if adult returns
async clearSupervisionTracking(camera_id: string) {
  this.supervisionTracking.delete(camera_id);
}
```

#### Task 2.4: Integrate RAG Query
```typescript
async createViolation(violationData: any) {
  // Query RAG for rule matching
  const context = `${violationData.children_count} children present, no adult supervision for ${violationData.duration_seconds} seconds`;
  
  const ragResponse = await axios.post(`${this.RAG_URL}/match`, {
    event_context: context,
    category: 'supervision',
    top_k: 1
  });
  
  const matchedRule = ragResponse.data.matches[0];
  
  if (!matchedRule) {
    this.logger.warn('No rule matched for violation');
    return;
  }
  
  // Create violation with rule reference
  const violation = await this.violationRepository.save({
    event_id: `EVT-${Date.now()}`,
    rule_id: matchedRule.rule_id,
    camera_id: violationData.camera_id,
    timestamp: new Date(),
    severity: matchedRule.severity,
    title: matchedRule.title,
    description: `${matchedRule.description}. Duration: ${violationData.duration_seconds}s`,
    context,
    rule_source: matchedRule.source,
    metadata: {
      children_count: violationData.children_count,
      duration_seconds: violationData.duration_seconds,
      similarity: matchedRule.similarity
    }
  });
  
  // Publish violation alert
  await this.publishViolationAlert(violation);
}
```

---

### Phase 3: Update VLM Service (1 day)

#### Task 3.1: Change Event Publishing
**Current**: VLM publishes to `violations.detected`  
**New**: VLM publishes to `nura.events.detection`

**File**: `services/nura-vlm/src/main.py` (hybrid router)

```python
# OLD:
nats.publish("violations.detected", {
    "violation_type": "no_adult_supervision",
    "severity": "high",
    ...
})

# NEW:
nats.publish("nura.events.detection", {
    "camera_id": camera_id,
    "timestamp": datetime.utcnow().isoformat(),
    "event_type": "persons_detected",
    "persons_detected": len(persons),
    "adults_detected": adults_count,
    "children_detected": children_count,
    "confidence": 0.95,
    "zone": zone_name
})
```

---

### Phase 4: Admin UI for Custom Rules (Optional, 2 days)

#### Task 4.1: Rule Management Endpoints
Already exists in nura-rag:
```typescript
POST /rules           # Create rule
GET /rules            # List rules
PATCH /rules/:id      # Update rule
DELETE /rules/:id     # Soft delete
```

#### Task 4.2: Simple Admin UI (Future)
```html
<!-- Admin can add school-specific rules -->
<form id="add-rule-form">
  <input name="rule_id" placeholder="SCHOOL-POLICY-001">
  <input name="title" placeholder="Playground Supervision">
  <textarea name="clause">At least 1 staff member per 8 children on playground</textarea>
  <select name="severity">
    <option>critical</option>
    <option>high</option>
    <option>medium</option>
  </select>
  <select name="category">
    <option>supervision</option>
    <option>capacity</option>
    <option>restricted_area</option>
  </select>
  <button type="submit">Add Rule</button>
</form>
```

---

## Testing Plan

### Test 1: RAG Service
```bash
# 1. Start RAG service
docker compose up -d nura-rag

# 2. Load test rules (see Phase 1.2)

# 3. Test matching
curl -X POST http://localhost:3002/match -d '{
  "event_context": "no adult visible with children for 45 seconds"
}'

# Should return RULE-001 with high similarity
```

### Test 2: Rules Engine
```bash
# 1. Start Rules service
docker compose up -d nura-rules

# 2. Publish test detection event
docker run --rm --network nura_network natsio/nats-box \
  nats pub nura.events.detection '{
    "camera_id": "classroom-1",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "event_type": "persons_detected",
    "adults_detected": 0,
    "children_detected": 2,
    "confidence": 0.95
  }'

# 3. Wait 35 seconds (threshold is 30s)

# 4. Check violations
curl http://localhost:3003/violations

# Should show violation with RULE-001 matched
```

### Test 3: End-to-End
```bash
# 1. Start full stack
docker compose up -d

# 2. Trigger real camera detection
# (camera should detect children without adult)

# 3. Monitor flow
docker compose logs -f nura-rules

# Should see:
# - Detection event received
# - Tracking started
# - Threshold exceeded
# - RAG query sent
# - Violation created
# - Alert published
```

---

## Benefits Summary

### Before (Week 1-5):
- ❌ Hard-coded violation logic
- ❌ No rule matching
- ❌ No compliance reporting
- ❌ No violation history
- ❌ No duration tracking

### After (Week 6):
- ✅ Rule-based violations
- ✅ Matched to regulations (Ministry/State/School)
- ✅ Compliance reporting
- ✅ Full violation audit trail
- ✅ Duration-based thresholds
- ✅ Custom school rules
- ✅ Semantic similarity matching

---

## Timeline

| Day | Task | Deliverable |
|-----|------|-------------|
| **Day 1** | RAG setup + load rules | RAG service running |
| **Day 2** | Test RAG matching | Verified rule matching |
| **Day 3** | Rules engine setup | Rules service running |
| **Day 4** | Implement threshold tracking | Duration-based violations |
| **Day 5** | RAG integration | End-to-end flow working |
| **Day 6** | VLM event changes | All services integrated |
| **Day 7** | Testing + documentation | Production ready |

---

## Next Steps

1. ✅ Approve this integration plan
2. 🚀 Start Phase 1: RAG setup (Day 1-2)
3. 🚀 Continue Phase 2: Rules engine (Day 3-5)
4. 🚀 Complete Phase 3: VLM updates (Day 6)
5. ✅ Test end-to-end (Day 7)

**Ready to proceed with Week 6 implementation?**
