"""
Person Tracking (Phase 4)

Multi-person detection and tracking using:
- YOLOv8 for person detection
- ByteTrack for tracking across frames
- Per-person action history

Usage:
    from nura_detectors import PersonTracker

    tracker = PersonTracker()
    tracks = tracker.update(frame)

    for track in tracks:
        person_id = track['id']
        bbox = track['bbox']
        print(f"Person {person_id} at {bbox}")
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Optional dependencies
try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False
    logger.warning("ultralytics not installed - person detection unavailable")

try:
    from scipy.optimize import linear_sum_assignment
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    logger.warning("scipy not installed - tracking will use greedy matching")

try:
    from filterpy.kalman import KalmanFilter
    HAS_FILTERPY = True
except ImportError:
    HAS_FILTERPY = False
    logger.warning("filterpy not installed - tracking without Kalman filter")


@dataclass
class PersonAction:
    """Single action detected for a person"""
    timestamp: datetime
    action_type: str  # 'violence', 'distress', 'walking', etc.
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    details: str = ""


class PersonDetector:
    """
    Detect persons in frame using YOLOv8

    Uses YOLO's person class (class_id=0) for detection.
    """

    def __init__(self, model_size='n', conf_threshold=0.3):
        """
        Args:
            model_size: 'n' (nano), 's' (small), 'm' (medium)
            conf_threshold: Minimum confidence for detection
        """
        if not HAS_YOLO:
            raise ImportError("ultralytics not installed. Install: pip install ultralytics")

        self.model_size = model_size
        self.conf_threshold = conf_threshold

        # Load YOLO model
        model_name = f'yolov8{model_size}.pt'
        logger.info(f"Loading YOLO model: {model_name}")
        self.model = YOLO(model_name)

        logger.info(f"✓ Person detector initialized ({model_name})")

    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect persons in frame

        Args:
            frame: Input image (BGR format)

        Returns:
            List of detections: [{'bbox': [x1,y1,x2,y2], 'conf': float}]
        """
        # Run YOLO detection (class 0 = person)
        results = self.model(frame, classes=[0], conf=self.conf_threshold, verbose=False)

        detections = []
        for r in results:
            for box in r.boxes:
                detections.append({
                    'bbox': box.xyxy[0].cpu().numpy().tolist(),
                    'conf': float(box.conf[0])
                })

        return detections


