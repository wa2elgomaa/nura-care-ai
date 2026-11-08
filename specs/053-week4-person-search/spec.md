# Feature Specification: Week 4 - Person Search & Locate

**Feature Branch**: `053-week4-person-search`
**Created**: 2026-11-08
**Sprint**: Week 4 of 8

## Overview
Find any person across all cameras by name or photo. Shows current location and movement history.

## User Stories

### Story 1 - Search by Name (P1)
Search "Jane Doe" → Find current location in <2s

**Acceptance**:
- Returns person_id, current camera/zone, last_seen timestamp
- <2s response time
- Fuzzy matching ("jan" finds "Jane")

### Story 2 - Search by Image (P1)
Upload photo → Identify person → Show location

**Acceptance**:
- Face recognition from uploaded image
- Returns same person data as name search
- <5s response time

### Story 3 - Movement History (P2)
View where person has been in last 24 hours

**Acceptance**:
- List of camera/zone transitions
- Entry/exit timestamps
- Duration in each location

## Implementation

### Task 1: Search API (2 days)
- GET /api/persons/search?name=Jane
- POST /api/persons/search/by-image
- Fuzzy name matching (PostgreSQL SIMILARITY)

### Task 2: Real-time Location Cache (1 day)
- Redis cache for current locations
- 5-minute TTL
- Updated by stream processor

### Task 3: Movement History (1 day)
- Query person_detections table
- Aggregate by camera/zone
- Return chronological movements

### Task 4: Add Redis to Stack (0.5 day)
- Update compose.yaml
- Redis service for location cache

## Testing
```bash
# Search by name
curl "http://localhost:8001/api/persons/search?name=Jane"

# Search by image  
curl -X POST /api/persons/search/by-image -F 'photo=@face.jpg'

# Movement history
curl "/api/persons/{id}/movements?from=2026-11-08T08:00"
```

## Success Metrics
- [ ] <2s name search
- [ ] <5s image search
- [ ] 90%+ location accuracy
- [ ] Movement history 100% complete

**Duration:** 1 week  
**Next:** Week 5
