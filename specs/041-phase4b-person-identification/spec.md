# Phase 4B: Person Identification & Multi-Camera Tracking

**Date:** 2026-11-06  
**Status:** 📋 Planning  
**Dependencies:** Phase 4 (Person Tracking with ByteTrack)

---

## Executive Summary

Phase 4B extends the person tracking system with **person identification** and **multi-camera handoff**, enabling the system to:

1. **Link tracked persons to real identities** (e.g., "Person 1" → "Adam W.")
2. **Track individuals across multiple cameras** (camera handoff)
3. **Enable name-based search and alerting** (e.g., "Where is Noah M?", "Alert: Adam W. and Sarah K. involved in violence")
4. **Maintain persistent identity across occlusions, re-entries, and camera switches**

---

## Problem Statement

### Current State (Phase 4)
- ✅ ByteTrack assigns **session IDs** (1, 2, 3...) within a single camera feed
- ✅ IDs are consistent across frames (same person keeps same ID)
- ⚠️ IDs are **anonymous** - no link to real identities
- ⚠️ IDs are **per-camera** - same child gets different IDs on different cameras
- ⚠️ IDs are **session-based** - restart → IDs reset

### Desired State (Phase 4B)
- ✅ System knows "Person ID 5" is "Adam W." from the school database
- ✅ Alert says: **"Violence detected: Adam W. pushed Noah M."** (not "Person 1 pushed Person 2")
- ✅ Search: **"Where is Adam W?"** → "Camera 3, Zone A, last seen 2 minutes ago"
- ✅ Track Adam across cameras: Camera 1 (9:00 AM) → Camera 2 (9:15 AM) → Camera 3 (9:30 AM)
- ✅ Persistent identity: Adam is recognized even after leaving and re-entering

---

## Use Cases

### UC1: Alert with Named Persons
**Actor:** Safety Monitor  
**Trigger:** Violence detected  
**Flow:**
1. System detects violence between two tracked persons (IDs 3 and 7)
2. System identifies ID 3 = "Adam W.", ID 7 = "Noah M."
3. Alert displays: **"Violence: Adam W. (aggressor) pushed Noah M. (victim)"**
4. Monitor can quickly identify children involved

**Benefit:** Faster response, clear communication with parents/staff

---

### UC2: Search by Name
**Actor:** Teacher  
**Trigger:** "Where is Adam W.?"  
**Flow:**
1. Teacher searches for "Adam W." in the app
2. System looks up Adam's current person ID(s) across all cameras
3. Returns: **"Camera 3, Zone A, last seen 2 minutes ago"** + live thumbnail
4. If not currently visible: **"Last seen: Camera 1, 15 minutes ago"**

**Benefit:** Quick child location, lost child recovery

---

### UC3: Multi-Camera Tracking
**Actor:** System  
**Trigger:** Adam W. walks from one camera zone to another  
**Flow:**
1. Adam tracked as ID 5 on Camera 1
2. Adam enters Camera 2's view (new environment, would get new ID 12)
3. System recognizes Adam via face/appearance and **merges IDs** (5 → 12 are same person)
4. Timeline shows: **"Adam W.: Camera 1 (9:00-9:15) → Camera 2 (9:15-9:30)"**

**Benefit:** Complete movement history, pattern analysis

---

### UC4: Persistent Re-identification
**Actor:** System  
**Trigger:** Adam leaves and re-enters camera view  
**Flow:**
1. Adam tracked as ID 5, then leaves camera FOV
2. 10 minutes later, Adam re-enters (ByteTrack would assign new ID 18)
3. System recognizes Adam and **reuses ID 5** (or links 18 → "Adam W.")
4. Action history preserved

**Benefit:** Continuous behavior tracking, accurate incident reporting

---

## Technical Approaches

### Option 1: Face Recognition (Recommended)
**Method:** Extract face embeddings + match against enrollment database

**Pros:**
- ✅ **High accuracy** (>95% with good lighting)
- ✅ **Fast** (~20-50ms per face)
- ✅ **Non-intrusive** (no wearables)
- ✅ **Proven tech** (libraries: dlib, face_recognition, DeepFace, ArcFace)
- ✅ **Works across cameras** (face is consistent across views)

**Cons:**
- ⚠️ **Privacy concerns** (face biometrics)
- ⚠️ **Lighting sensitive** (shadows, backlighting)
- ⚠️ **Angle sensitive** (profile views harder)
- ⚠️ **Requires enrollment** (initial face capture)

