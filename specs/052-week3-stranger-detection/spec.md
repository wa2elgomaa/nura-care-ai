# Feature Specification: Week 3 - WiFi Sensing Data Source & Stranger Detection

**Feature Branch**: `052-week3-wifi-sensing-strangers`
**Created**: 2026-11-08
**Status**: Ready for Implementation
**Sprint**: Core Safety Routes - Week 3 of 8

## Overview

**CRITICAL ARCHITECTURE CHANGE:** WiFi sensing is now a PRIMARY data source (equal to cameras), not an add-on feature.

Two core implementations:
1. **WiFi Sensing Infrastructure** - RuView integration as primary occupancy/movement data source
2. **Stranger Detection** - Identify unknown persons from camera feeds + visitor management

**Vision:** System ingests data from TWO sources:
- **Camera feeds** → Person detection, face recognition, activities
- **WiFi sensing** → Occupancy, movement, presence (camera-free zones)

Both sources feed into the same alert/analysis pipeline.

---

## PART A: WiFi SENSING AS PRIMARY DATA SOURCE

### User Story 1 - WiFi Occupancy Detection (P0 - FOUNDATIONAL)

As the system, I ingest occupancy data from WiFi sensing (ESP32 + RuView) as a PRIMARY data source for all areas, especially camera-free zones like bathrooms and changing rooms.

**Why P0**: WiFi sensing covers blind spots where cameras cannot go. It's not optional - it's a core data source.

**Acceptance Scenarios**:

1. **Given** ESP32 nodes installed in 6 locations (bathrooms, storage, kitchen),
   **When** RuView processes WiFi signals,
   **Then** occupancy events published to MQTT every 5 seconds
   **And** system receives: room_id, occupancy_count, device_count, timestamp

2. **Given** bathroom with 2 ESP32 nodes,
   **When** 1 person enters,
   **Then** WiFi sensing detects occupancy_count: 1
   **And** event stored in wifi_sensing_events table

3. **Given** storage room with WiFi sensing,
   **When** 2 persons detected for 30 seconds,
   **Then** WiFi occupancy event shows occupancy_count: 2, duration: 30s

### User Story 2 - Bathroom Multi-Occupancy Alert (P0)

As a school administrator, when a bathroom has 2+ people for >2 minutes, I receive an alert to investigate potential safety concerns.

**Acceptance**:
- 2+ persons in bathroom >2min → Alert (severity: high)
- 1 person in bathroom (any duration) → No alert
- Alert includes: room name, occupancy count, duration, timestamp

### User Story 3 - After-Hours Movement Detection (P1)

As school security, when WiFi sensing detects movement in restricted areas after hours, I receive an alert.

**Acceptance**:
- Occupancy detected outside operating hours (6am-6pm) → Alert (severity: critical)
- Alert for: bathrooms, storage, kitchen, mechanical rooms
- No alert during operating hours

### User Story 4 - WiFi + Camera Data Fusion (P1)

As the system, I correlate WiFi occupancy with camera detections to provide complete situational awareness.

**Acceptance**:
- Bathroom WiFi shows 2 persons, camera at entrance shows adult + child entering → Correlated event
- WiFi shows occupancy but no camera view → WiFi-only alert
- Camera shows person but no WiFi → Camera-only detection (normal)

---

## PART B: STRANGER DETECTION

### User Story 5 - Unknown Person Alert (P1)

As school admin, when unknown person appears on camera, immediate alert with photo.

**Acceptance**:
- Unknown face detected → Alert within 30s
- Alert includes: face photo, camera location, timestamp
- Same stranger on multiple cameras (5min) → Single alert with all locations

### User Story 6 - Visitor Whitelist (P1)

As staff, I check in visitors temporarily so they don't trigger stranger alerts.

**Acceptance**:
- Visitor enrolled (valid 9am-10am) → No stranger alerts during window
- Visitor auto-expires at 10am → Future detections trigger alerts
- Manual checkout → Immediate removal from whitelist

---

## Data Model

### WiFi Sensing (Primary)

```typescript
interface WiFiSensingEvent {
  event_id: string;
  room_id: string;
  room_type: 'bathroom' | 'storage' | 'kitchen' | 'mechanical' | 'classroom';
  occupancy_count: number;
  device_count: number;
  timestamp: Date;
  duration_seconds?: number;
  esp32_nodes: string[];  // MAC addresses that detected
}

interface WiFiRoom {
  room_id: string;
  room_type: string;
  room_name: string;
  esp32_node_ids: string[];
  camera_coverage: boolean;  // True if room also has cameras
  multi_occupancy_threshold: number;  // Default 2 for bathrooms
  multi_occupancy_duration_seconds: number;  // Default 120
  operating_hours_start: string;  // "06:00"
  operating_hours_end: string;    // "18:00"
  enabled: boolean;
}

interface WiFiAlert extends Alert {
  type: 'wifi_anomaly';
  severity: 'high' | 'critical';
  data_source: 'wifi';  // Mark as WiFi-sourced
  wifi_event: {
    room_id: string;
    room_type: string;
    anomaly_type: 'multi_occupancy' | 'after_hours' | 'unauthorized_access';
    occupancy_count: number;
    duration_seconds: number;
    started_at: string;
  };
  correlation?: {
    camera_id?: string;
    persons_detected?: string[];  // If camera also saw them
  };
}
```

