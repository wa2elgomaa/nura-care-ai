"""
Hybrid Router
Routes frames to fast-path detectors or VLM based on confidence

Spec: specs/026-hybrid-fast-path/spec.md
"""
import sys
sys.path.append('/app')  # For Docker imports

import asyncio
import numpy as np
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import time

logger = logging.getLogger(__name__)


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

        # Import detectors (these will use OpenCV, no external dependencies)
        try:
            # These imports will work once the perception service is built
            from detectors.violence_detector import ViolenceDetector
            from detectors.distress_detector import DistressDetector
            from detectors.supervision_detector import SupervisionDetector

            self.violence_detector = ViolenceDetector()
            self.distress_detector = DistressDetector()
            self.supervision_detector = SupervisionDetector()

            logger.info("✓ Fast-path detectors initialized")
        except ImportError as e:
            logger.warning(f"Fast-path detectors not available: {e}")
            logger.warning("Will fall back to VLM-only mode")
            self.violence_detector = None
            self.distress_detector = None
            self.supervision_detector = None

    async def analyze_frame(
        self,
        frame: np.ndarray,
        camera_id: Optional[str] = None
    ) -> ViolationAlert:
        """
        Analyze frame using hybrid approach

        Args:
            frame: Input image (BGR format)
            camera_id: Camera identifier

        Returns:
            ViolationAlert with results
        """
        start_time = time.time()

        # Step 1: Run fast-path detectors (if available)
        if self._fast_path_available():
            fast_path_results = await self._run_fast_path(frame)
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
            self.supervision_detector is not None
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

        return {
            "violence": asdict(violence_result),
            "distress": asdict(distress_result),
            "supervision": asdict(supervision_result)
        }

    def _make_routing_decision(self, fast_path_results: Dict) -> Dict:
        """
        Decide whether to alert directly, send to VLM, or ignore

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

        # Check for high-confidence violations (direct alert)
        if violence["violence_detected"] and violence["confidence"] > 0.9:
            return {
                "route": "direct_alert",
                "confidence": violence["confidence"],
                "primary_violation": "violence"
            }

        if distress["distress_detected"] and distress["confidence"] > 0.85:
            return {
                "route": "direct_alert",
                "confidence": distress["confidence"],
                "primary_violation": "distress"
            }

        if supervision["violation_detected"] and supervision["confidence"] > 0.8:
            return {
                "route": "direct_alert",
                "confidence": supervision["confidence"],
                "primary_violation": "supervision"
            }

        # Check for medium-confidence violations (VLM validation needed)
        if (violence["violence_detected"] and
            0.5 < violence["confidence"] <= 0.9):
            return {
                "route": "vlm_validation",
                "confidence": violence["confidence"],
                "primary_violation": "violence"
            }

        if (distress["distress_detected"] and
            0.5 < distress["confidence"] <= 0.85):
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

        # TODO: Call VLM with improved prompts
        # For now, return placeholder
        return "VLM analysis would go here"

    def _create_alert_from_fast_path(
        self,
        fast_path_results: Dict,
        decision: Dict
    ) -> ViolationAlert:
        """Create alert from fast-path detection"""
        violation_type = decision["primary_violation"]
        result = fast_path_results[violation_type]

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
