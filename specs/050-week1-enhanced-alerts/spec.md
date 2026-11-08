# Feature Specification: Week 1 - Enhanced Alerts with Person Identity

**Feature Branch**: `050-week1-enhanced-alerts`

**Created**: 2026-11-08

**Status**: Ready for Implementation

**Sprint**: Core Safety Routes - Week 1 of 8

**Input**: Route 1 (Incident Detection) - Add person names, images, and context to all alerts

## Overview

Enhance the alert system to include person identification in all incident alerts. When violence, distress, supervision violations, or other incidents are detected, the alert must include:
- Names and roles of all persons involved
- Face images for identification
- Primary subject determination (who is the main person affected)
- Environmental context (occupancy, adults present, children present)

**Current State:** Alerts contain only incident type, confidence, camera ID, and timestamp  
**Target State:** Alerts contain full person context with names, roles, images, and evidence

**Dependencies:**
- Person tracking (YOLOv8 + ByteTrack) - ✅ Working
- Face recognition (InsightFace) - ✅ Working
- Enrollment database - ✅ Working
- Alert service - ✅ Working

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Identify Persons in Incident Alerts (Priority: P1)

As a school administrator, when I receive an incident alert (distress, violence, supervision violation), I need to immediately know which child or staff member is involved by name and photo, so I can respond appropriately.

**Why this priority**: Knowing WHO is involved is critical for emergency response. Without person identity, staff must review video manually to identify the child, wasting precious response time.

**Independent Test**: Can be fully tested by triggering a distress alert with an enrolled child in frame, then verifying the alert includes the child's name, role, face image, and confidence score.

**Acceptance Scenarios**:

1. **Given** an enrolled child (Jane Doe) is detected crying in frame,
   **When** the distress detector triggers an alert,
   **Then** the alert contains:
   - Person name: "Jane Doe"
   - Role: "child"
   - Face image URL: `/api/alerts/{alert_id}/persons/jane_face.jpg`
   - Confidence: ≥ 0.8
   - is_primary_subject: true

2. **Given** multiple persons in frame during a violence incident,
   **When** the alert is created,
   **Then** all detected persons are included in `persons_involved[]` array
   **And** the person closest to the incident is marked `is_primary_subject: true`

3. **Given** an unknown person (not enrolled) triggers an incident,
   **When** the alert is created,
   **Then** the person is included with name: "Unknown" and role: "unknown"
   **And** their face image is still attached for later identification

4. **Given** a staff member and child are both present during supervision violation,
   **When** the alert is created,
   **Then** both persons are listed with correct roles
   **And** the alert email shows "Staff: John Smith, Child: Jane Doe"

---

### User Story 2 - Understand Environmental Context (Priority: P2)

As a school administrator reviewing an incident alert, I need to know how many people were present (total, adults, children) so I can assess whether supervision ratios were met and understand the incident context.

**Why this priority**: Supervision ratio violations are regulatory compliance issues. Context helps determine if the incident was due to understaffing.

**Independent Test**: Can be fully tested by creating a scene with known occupancy (2 adults, 5 children), triggering an alert, and verifying the context shows correct counts.

**Acceptance Scenarios**:

1. **Given** a classroom with 2 adults and 8 children,
   **When** a distress alert is triggered,
   **Then** the alert context shows:
   - occupancy_count: 10
   - adults_present: 2
   - children_present: 8

2. **Given** a supervision violation (no adults present),
   **When** the alert is triggered,
   **Then** the alert context shows adults_present: 0
   **And** the alert severity is escalated to "critical"

---

### User Story 3 - Primary Subject Identification (Priority: P1)

As a school administrator, when multiple people are in the frame during an incident, I need the system to identify the PRIMARY subject (the child crying, the person involved in violence) so I know who needs immediate attention.

**Why this priority**: In chaotic scenes with multiple children, knowing which specific child needs help is critical for effective response.

**Independent Test**: Can be tested by creating a scene with 3 children, where only 1 is crying. Verify the crying child is marked as primary subject.

**Acceptance Scenarios**:

1. **Given** 3 children in frame, where 1 child (Jane Doe) is crying,
   **When** the distress alert is created,
   **Then** Jane Doe has `is_primary_subject: true`
   **And** the other 2 children have `is_primary_subject: false`

2. **Given** a violence incident with 2 children pushing each other,
   **When** the alert is created,
   **Then** the child closest to the motion center is marked as primary subject

3. **Given** a supervision violation with no adults,
   **When** the alert is created,
   **Then** the first detected child is marked as primary subject (arbitrary choice acceptable)

