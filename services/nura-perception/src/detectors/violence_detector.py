"""
Violence/Aggression Detector
Fast-path detector for physical aggression in childcare settings

Spec: specs/026-hybrid-fast-path/spec.md
"""
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ViolenceType(Enum):
    """Types of violent actions"""
    HITTING = "hitting"
    PUSHING = "pushing"
    KICKING = "kicking"
    THROWING = "throwing"
    HAIR_PULLING = "hair_pulling"
    UNKNOWN = "unknown"


class Severity(Enum):
    """Severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ViolenceDetection:
    """Violence detection result"""
    violence_detected: bool
    confidence: float
    action_type: ViolenceType
    bbox: Optional[Tuple[int, int, int, int]]  # x, y, w, h
    severity: Severity
    details: str


class ViolenceDetector:
    """
    Detects physical aggression and violence using:
    1. Motion detection (sudden movements)
    2. Pose estimation (hitting/pushing poses)
    3. Object trajectory (throwing)
    4. Spatial proximity (too close/contact)

    Phase 1: Rule-based heuristics (fast, works immediately)
    Phase 2: ML model (I3D or YOLO-based action detection)
    """

    def __init__(self, use_ml_model: bool = False):
        """
        Args:
            use_ml_model: If True, use ML model. If False, use heuristics.
        """
        self.use_ml_model = use_ml_model
        self.prev_frame = None
        self.person_detector = None  # Will initialize if needed

        # Heuristic thresholds
        self.motion_threshold = 50  # Pixel intensity change threshold
        self.proximity_threshold = 30  # Pixels - too close
        self.velocity_threshold = 15  # Sudden movement speed

        logger.info(f"ViolenceDetector initialized (ML model: {use_ml_model})")

    def detect(self, frame: np.ndarray) -> ViolenceDetection:
        """
        Detect violence in a single frame

        Args:
            frame: Input image (BGR format)

        Returns:
            ViolenceDetection object with results
        """
        if self.use_ml_model:
            return self._detect_ml(frame)
        else:
            return self._detect_heuristic(frame)

    def _detect_heuristic(self, frame: np.ndarray) -> ViolenceDetection:
        """
        Heuristic-based detection (Phase 1)

        Uses:
        1. Motion analysis (sudden high-velocity movements)
        2. Color-based hand detection (skin color)
        3. Spatial analysis (children too close)

        This is fast (<10ms) and works immediately without ML models.
        """
        # Convert to grayscale for motion detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Initialize on first frame
        if self.prev_frame is None:
            self.prev_frame = gray
            return ViolenceDetection(
                violence_detected=False,
                confidence=1.0,
                action_type=ViolenceType.UNKNOWN,
                bbox=None,
                severity=Severity.LOW,
                details="First frame - no motion to analyze"
            )

        # Detect motion
        motion_detected, motion_intensity, motion_bbox = self._detect_motion(
            self.prev_frame, gray
        )

        # Detect hands (potential hitting)
        hands_detected, hand_bboxes = self._detect_hands(frame)

        # Analyze spatial proximity
        proximity_violation = self._detect_proximity_violation(frame)

        # Update previous frame
        self.prev_frame = gray.copy()

        # Combine signals
        violence_score = 0.0
        details = []
        detected_type = ViolenceType.UNKNOWN
        severity = Severity.LOW
        bbox = None

        # High motion intensity suggests violent action
        if motion_detected and motion_intensity > self.motion_threshold:
            violence_score += 0.4
            details.append(f"High motion intensity: {motion_intensity:.1f}")
            bbox = motion_bbox

            # If hands also detected in motion area, likely hitting
            if hands_detected and self._overlaps(motion_bbox, hand_bboxes):
                violence_score += 0.3
                detected_type = ViolenceType.HITTING
                severity = Severity.MEDIUM
                details.append("Hand detected in motion area - potential hitting")

        # Proximity violation + motion = potential pushing
        if proximity_violation and motion_detected:
            violence_score += 0.3
            details.append("Children too close with motion - potential contact")
            if detected_type == ViolenceType.UNKNOWN:
                detected_type = ViolenceType.PUSHING
                severity = Severity.MEDIUM

        # Determine if violence detected
        violence_detected = violence_score >= 0.5
        confidence = min(violence_score, 1.0)

        if violence_detected:
            details.append(f"Violence score: {violence_score:.2f}")
        else:
            details.append("Normal activity detected")

        return ViolenceDetection(
            violence_detected=violence_detected,
            confidence=confidence,
            action_type=detected_type,
            bbox=bbox,
            severity=severity,
            details=" | ".join(details)
        )

    def _detect_motion(
        self,
        prev_gray: np.ndarray,
        curr_gray: np.ndarray
    ) -> Tuple[bool, float, Optional[Tuple[int, int, int, int]]]:
        """
        Detect sudden high-velocity motion

        Returns:
            (motion_detected, intensity, bbox)
        """
        # Frame difference
        diff = cv2.absdiff(prev_gray, curr_gray)

        # Threshold
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        # Calculate motion intensity
        motion_pixels = np.count_nonzero(thresh)
        total_pixels = thresh.shape[0] * thresh.shape[1]
        motion_intensity = (motion_pixels / total_pixels) * 100

        # Find motion region
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        bbox = None
        if contours:
            # Largest motion region
            largest = max(contours, key=cv2.contourArea)
            bbox = cv2.boundingRect(largest)

        motion_detected = motion_intensity > 5.0  # 5% of frame changed

        return motion_detected, motion_intensity, bbox

    def _detect_hands(
        self,
        frame: np.ndarray
    ) -> Tuple[bool, List[Tuple[int, int, int, int]]]:
        """
        Detect hands using skin color detection

        Returns:
            (hands_detected, list of bboxes)
        """
        # Convert to HSV for skin detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Skin color range (simplified - works for various skin tones)
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)

        # Create mask
        mask = cv2.inRange(hsv, lower_skin, upper_skin)

        # Morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Filter by size (hands are typically 50-500 pixels)
        hand_bboxes = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 50 < area < 5000:  # Reasonable hand size
                bbox = cv2.boundingRect(contour)
                hand_bboxes.append(bbox)

        hands_detected = len(hand_bboxes) > 0

        return hands_detected, hand_bboxes

    def _detect_proximity_violation(self, frame: np.ndarray) -> bool:
        """
        Detect if children are too close (potential contact)

        Simplified: Check if there are clusters of skin-colored regions
        Full implementation would use person detection + tracking
        """
        # This is a placeholder - full implementation would use YOLO
        # For now, return False (no violation)
        return False

    def _overlaps(
        self,
        bbox1: Optional[Tuple[int, int, int, int]],
        bbox_list: List[Tuple[int, int, int, int]]
    ) -> bool:
        """Check if bbox1 overlaps with any bbox in bbox_list"""
        if bbox1 is None or not bbox_list:
            return False

        x1, y1, w1, h1 = bbox1

        for x2, y2, w2, h2 in bbox_list:
            # Check overlap
            if not (x1 + w1 < x2 or x2 + w2 < x1 or
                    y1 + h1 < y2 or y2 + h2 < y1):
                return True

        return False

    def _detect_ml(self, frame: np.ndarray) -> ViolenceDetection:
        """
        ML-based detection (Phase 2)

        Uses trained I3D or YOLO-based action detection model
        This will be implemented when models are ready.
        """
        # TODO: Implement ML-based detection
        # For now, fall back to heuristic
        logger.warning("ML model not yet implemented, using heuristics")
        return self._detect_heuristic(frame)


# Convenience function for easy testing
def detect_violence(frame: np.ndarray, use_ml: bool = False) -> Dict:
    """
    Quick violence detection function

    Args:
        frame: Input image (BGR)
        use_ml: Use ML model if available

    Returns:
        Dict with detection results
    """
    detector = ViolenceDetector(use_ml_model=use_ml)
    result = detector.detect(frame)

    return {
        "violence_detected": result.violence_detected,
        "confidence": result.confidence,
        "action_type": result.action_type.value,
        "bbox": result.bbox,
        "severity": result.severity.value,
        "details": result.details
    }
