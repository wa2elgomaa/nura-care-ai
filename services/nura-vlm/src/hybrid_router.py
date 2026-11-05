"""
Hybrid Router
Routes frames to fast-path detectors or VLM based on confidence

Spec: specs/026-hybrid-fast-path/spec.md
"""
import sys
sys.path.append('/app')  # For Docker imports

import asyncio
import numpy as np
import os
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import time

logger = logging.getLogger(__name__)

# Load thresholds from environment variables
DIRECT_ALERT_VIOLENCE_THRESHOLD = float(os.getenv('DIRECT_ALERT_VIOLENCE_THRESHOLD', '0.65'))
DIRECT_ALERT_BODY_LANGUAGE_THRESHOLD = float(os.getenv('DIRECT_ALERT_BODY_LANGUAGE_THRESHOLD', '0.70'))
DIRECT_ALERT_DISTRESS_THRESHOLD = float(os.getenv('DIRECT_ALERT_DISTRESS_THRESHOLD', '0.70'))
DIRECT_ALERT_SUPERVISION_THRESHOLD = float(os.getenv('DIRECT_ALERT_SUPERVISION_THRESHOLD', '0.80'))

VLM_VALIDATION_MIN_THRESHOLD = float(os.getenv('VLM_VALIDATION_MIN_THRESHOLD', '0.5'))
VLM_VALIDATION_VIOLENCE_MAX = float(os.getenv('VLM_VALIDATION_VIOLENCE_MAX', '0.9'))
VLM_VALIDATION_BODY_LANGUAGE_MAX = float(os.getenv('VLM_VALIDATION_BODY_LANGUAGE_MAX', '0.85'))
VLM_VALIDATION_DISTRESS_MAX = float(os.getenv('VLM_VALIDATION_DISTRESS_MAX', '0.85'))


class DetectionSource(Enum):
    """Source of detection"""
    FAST_PATH = "fast_path"
    VLM = "vlm"
    HYBRID = "hybrid"  # Both fast-path and VLM


@dataclass
class ViolationAlert:
    """Unified violation alert"""
    violation_detected: bool
    violation_type: str  # "violence", "distress", "supervision", "multiple"
    severity: str  # "low", "medium", "high"
    confidence: float
    source: str  # "fast_path", "vlm", "hybrid"
    details: str
    fast_path_results: Optional[Dict] = None
    vlm_result: Optional[str] = None
    processing_time_ms: float = 0.0
    immediate_action_required: bool = False