---

### User Story 4 - Email Notifications with Person Images (Priority: P2)

As a school administrator, when I receive an email alert, I need to see the person's photo inline so I can immediately recognize who is involved without logging into the system.

**Why this priority**: Email is the primary notification channel. Inline images enable instant recognition and faster response.

**Independent Test**: Can be tested by triggering an alert and verifying the email contains embedded person images and names in the subject line.

**Acceptance Scenarios**:

1. **Given** a distress alert for "Jane Doe",
   **When** the email notification is sent,
   **Then** the email subject is: "🚨 DISTRESS Alert - Jane Doe"
   **And** the email body contains an embedded image of Jane's face
   **And** the image is labeled "⚠️ Primary Subject"

2. **Given** multiple persons in an alert,
   **When** the email is sent,
   **Then** the primary subject's image is shown first with red border
   **And** other persons are listed below with smaller images

3. **Given** an unknown person in the alert,
   **When** the email is sent,
   **Then** the subject says "Unknown Person" 
   **And** the face image is included with a note: "Not enrolled - verify identity"

---

### Edge Cases

1. **No face visible** - Person detected by body but face not visible
   - **Expected**: Include person with name "Unknown" and no face image
   - **Test**: Cover a child's face, trigger alert, verify graceful handling

2. **Low confidence face match** - Face recognition confidence < 0.6
   - **Expected**: Include person with possible match name + confidence score
   - **Test**: Use poor quality face image, verify alert shows "Possible match: Jane Doe (55%)"

3. **Multiple faces in same person bbox** - Two children very close together
   - **Expected**: System picks the dominant face or creates 2 person records
   - **Test**: Have 2 children hugging, trigger alert, verify both are detected

4. **Person exits frame before alert created** - Face detected but person leaves
   - **Expected**: Alert still includes last known face image
   - **Test**: Person walks out of frame, verify alert contains their info from last detection

5. **Database connection failure** - Cannot fetch person details
   - **Expected**: Alert created with person_id only, name shown as "Person {ID}"
   - **Test**: Simulate DB failure, verify alert still created with degraded info

---

## Data Model

### Updated Alert Schema

```typescript
interface Alert {
  alert_id: string;
  type: 'violence' | 'distress' | 'supervision' | 'body_language';
  confidence: number;
  timestamp: string;
  camera_id: string;
  zone?: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  
  // NEW: Person identification
  persons_involved: PersonInAlert[];
  
  // NEW: Context
  context: AlertContext;
}

interface PersonInAlert {
  person_id: string;
  name: string;
  role: 'child' | 'staff' | 'visitor' | 'unknown';
  confidence: number;              // Face recognition confidence
  image_url: string;               // Face crop from frame
  bbox: [number, number, number, number];
  is_primary_subject: boolean;
}

interface AlertContext {
  detection_method: 'fast_path' | 'vlm_validation' | 'hybrid';
  detector_scores: {
    violence?: number;
    distress?: number;
    supervision?: number;
    body_language?: number;
  };
  vlm_analysis?: string;
  environment: {
    time_of_day: 'morning' | 'afternoon' | 'evening' | 'night';
    occupancy_count: number;
    adults_present: number;
    children_present: number;
  };
}
```

### Database Migration

```sql
-- File: edge/postgres/migrations/006_enhanced_alerts.sql

ALTER TABLE alerts 
  ADD COLUMN persons_involved JSONB,
  ADD COLUMN context JSONB;

CREATE INDEX idx_alerts_persons ON alerts USING GIN (persons_involved);
CREATE INDEX idx_alerts_context ON alerts USING GIN (context);

-- Add storage for person face images
CREATE TABLE alert_person_images (
  image_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_id UUID REFERENCES alerts(alert_id) ON DELETE CASCADE,
  person_id VARCHAR(255),
  image_data BYTEA NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alert_person_images_alert ON alert_person_images(alert_id);
```

---

## Technical Architecture

### Component Changes

**1. VLM Service (`services/nura-vlm/src/hybrid_router.py`)**
- ✅ Already has person tracking
- ✅ Already has face identification
- ⚠️ Need to add: Person detail lookup from database
- ⚠️ Need to add: Primary subject determination logic
- ⚠️ Need to add: Environment context calculation

**2. Alert Service (`services/nura-alerts/src/services/alert.service.ts`)**
- ✅ Already creates alerts
- ⚠️ Need to add: Save person face images to storage
- ⚠️ Need to add: Build persons_involved array
- ⚠️ Need to add: Build context object

