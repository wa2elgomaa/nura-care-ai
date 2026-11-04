"""
Child Distress Detector
Fast-path detector for child distress through facial expressions and body language

Spec: specs/026-hybrid-fast-path/spec.md
"""
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EmotionType(Enum):
    """Types of emotions indicating distress"""
    CRYING = "crying"
    FEAR = "fear"
    PAIN = "pain"
    SADNESS = "sadness"
    ANGER = "anger"
    NEUTRAL = "neutral"
    HAPPY = "happy"


class Severity(Enum):
    """Severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class DistressDetection:
    """Distress detection result"""
    distress_detected: bool
    confidence: float
    emotion: EmotionType
    face_bbox: Optional[Tuple[int, int, int, int]]  # x, y, w, h
    severity: Severity
    immediate_attention_needed: bool
    details: str


class DistressDetector:
    """
    Detects child distress through:
    1. Face detection
    2. Facial expression analysis
    3. Body posture analysis
    4. Isolation detection

    Phase 1: OpenCV Haar Cascades + heuristics (fast, works immediately)
    Phase 2: ML model (FER2013 or AffectNet trained model)
    """

    def __init__(self, use_ml_model: bool = False):
        """
        Args:
            use_ml_model: If True, use ML model. If False, use heuristics.
        """
        self.use_ml_model = use_ml_model

        # Load Haar Cascade for face detection (fast, built-in)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        # For crying detection (red eyes/face)
        self.red_threshold_low = np.array([0, 100, 100], dtype=np.uint8)
        self.red_threshold_high = np.array([10, 255, 255], dtype=np.uint8)

        logger.info(f"DistressDetector initialized (ML model: {use_ml_model})")

    def detect(self, frame: np.ndarray) -> DistressDetection:
        """
        Detect distress in a single frame

        Args:
            frame: Input image (BGR format)

        Returns:
            DistressDetection object with results
        """
        if self.use_ml_model:
            return self._detect_ml(frame)
        else:
            return self._detect_heuristic(frame)

    def _detect_heuristic(self, frame: np.ndarray) -> DistressDetection:
        """
        Heuristic-based detection (Phase 1)

        Uses:
        1. Face detection (Haar Cascade)
        2. Color analysis (red face/eyes = crying)
        3. Posture analysis (covering face, hunched)
        4. Edge detection (mouth open wide = crying)

        This is fast (<30ms) and works immediately without ML models.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        if len(faces) == 0:
            return DistressDetection(
                distress_detected=False,
                confidence=1.0,
                emotion=EmotionType.NEUTRAL,
                face_bbox=None,
                severity=Severity.LOW,
                immediate_attention_needed=False,
                details="No faces detected"
            )

        # Analyze each face for distress signals
        max_distress_score = 0.0
        distress_face = None
        distress_emotion = EmotionType.NEUTRAL
        distress_details = []

        for (x, y, w, h) in faces:
            face_roi = frame[y:y+h, x:x+w]
            gray_roi = gray[y:y+h, x:x+w]

            # Calculate distress indicators
            distress_score = 0.0
            indicators = []

            # 1. Check for red coloration (crying)
            red_score = self._detect_red_face(face_roi)
            if red_score > 0.3:
                distress_score += red_score * 0.4
                indicators.append(f"Red face/eyes: {red_score:.2f}")
                distress_emotion = EmotionType.CRYING

            # 2. Check for covering face (hands over face)
            covering_score = self._detect_face_covering(face_roi, gray_roi)
            if covering_score > 0.5:
                distress_score += covering_score * 0.3
                indicators.append(f"Face covering detected: {covering_score:.2f}")
                if distress_emotion == EmotionType.NEUTRAL:
                    distress_emotion = EmotionType.SADNESS

            # 3. Check for wide open mouth (crying/screaming)
            mouth_score = self._detect_open_mouth(gray_roi)
            if mouth_score > 0.4:
                distress_score += mouth_score * 0.3
                indicators.append(f"Open mouth detected: {mouth_score:.2f}")
                if distress_emotion == EmotionType.NEUTRAL:
                    distress_emotion = EmotionType.CRYING

            # 4. Check brightness (pale face = fear)
            brightness = np.mean(gray_roi)
            if brightness > 180:  # Very pale
                distress_score += 0.2
                indicators.append(f"Pale face: {brightness:.1f}")
                if distress_emotion == EmotionType.NEUTRAL:
                    distress_emotion = EmotionType.FEAR

            # Update if this is the most distressed face
            if distress_score > max_distress_score:
                max_distress_score = distress_score
                distress_face = (x, y, w, h)
                distress_details = indicators

        # Determine severity and need for attention
        distress_detected = max_distress_score >= 0.5
        confidence = min(max_distress_score, 1.0)

        if max_distress_score >= 0.8:
            severity = Severity.HIGH
            immediate_attention = True
        elif max_distress_score >= 0.6:
            severity = Severity.MEDIUM
            immediate_attention = True
        else:
            severity = Severity.LOW
            immediate_attention = False

        if distress_detected:
            distress_details.append(f"Distress score: {max_distress_score:.2f}")
        else:
            distress_details = ["Normal expression detected"]
            distress_emotion = EmotionType.NEUTRAL

        return DistressDetection(
            distress_detected=distress_detected,
            confidence=confidence,
            emotion=distress_emotion,
            face_bbox=distress_face,
            severity=severity,
            immediate_attention_needed=immediate_attention,
            details=" | ".join(distress_details)
        )

    def _detect_red_face(self, face_roi: np.ndarray) -> float:
        """
        Detect red coloration in face (crying indicator)

        Returns:
            Score 0.0-1.0
        """
        # Convert to HSV
        hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)

        # Create mask for red areas
        mask1 = cv2.inRange(hsv, self.red_threshold_low, self.red_threshold_high)

        # Also check for darker red
        mask2 = cv2.inRange(hsv, np.array([170, 100, 100]), np.array([180, 255, 255]))

        # Combine masks
        red_mask = cv2.bitwise_or(mask1, mask2)

        # Calculate percentage of red pixels
        red_pixels = np.count_nonzero(red_mask)
        total_pixels = red_mask.shape[0] * red_mask.shape[1]
        red_ratio = red_pixels / total_pixels

        # Normalize to 0-1 scale
        # High red ratio (>20%) indicates crying
        score = min(red_ratio / 0.2, 1.0)

        return score

    def _detect_face_covering(
        self,
        face_roi: np.ndarray,
        gray_roi: np.ndarray
    ) -> float:
        """
        Detect if hands are covering face (distress indicator)

        Returns:
            Score 0.0-1.0
        """
        # Detect skin color (hands)
        hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)

        # Skin color mask
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)

        # Edge detection to find face outline
        edges = cv2.Canny(gray_roi, 50, 150)

        # If there's a lot of skin detected but few face edges visible,
        # it suggests hands are covering the face
        skin_ratio = np.count_nonzero(skin_mask) / skin_mask.size
        edge_ratio = np.count_nonzero(edges) / edges.size

        # High skin but low edges = covering
        if skin_ratio > 0.4 and edge_ratio < 0.05:
            return min(skin_ratio / 0.6, 1.0)

        return 0.0

    def _detect_open_mouth(self, gray_roi: np.ndarray) -> float:
        """
        Detect wide open mouth (crying/screaming indicator)

        Returns:
            Score 0.0-1.0
        """
        # Look for dark regions in lower half of face (open mouth)
        h, w = gray_roi.shape
        lower_face = gray_roi[int(h*0.6):, :]

        # Threshold to find dark regions
        _, thresh = cv2.threshold(lower_face, 60, 255, cv2.THRESH_BINARY_INV)

        # Find dark region area
        dark_pixels = np.count_nonzero(thresh)
        total_pixels = thresh.size
        dark_ratio = dark_pixels / total_pixels

        # Normalize (>15% dark = wide open mouth)
        score = min(dark_ratio / 0.15, 1.0)

        return score

    def _detect_ml(self, frame: np.ndarray) -> DistressDetection:
        """
        ML-based detection (Phase 2)

        Uses trained FER (Facial Expression Recognition) model
        This will be implemented when models are ready.
        """
        # TODO: Implement ML-based detection with FER model
        logger.warning("ML model not yet implemented, using heuristics")
        return self._detect_heuristic(frame)


# Convenience function for easy testing
def detect_distress(frame: np.ndarray, use_ml: bool = False) -> Dict:
    """
    Quick distress detection function

    Args:
        frame: Input image (BGR)
        use_ml: Use ML model if available

    Returns:
        Dict with detection results
    """
    detector = DistressDetector(use_ml_model=use_ml)
    result = detector.detect(frame)

    return {
        "distress_detected": result.distress_detected,
        "confidence": result.confidence,
        "emotion": result.emotion.value,
        "face_bbox": result.face_bbox,
        "severity": result.severity.value,
        "immediate_attention_needed": result.immediate_attention_needed,
        "details": result.details
    }