class Track:
    """Single person track with Kalman filter"""

    def __init__(self, detection: Dict, track_id: int, use_kalman: bool = True):
        self.track_id = track_id
        self.bbox = detection['bbox']
        self.conf = detection['conf']
        self.age = 0
        self.time_since_update = 0
        self.state = 'active'  # 'active', 'lost', 'removed'

        # Velocity estimation
        self.prev_bbox = None
        self.velocity = [0.0, 0.0]  # [vx, vy]

        # Kalman filter for motion prediction
        self.use_kalman = use_kalman and HAS_FILTERPY
        if self.use_kalman:
            self._init_kalman()

    def _init_kalman(self):
        """Initialize Kalman filter"""
        self.kf = KalmanFilter(dim_x=8, dim_z=4)

        # State: [x, y, w, h, vx, vy, vw, vh]
        x, y, w, h = self._bbox_to_xywh(self.bbox)
        self.kf.x = np.array([x, y, w, h, 0, 0, 0, 0])

        # State transition matrix (constant velocity model)
        self.kf.F = np.array([
            [1, 0, 0, 0, 1, 0, 0, 0],
            [0, 1, 0, 0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0, 0, 1, 0],
            [0, 0, 0, 1, 0, 0, 0, 1],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1]
        ])

        # Measurement matrix (we observe x, y, w, h)
        self.kf.H = np.array([
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0]
        ])

        # Covariances
        self.kf.P *= 10.0  # Initial uncertainty
        self.kf.R *= 1.0   # Measurement noise
        self.kf.Q *= 0.01  # Process noise

    def predict(self):
        """Predict next position"""
        self.age += 1
        self.time_since_update += 1

        if self.use_kalman:
            self.kf.predict()
            x, y, w, h = self.kf.x[:4]
            self.bbox = self._xywh_to_bbox([x, y, w, h])
        else:
            # Simple velocity-based prediction
            x1, y1, x2, y2 = self.bbox
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            cx += self.velocity[0]
            cy += self.velocity[1]
            w, h = x2 - x1, y2 - y1
            self.bbox = [cx - w/2, cy - h/2, cx + w/2, cy + h/2]

    def update(self, detection: Dict):
        """Update track with new detection"""
        # Update velocity
        if self.prev_bbox:
            x1_old, y1_old, x2_old, y2_old = self.prev_bbox
            x1_new, y1_new, x2_new, y2_new = detection['bbox']

            cx_old, cy_old = (x1_old + x2_old) / 2, (y1_old + y2_old) / 2
            cx_new, cy_new = (x1_new + x2_new) / 2, (y1_new + y2_new) / 2

            self.velocity = [cx_new - cx_old, cy_new - cy_old]

        self.prev_bbox = self.bbox
        self.bbox = detection['bbox']
        self.conf = detection['conf']
        self.time_since_update = 0
        self.state = 'active'

        if self.use_kalman:
            measurement = self._bbox_to_xywh(detection['bbox'])
            self.kf.update(measurement)

    def mark_lost(self):
        """Mark track as lost"""
        self.state = 'lost'

    def mark_removed(self):
        """Mark track as removed"""
        self.state = 'removed'

    def reactivate(self, detection: Dict):
        """Reactivate lost track"""
        self.update(detection)
        self.state = 'active'
        self.time_since_update = 0

    def _bbox_to_xywh(self, bbox):
        """Convert [x1,y1,x2,y2] to [cx,cy,w,h]"""
        x1, y1, x2, y2 = bbox
        return [(x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1]

    def _xywh_to_bbox(self, xywh):
        """Convert [cx,cy,w,h] to [x1,y1,x2,y2]"""
        cx, cy, w, h = xywh
        return [cx - w/2, cy - h/2, cx + w/2, cy + h/2]


class ByteTracker:
    """
    ByteTrack algorithm for multi-object tracking

    Paper: "ByteTrack: Multi-Object Tracking by Associating Every Detection Box"
    https://arxiv.org/abs/2110.06864
    """

    def __init__(self,
                 track_thresh: float = 0.6,
                 track_buffer: int = 30,
                 match_thresh: float = 0.8,
                 use_kalman: bool = True):
        """
        Args:
            track_thresh: High confidence threshold
            track_buffer: Frames to keep lost tracks
            match_thresh: IoU threshold for matching
            use_kalman: Use Kalman filter for prediction
        """
        self.track_thresh = track_thresh
        self.track_buffer = track_buffer
        self.match_thresh = match_thresh
        self.use_kalman = use_kalman and HAS_FILTERPY

        self.tracked_tracks: List[Track] = []
        self.lost_tracks: List[Track] = []
        self.removed_tracks: List[Track] = []

        self.frame_id = 0
        self.track_id_count = 0

        logger.info(f"✓ ByteTracker initialized (Kalman: {self.use_kalman})")

    def update(self, detections: List[Dict]) -> List[Dict]:
        """
        Update tracks with new detections

        Args:
            detections: List of {'bbox': [x1,y1,x2,y2], 'conf': float}

        Returns:
            List of {'id': int, 'bbox': [x1,y1,x2,y2], 'conf': float, 'velocity': [vx,vy], 'age': int}
        """
        self.frame_id += 1

        # Separate high and low confidence detections
        high_dets = [d for d in detections if d['conf'] >= self.track_thresh]
        low_dets = [d for d in detections if 0.3 <= d['conf'] < self.track_thresh]

        # Predict current positions
        for track in self.tracked_tracks:
            track.predict()

        # Step 1: Match high-confidence detections to tracks
        matches_a, unmatched_tracks_a, unmatched_dets_a = self._match(
            self.tracked_tracks, high_dets
        )

        # Update matched tracks
        for track_idx, det_idx in matches_a:
            self.tracked_tracks[track_idx].update(high_dets[det_idx])

        # Step 2: Match low-confidence detections to unmatched tracks
        unmatched_track_objs = [self.tracked_tracks[i] for i in unmatched_tracks_a]
        matches_b, unmatched_tracks_b, unmatched_dets_b = self._match(
            unmatched_track_objs, low_dets, thresh=0.5
        )

        # Update tracks matched with low-confidence detections
        for track_idx, det_idx in matches_b:
            orig_idx = unmatched_tracks_a[track_idx]
            self.tracked_tracks[orig_idx].update(low_dets[det_idx])

        # Step 3: Mark unmatched tracks as lost
        for track_idx in unmatched_tracks_b:
            orig_idx = unmatched_tracks_a[track_idx]
            track = self.tracked_tracks[orig_idx]
            track.mark_lost()
            self.lost_tracks.append(track)

        # Remove from tracked
        self.tracked_tracks = [
            t for i, t in enumerate(self.tracked_tracks)
            if i not in [unmatched_tracks_a[j] for j in unmatched_tracks_b]
        ]

        # Step 4: Create new tracks for unmatched high-confidence detections
        for det_idx in unmatched_dets_a:
            track = Track(high_dets[det_idx], self.track_id_count, self.use_kalman)
            self.track_id_count += 1
            self.tracked_tracks.append(track)

        # Step 5: Try to re-match lost tracks
        matches_lost, unmatched_lost, _ = self._match(
            self.lost_tracks, high_dets, thresh=0.5
        )

        for track_idx, det_idx in matches_lost:
            self.lost_tracks[track_idx].reactivate(high_dets[det_idx])
            self.tracked_tracks.append(self.lost_tracks[track_idx])

        self.lost_tracks = [
            t for i, t in enumerate(self.lost_tracks)
            if i not in [m[0] for m in matches_lost]
        ]

        # Step 6: Remove old lost tracks
        for track in self.lost_tracks:
            if track.time_since_update > self.track_buffer:
                track.mark_removed()
                self.removed_tracks.append(track)

        self.lost_tracks = [t for t in self.lost_tracks if t.state != 'removed']

        # Return active tracks
        return [
            {
                'id': t.track_id,
                'bbox': t.bbox,
                'conf': t.conf,
                'velocity': t.velocity,
                'age': t.age
            }
            for t in self.tracked_tracks
        ]

    def _match(self, tracks: List[Track], detections: List[Dict], thresh: Optional[float] = None) -> Tuple:
        """Match tracks to detections using IoU"""
        if thresh is None:
            thresh = self.match_thresh

        if len(tracks) == 0 or len(detections) == 0:
            return [], list(range(len(tracks))), list(range(len(detections)))

        # Compute IoU matrix
        iou_matrix = np.zeros((len(tracks), len(detections)))
        for i, track in enumerate(tracks):
            for j, det in enumerate(detections):
                iou_matrix[i, j] = self._iou(track.bbox, det['bbox'])

        # Use Hungarian algorithm if available, else greedy
        if HAS_SCIPY:
            row_ind, col_ind = linear_sum_assignment(-iou_matrix)
            matched_indices = list(zip(row_ind, col_ind))
        else:
            # Greedy matching
            matched_indices = []
            used_tracks = set()
            used_dets = set()

            # Sort by IoU (highest first)
            ious = [(i, j, iou_matrix[i, j])
                    for i in range(len(tracks))
                    for j in range(len(detections))]
            ious.sort(key=lambda x: x[2], reverse=True)

            for i, j, iou in ious:
                if i not in used_tracks and j not in used_dets and iou >= thresh:
                    matched_indices.append((i, j))
                    used_tracks.add(i)
                    used_dets.add(j)

        # Filter by threshold
        matches = []
        unmatched_tracks = []
        unmatched_dets = []

        for i, j in matched_indices:
            if iou_matrix[i, j] >= thresh:
                matches.append((i, j))

        matched_track_ids = set(m[0] for m in matches)
        matched_det_ids = set(m[1] for m in matches)

        unmatched_tracks = [i for i in range(len(tracks)) if i not in matched_track_ids]
        unmatched_dets = [j for j in range(len(detections)) if j not in matched_det_ids]

        return matches, unmatched_tracks, unmatched_dets

    def _iou(self, bbox1: List[float], bbox2: List[float]) -> float:
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


class PersonHistoryTracker:
    """Track action history for each person"""

    def __init__(self, history_length: int = 300):
        """
        Args:
            history_length: Number of actions to keep (frames)
        """
        self.history_length = history_length
        self.person_histories = defaultdict(lambda: deque(maxlen=history_length))
        self.person_metadata = {}

        logger.info(f"✓ Person history tracker initialized (length: {history_length})")

    def update(self, person_id: int, action: PersonAction):
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

    def get_history(self, person_id: int, last_n: Optional[int] = None) -> List[PersonAction]:
        """Get person's action history"""
        history = list(self.person_histories[person_id])
        if last_n:
            return history[-last_n:]
        return history

    def get_recent_pattern(self, person_id: int, window_seconds: int = 5, fps: int = 30) -> Dict:
        """Analyze recent behavior pattern"""
        recent_actions = self.get_history(person_id, last_n=window_seconds * fps)

        if not recent_actions:
            return {
                'dominant_action': None,
                'action_distribution': {},
                'duration': 0
            }

        # Count action types
        action_counts = defaultdict(int)
        for action in recent_actions:
            action_counts[action.action_type] += 1

        return {
            'dominant_action': max(action_counts, key=action_counts.get),
            'action_distribution': dict(action_counts),
            'duration': len(recent_actions) / fps
        }

    def detect_sustained_behavior(self, person_id: int, action_type: str,
                                  min_duration: int = 3, fps: int = 30) -> bool:
        """Detect if person has been doing something for a while"""
        recent = self.get_history(person_id, last_n=min_duration * fps)

        if len(recent) < min_duration * fps:
            return False

        # Check if action is sustained (70%+ of frames)
        matching_actions = sum(1 for a in recent if a.action_type == action_type)
        ratio = matching_actions / len(recent)

        return ratio > 0.7


class PersonTracker:
    """
    Complete person tracking system combining detection and tracking

    Usage:
        tracker = PersonTracker()
        tracks = tracker.update(frame)
    """

    def __init__(self,
                 detector_model='n',
                 enable_history=True,
                 history_length=300):
        """
        Args:
            detector_model: YOLO model size ('n', 's', 'm')
            enable_history: Track per-person action history
            history_length: Actions to keep per person
        """
        self.detector = PersonDetector(model_size=detector_model)
        self.tracker = ByteTracker()

        self.enable_history = enable_history
        if enable_history:
            self.history = PersonHistoryTracker(history_length=history_length)
        else:
            self.history = None

        logger.info("✓ Person tracking system initialized")

    def update(self, frame: np.ndarray) -> List[Dict]:
        """
        Update tracking with new frame

        Args:
            frame: Input image (BGR format)

        Returns:
            List of tracks with IDs and bounding boxes
        """
        # Detect persons
        detections = self.detector.detect(frame)

        # Update tracking
        tracks = self.tracker.update(detections)

        return tracks

    def update_person_action(self, person_id: int, action: PersonAction):
        """Add action to person's history"""
        if self.history:
            self.history.update(person_id, action)

    def get_person_history(self, person_id: int, last_n: Optional[int] = None):
        """Get person's action history"""
        if self.history:
            return self.history.get_history(person_id, last_n)
        return []

    def get_person_pattern(self, person_id: int, window_seconds: int = 5):
        """Get recent behavior pattern for person"""
        if self.history:
            return self.history.get_recent_pattern(person_id, window_seconds)
        return {}