**Implementation:**
```python
# 1. Enrollment (one-time per child)
enrollment_db = {
    "adam_w": face_embedding_vector_128d,
    "noah_m": face_embedding_vector_128d,
    ...
}

# 2. Per-frame identification
for track in person_tracks:
    face_roi = extract_face(frame, track['bbox'])
    if face_roi:
        embedding = face_encoder.encode(face_roi)  # 128D vector
        
        # Compare with enrolled faces
        best_match, distance = find_closest(embedding, enrollment_db)
        
        if distance < threshold:  # e.g., 0.6
            track['identity'] = best_match  # "adam_w"
            track['confidence'] = 1.0 - distance
```

**Libraries:**
- **face_recognition** (dlib-based, easy to use)
- **DeepFace** (supports ArcFace, FaceNet, VGG-Face)
- **InsightFace** (ArcFace, state-of-the-art)

---

### Option 2: Appearance-Based Re-ID (ReID)
**Method:** Extract appearance embeddings from full body + clothing

**Pros:**
- ✅ **Less privacy-sensitive** (no face biometrics)
- ✅ **Works from any angle** (back, side views)
- ✅ **Good for camera handoff** (recognizes same clothing across cameras)

**Cons:**
- ⚠️ **Lower accuracy than face** (~70-85%)
- ⚠️ **Clothing changes break identity** (jacket on/off, uniform changes)
- ⚠️ **Requires more computation** (~50-100ms per person)

**Implementation:**
```python
# Extract appearance embedding (512D vector)
person_roi = frame[y1:y2, x1:x2]
appearance_embedding = reid_model.extract_features(person_roi)

# Compare with recent sightings (sliding window)
best_match = find_closest(appearance_embedding, recent_embeddings)

if similarity > threshold:
    track['global_id'] = best_match['global_id']
```

**Models:**
- **OSNet** (lightweight, ~50ms)
- **FastReID** (PyTorch library)
- **TransReID** (Transformer-based, SOTA)

---

### Option 3: Hybrid (Face + Appearance + Motion)
**Method:** Combine multiple signals for robust identification

**Approach:**
```python
confidence_scores = {
    'face': face_match_confidence,      # 0.95 if face visible
    'appearance': appearance_similarity, # 0.75
    'motion': motion_pattern_match,     # 0.60 (gait, typical paths)
    'temporal': last_seen_timestamp     # Recent sighting boosts confidence
}

# Weighted fusion
final_confidence = (
    0.6 * face +
    0.3 * appearance +
    0.1 * motion
)

if final_confidence > threshold:
    assign_identity(track, identity_candidate)
```

**Best for:**
- Challenging lighting (appearance helps when face unclear)
- Partial occlusions
- Camera handoff (appearance + motion for transition zones)

---

### Option 4: RFID/Wearables (Not Recommended)
**Method:** Children wear RFID tags, BLE beacons, or smart badges

**Pros:**
- ✅ **100% accurate** (direct identity link)
- ✅ **No computer vision needed**

**Cons:**
- ❌ **Requires wearables** (lost/swapped tags)
- ❌ **Kids can swap tags** (defeats purpose)
- ❌ **Not scalable** (battery management, cost)
- ❌ **Invasive** (tracking concerns)

**Verdict:** Not suitable for childcare

---

## Recommended Architecture

### Phase 4B: Hybrid Face + Appearance + Motion