class HybridRouter:
    """
    Routes frames to fast-path detectors or VLM based on:
    1. Fast-path detector confidence
    2. Violation type
    3. Ambiguity level

    Decision Logic:
    - High confidence violation (>0.9) → Direct alert (fast-path only)
    - Medium confidence (0.5-0.9) → Send to VLM for validation
    - Low confidence (<0.5) → No violation (fast-path only)
    - Ambiguous cases → Always send to VLM
    """

    def __init__(self, vlm_client=None):
        """
        Args:
            vlm_client: VLM client for complex analysis (optional, will lazy-load)
        """
        self.vlm_client = vlm_client

        # Lazy-load detectors on first use
        self._detectors_initialized = False
        self.violence_detector = None
        self.distress_detector = None
        self.supervision_detector = None
        self.body_language_detector = None
        self.pose_detector = None  # ML-based pose detector (Phase 2)
        self.temporal_detector = None  # Temporal sequence detector (Phase 3)

        # Frame buffer for temporal analysis (per camera)
        self.frame_buffers = {}  # camera_id -> list of frames
        self.enable_temporal = os.getenv('ENABLE_TEMPORAL_DETECTION', 'false').lower() == 'true'

    def _init_detectors(self):
        """Lazy-load detectors on first use"""
        if self._detectors_initialized:
            return

        self._detectors_initialized = True

        # Import detectors from shared package
        try:
            from nura_detectors import (
                ViolenceDetector,
                DistressDetector,
                SupervisionDetector,
                BodyLanguageDetector,
                PoseBodyLanguageDetector
            )

            self.violence_detector = ViolenceDetector()
            self.distress_detector = DistressDetector()
            self.supervision_detector = SupervisionDetector()
            self.body_language_detector = BodyLanguageDetector()

            # Try to load ML-based pose detector (Phase 2)
            try:
                self.pose_detector = PoseBodyLanguageDetector(model_size='n')  # nano = fastest
                logger.info("✓ ML pose detector initialized (YOLOv8-pose)")
            except Exception as pose_err:
                logger.warning(f"Pose detector unavailable: {pose_err}")
                self.pose_detector = None

            # Try to load temporal sequence detector (Phase 3)
            if self.enable_temporal:
                try:
                    from nura_detectors import TemporalViolenceDetector

                    # Check if we have a trained model
                    model_path = os.getenv('TEMPORAL_MODEL_PATH', 'models/temporal_violence.h5')
                    if os.path.exists(model_path):
                        self.temporal_detector = TemporalViolenceDetector(
                            sequence_length=int(os.getenv('TEMPORAL_SEQUENCE_LENGTH', '20')),
                            model_path=model_path
                        )
                        logger.info(f"✓ Temporal detector initialized (model: {model_path})")
                    else:
                        logger.warning(f"Temporal model not found at {model_path}, temporal detection disabled")
                        self.temporal_detector = None
                except (ImportError, Exception) as temp_err:
                    logger.warning(f"Temporal detector unavailable: {temp_err}")
                    self.temporal_detector = None

            logger.info("✓ Fast-path detectors initialized (violence, distress, supervision, body_language, pose)")
        except (ImportError, Exception) as e:
            logger.warning(f"Fast-path detectors not available: {e}")
            logger.warning("Will fall back to VLM-only mode")
            self.violence_detector = None
            self.distress_detector = None
            self.supervision_detector = None
            self.body_language_detector = None
            self.pose_detector = None

    async def analyze_frame(
        self,
        frame: np.ndarray,
        camera_id: Optional[str] = None
    ) -> ViolationAlert:
        """
        Analyze frame using hybrid approach (with optional temporal analysis)

        Args:
            frame: Input image (BGR format)
            camera_id: Camera identifier

        Returns:
            ViolationAlert with results
        """
        start_time = time.time()

        # Lazy-init detectors on first use
        self._init_detectors()

        # Step 0: Add frame to temporal buffer (if enabled)
        temporal_result = None
        if self.temporal_detector and camera_id:
            temporal_ready = self.temporal_detector.add_frame(frame)
            if temporal_ready:
                temporal_result = self.temporal_detector.detect(ready_for_inference=True)
                logger.info(f"Temporal analysis: violence_prob={temporal_result.violence_probability:.2f}, "
                           f"detected={temporal_result.violence_detected}")

        # Step 1: Run fast-path detectors (if available)
        if self._fast_path_available():
            fast_path_results = await self._run_fast_path(frame)

            # Incorporate temporal result if available
            if temporal_result:
                fast_path_results["temporal"] = {
                    "violence_detected": temporal_result.violence_detected,
                    "confidence": temporal_result.confidence,
                    "probability": temporal_result.violence_probability,
                    "sequence_length": temporal_result.sequence_length,
                    "details": temporal_result.details
                }

            decision = self._make_routing_decision(fast_path_results)

            # High confidence → Direct alert (no VLM needed)
            if decision["route"] == "direct_alert":
                alert = self._create_alert_from_fast_path(
                    fast_path_results,
                    decision
                )
                alert.processing_time_ms = (time.time() - start_time) * 1000
                logger.info(
                    f"Fast-path alert: {alert.violation_type} "
                    f"(confidence: {alert.confidence:.2f}, "
                    f"{alert.processing_time_ms:.0f}ms)"
                )
                return alert

            # No violation → Return negative result
            elif decision["route"] == "no_violation":
                alert = ViolationAlert(
                    violation_detected=False,
                    violation_type="none",
                    severity="low",
                    confidence=decision["confidence"],
                    source=DetectionSource.FAST_PATH.value,
                    details="No violations detected by fast-path",
                    fast_path_results=fast_path_results,
                    processing_time_ms=(time.time() - start_time) * 1000
                )
                return alert

            # Ambiguous → Send to VLM
            else:  # decision["route"] == "vlm_validation"
                logger.info(
                    f"Ambiguous detection (conf: {decision['confidence']:.2f}), "
                    f"sending to VLM for validation"
                )
                vlm_result = await self._analyze_with_vlm(
                    frame,
                    context=fast_path_results
                )
                alert = self._create_alert_from_hybrid(
                    fast_path_results,
                    vlm_result,
                    decision
                )
                alert.processing_time_ms = (time.time() - start_time) * 1000
                logger.info(
                    f"Hybrid alert: {alert.violation_type} "
                    f"(confidence: {alert.confidence:.2f}, "
                    f"{alert.processing_time_ms:.0f}ms)"
                )
                return alert

        # Step 2: Fall back to VLM-only if fast-path not available
        else:
            logger.warning("Fast-path not available, using VLM-only mode")
            vlm_result = await self._analyze_with_vlm(frame, context=None)
            alert = ViolationAlert(
                violation_detected=True,  # Assume VLM found something
                violation_type="unknown",
                severity="medium",
                confidence=0.7,
                source=DetectionSource.VLM.value,
                details="VLM-only analysis (fast-path unavailable)",
                vlm_result=vlm_result,
                processing_time_ms=(time.time() - start_time) * 1000
            )
            return alert

    def _fast_path_available(self) -> bool:
        """Check if fast-path detectors are available"""
        return (
            self.violence_detector is not None and
            self.distress_detector is not None and
            self.supervision_detector is not None and
            self.body_language_detector is not None
        )

    async def _run_fast_path(self, frame: np.ndarray) -> Dict:
        """
        Run all fast-path detectors in parallel

        Returns:
            Dict with results from all detectors
        """
        # Run detectors (these are CPU-bound, but fast <100ms total)
        violence_result = self.violence_detector.detect(frame)
        distress_result = self.distress_detector.detect(frame)
        supervision_result = self.supervision_detector.detect(frame)

        # Prefer ML pose detector if available, fallback to heuristic
        if self.pose_detector is not None:
            body_language_result = self.pose_detector.detect(frame)
        else:
            body_language_result = self.body_language_detector.detect(frame)

        # Log detector scores for debugging
        logger.info(
            f"Fast-path scores: "
            f"violence={violence_result.confidence:.2f} (detected={violence_result.violence_detected}), "
            f"distress={distress_result.confidence:.2f} (detected={distress_result.distress_detected}), "
            f"supervision={supervision_result.confidence:.2f} (violation={supervision_result.violation_detected}), "
            f"body_language={body_language_result.power_imbalance_score:.2f} (intimidation={body_language_result.intimidation_detected})"
        )

        return {
            "violence": asdict(violence_result),
            "distress": asdict(distress_result),
            "supervision": asdict(supervision_result),
            "body_language": asdict(body_language_result)
        }

    def _make_routing_decision(self, fast_path_results: Dict) -> Dict:
        """
        Decide whether to alert directly, send to VLM, or ignore
        Now includes temporal detection results if available

        Returns:
            {
                "route": "direct_alert" | "vlm_validation" | "no_violation",
                "confidence": float,
                "primary_violation": str
            }
        """
        violence = fast_path_results["violence"]
        distress = fast_path_results["distress"]
        supervision = fast_path_results["supervision"]
        body_language = fast_path_results["body_language"]
        temporal = fast_path_results.get("temporal")  # May be None

        # Check temporal detector first (highest priority for sustained violence)
        if temporal and temporal["violence_detected"]:
            # Temporal detector found sustained violence over sequence
            if temporal["probability"] > 0.7:  # High confidence sustained violence
                return {
                    "route": "direct_alert",
                    "confidence": temporal["confidence"],
                    "primary_violation": "sustained_violence"
                }
            elif temporal["probability"] > 0.5:  # Medium confidence, validate with VLM
                return {
                    "route": "vlm_validation",
                    "confidence": temporal["confidence"],
                    "primary_violation": "sustained_violence"
                }

        # Check for high-confidence violations (direct alert)
        # Thresholds configured via environment variables
        if violence["violence_detected"] and violence["confidence"] > DIRECT_ALERT_VIOLENCE_THRESHOLD:
            return {
                "route": "direct_alert",
                "confidence": violence["confidence"],
                "primary_violation": "violence"
            }

        if body_language["intimidation_detected"] and body_language["confidence"] > DIRECT_ALERT_BODY_LANGUAGE_THRESHOLD:
            return {
                "route": "direct_alert",
                "confidence": body_language["confidence"],
                "primary_violation": "psychological_bullying"
            }

        if distress["distress_detected"] and distress["confidence"] > DIRECT_ALERT_DISTRESS_THRESHOLD:
            return {
                "route": "direct_alert",
                "confidence": distress["confidence"],
                "primary_violation": "distress"
            }

        if supervision["violation_detected"] and supervision["confidence"] > DIRECT_ALERT_SUPERVISION_THRESHOLD:
            return {
                "route": "direct_alert",
                "confidence": supervision["confidence"],
                "primary_violation": "supervision"
            }

        # Check for medium-confidence violations (VLM validation needed)
        if (violence["violence_detected"] and
            VLM_VALIDATION_MIN_THRESHOLD < violence["confidence"] <= VLM_VALIDATION_VIOLENCE_MAX):
            return {
                "route": "vlm_validation",
                "confidence": violence["confidence"],
                "primary_violation": "violence"
            }

        if (body_language["intimidation_detected"] and
            VLM_VALIDATION_MIN_THRESHOLD < body_language["confidence"] <= VLM_VALIDATION_BODY_LANGUAGE_MAX):
            return {
                "route": "vlm_validation",
                "confidence": body_language["confidence"],
                "primary_violation": "psychological_bullying"
            }

        if (distress["distress_detected"] and
            VLM_VALIDATION_MIN_THRESHOLD < distress["confidence"] <= VLM_VALIDATION_DISTRESS_MAX):
            return {
                "route": "vlm_validation",
                "confidence": distress["confidence"],
                "primary_violation": "distress"
            }

        # No violation detected
        return {
            "route": "no_violation",
            "confidence": 0.9,
            "primary_violation": "none"
        }

    async def _analyze_with_vlm(
        self,
        frame: np.ndarray,
        context: Optional[Dict] = None
    ) -> str:
        """
        Analyze with VLM (slow but accurate for complex cases)

        Args:
            frame: Input image
            context: Fast-path results to give VLM context

        Returns:
            VLM analysis string
        """
        if self.vlm_client is None:
            logger.error("VLM client not initialized")
            return "VLM unavailable"

        # Import here to avoid circular dependency
        import base64
        import cv2
        from src.prompts.childcare_prompts import get_prompt_with_context

        # Encode frame to base64
        _, buffer = cv2.imencode('.jpg', frame)
        image_b64 = base64.b64encode(buffer).decode('utf-8')

        # Determine prompt type based on context
        prompt_type = "general"
        fast_path_context = {}

        if context:
            # Check which violation was flagged
            if context.get("violence", {}).get("violence_detected"):
                prompt_type = "violence"
                fast_path_context = {"violence": context["violence"]}
            elif context.get("distress", {}).get("distress_detected"):
                prompt_type = "distress"
                fast_path_context = {"distress": context["distress"]}
            elif context.get("supervision", {}).get("violation_detected"):
                prompt_type = "supervision"
                fast_path_context = {"supervision": context["supervision"]}

        # Get context-aware prompt
        prompt = get_prompt_with_context(prompt_type, fast_path_context)

        # Call VLM
        result = await self.vlm_client.analyze_scene(
            image_base64=image_b64,
            prompt=prompt,
            temperature=0.3
        )

        return result.get("raw_response", "No response from VLM")

    def _create_alert_from_fast_path(
        self,
        fast_path_results: Dict,
        decision: Dict
    ) -> ViolationAlert:
        """Create alert from fast-path detection"""
        violation_type = decision["primary_violation"]

        # Map violation type to detector result key
        detector_key_map = {
            "violence": "violence",
            "distress": "distress",
            "supervision": "supervision",
            "psychological_bullying": "body_language"
        }

        detector_key = detector_key_map.get(violation_type, violation_type)
        result = fast_path_results.get(detector_key, {})

        return ViolationAlert(
            violation_detected=True,
            violation_type=violation_type,
            severity=result.get("severity", "medium"),
            confidence=decision["confidence"],
            source=DetectionSource.FAST_PATH.value,
            details=result.get("details", "Fast-path detection"),
            fast_path_results=fast_path_results,
            immediate_action_required=(
                result.get("severity") == "high" or
                result.get("immediate_attention_needed", False)
            )
        )

    def _create_alert_from_hybrid(
        self,
        fast_path_results: Dict,
        vlm_result: str,
        decision: Dict
    ) -> ViolationAlert:
        """Create alert from hybrid detection (fast-path + VLM)"""
        violation_type = decision["primary_violation"]

        # Parse VLM verdict to check if it confirmed or rejected the fast-path detection
        vlm_confirmed = self._parse_vlm_verdict(vlm_result, violation_type)

        # If VLM says no violation, trust it over fast-path
        if not vlm_confirmed:
            return ViolationAlert(
                violation_detected=False,
                violation_type="none",
                severity="low",
                confidence=0.1,
                source=DetectionSource.HYBRID.value,
                details=f"Fast-path detected {violation_type}, but VLM rejected it as false positive",
                fast_path_results=fast_path_results,
                vlm_result=vlm_result,
                immediate_action_required=False
            )

        # VLM confirmed the violation
        return ViolationAlert(
            violation_detected=True,
            violation_type=violation_type,
            severity="medium",  # VLM validation suggests not highest severity
            confidence=min(decision["confidence"] * 1.2, 0.95),  # Boost confidence
            source=DetectionSource.HYBRID.value,
            details=f"Fast-path + VLM validation: {violation_type}",
            fast_path_results=fast_path_results,
            vlm_result=vlm_result,
            immediate_action_required=False  # VLM validation means not immediate
        )

    def _parse_vlm_verdict(self, vlm_result: str, violation_type: str) -> bool:
        """
        Parse VLM verdict from JSON to determine if it confirmed the violation

        Returns:
            True if VLM confirmed, False if VLM rejected
        """
        import json
        import re

        # Try to extract JSON from markdown code fence or raw JSON
        try:
            # Look for JSON in markdown code fence first
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', vlm_result, re.DOTALL)
            if json_match:
                verdict = json.loads(json_match.group(1))
            else:
                # Try to find raw JSON object
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', vlm_result, re.DOTALL)
                if json_match:
                    verdict = json.loads(json_match.group(0))
                else:
                    verdict = None

            if verdict:
                # Successfully parsed JSON - extract confirmation
                if violation_type == "violence":
                    confirmed = verdict.get("violence_confirmed", False)
                elif violation_type == "distress":
                    confirmed = verdict.get("distress_confirmed", False)
                else:
                    # Fallback to fast_path_correct
                    confirmed = verdict.get("fast_path_correct", True)

                # Log the parsed verdict
                logger.info(f"VLM JSON verdict parsed: {json.dumps(verdict, indent=2)}")
                logger.info(f"Violation type '{violation_type}' confirmed: {confirmed}")
                return bool(confirmed)

        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Failed to parse VLM JSON response, falling back to text parsing: {e}")

        # Fallback to text-based parsing (for old format responses)
        vlm_lower = vlm_result.lower()

        # Check for explicit confirmation/rejection (JSON format)
        if violation_type == "violence":
            if any(x in vlm_lower for x in ["violence_confirmed\": true", "violence_confirmed\":true"]):
                return True
            if any(x in vlm_lower for x in ["violence_confirmed\": false", "violence_confirmed\":false", "violence_confirmed: no"]):
                return False

        elif violation_type == "distress":
            if any(x in vlm_lower for x in ["distress_confirmed\": true", "distress_confirmed\":true"]):
                return True
            if any(x in vlm_lower for x in ["distress_confirmed\": false", "distress_confirmed\":false", "distress_confirmed: no"]):
                return False

        # Check fast_path_correct (both JSON and old text format)
        if any(x in vlm_lower for x in ["fast_path_correct\": false", "fast_path_correct\":false", "fast_path_correct: no"]):
            return False
        if any(x in vlm_lower for x in ["fast_path_correct\": true", "fast_path_correct\":true", "fast_path_correct: yes"]):
            return True

        # Default: assume VLM confirmed (conservative - alert if unsure)
        logger.warning(f"Could not parse VLM verdict for {violation_type}, defaulting to confirmed")
        return True
