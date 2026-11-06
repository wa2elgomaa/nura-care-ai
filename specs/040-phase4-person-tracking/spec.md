# Phase 4: Person Tracking - Detailed Specification

**Created:** 2026-11-06  
**Author:** Claude + Wael  
**Status:** Design Phase

---

## Table of Contents

1. [Motivation](#motivation)
2. [Technical Design](#technical-design)
3. [Algorithm Comparison](#algorithm-comparison)
4. [Implementation Details](#implementation-details)
5. [Integration](#integration)
6. [Performance Targets](#performance-targets)
7. [Testing Strategy](#testing-strategy)

---

## Motivation

### Current Limitations

**Without person tracking:**
- ❌ Can't distinguish between multiple children
- ❌ Can't track who did what
- ❌ Can't identify aggressor vs victim
- ❌ Can't build behavior patterns per child
- ❌ Can't track children across cameras

**With person tracking:**
- ✅ Know which specific child is involved
- ✅ Track individual behavior over time
- ✅ Identify repeat offenders
- ✅ Monitor vulnerable children
- ✅ Build comprehensive incident reports

### Use Cases

**1. Violence Detection**
```
Before: "Violence detected in classroom"
After:  "Child #3 (blue shirt) pushed Child #7 (red shirt)"
```

**2. Distress Monitoring**
```
Before: "Child crying detected"
After:  "Child #5 has been crying for 3 minutes"
```

**3. Supervision**
```
Before: "No adult present"
After:  "5 children (IDs: 1,3,5,7,9) unattended for 45 seconds"
```

**4. Behavior Patterns**
```
Track: Child #3 involved in 3 aggressive incidents today
Alert: Pattern of aggression detected, intervention needed
```

---

## Technical Design

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Camera Frame Input                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Person Detection (YOLOv8)                       │
│  - Detect all persons in frame                               │
│  - Bounding boxes + confidence                               │
│  - ~50-100ms                                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          Person Tracking (ByteTrack/DeepSORT)                │
│  - Match detections to existing tracks                       │
│  - Assign/maintain person IDs                                │
│  - Handle occlusions and re-entry                            │
│  - ~10-30ms                                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            Per-Person Detection Analysis                     │
│  - Run temporal detector per person ROI                      │
│  - Track each person's action history                        │
│  - Identify interactions between people                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Enhanced VLM Validation                         │
│  - Include person IDs in prompt                              │
│  - "Verify if person #3 (blue shirt) hit person #7"         │
│  - More specific validation                                  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```python
Frame → Person Detector → Tracking → Per-Person Analysis → VLM
  ↓
Detections: [{bbox, conf}]
  ↓
Tracks: [{id, bbox, velocity, age}]
  ↓
Person Actions: {
  person_3: [violence at t=10s, walking at t=12s],
  person_7: [distress at t=10s, crying at t=11s]
}
  ↓
Enhanced Alert: "Person #3 (aggressor) hit Person #7 (victim)"
```

---

## Algorithm Comparison

### ByteTrack (Recommended)

**How it works:**
1. Get high-confidence detections (conf > 0.6)
2. Match to existing tracks using IoU
3. Get low-confidence detections (conf 0.3-0.6)
4. Try to match these too (recover occluded objects)
5. Use Kalman filter to predict motion

**Pros:**
- ✅ Very fast (~10ms overhead)
- ✅ State-of-the-art accuracy
- ✅ Simple implementation
- ✅ No appearance model needed
- ✅ Great for multi-object tracking

**Cons:**
- ⚠️ Struggles with long occlusions (>3s)
- ⚠️ May lose ID after camera switches
- ⚠️ Relies on motion prediction

**Performance:**
- MOTA: 80.3% (MOT17 dataset)
- Speed: ~30 FPS (including detection)
- Good for: Real-time childcare monitoring

---

### DeepSORT

**How it works:**
1. Get detections from YOLO
2. Extract appearance features (CNN)
3. Match using motion + appearance
4. Kalman filter for motion
5. Deep features for re-identification

**Pros:**
- ✅ Handles occlusions better
- ✅ Re-identification after disappearance
- ✅ More robust to ID switches
- ✅ Works across camera views (with training)

**Cons:**
- ❌ Slower (~30-50ms overhead for features)
- ❌ Needs appearance model
- ❌ More complex implementation
- ❌ Requires more compute

**Performance:**
- MOTA: 76.6% (MOT17)
- Speed: ~15-20 FPS (including detection + features)
- Good for: High-accuracy, offline analysis

---

### Comparison Table

| Feature | ByteTrack | DeepSORT | Winner |
|---------|-----------|----------|---------|
| **Speed** | ~10ms | ~30-50ms | ByteTrack |
| **Accuracy** | 80.3% MOTA | 76.6% MOTA | ByteTrack |
| **Occlusion Handling** | Fair (2-3s) | Good (5-10s) | DeepSORT |
| **Re-identification** | Poor | Good | DeepSORT |
| **Implementation** | Simple | Complex | ByteTrack |
| **Memory Usage** | Low | Medium | ByteTrack |
| **CPU Usage** | Low | Medium | ByteTrack |
| **GPU Needed** | No | Optional | ByteTrack |

**Recommendation for Childcare:** **ByteTrack**

**Why:**
- Children rarely occluded for >3s in classroom
- Speed is critical (10+ cameras)
- Simpler to deploy and maintain
- Better accuracy on standard benchmarks
- Lower resource usage

---

## Implementation Details

### 1. Person Detection

**Use existing YOLOv8:**
```python
from ultralytics import YOLO

class PersonDetector:
    def __init__(self):
        self.model = YOLO('yolov8n.pt')  # nano = fastest
    
    def detect(self, frame):
        # Detect only 'person' class (class_id = 0)
        results = self.model(frame, classes=[0])
        
        detections = []
        for r in results:
            for box in r.boxes:
                detections.append({
                    'bbox': box.xyxy[0].tolist(),  # [x1, y1, x2, y2]
                    'conf': float(box.conf[0]),
                    'class_id': int(box.cls[0])
                })
        
        return detections
```

**Performance:** ~50ms on CPU, ~10ms on GPU

---

### 2. ByteTrack Implementation

```python
from collections import deque
import numpy as np

class ByteTracker:
    def __init__(self, 
                 track_thresh=0.6,      # High confidence threshold
                 track_buffer=30,        # Frames to keep lost tracks
                 match_thresh=0.8):      # IoU threshold for matching
        
        self.track_thresh = track_thresh
        self.track_buffer = track_buffer
        self.match_thresh = match_thresh
        
        self.tracked_tracks = []  # Active tracks
        self.lost_tracks = []     # Recently lost tracks
        self.removed_tracks = []  # Permanently removed
        
        self.frame_id = 0
        self.track_id_count = 0
    
    def update(self, detections):
        """
        Update tracks with new detections
        
        Args:
            detections: List of {bbox, conf}
        
        Returns:
            List of {id, bbox, velocity, age}
        """
        self.frame_id += 1
        
        # Separate high and low confidence detections
        high_dets = [d for d in detections if d['conf'] >= self.track_thresh]
        low_dets = [d for d in detections if 0.3 <= d['conf'] < self.track_thresh]
        
        # Predict current positions of existing tracks
        for track in self.tracked_tracks:
            track.predict()
        
        # Match high-confidence detections to tracks
        matches, unmatched_tracks, unmatched_dets = self._match(
            self.tracked_tracks, high_dets
        )
        
        # Update matched tracks
        for track_idx, det_idx in matches:
            self.tracked_tracks[track_idx].update(high_dets[det_idx])
        
        # Try to match low-confidence detections to unmatched tracks
        low_matches, low_unmatched_tracks, _ = self._match(
            [self.tracked_tracks[i] for i in unmatched_tracks],
            low_dets
        )
        
        # Update tracks matched with low-confidence detections
        for track_idx, det_idx in low_matches:
            self.tracked_tracks[unmatched_tracks[track_idx]].update(low_dets[det_idx])
        
        # Mark unmatched tracks as lost
        for track_idx in low_unmatched_tracks:
            track = self.tracked_tracks[unmatched_tracks[track_idx]]
            track.mark_lost()
            self.lost_tracks.append(track)
        
        # Create new tracks for unmatched high-confidence detections
        for det_idx in unmatched_dets:
            track = Track(high_dets[det_idx], self.track_id_count)
            self.track_id_count += 1
            self.tracked_tracks.append(track)
        
        # Remove dead tracks
        self.tracked_tracks = [t for t in self.tracked_tracks if t.state != 'removed']
        
        # Try to re-match lost tracks
        matches, _, _ = self._match(self.lost_tracks, high_dets)
        for track_idx, det_idx in matches:
            self.lost_tracks[track_idx].reactivate(high_dets[det_idx])
            self.tracked_tracks.append(self.lost_tracks[track_idx])
        
        self.lost_tracks = [t for t in self.lost_tracks if t.state != 'removed']
        
        # Return active tracks
        return [
            {
                'id': t.track_id,
                'bbox': t.bbox,
                'velocity': t.velocity,
                'age': t.age,
                'conf': t.conf
            }
            for t in self.tracked_tracks
        ]
    
    def _match(self, tracks, detections):
        """Match tracks to detections using IoU"""
        if len(tracks) == 0 or len(detections) == 0:
            return [], list(range(len(tracks))), list(range(len(detections)))
        
        # Compute IoU matrix
        iou_matrix = np.zeros((len(tracks), len(detections)))
        for i, track in enumerate(tracks):
            for j, det in enumerate(detections):
                iou_matrix[i, j] = self._iou(track.bbox, det['bbox'])
        
        # Hungarian algorithm for optimal matching
        from scipy.optimize import linear_sum_assignment
        matched_indices = linear_sum_assignment(-iou_matrix)
        
        matches = []
        unmatched_tracks = []
        unmatched_dets = []
        
        # Filter matches by threshold
        for i, j in zip(*matched_indices):
            if iou_matrix[i, j] >= self.match_thresh:
                matches.append((i, j))
            else:
                unmatched_tracks.append(i)
                unmatched_dets.append(j)
        
        # Find completely unmatched
        matched_track_ids = set(m[0] for m in matches)
        matched_det_ids = set(m[1] for m in matches)
        
        unmatched_tracks.extend([i for i in range(len(tracks)) if i not in matched_track_ids])
        unmatched_dets.extend([j for j in range(len(detections)) if j not in matched_det_ids])
        
        return matches, unmatched_tracks, unmatched_dets
    
    def _iou(self, bbox1, bbox2):
        """Compute IoU between two bounding boxes"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i < x1_i or y2_i < y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0


class Track:
    """Single person track"""
    def __init__(self, detection, track_id):
        self.track_id = track_id
        self.bbox = detection['bbox']
        self.conf = detection['conf']
        self.velocity = [0, 0]  # [vx, vy]
        self.age = 0
        self.time_since_update = 0
        self.state = 'active'
        
        # Kalman filter for motion prediction
        from filterpy.kalman import KalmanFilter
        self.kf = KalmanFilter(dim_x=8, dim_z=4)
        # State: [x, y, w, h, vx, vy, vw, vh]
        # Measurement: [x, y, w, h]
        
    def predict(self):
        """Predict next position"""
        self.kf.predict()
        self.age += 1
        self.time_since_update += 1
        
    def update(self, detection):
        """Update with new detection"""
        self.bbox = detection['bbox']
        self.conf = detection['conf']
        self.kf.update(self._bbox_to_measurement(detection['bbox']))
        self.time_since_update = 0
        self.state = 'active'
        
    def mark_lost(self):
        """Mark track as lost"""
        self.state = 'lost'
        
    def reactivate(self, detection):
        """Reactivate lost track"""
        self.update(detection)
        self.state = 'active'
        
    def _bbox_to_measurement(self, bbox):
        """Convert bbox to measurement format"""
        x1, y1, x2, y2 = bbox
        return [(x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1]
```

---

### 3. Person History Tracker

```python
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PersonAction:
    timestamp: datetime
    action_type: str  # 'violence', 'distress', 'walking', etc.
    confidence: float
    bbox: list
    details: str

class PersonHistoryTracker:
    def __init__(self, history_length=300):  # 10 seconds at 30fps
        self.history_length = history_length
        self.person_histories = defaultdict(lambda: deque(maxlen=history_length))
        self.person_metadata = {}  # Store appearance, last seen, etc.
    
    def update(self, person_id, action):
        """Add action to person's history"""
        self.person_histories[person_id].append(action)
        
        # Update metadata
        if person_id not in self.person_metadata:
            self.person_metadata[person_id] = {
                'first_seen': datetime.now(),
                'last_seen': datetime.now(),
                'total_actions': 0
            }
        
        self.person_metadata[person_id]['last_seen'] = datetime.now()
        self.person_metadata[person_id]['total_actions'] += 1
    
    def get_history(self, person_id, last_n=None):
        """Get person's action history"""
        history = list(self.person_histories[person_id])
        if last_n:
            return history[-last_n:]
        return history
    
    def get_recent_pattern(self, person_id, window_seconds=5, fps=30):
        """Analyze recent behavior pattern"""
        recent_actions = self.get_history(person_id, last_n=window_seconds * fps)
        
        # Count action types
        action_counts = defaultdict(int)
        for action in recent_actions:
            action_counts[action.action_type] += 1
        
        return {
            'dominant_action': max(action_counts, key=action_counts.get) if action_counts else None,
            'action_distribution': dict(action_counts),
            'duration': len(recent_actions) / fps if recent_actions else 0
        }
    
    def detect_sustained_behavior(self, person_id, action_type, min_duration=3, fps=30):
        """Detect if person has been doing something for a while"""
        recent = self.get_history(person_id, last_n=min_duration * fps)
        
        if len(recent) < min_duration * fps:
            return False
        
        # Check if action is sustained
        matching_actions = sum(1 for a in recent if a.action_type == action_type)
        ratio = matching_actions / len(recent)
        
        return ratio > 0.7  # 70% of frames show this action
```

---

## Integration with Existing System

### Updated Hybrid Router

```python
class HybridRouter:
    def __init__(self, vlm_client=None):
        # Existing detectors...
        self.person_detector = None
        self.person_tracker = None
        self.person_history = None
    
    def _init_detectors(self):
        # Existing initialization...
        
        # Add person tracking
        try:
            from nura_detectors import PersonDetector, ByteTracker, PersonHistoryTracker
            
            self.person_detector = PersonDetector()
            self.person_tracker = ByteTracker()
            self.person_history = PersonHistoryTracker()
            
            logger.info("✓ Person tracking initialized")
        except Exception as e:
            logger.warning(f"Person tracking unavailable: {e}")
    
    async def analyze_frame(self, frame, camera_id=None):
        # 1. Detect and track people
        person_tracks = None
        if self.person_tracker:
            detections = self.person_detector.detect(frame)
            person_tracks = self.person_tracker.update(detections)
        
        # 2. Run detectors (violence, distress, etc.)
        fast_path_results = await self._run_fast_path(frame)
        
        # 3. If we have person tracks, analyze per-person
        if person_tracks:
            for track in person_tracks:
                person_id = track['id']
                bbox = track['bbox']
                
                # Crop person ROI
                x1, y1, x2, y2 = [int(v) for v in bbox]
                person_roi = frame[y1:y2, x1:x2]
                
                # Run detectors on this person
                person_results = await self._analyze_person(person_roi, person_id)
                
                # Update history
                for action_type, result in person_results.items():
                    if result.get('detected'):
                        self.person_history.update(person_id, PersonAction(
                            timestamp=datetime.now(),
                            action_type=action_type,
                            confidence=result['confidence'],
                            bbox=bbox,
                            details=result.get('details', '')
                        ))
        
        # 4. Enhanced routing decision with person context
        decision = self._make_routing_decision_with_people(
            fast_path_results,
            person_tracks
        )
        
        # 5. VLM validation with person context
        if decision['route'] == 'vlm_validation':
            vlm_result = await self._analyze_with_vlm_and_people(
                frame,
                fast_path_results,
                person_tracks
            )
        
        # ... rest of logic
```

---

## Performance Targets

### Speed

| Component | Target | Measured |
|-----------|--------|----------|
| Person Detection | <100ms CPU | TBD |
| Tracking (ByteTrack) | <20ms | TBD |
| Per-Person Analysis | <50ms per person | TBD |
| **Total Overhead** | **<200ms for 5 people** | TBD |

### Accuracy

| Metric | Target | Notes |
|--------|--------|-------|
| MOTA | >75% | Multi-object tracking accuracy |
| ID Switches | <5 per minute | Per camera |
| False Positives | <10% | Wrong person IDs |
| Occlusion Recovery | >80% | For <3s occlusions |

### Scalability

| Scenario | Target |
|----------|--------|
| People per frame | Up to 10 |
| Cameras | 10-15 simultaneously |
| Tracking duration | Hours (persistent IDs) |
| History per person | 10 seconds @ 30fps |

---

## Testing Strategy

### 1. Unit Tests
- Person detector accuracy
- Tracking IoU matching
- Kalman filter predictions
- History management

### 2. Integration Tests
- Full pipeline with real videos
- Multi-person scenarios
- Occlusion handling
- Camera handoffs

### 3. Performance Tests
- Benchmark on target hardware
- Measure overhead per person
- Test with 10+ people
- Multi-camera stress test

### 4. Accuracy Tests
- MOT17 benchmark dataset
- Childcare-specific scenarios
- Re-identification tests
- Long-term tracking (minutes)

---

## Deployment Considerations

### Resource Usage

**CPU-only (Mac development):**
- YOLOv8n: ~50ms
- ByteTrack: ~10ms
- 5 people: ~60ms total

**With GPU (Linux production):**
- YOLOv8n: ~10ms
- ByteTrack: ~5ms
- 5 people: ~15ms total

### Configuration

```bash
# .env additions
ENABLE_PERSON_TRACKING=true
PERSON_DETECTOR_MODEL=yolov8n  # n=nano, s=small, m=medium
TRACKING_ALGORITHM=bytetrack    # or deepsort
TRACK_HIGH_THRESHOLD=0.6
TRACK_LOW_THRESHOLD=0.3
TRACK_BUFFER=30  # frames
PERSON_HISTORY_LENGTH=300  # frames (10s at 30fps)
```

---

## Next Steps

1. ✅ Specification complete
2. ⏳ Implement PersonDetector
3. ⏳ Implement ByteTracker
4. ⏳ Integrate with HybridRouter
5. ⏳ Add person history tracking
6. ⏳ Test with multi-person videos
7. ⏳ Benchmark and optimize

---

**Status:** Ready for implementation  
**Estimated time:** 2-3 days  
**Dependencies:** Phase 3 complete ✅