**3. Notification Service (`services/nura-alerts/src/services/notification.service.ts`)**
- ✅ Already sends email alerts
- ⚠️ Need to update: Email template with person images
- ⚠️ Need to update: Email subject with primary person name
- ⚠️ Need to update: Attach face images as inline attachments

### API Changes

**VLM Service Response (Enhanced)**
```python
# POST /analyze/hybrid
{
  "detections": {...},
  "decision": "ALERT",
  "confidence": 0.84,
  
  # NEW
  "persons_detected": [
    {
      "track_id": 1,
      "person_id": "uuid-jane",
      "name": "Jane Doe",
      "role": "child",
      "confidence": 0.92,
      "bbox": [100, 50, 200, 300],
      "face_image": "base64...",
      "is_primary_subject": true
    }
  ],
  
  # NEW
  "analysis_context": {
    "detection_method": "hybrid",
    "detector_scores": {...},
    "vlm_analysis": "Child appears to be crying...",
    "environment": {
      "occupancy_count": 5,
      "adults_present": 1,
      "children_present": 4
    }
  }
}
```

---

## Implementation Tasks

### Task 1: Update VLM Service (3 days)

**Files to modify:**
- `services/nura-vlm/src/hybrid_router.py`
- `services/nura-vlm/src/models.py`

**Sub-tasks:**
1. Add database connection pool for person lookups (4 hours)
2. Implement `_get_person_details()` method (2 hours)
3. Implement `_determine_primary_subject()` logic (4 hours)
4. Implement `_calculate_environment_context()` (2 hours)
5. Update `analyze_frame_hybrid()` to include new fields (4 hours)
6. Add unit tests (4 hours)

**Acceptance Criteria:**
- [ ] VLM response includes `persons_detected` array
- [ ] Each person has name, role, face_image
- [ ] Primary subject correctly identified in test scenarios
- [ ] Environment context shows correct counts
- [ ] All unit tests pass

### Task 2: Update Alert Service (2 days)

**Files to modify:**
- `services/nura-alerts/src/models/alert.model.ts`
- `services/nura-alerts/src/services/alert.service.ts`
- `services/nura-alerts/src/controllers/alert.controller.ts`

**Sub-tasks:**
1. Update Alert model with new fields (2 hours)
2. Create database migration (2 hours)
3. Implement `savePersonImage()` method (3 hours)
4. Update `createAlert()` to build persons_involved (4 hours)
5. Add API endpoint to serve person images (2 hours)
6. Add integration tests (3 hours)

**Acceptance Criteria:**
- [ ] Alert model includes persons_involved and context
- [ ] Database migration applied successfully
- [ ] Person face images saved to disk
- [ ] GET `/api/alerts/{id}/persons/{filename}` works
- [ ] Integration tests pass

### Task 3: Update Email Notifications (2 days)

**Files to modify:**
- `services/nura-alerts/src/services/notification.service.ts`
- `services/nura-alerts/src/templates/alert-email.html`

**Sub-tasks:**
1. Update email template HTML (4 hours)
2. Add inline image attachments (3 hours)
3. Update email subject with person name (1 hour)
4. Add fallback for unknown persons (2 hours)
5. Test email rendering in multiple clients (4 hours)
6. Add email tests (2 hours)

**Acceptance Criteria:**
- [ ] Email subject includes primary person name
- [ ] Person face images embedded inline
- [ ] Primary subject highlighted with red border
- [ ] Email renders correctly in Gmail, Outlook
- [ ] Email tests pass

---

## Testing Strategy

### Unit Tests

**VLM Service:**
```python
# tests/test_hybrid_router.py

def test_person_identification():
    """Test person details fetched from DB"""
    # Given: enrolled person in frame
    # When: analyze_frame_hybrid called
    # Then: person name and role included

def test_primary_subject_distress():
    """Test crying child marked as primary"""
    # Given: 3 children, 1 crying
    # When: distress detected
    # Then: crying child is_primary_subject=true

def test_environment_context():
    """Test environment counts calculated"""
    # Given: 2 adults, 5 children
    # When: context calculated
    # Then: adults_present=2, children_present=5
```

**Alert Service:**
```typescript
// tests/alert.service.spec.ts

describe('Alert Service', () => {
  it('should save person face images', async () => {
    // Given: alert with person face_image
    // When: createAlert called
    // Then: image saved to disk
  });
  
  it('should build persons_involved array', async () => {
    // Given: VLM response with persons
    // When: createAlert called
    // Then: persons_involved populated
  });
});
```

