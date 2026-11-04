"""
Body Language Detector
Detects defensive postures, power imbalances, and intimidation through body language

This addresses cases like psychological bullying where there's no physical violence
but clear intimidation through posture and spatial dynamics.
"""
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class BodyLanguageDetection:
    """Body language detection result"""
    intimidation_detected: bool
    defensive_posture_detected: bool
    power_imbalance_score: float
    confidence: float
    details: str
    person_positions: List[Tuple[int, int, int, int]]  # x, y, w, h


class BodyLanguageDetector:
    """
    Detects intimidation and bullying through body language analysis:
    1. Defensive postures (backed against wall, head down, arms up)
    2. Power imbalances (standing over someone, cornering)
    3. Spatial dynamics (personal space violations, positioning)

    Use case: Psychological bullying like test_classroom2.jpg
    """

    def __init__(self):
        # Load person detector (HOG)
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        # Pose estimation model (optional, for Phase 2)
        self.pose_detector = None

        logger.info("BodyLanguageDetector initialized")

    def detect(self, frame: np.ndarray) -> BodyLanguageDetection:
        """
        Detect intimidation and defensive postures

        Args:
            frame: Input image (BGR format)

        Returns:
            BodyLanguageDetection with results
        """
        # Detect people
        people, weights = self.hog.detectMultiScale(
            frame,
            winStride=(4, 4),
            padding=(8, 8),
            scale=1.05
        )

        if len(people) < 2:
            # Need at least 2 people for intimidation
            return BodyLanguageDetection(
                intimidation_detected=False,
                defensive_posture_detected=False,
                power_imbalance_score=0.0,
                confidence=1.0,
                details="Less than 2 people detected",
                person_positions=[]
            )

        # Analyze spatial relationships
        intimidation_score = 0.0
        defensive_score = 0.0
        details = []

        # Sort by vertical position (y-coordinate)
        people_sorted = sorted(people, key=lambda p: p[1])

        for i, (x1, y1, w1, h1) in enumerate(people):
            for j, (x2, y2, w2, h2) in enumerate(people):
                if i >= j:
                    continue

                # Calculate centers
                cx1, cy1 = x1 + w1//2, y1 + h1//2
                cx2, cy2 = x2 + w2//2, y2 + h2//2

                # Calculate distance
                distance = np.sqrt((cx1 - cx2)**2 + (cy1 - cy2)**2)

                # Personal space violation (too close)
                if distance < min(w1, w2) * 1.5:
                    intimidation_score += 0.3
                    details.append(f"Personal space violation: {distance:.0f}px")

                # Check if one person is cornered (near edge)
                frame_h, frame_w = frame.shape[:2]

                # Person near wall/edge
                margin = 50
                if (x2 < margin or x2 + w2 > frame_w - margin or
                    y2 < margin or y2 + h2 > frame_h - margin):
                    intimidation_score += 0.4
                    details.append("Person backed against wall/edge")

                # Height difference (standing over someone)
                if h1 > h2 * 1.3 and y1 < y2:
                    intimidation_score += 0.3
                    details.append(f"Height imbalance: {h1}px vs {h2}px")

        # Check for defensive postures
        defensive_score = self._detect_defensive_posture(frame, people)
        if defensive_score > 0.3:
            intimidation_score += defensive_score
            details.append(f"Defensive posture detected: {defensive_score:.2f}")

        # Final decision
        intimidation_detected = intimidation_score >= 0.5
        confidence = min(intimidation_score, 1.0) if intimidation_detected else 0.9

        if intimidation_detected:
            details.append(f"Intimidation score: {intimidation_score:.2f}")
        else:
            details = ["Normal interaction"]

        return BodyLanguageDetection(
            intimidation_detected=intimidation_detected,
            defensive_posture_detected=defensive_score > 0.3,
            power_imbalance_score=intimidation_score,
            confidence=confidence,
            details=" | ".join(details),
            person_positions=people.tolist() if len(people) > 0 else []
        )

    def _detect_defensive_posture(
        self,
        frame: np.ndarray,
        people: np.ndarray
    ) -> float:
        """
        Detect defensive postures:
        - Arms raised to protect head/face
        - Head bowed down
        - Hunched/withdrawn posture

        Returns score 0.0-1.0
        """
        if len(people) == 0:
            return 0.0

        defensive_score = 0.0

        for (x, y, w, h) in people:
            person_roi = frame[y:y+h, x:x+w]

            # Check upper body area for raised arms
            upper_body = person_roi[:h//2, :]

            # Detect skin color in upper body (arms up to protect face)
            hsv = cv2.cvtColor(upper_body, cv2.COLOR_BGR2HSV)
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)

            skin_ratio = np.count_nonzero(skin_mask) / skin_mask.size

            # High skin in upper body = arms raised
            if skin_ratio > 0.4:
                defensive_score += 0.5

            # Check for head down (dark area in top portion)
            head_area = person_roi[:h//4, :]
            head_brightness = np.mean(cv2.cvtColor(head_area, cv2.COLOR_BGR2GRAY))

            # Dark top = head bowed down
            if head_brightness < 80:
                defensive_score += 0.3

        return min(defensive_score, 1.0)


# Convenience function
def detect_intimidation(frame: np.ndarray) -> Dict:
    """
    Quick intimidation detection

    Args:
        frame: Input image (BGR)

    Returns:
        Dict with detection results
    """
    detector = BodyLanguageDetector()
    result = detector.detect(frame)

    return {
        "intimidation_detected": result.intimidation_detected,
        "defensive_posture": result.defensive_posture_detected,
        "power_imbalance_score": result.power_imbalance_score,
        "confidence": result.confidence,
        "details": result.details,
        "person_count": len(result.person_positions)
    }