### Stranger Detection

```typescript
interface StrangerAlert extends Alert {
  type: 'stranger';
  data_source: 'camera';  // Mark as camera-sourced
  stranger: {
    face_image_url: string;
    locations: StrangerLocation[];
    possible_matches?: PossibleMatch[];
  };
}

interface Visitor {
  visitor_id: string;
  name: string;
  face_encoding: number[];
  valid_from: Date;
  valid_until: Date;
  purpose: string;
  approved_by: string;
}
```

---

## Architecture: Dual Data Sources

```
┌─────────────────────────────────────────────────────┐
│               DATA INGESTION LAYER                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Source 1: CAMERAS                                  │
│  ┌──────────┐                                       │
│  │ Frigate  │→ MQTT → Stream Processor              │
│  │ (NVR)    │   ↓                                   │
│  └──────────┘   Person Detection                    │
│                 Face Recognition                    │
│                 Activity Detection                  │
│                                                     │
│  Source 2: WiFi SENSING                             │
│  ┌──────────┐                                       │
│  │ RuView   │→ MQTT → WiFi Sensing Service          │
│  │ (ESP32)  │   ↓                                   │
│  └──────────┘   Occupancy Detection                 │
│                 Movement Tracking                   │
│                 Presence Analytics                  │
│                                                     │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              UNIFIED ALERT PIPELINE                 │
│                                                     │
│  Both sources publish to NATS:                      │
│  - alerts.camera                                    │
│  - alerts.wifi                                      │
│                                                     │
│  Alert Service consumes both streams                │
└─────────────────────────────────────────────────────┘
```

---

## Implementation Tasks

### Task 1: WiFi Sensing Service (2 days) - PRIMARY FOCUS

**File:** `services/nura-wifi-sensing/src/index.ts`

Core responsibilities:
- Consume RuView MQTT events (occupancy data)
- Store events in database (wifi_sensing_events table)
- Detect anomalies (multi-occupancy, after-hours)
- Publish alerts to NATS (alerts.wifi channel)
- Correlate with camera data when available

**Code:** (See full implementation in detailed spec above)

### Task 2: Stranger Detector (1.5 days)

**File:** `packages/nura-detectors/src/stranger_detector.py`

Core responsibilities:
- Detect unknown faces
- Check visitor whitelist
- Return stranger detections with confidence

### Task 3: Visitor Management API (1 day)

**File:** `services/nura-vlm/src/enrollment_api.py`

Endpoints:
- POST /api/visitors/enroll
- POST /api/visitors/{id}/checkout
- Background job to auto-expire visitors

### Task 4: RuView Integration (0.5 days)

**Update:** `compose.yaml`

Add:
- ruview service (sensing profile)
- nura-wifi-sensing service
- Configure MQTT routing

### Task 5: Dual-Source Alert Dashboard (1 day)

**Update:** Alert service to handle both sources

Mark alerts by source:
- `data_source: 'camera'` - From camera feeds
- `data_source: 'wifi'` - From WiFi sensing
- `data_source: 'hybrid'` - Correlated (both sources confirm)

---

## Database Migration