### Integration Tests

```bash
# tests/integration/test_enhanced_alerts.sh

# Test 1: End-to-end with enrolled person
./demo.sh crying  # Uses Jane Doe enrolled image
# Verify:
# - Alert contains name "Jane Doe"
# - Face image URL present
# - Email subject has name

# Test 2: Unknown person
./demo.sh unknown_person.jpg
# Verify:
# - Alert created with name "Unknown"
# - Face image still captured
# - Email has warning about unknown

# Test 3: Multiple persons
./demo.sh classroom_violence.mp4
# Verify:
# - Multiple persons in alert
# - Primary subject identified
# - All persons in email
```

### Manual Testing Checklist

- [ ] Trigger distress alert with enrolled child - verify name appears
- [ ] Trigger alert with unknown person - verify "Unknown" shown
- [ ] Trigger alert with multiple people - verify all listed
- [ ] Check email - verify images embedded correctly
- [ ] Test low confidence match - verify "Possible match" shown
- [ ] Test no face visible - verify graceful degradation
- [ ] Test database offline - verify alert still created

---

## Deployment Plan

### Pre-deployment Checklist

- [ ] Database migration tested in staging
- [ ] VLM service updated and tested
- [ ] Alert service updated and tested
- [ ] Email template tested in multiple clients
- [ ] Storage directory created (`/data/alerts/persons/`)
- [ ] Environment variables configured
- [ ] All tests passing (unit + integration)

### Deployment Steps

1. **Database migration** (5 minutes)
   ```bash
   psql -U nura -d nura_db -f edge/postgres/migrations/006_enhanced_alerts.sql
   ```

2. **Create storage directories** (1 minute)
   ```bash
   mkdir -p /data/alerts/persons
   chown nura:nura /data/alerts/persons
   chmod 755 /data/alerts/persons
   ```

3. **Deploy VLM service** (2 minutes)
   ```bash
   docker compose restart nura-vlm
   # Or for native:
   ./runner/stop_services.sh vlm
   ./runner/run_vlm_service.sh
   ```

4. **Deploy alert service** (2 minutes)
   ```bash
   docker compose restart nura-alerts
   ```

5. **Smoke test** (5 minutes)
   ```bash
   ./demo.sh crying
   # Verify alert has person name
   # Check email inbox
   ```

### Rollback Plan

If issues occur:
```bash
# 1. Revert services
docker compose down
git checkout main
docker compose up -d

# 2. Rollback database (if needed)
psql -U nura -d nura_db -c "
  ALTER TABLE alerts DROP COLUMN persons_involved;
  ALTER TABLE alerts DROP COLUMN context;
"
```

---

## Success Metrics

### Functional Metrics
- [ ] 90%+ of alerts include person names (when face visible)
- [ ] Primary subject correctly identified in 85%+ of multi-person scenes
- [ ] Email open rate increases (more actionable with names)
- [ ] Time to identify child in alert reduces from 30s → 5s

### Technical Metrics
- [ ] Alert creation latency remains <2s
- [ ] Face image storage <100KB per image
- [ ] Database query time <50ms for person lookup
- [ ] Email delivery time <5s

### User Feedback
- [ ] Staff report faster incident response
- [ ] Administrators find emails more actionable
- [ ] Zero complaints about wrong person identification

---

## Documentation Updates

- [ ] Update API documentation with new alert schema
- [ ] Update admin guide with person identification explanation
- [ ] Create troubleshooting guide for missing person names
- [ ] Update email notification samples in user docs

---

## Dependencies & Risks

### Dependencies
- ✅ Person tracking working (YOLOv8 + ByteTrack)
- ✅ Face recognition working (InsightFace 95%+)
- ✅ Enrollment database populated with staff/children
- ⚠️ Storage space for person images (~100KB × 100 alerts/day = 10MB/day)

### Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Face not visible | No person name in alert | Medium | Show "Unknown" gracefully |
| Low recognition confidence | Wrong person identified | Low | Show confidence score, allow corrections |
| Database query slow | Alert latency increase | Low | Add caching, optimize queries |
| Storage fills up | Cannot save images | Low | Add cleanup policy, monitor disk |
| Email images too large | Email blocked | Low | Resize images to max 50KB |

---

**Sprint Duration:** 1 week (5 working days)  
**Team Size:** 1-2 backend engineers  
**Status:** ✅ Ready to implement  
**Next:** Week 2 - Video Evidence Clips
