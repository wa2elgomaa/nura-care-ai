# Feature Specification: Week 5 - Behavioral Analytics

**Feature Branch**: `054-week5-behavioral-analytics`
**Created**: 2026-11-08
**Sprint**: Week 5 of 8

## Overview
Track all persons, auto-create "Unknown Person N" for unidentified individuals, analyze activities, generate daily reports.

## User Stories

### Story 1 - Unknown Person Auto-Creation (P1)
When unknown face detected, auto-create "Unknown Person N" record for later linking.

**Acceptance**:
- Unknown faces get persistent ID
- Face encoding stored
- Can track same unknown across cameras
- Admin can manually link to real person later

### Story 2 - Activity Classification (P1)
Detect and track activities (playing, eating, crying, sitting, running, etc.)

**Acceptance**:
- 11 activity classes (from ToddlerActions)
- 80%+ classification accuracy
- Activities stored per person

### Story 3 - Daily Behavior Reports (P2)
Generate daily summary per person: time in each zone, activities, interactions.

**Acceptance**:
- Report shows time distribution
- Activity breakdown
- Persons interacted with
- Anomaly detection (isolated child)

## Implementation

### Task 1: Unknown Person Handler (2 days)
- Auto-create Unknown Person N
- Store face encoding
- Match future detections to same unknown
- Deduplication logic

### Task 2: Activity Classifier Training (3 days)
- Train MobileNetV3 on ToddlerActions (11 classes)
- Target: 80%+ accuracy
- Deploy to packages/nura-detectors

### Task 3: Behavior Analysis Service (2 days)
- New service: nura-analytics
- Consume person_detections events
- Aggregate daily statistics
- Generate reports

### Task 4: Manual Linking UI Endpoint (1 day)
- GET /admin/unknown-persons
- POST /api/persons/unknown/{id}/link
- Link unknown to existing or new person

## Testing
```bash
# Test unknown auto-creation
./demo.sh unknown_child.jpg
# Check database for "Unknown Person 1"

# Test activity classification
./demo.sh playing_video.mp4
# Verify activity: "playing"

# Test daily report
curl "/api/analytics/reports/daily?person_id=uuid&date=2026-11-08"
```

## Success Metrics
- [ ] 100% unknown auto-creation
- [ ] 80%+ activity accuracy
- [ ] Daily reports for all enrolled persons
- [ ] Manual linking UI functional

**Duration:** 1 week  
**Next:** Week 6