```sql
-- File: edge/postgres/migrations/008_wifi_sensing_visitors.sql

-- WiFi sensing events (PRIMARY data source)
CREATE TABLE wifi_sensing_events (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  room_id VARCHAR(100) NOT NULL,
  room_type VARCHAR(50) NOT NULL,
  occupancy_count INTEGER NOT NULL,
  device_count INTEGER NOT NULL,
  timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
  duration_seconds INTEGER,
  esp32_nodes TEXT[],  -- Array of ESP32 MAC addresses
  
  CONSTRAINT valid_room_type CHECK (room_type IN ('bathroom', 'kitchen', 'storage', 'mechanical', 'classroom'))
);

CREATE INDEX idx_wifi_events_room ON wifi_sensing_events(room_id, timestamp);
CREATE INDEX idx_wifi_events_timestamp ON wifi_sensing_events(timestamp DESC);

-- WiFi room configuration
CREATE TABLE wifi_rooms (
  room_id VARCHAR(100) PRIMARY KEY,
  room_type VARCHAR(50) NOT NULL,
  room_name VARCHAR(255) NOT NULL,
  esp32_node_ids TEXT[],
  camera_coverage BOOLEAN DEFAULT FALSE,  -- Does room also have cameras?
  multi_occupancy_threshold INTEGER DEFAULT 2,
  multi_occupancy_duration_seconds INTEGER DEFAULT 120,
  operating_hours_start TIME DEFAULT '06:00',
  operating_hours_end TIME DEFAULT '18:00',
  enabled BOOLEAN DEFAULT TRUE
);

-- Visitors table
CREATE TABLE visitors (
  visitor_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  face_encoding VECTOR(512),
  photo BYTEA,
  valid_from TIMESTAMP NOT NULL,
  valid_until TIMESTAMP NOT NULL,
  purpose TEXT,
  approved_by VARCHAR(255),
  checked_out TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Update alerts to track data source
ALTER TABLE alerts ADD COLUMN data_source VARCHAR(20);
ALTER TABLE alerts ADD CONSTRAINT valid_data_source 
  CHECK (data_source IN ('camera', 'wifi', 'hybrid'));

-- Add is_visitor to persons
ALTER TABLE persons ADD COLUMN is_visitor BOOLEAN DEFAULT FALSE;

-- Insert example WiFi rooms
INSERT INTO wifi_rooms (room_id, room_type, room_name, esp32_node_ids, camera_coverage) VALUES
  ('bathroom_boys_1f', 'bathroom', 'Boys Bathroom 1F', ARRAY['AA:BB:CC:DD:EE:01'], FALSE),
  ('bathroom_girls_1f', 'bathroom', 'Girls Bathroom 1F', ARRAY['AA:BB:CC:DD:EE:02'], FALSE),
  ('storage_main', 'storage', 'Main Storage Room', ARRAY['AA:BB:CC:DD:EE:03'], FALSE),
  ('kitchen', 'kitchen', 'Kitchen', ARRAY['AA:BB:CC:DD:EE:04'], TRUE);
```

---

## Testing

```bash
# Test WiFi Sensing (requires ESP32 nodes or simulation)
# Simulate RuView event
mosquitto_pub -t 'ruview/occupancy/bathroom_boys_1f' \
  -m '{"room_id":"bathroom_boys_1f","occupancy_count":2,"device_count":3,"timestamp":"2026-11-08T10:30:00Z"}'

# Wait 2+ minutes, check for alert
curl http://localhost:3011/api/alerts | jq '.[] | select(.type=="wifi_anomaly")'

# Test stranger detection
./demo.sh unknown_person.jpg
# Expected: Stranger alert within 30s

# Test visitor enrollment
curl -X POST /api/visitors/enroll \
  -F 'name=John Parent' \
  -F 'photo=@visitor.jpg' \
  -F 'valid_until=2026-11-08T17:00:00Z' \
  -F 'purpose=Meeting'

# Test visitor doesn't trigger stranger alert
./demo.sh visitor_john.jpg
# Expected: No stranger alert
```

---

## Success Metrics

### WiFi Sensing (Primary Data Source)
- [ ] 100% WiFi events captured from RuView
- [ ] 90%+ occupancy detection accuracy
- [ ] Bathroom multi-occupancy alerts 95%+ accuracy
- [ ] After-hours detection 100%
- [ ] <30s event-to-alert latency

### Stranger Detection
- [ ] 95%+ stranger detection rate
- [ ] <5% false positives
- [ ] Visitor whitelist 100% effective
- [ ] <30s alert time

### Data Source Coverage
- [ ] Cameras cover 80% of school
- [ ] WiFi sensing covers 20% camera-free zones
- [ ] **100% combined coverage** (cameras + WiFi)

---

## Hardware Requirements

### WiFi Sensing
- **6-10 ESP32 nodes** per school
  - 2 nodes per bathroom (boys, girls)
  - 1 node per storage room
  - 1 node in kitchen
  - 1 node in mechanical room
- **RuView server** (Docker container)
- **WiFi AP** for ESP32 connectivity

### Estimated Cost
- ESP32 nodes: $5-10 each × 10 = $50-100
- WiFi AP: $50-100
- **Total: $100-200 per school**

---

**Sprint Duration:** 1 week  
**Team:** 2 engineers (1 WiFi, 1 Stranger)  
**Dependencies:** Week 1 complete  
**Hardware:** ESP32 nodes + RuView  
**Next:** Week 4 - Person Search

---

**CRITICAL:** WiFi sensing is now a PRIMARY data source, not optional. Week 3 establishes dual-source architecture (cameras + WiFi) as foundation for complete school coverage.