```
┌─────────────────────────────────────────────────────────────────┐
│                      Phase 4B Architecture                      │
└─────────────────────────────────────────────────────────────────┘

1. PER-CAMERA TRACKING (existing Phase 4)
   ┌──────────────────────────────────────────┐
   │  Camera 1                                │
   │  ┌────────────────────────────────────┐  │
   │  │  ByteTracker                       │  │
   │  │  - Assigns local IDs (1, 2, 3...)  │  │
   │  │  - Tracks across frames            │  │
   │  └────────────────────────────────────┘  │
   └──────────────────────────────────────────┘

2. PERSON IDENTIFICATION (NEW)
   ┌──────────────────────────────────────────┐
   │  FaceIdentifier                          │
   │  ┌────────────────────────────────────┐  │
   │  │  Extract face ROI from bbox        │  │
   │  │  Face detection (YOLO/MTCNN)       │  │
   │  │  Face embedding (ArcFace/FaceNet)  │  │
   │  │  Match vs enrollment DB            │  │
   │  │  Confidence scoring                │  │
   │  └────────────────────────────────────┘  │
   └──────────────────────────────────────────┘

3. RE-IDENTIFICATION (NEW)
   ┌──────────────────────────────────────────┐
   │  AppearanceReID                          │
   │  ┌────────────────────────────────────┐  │
   │  │  Extract person ROI                │  │
   │  │  Appearance embedding (OSNet)      │  │
   │  │  Compare with recent sightings     │  │
   │  │  Temporal voting (consistency)     │  │
   │  └────────────────────────────────────┘  │
   └──────────────────────────────────────────┘

4. GLOBAL IDENTITY MANAGER (NEW)
   ┌──────────────────────────────────────────┐
   │  GlobalIdentityManager                   │
   │  ┌────────────────────────────────────┐  │
   │  │  Maps: local_id → global_id        │  │
   │  │  Maps: global_id → real_name       │  │
   │  │  Cross-camera ID merging           │  │
   │  │  Identity persistence (DB)         │  │
   │  │  Confidence fusion                 │  │
   │  └────────────────────────────────────┘  │
   └──────────────────────────────────────────┘

5. MULTI-CAMERA TRACKER (NEW)
   ┌──────────────────────────────────────────┐
   │  MultiCameraTracker                      │
   │  ┌────────────────────────────────────┐  │
   │  │  Tracks movement across cameras    │  │
   │  │  Camera topology (adjacency graph) │  │
   │  │  Handoff detection (exit/entry)    │  │
   │  │  Timeline reconstruction           │  │
   │  └────────────────────────────────────┘  │
   └──────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 4B.1: Face Enrollment & Identification (Week 1)

**Components:**
1. **Enrollment System**
   - UI for capturing child faces (multiple angles)
   - Face quality validation (frontal, good lighting)
   - Store embeddings in DB (PostgreSQL or Qdrant)

2. **FaceIdentifier Class**
   ```python
   class FaceIdentifier:
       def __init__(self, enrollment_db_path):
           self.face_detector = YOLO('yolov8n-face.pt')
           self.face_encoder = load_face_encoder()  # ArcFace/FaceNet
           self.enrollment_db = load_enrollment_db()
       
       def identify(self, frame, bbox):
           # Crop person ROI
           person_roi = crop_bbox(frame, bbox)
           
           # Detect face within person ROI
           faces = self.face_detector(person_roi)
           if not faces:
               return None
           
           # Extract face embedding
           face_roi = extract_largest_face(faces)
           embedding = self.face_encoder.encode(face_roi)
           
           # Match against enrollment DB
           best_match, distance = self.enrollment_db.find_closest(embedding)
           
           if distance < 0.6:  # Threshold
               return {
                   'identity': best_match['name'],  # "adam_w"
                   'confidence': 1.0 - distance,
                   'method': 'face'
               }
           return None
   ```

3. **Integration with PersonTracker**
   ```python
   # In hybrid_router.py
   if self.face_identifier:
       for track in person_tracks:
           identity = self.face_identifier.identify(frame, track['bbox'])
           if identity:
               track['identity'] = identity['identity']
               track['identity_confidence'] = identity['confidence']
               
               # Update global identity map
               self.global_identity_manager.update(
                   local_id=track['id'],
                   camera_id=camera_id,
                   global_identity=identity['identity']
               )
   ```

**Deliverables:**
- Face enrollment UI (simple web form)
- Face database schema
- FaceIdentifier implementation
- Integration tests

---

### Phase 4B.2: Appearance-Based Re-ID (Week 2)

**Components:**
1. **AppearanceReID Model**
   - Use OSNet (lightweight, fast)
   - Extract 512D appearance embeddings
   - Maintain sliding window of recent sightings (last 5 minutes)

2. **ReID Matching**
   ```python
   class AppearanceReID:
       def __init__(self):
           self.reid_model = OSNet()
           self.recent_sightings = {}  # global_id -> {embedding, timestamp}
       
       def identify(self, frame, bbox):
           person_roi = crop_bbox(frame, bbox)
           embedding = self.reid_model.extract_features(person_roi)
           
           # Compare with recent sightings
           best_match = None
           best_similarity = 0
           
           for global_id, data in self.recent_sightings.items():
               similarity = cosine_similarity(embedding, data['embedding'])
               if similarity > best_similarity:
                   best_similarity = similarity
                   best_match = global_id
           
           if best_similarity > 0.7:
               return {
                   'identity': best_match,
                   'confidence': best_similarity,
                   'method': 'appearance'
               }
           return None
   ```

3. **Temporal Voting**
   - Track identity consistency over last N frames
   - Boost confidence if same identity confirmed repeatedly

**Deliverables:**
- OSNet model integration
- ReID matcher implementation
- Temporal voting logic

---

### Phase 4B.3: Global Identity Manager (Week 3)

**Components:**
1. **Database Schema**
   ```sql
   -- Enrollment database
   CREATE TABLE enrolled_persons (
       id SERIAL PRIMARY KEY,
       name VARCHAR(100) UNIQUE NOT NULL,
       face_embedding VECTOR(128),  -- ArcFace embedding
       metadata JSONB,              -- Age, class, photo_url
       enrolled_at TIMESTAMP DEFAULT NOW()
   );
   
   -- Active tracking
   CREATE TABLE person_sightings (
       id SERIAL PRIMARY KEY,
       global_id VARCHAR(50),       -- "adam_w"
       camera_id VARCHAR(50),
       local_track_id INT,          -- ByteTrack ID
       timestamp TIMESTAMP,
       bbox JSONB,                  -- [x1, y1, x2, y2]
       identity_confidence FLOAT,
       identification_method VARCHAR(20)  -- 'face', 'appearance', 'fusion'
   );
   
   -- Camera topology
   CREATE TABLE camera_adjacency (
       camera_a VARCHAR(50),
       camera_b VARCHAR(50),
       transition_zone JSONB,       -- Overlap area coordinates
       avg_transition_time_sec INT  -- Typical time to cross
   );
   ```

2. **GlobalIdentityManager**
   ```python
   class GlobalIdentityManager:
       def __init__(self, db_connection):
           self.db = db_connection
           self.local_to_global = {}  # {(camera_id, local_id): global_id}
       
       def update(self, camera_id, local_id, global_identity, confidence, method):
           # Map local ID to global identity
           key = (camera_id, local_id)
           self.local_to_global[key] = global_identity
           
           # Record sighting
           self.db.execute("""
               INSERT INTO person_sightings
               (global_id, camera_id, local_track_id, timestamp, identity_confidence, identification_method)
               VALUES (%s, %s, %s, NOW(), %s, %s)
           """, (global_identity, camera_id, local_id, confidence, method))
       
       def get_identity(self, camera_id, local_id):
           key = (camera_id, local_id)
           return self.local_to_global.get(key)
       
       def search_by_name(self, name):
           # Find current location of person
           result = self.db.execute("""
               SELECT camera_id, timestamp, bbox
               FROM person_sightings
               WHERE global_id = %s
               ORDER BY timestamp DESC
               LIMIT 1
           """, (name,))
           return result
   ```

**Deliverables:**
- Database schema + migrations
- GlobalIdentityManager implementation
- Search API endpoints

---

### Phase 4B.4: Multi-Camera Handoff (Week 4)

**Components:**
1. **Camera Topology**
   - Define camera adjacency graph
   - Mark overlap zones (areas visible to multiple cameras)
   - Estimate typical transition times

2. **Handoff Detector**
   ```python
   class MultiCameraTracker:
       def __init__(self, camera_topology):
           self.topology = camera_topology
           self.pending_exits = {}  # Track people exiting camera FOV
       
       def detect_handoff(self, camera_id, person_tracks):
           # Check for people exiting this camera
           for track in person_tracks:
               if self._is_exiting(track, camera_id):
                   global_id = self.global_identity_manager.get_identity(
                       camera_id, track['id']
                   )
                   
                   # Register pending exit
                   self.pending_exits[global_id] = {
                       'exit_camera': camera_id,
                       'timestamp': time.time(),
                       'exit_direction': self._estimate_exit_direction(track),
                       'appearance_embedding': track['appearance_embedding']
                   }
           
           # Check for people entering from adjacent cameras
           for track in person_tracks:
               if self._is_entering(track, camera_id):
                   # Look for recent exits from adjacent cameras
                   adjacent_cameras = self.topology.get_adjacent(camera_id)
                   
                   for exit_data in self.pending_exits.values():
                       if (exit_data['exit_camera'] in adjacent_cameras and
                           time.time() - exit_data['timestamp'] < 30):  # 30s window
                           
                           # Compare appearance
                           similarity = cosine_similarity(
                               track['appearance_embedding'],
                               exit_data['appearance_embedding']
                           )
                           
                           if similarity > 0.8:
                               # Handoff detected!
                               self._merge_identities(exit_data, track, camera_id)
   ```

3. **Movement Timeline**
   - Track complete movement history across cameras
   - Visualize paths: "Adam W.: Playground (9:00) → Hallway (9:15) → Classroom (9:20)"

**Deliverables:**
- Camera topology configuration
- Handoff detection logic
- Movement timeline API

---

## Privacy & Security Considerations

### 1. Face Biometrics
- ⚠️ **Highly sensitive** - face embeddings are biometric data
- ✅ **Store embeddings, not images** (embeddings can't reconstruct faces)
- ✅ **Encrypt DB** at rest
- ✅ **Access control** - only authorized staff
- ✅ **Parental consent** required
- ✅ **Data retention policy** (delete after child leaves school)

### 2. GDPR/COPPA Compliance
- **GDPR (Europe):** Biometric data = "special category" → explicit consent required
- **COPPA (US):** Children <13 → parental consent required
- **Solution:**
  - Enrollment requires parent signature
  - Opt-out option (use appearance-only, lower accuracy)
  - Data deletion on request

### 3. Data Minimization
- Only store **essential data** (embeddings, name, enrollment date)
- **Don't store:** raw images, full video, unrelated metadata
- **Auto-delete:** sightings older than 90 days

---

## Performance Targets

| Component | Target Latency | Notes |
|-----------|---------------|-------|
| **Face Detection** | <20ms | YOLO-Face (GPU) or MTCNN (CPU) |
| **Face Encoding** | <30ms | ArcFace/FaceNet |
| **Face Matching** | <10ms | Cosine similarity (100 enrolled) |
| **Appearance ReID** | <50ms | OSNet inference |
| **Total Overhead** | <100ms | Per-person, per-frame |
| **Multi-Camera Handoff** | <2s | Detection latency for camera transitions |

**Scalability:**
- 100 enrolled children
- 10 cameras
- 5-10 people per camera simultaneously
- **Total:** ~500-1000 identifications/sec (achievable on GPU)

---

## Alternative Creative Ideas

### Idea 1: Voice Identification
- Use speech recognition to identify children by voice
- **Pros:** Non-visual, works in audio-only zones
- **Cons:** Noisy environment, overlapping speech, privacy concerns

### Idea 2: Gait Analysis
- Identify children by walking pattern
- **Pros:** Works from any angle, no face needed
- **Cons:** Lower accuracy (~60-70%), requires long observation

### Idea 3: Clothing Color Tracking (Short-Term)
- Track by dominant clothing colors (temporary identity)
- **Pros:** Simple, privacy-friendly
- **Cons:** Breaks when children wear same colors, clothing changes

### Idea 4: QR Code Badges (Hybrid)
- Children wear QR code badges (like name tags)
- Camera reads QR code for instant ID
- **Pros:** 100% accurate, cheap
- **Cons:** Requires visible badge, kids can swap

---

## Recommended Approach: **Hybrid Face + Appearance**

### Why?
1. **Face recognition** for high-confidence ID when face is visible (95%+ accuracy)
2. **Appearance ReID** for fallback when face is obscured/angled (70-85% accuracy)
3. **Temporal voting** to boost confidence over time
4. **Multi-camera handoff** for complete movement tracking

### Phased Rollout:
- **Phase 4B.1:** Face enrollment + identification (2 weeks)
- **Phase 4B.2:** Appearance ReID (1 week)
- **Phase 4B.3:** Global identity manager + database (1 week)
- **Phase 4B.4:** Multi-camera handoff (1 week)
- **Total:** ~5-6 weeks

---

## Success Criteria

### Functional:
- ✅ 90%+ face recognition accuracy (enrolled children, good lighting)
- ✅ 70%+ appearance ReID accuracy (fallback)
- ✅ <2s camera handoff detection
- ✅ Name-based search: "Where is Adam?" → camera + location
- ✅ Named alerts: "Violence: Adam W. pushed Noah M."

### Performance:
- ✅ <100ms total overhead per person per frame
- ✅ Support 100 enrolled children
- ✅ Support 10 cameras simultaneously

### Privacy:
- ✅ Parental consent for face enrollment
- ✅ Encrypted biometric storage
- ✅ Data deletion on request

---

## Next Steps

1. **Review & approve** this specification
2. **Setup enrollment database** (PostgreSQL + pgvector)
3. **Choose face recognition library** (InsightFace recommended)
4. **Build enrollment UI** (web-based, 3-5 photos per child)
5. **Implement FaceIdentifier** (2-3 days)
6. **Integration testing** with hybrid router

**Ready to proceed with Phase 4B.1?**
