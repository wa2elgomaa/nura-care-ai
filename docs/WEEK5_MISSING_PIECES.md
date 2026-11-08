# Week 5 - Missing Pieces & Integration Plan

**Status**: Foundation Complete, Integration Needed  
**Time to Complete**: 2-3 hours

---

## What's Missing

### 1. Database Integration (1 hour)

**Current State:**
- Stream processor processes frames ✅
- Gets AI results ✅  
- Does NOT save to database ❌

**What's Needed:**
Add database connection to stream processor and save every detection:

```typescript
// services/nura-stream-processor/src/stream-processor/detection-storage.service.ts
@Injectable()
export class DetectionStorageService {
  async saveDetection(data: {
    person_id: string;
    camera_id: string;
    zone_name: string;
    activity: string;
    confidence: number;
  }) {
    await this.db.query(`
      INSERT INTO person_detections 
      (person_id, camera_id, zone_name, activity, confidence, detected_at)
      VALUES ($1, $2, $3, $4, $5, NOW())
    `, [data.person_id, data.camera_id, data.zone_name, data.activity, data.confidence]);
  }
}
```

**Impact:** Automatic data collection for analytics!

---

### 2. Face Recognition Integration (1 hour)

**Current State:**
- Stream processor detects persons ✅
- Does NOT identify who they are ❌

**What's Needed:**
Call face recognition after person detection:

```typescript
// In stream-processor.service.ts
private async processDetectionEvent(event: any) {
  // ... existing code ...
  
  // NEW: Identify person
  const person_id = await this.identifyPerson(frame, bbox);
  
  // Save detection with person_id
  await this.detectionStorage.saveDetection({
    person_id,  // 'adam_w' or 'unknown_001'
    camera_id: camera,
    zone_name: this.getZoneName(camera),
    activity: aiResult.activity || 'other',
    confidence: aiResult.confidence
  });
}

private async identifyPerson(frame: Buffer, bbox: any): Promise<string> {
  // Call face recognition endpoint
  const response = await axios.post(`${this.VLM_URL}/api/persons/search/by-image`, {
    photo: frame  // crop to bbox first
  });
  
  if (response.data) {
    return response.data.person_id;  // 'adam_w'
  }
  
  // Unknown person - create unknown_NNN
  return await this.unknownHandler.createUnknown(face_embedding);
}
```

**Impact:** Know WHO is doing WHAT!

---

### 3. Activity Classification (30 min)

**Current State:**
- Hybrid router detects violations ✅
- Does NOT classify normal activities ❌

**What's Needed:**
Simple rule-based activity classifier:

```typescript
// services/nura-stream-processor/src/stream-processor/activity-classifier.service.ts
@Injectable()
export class ActivityClassifierService {
  classifyActivity(current_bbox: any, previous_bbox: any): string {
    if (!previous_bbox) return 'other';
    
    const movement = this.calculateMovement(current_bbox, previous_bbox);
    const aspect_ratio = this.getAspectRatio(current_bbox);
    
    // Rule-based classification
    if (movement > 50) return 'running';
    if (movement > 15) return 'playing';
    if (aspect_ratio > 1.8) return 'standing';
    if (aspect_ratio < 1.2) return 'sitting';
    
    return 'other';
  }
  
  private calculateMovement(current: any, previous: any): number {
    const dx = current.x - previous.x;
    const dy = current.y - previous.y;
    return Math.sqrt(dx * dx + dy * dy);
  }
  
  private getAspectRatio(bbox: any): number {
    const height = bbox.y2 - bbox.y1;
    const width = bbox.x2 - bbox.x1;
    return height / width;
  }
}
```

**Impact:** Automatic activity detection!

---

## Integration Steps

### Step 1: Add Dependencies (5 min)

```bash
cd services/nura-stream-processor
npm install pg @types/pg
```

### Step 2: Create New Services (30 min)

Create 3 new files:
1. `detection-storage.service.ts` - Database operations
2. `activity-classifier.service.ts` - Activity detection
3. `unknown-handler.service.ts` - Unknown person creation

### Step 3: Update Stream Processor (30 min)

Update `stream-processor.service.ts`:
- Add face recognition call
- Add activity classification
- Add database storage
- Update location cache (Redis)

### Step 4: Test & Deploy (30 min)

```bash
# Build
docker compose build nura-stream-processor

# Deploy
docker compose up -d nura-stream-processor

# Test
docker compose logs nura-stream-processor -f

# Verify database
docker exec postgres psql -U nura -d nura_db \
  -c "SELECT COUNT(*) FROM person_detections WHERE detected_at > NOW() - INTERVAL '1 hour';"
```

---

## Why I Didn't Suggest It Initially

**Honest Answer:**

1. **Scope Creep Concern**: I wanted to show the analytics foundation first before diving into stream processor changes
2. **Testing Without Cameras**: Wanted to prove analytics works with test data before requiring live camera feed
3. **Incremental Progress**: Showed what's complete vs. what's pending separately

**But you're right** - I should have immediately said:

> "Week 5 analytics API is complete. Now let's integrate it with the stream processor to make it automatic. This will take 2-3 hours and then everything works end-to-end."

---

## Complete Integration (Ready to Do)

**Do you want me to:**

1. ✅ Update stream processor with all 3 integrations
2. ✅ Add face recognition calls
3. ✅ Add activity classifier
4. ✅ Add database storage
5. ✅ Test end-to-end with live cameras

**Time**: 2-3 hours  
**Result**: Fully automatic student analytics from live cameras

**Should I proceed with the integration now?**
