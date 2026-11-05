"""
Pose-Based Body Language Detector (Phase 2 - ML)
Uses YOLOv8 pose estimation for accurate body language analysis

This replaces the heuristic HOG-based detector with ML-based pose detection
for significantly better accuracy in detecting:
- Defensive postures (hands up, covering face)
- Aggressive stances (raised arms, forward lean)
- Power dynamics (height differences, positioning)
- Physical contact and proximity
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False
    logger.warning("ultralytics not installed - pose detection unavailable")


@dataclass
class PoseDetection:
    """Pose-based detection result"""
    intimidation_detected: bool
    defensive_posture_detected: bool
    aggressive_posture_detected: bool
    power_imbalance_score: float
    confidence: float
    details: str
    person_count: int
    keypoints: Optional[List] = None


# COCO Keypoint indices
KP_NOSE = 0
KP_LEFT_EYE = 1
KP_RIGHT_EYE = 2
KP_LEFT_EAR = 3
KP_RIGHT_EAR = 4
KP_LEFT_SHOULDER = 5
KP_RIGHT_SHOULDER = 6
KP_LEFT_ELBOW = 7
KP_RIGHT_ELBOW = 8
KP_LEFT_WRIST = 9
KP_RIGHT_WRIST = 10
KP_LEFT_HIP = 11
KP_RIGHT_HIP = 12
KP_LEFT_KNEE = 13
KP_RIGHT_KNEE = 14
KP_LEFT_ANKLE = 15
KP_RIGHT_ANKLE = 16


class PoseBodyLanguageDetector:
    """
    ML-based body language detector using pose estimation

    Detects:
    1. Defensive postures - hands near face, cowering, backing away
    2. Aggressive stances - raised arms, forward lean, invading space
    3. Power dynamics - height differences, positioning, dominance
    4. Physical contact - hands on another person
    """

    def __init__(self, model_size: str = 'n'):
        """
        Args:
            model_size: 'n' (nano), 's' (small), 'm' (medium), 'l' (large)
                       nano is fastest, large is most accurate
        """
        if not HAS_YOLO:
            logger.error("ultralytics not installed. Install with: pip install ultralytics")
            self.model = None
            return

        # Try models folder first, then root (backwards compatibility)
        import os
        model_name = f'yolov8{model_size}-pose.pt'

        # Check common locations
        possible_paths = [
            f'models/{model_name}',  # Preferred location
            model_name,              # Root (legacy)
            f'../../{model_name}',   # When running from package
        ]

        model_path = None
        for path in possible_paths:
            if os.path.exists(path):
                model_path = path
                break

        if not model_path:
            # Download to models folder if not found
            os.makedirs('models', exist_ok=True)
            model_path = f'models/{model_name}'

        try:
            self.model = YOLO(model_path)
            logger.info(f"✓ YOLO pose model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load YOLO pose model: {e}")
            self.model = None

    def detect(self, frame: np.ndarray) -> PoseDetection:
        """
        Detect body language from pose keypoints

        Args:
            frame: Input image (BGR format)

        Returns:
            PoseDetection with analysis results
        """
        if self.model is None:
            return self._fallback_detection()

        try:
            # Run pose detection
            results = self.model(frame, verbose=False)

            if len(results) == 0:
                return self._no_detection()

            result = results[0]
            boxes = result.boxes
            keypoints = result.keypoints

            if keypoints is None or len(keypoints) == 0:
                return self._no_detection()

            # Analyze poses
            return self._analyze_poses(keypoints, frame.shape)

        except Exception as e:
            logger.error(f"Pose detection error: {e}")
            return self._fallback_detection()

    def _analyze_poses(self, keypoints, frame_shape) -> PoseDetection:
        """Analyze pose keypoints for body language indicators"""

        intimidation_score = 0.0
        defensive_score = 0.0
        aggressive_score = 0.0
        details = []

        person_count = len(keypoints)

        if person_count < 2:
            return PoseDetection(
                intimidation_detected=False,
                defensive_posture_detected=False,
                aggressive_posture_detected=False,
                power_imbalance_score=0.0,
                confidence=1.0,
                details="Less than 2 people - no interaction to analyze",
                person_count=person_count
            )

        # Extract keypoint data for all people
        people_kp = []
        for person_kp in keypoints:
            kp_data = person_kp.data[0].cpu().numpy()  # Shape: (17, 3)
            people_kp.append(kp_data)

        # Analyze each person's posture
        for i, kp in enumerate(people_kp):
            # Check for defensive posture
            defensive_indicators = self._check_defensive_posture(kp)
            if defensive_indicators['has_defensive']:
                defensive_score += defensive_indicators['score']
                details.append(f"Person {i+1}: {defensive_indicators['reason']}")

            # Check for aggressive posture
            aggressive_indicators = self._check_aggressive_posture(kp)
            if aggressive_indicators['has_aggressive']:
                aggressive_score += aggressive_indicators['score']
                details.append(f"Person {i+1}: {aggressive_indicators['reason']}")

        # Analyze interactions between people
        for i in range(len(people_kp)):
            for j in range(i + 1, len(people_kp)):
                interaction = self._analyze_interaction(
                    people_kp[i], people_kp[j], frame_shape
                )

                if interaction['has_violation']:
                    intimidation_score += interaction['score']
                    details.append(f"P{i+1} & P{j+1}: {interaction['reason']}")

        # Final decision
        total_score = intimidation_score + defensive_score + aggressive_score

        # Multi-detector consensus: Require BOTH posture indicators AND proximity/interaction
        # Further requires BOTH defensive AND (aggressive OR very close proximity)
        # This prevents false positives from kids sitting peacefully with hands on face
        has_interaction = intimidation_score > 0.3  # People interacting closely
        has_very_close_interaction = intimidation_score > 0.5  # Very close/threatening proximity
        has_defensive = defensive_score > 0.5  # Defensive posture detected
        has_aggressive = aggressive_score > 0.3  # Aggressive posture detected

        intimidation_detected = (
            total_score >= 0.8 and  # Higher threshold
            has_interaction and  # Must have close proximity/contact
            has_defensive and  # Must have defensive posture
            (has_aggressive or has_very_close_interaction)  # AND (aggressive OR very close)
        )

        confidence = min(total_score + 0.2, 1.0) if intimidation_detected else 0.9

        if not intimidation_detected:
            details = ["Normal interaction - no concerning body language"]

        return PoseDetection(
            intimidation_detected=intimidation_detected,
            defensive_posture_detected=defensive_score > 0.3,
            aggressive_posture_detected=aggressive_score > 0.3,
            power_imbalance_score=total_score,
            confidence=confidence,
            details=" | ".join(details),
            person_count=person_count,
            keypoints=people_kp
        )

    def _check_defensive_posture(self, kp: np.ndarray) -> Dict:
        """
        Check for defensive posture indicators

        Indicators:
        - Hands near/above face (covering, protecting)
        - Head lowered (looking down)
        - Arms crossed or raised defensively
        - Crouching (hips lower than normal)
        """
        score = 0.0
        reasons = []

        nose = kp[KP_NOSE]
        left_wrist = kp[KP_LEFT_WRIST]
        right_wrist = kp[KP_RIGHT_WRIST]
        left_shoulder = kp[KP_LEFT_SHOULDER]
        right_shoulder = kp[KP_RIGHT_SHOULDER]
        left_hip = kp[KP_LEFT_HIP]

        # Require good confidence for keypoints
        conf_threshold = 0.5

        # 1. Hands near face (defensive)
        if nose[2] > conf_threshold:
            if left_wrist[2] > conf_threshold:
                hand_face_dist = np.sqrt(
                    (left_wrist[0] - nose[0])**2 + (left_wrist[1] - nose[1])**2
                )
                if hand_face_dist < 100:  # pixels
                    score += 0.4
                    reasons.append("left hand covering face")

            if right_wrist[2] > conf_threshold:
                hand_face_dist = np.sqrt(
                    (right_wrist[0] - nose[0])**2 + (right_wrist[1] - nose[1])**2
                )
                if hand_face_dist < 100:
                    score += 0.4
                    reasons.append("right hand covering face")

        # 2. Hands raised above shoulders (defensive blocking)
        if (left_shoulder[2] > conf_threshold and left_wrist[2] > conf_threshold):
            if left_wrist[1] < left_shoulder[1] - 50:  # Hand above shoulder
                score += 0.3
                reasons.append("hands raised defensively")

        # 3. Crouching (fear response)
        if (left_shoulder[2] > conf_threshold and left_hip[2] > conf_threshold):
            torso_height = abs(left_shoulder[1] - left_hip[1])
            if torso_height < 80:  # Compressed torso
                score += 0.3
                reasons.append("crouching posture")

        return {
            'has_defensive': score > 0,
            'score': min(score, 1.0),
            'reason': ", ".join(reasons) if reasons else "none"
        }

    def _check_aggressive_posture(self, kp: np.ndarray) -> Dict:
        """
        Check for aggressive posture indicators

        Indicators:
        - Arms raised (threatening)
        - Forward lean (invading space)
        - Wide stance (power pose)
        - Pointing gesture
        """
        score = 0.0
        reasons = []

        left_shoulder = kp[KP_LEFT_SHOULDER]
        right_shoulder = kp[KP_RIGHT_SHOULDER]
        left_elbow = kp[KP_LEFT_ELBOW]
        right_elbow = kp[KP_RIGHT_ELBOW]
        left_wrist = kp[KP_LEFT_WRIST]
        right_wrist = kp[KP_RIGHT_WRIST]
        nose = kp[KP_NOSE]

        conf_threshold = 0.5

        # 1. Raised arms (threatening gesture)
        if (right_shoulder[2] > conf_threshold and right_elbow[2] > conf_threshold):
            if right_elbow[1] < right_shoulder[1]:  # Elbow above shoulder
                score += 0.3
                reasons.append("raised arms")

        # 2. Forward lean (nose ahead of shoulders)
        if (nose[2] > conf_threshold and left_shoulder[2] > conf_threshold
            and right_shoulder[2] > conf_threshold):
            shoulder_center_x = (left_shoulder[0] + right_shoulder[0]) / 2
            if nose[0] > shoulder_center_x + 30:  # Forward of shoulders
                score += 0.2
                reasons.append("forward lean")

        # 3. Pointing/jabbing (arm extended toward someone)
        if (right_shoulder[2] > conf_threshold and right_wrist[2] > conf_threshold):
            arm_extension = abs(right_wrist[0] - right_shoulder[0])
            if arm_extension > 150:  # Extended arm
                score += 0.3
                reasons.append("extended arm (pointing/jabbing)")

        return {
            'has_aggressive': score > 0,
            'score': min(score, 1.0),
            'reason': ", ".join(reasons) if reasons else "none"
        }

    def _analyze_interaction(
        self,
        kp1: np.ndarray,
        kp2: np.ndarray,
        frame_shape: Tuple
    ) -> Dict:
        """
        Analyze interaction between two people

        Looks for:
        - Proximity (too close)
        - Height imbalance (power dynamic)
        - Physical contact (hand on other person)
        - Cornering (backed against edge)
        """
        score = 0.0
        reasons = []

        # Get center points (average of shoulders)
        def get_center(kp):
            left_shoulder = kp[KP_LEFT_SHOULDER]
            right_shoulder = kp[KP_RIGHT_SHOULDER]
            if left_shoulder[2] > 0.5 and right_shoulder[2] > 0.5:
                return (left_shoulder[0] + right_shoulder[0]) / 2, \
                       (left_shoulder[1] + right_shoulder[1]) / 2
            return None, None

        cx1, cy1 = get_center(kp1)
        cx2, cy2 = get_center(kp2)

        if cx1 is None or cx2 is None:
            return {'has_violation': False, 'score': 0.0, 'reason': 'insufficient keypoints'}

        # 1. Proximity
        distance = np.sqrt((cx1 - cx2)**2 + (cy1 - cy2)**2)
        if distance < 150:  # Very close
            score += 0.3
            reasons.append(f"close proximity ({distance:.0f}px)")

        # 2. Height imbalance
        height_diff = abs(cy1 - cy2)
        if height_diff > 80:  # Significant height difference
            score += 0.2
            reasons.append(f"height imbalance ({height_diff:.0f}px)")

        # 3. Cornering (person near edge of frame)
        frame_h, frame_w = frame_shape[:2]
        margin = 100

        if (kp2[KP_NOSE][0] < margin or kp2[KP_NOSE][0] > frame_w - margin or
            kp2[KP_NOSE][1] < margin or kp2[KP_NOSE][1] > frame_h - margin):
            if distance < 200:  # And someone is close
                score += 0.4
                reasons.append("person cornered at edge")

        # 4. Physical contact (hand of person 1 near body of person 2)
        p1_left_wrist = kp1[KP_LEFT_WRIST]
        p1_right_wrist = kp1[KP_RIGHT_WRIST]
        p2_nose = kp2[KP_NOSE]

        if p1_right_wrist[2] > 0.5 and p2_nose[2] > 0.5:
            hand_to_p2 = np.sqrt(
                (p1_right_wrist[0] - p2_nose[0])**2 +
                (p1_right_wrist[1] - p2_nose[1])**2
            )
            if hand_to_p2 < 80:  # Hand touching other person
                score += 0.5
                reasons.append("physical contact detected")

        return {
            'has_violation': score > 0.3,
            'score': min(score, 1.0),
            'reason': ", ".join(reasons) if reasons else "normal distance"
        }

    def _no_detection(self) -> PoseDetection:
        """Return result when no people detected"""
        return PoseDetection(
            intimidation_detected=False,
            defensive_posture_detected=False,
            aggressive_posture_detected=False,
            power_imbalance_score=0.0,
            confidence=1.0,
            details="No people detected",
            person_count=0
        )

    def _fallback_detection(self) -> PoseDetection:
        """Return result when YOLO unavailable"""
        return PoseDetection(
            intimidation_detected=False,
            defensive_posture_detected=False,
            aggressive_posture_detected=False,
            power_imbalance_score=0.0,
            confidence=0.0,
            details="Pose detection unavailable (YOLO not loaded)",
            person_count=0
        )


# Convenience function
def detect_pose_body_language(frame: np.ndarray) -> Dict:
    """
    Quick pose-based body language detection

    Args:
        frame: Input image (BGR)

    Returns:
        Dict with detection results
    """
    detector = PoseBodyLanguageDetector()
    result = detector.detect(frame)

    return {
        "intimidation_detected": result.intimidation_detected,
        "defensive_posture": result.defensive_posture_detected,
        "aggressive_posture": result.aggressive_posture_detected,
        "power_imbalance_score": result.power_imbalance_score,
        "confidence": result.confidence,
        "details": result.details,
        "person_count": result.person_count
    }
