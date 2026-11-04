"""
Supervision Ratio Detector
Fast-path detector for supervision ratio violations

Spec: specs/026-hybrid-fast-path/spec.md
"""
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SupervisionDetection:
    """Supervision detection result"""
    violation_detected: bool
    adult_count: int
    child_count: int
    ratio: float
    required_ratio: float
    confidence: float
    details: str
    person_bboxes: List[Tuple[int, int, int, int, str]]  # x, y, w, h, type


class SupervisionDetector:
    """
    Detects supervision ratio violations through:
    1. Person detection (HOG or YOLO)
    2. Height-based age estimation (adults taller than children)
    3. Ratio calculation

    Phase 1: OpenCV HOG + height heuristics (fast, works immediately)
    Phase 2: YOLO-based person detection + age classifier
    """

    def __init__(self, required_ratio: float = 0.25, use_ml_model: bool = False):
        """
        Args:
            required_ratio: Required adult-to-child ratio (e.g., 0.25 = 1:4)
            use_ml_model: If True, use ML model. If False, use heuristics.
        """
        self.required_ratio = required_ratio
        self.use_ml_model = use_ml_model

        # Load HOG person detector (fast, built-in)
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        # Height thresholds for age estimation (in pixels)
        # These will vary based on camera height and angle
        # Typical classroom: adults 150-250px, children 80-150px
        self.adult_height_min = 150
        self.child_height_max = 150

        logger.info(f"SupervisionDetector initialized (required ratio: {required_ratio}, ML: {use_ml_model})")

    def detect(self, frame: np.ndarray) -> SupervisionDetection:
        """
        Detect supervision ratio violations

        Args:
            frame: Input image (BGR format)

        Returns:
            SupervisionDetection object with results
        """
        if self.use_ml_model:
            return self._detect_ml(frame)
        else:
            return self._detect_heuristic(frame)

    def _detect_heuristic(self, frame: np.ndarray) -> SupervisionDetection:
        """
        Heuristic-based detection (Phase 1)

        Uses:
        1. HOG person detector
        2. Height-based age classification
        3. Ratio calculation

        This is fast (<50ms) and works immediately without ML models.
        """
        # Detect people using HOG
        people, weights = self.hog.detectMultiScale(
            frame,
            winStride=(4, 4),
            padding=(8, 8),
            scale=1.05,
            useMeanshiftGrouping=False
        )

        if len(people) == 0:
            return SupervisionDetection(
                violation_detected=False,
                adult_count=0,
                child_count=0,
                ratio=0.0,
                required_ratio=self.required_ratio,
                confidence=0.5,  # Low confidence when no people detected
                details="No people detected",
                person_bboxes=[]
            )

        # Classify people as adults or children based on height
        adults = []
        children = []
        person_bboxes = []

        for i, (x, y, w, h) in enumerate(people):
            confidence = weights[i] if len(weights) > i else 0.5

            # Height-based classification
            if h >= self.adult_height_min:
                adults.append((x, y, w, h))
                person_bboxes.append((x, y, w, h, "adult"))
            else:
                children.append((x, y, w, h))
                person_bboxes.append((x, y, w, h, "child"))

        adult_count = len(adults)
        child_count = len(children)

        # Calculate ratio
        if child_count == 0:
            # No children, no violation
            ratio = float('inf')
            violation = False
            details = f"No children detected (only {adult_count} adults)"
        else:
            ratio = adult_count / child_count
            violation = ratio < self.required_ratio

            if violation:
                details = (
                    f"Ratio violation: {adult_count} adults : {child_count} children "
                    f"= {ratio:.2f} (required: {self.required_ratio:.2f})"
                )
            else:
                details = (
                    f"Adequate supervision: {adult_count} adults : {child_count} children "
                    f"= {ratio:.2f}"
                )

        # Confidence based on detection weights
        avg_confidence = np.mean(weights) if len(weights) > 0 else 0.5
        confidence = float(avg_confidence)

        return SupervisionDetection(
            violation_detected=violation,
            adult_count=adult_count,
            child_count=child_count,
            ratio=ratio if ratio != float('inf') else 99.0,
            required_ratio=self.required_ratio,
            confidence=confidence,
            details=details,
            person_bboxes=person_bboxes
        )

    def set_ratio_from_age_group(self, age_group: str):
        """
        Set required ratio based on age group

        Common ratios (varies by jurisdiction):
        - Infants (0-12 months): 1:4
        - Toddlers (12-36 months): 1:5
        - Preschool (3-5 years): 1:10
        - School age (6+ years): 1:15
        """
        ratios = {
            "infant": 1/4,
            "toddler": 1/5,
            "preschool": 1/10,
            "school_age": 1/15
        }

        self.required_ratio = ratios.get(age_group, 0.25)
        logger.info(f"Ratio updated to {self.required_ratio} for {age_group}")

    def _detect_ml(self, frame: np.ndarray) -> SupervisionDetection:
        """
        ML-based detection (Phase 2)

        Uses YOLO person detection + age classifier
        This will be implemented when models are ready.
        """
        # TODO: Implement YOLO-based detection with age classification
        logger.warning("ML model not yet implemented, using heuristics")
        return self._detect_heuristic(frame)


# Convenience function for easy testing
def detect_supervision_violation(
    frame: np.ndarray,
    required_ratio: float = 0.25,
    use_ml: bool = False
) -> Dict:
    """
    Quick supervision detection function

    Args:
        frame: Input image (BGR)
        required_ratio: Required adult-to-child ratio
        use_ml: Use ML model if available

    Returns:
        Dict with detection results
    """
    detector = SupervisionDetector(
        required_ratio=required_ratio,
        use_ml_model=use_ml
    )
    result = detector.detect(frame)

    return {
        "violation_detected": result.violation_detected,
        "adult_count": result.adult_count,
        "child_count": result.child_count,
        "ratio": result.ratio,
        "required_ratio": result.required_ratio,
        "confidence": result.confidence,
        "details": result.details,
        "person_count": len(result.person_bboxes)
    }
