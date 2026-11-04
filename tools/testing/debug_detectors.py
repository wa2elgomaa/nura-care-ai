#!/usr/bin/env python3
"""
Debug Detector Script
Shows raw detector scores to understand why violations aren't being detected
"""
import sys
import cv2
import numpy as np
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "nura-detectors" / "src"))

from nura_detectors import (
    ViolenceDetector,
    DistressDetector,
    SupervisionDetector,
    BodyLanguageDetector
)


def debug_image(image_path):
    """Debug all detectors on an image"""
    print(f"\n{'='*70}")
    print(f"DEBUG DETECTORS: {Path(image_path).name}")
    print(f"{'='*70}\n")

    # Load image
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"❌ Failed to load {image_path}")
        return

    print(f"✓ Image loaded: {frame.shape}")

    # Initialize detectors
    print("\n🔧 Initializing detectors...")
    violence_det = ViolenceDetector()
    distress_det = DistressDetector()
    supervision_det = SupervisionDetector()
    body_language_det = BodyLanguageDetector()
    print("✓ All detectors initialized\n")

    # Run violence detector
    print("="*70)
    print("🔴 VIOLENCE DETECTOR")
    print("="*70)
    v_result = violence_det.detect(frame)
    print(f"  Detected: {v_result.violence_detected}")
    print(f"  Confidence: {v_result.confidence:.2%}")
    print(f"  Action Type: {v_result.action_type}")
    print(f"  Severity: {v_result.severity}")
    print(f"  Details: {v_result.details}")
    print()

    # Run distress detector
    print("="*70)
    print("😢 DISTRESS DETECTOR")
    print("="*70)
    d_result = distress_det.detect(frame)
    print(f"  Detected: {d_result.distress_detected}")
    print(f"  Confidence: {d_result.confidence:.2%}")
    print(f"  Face Count: {d_result.face_count}")
    print(f"  Max Score: {d_result.max_distress_score:.2%}")
    print(f"  Details: {d_result.details}")
    print()

    # Run supervision detector
    print("="*70)
    print("👥 SUPERVISION DETECTOR")
    print("="*70)
    s_result = supervision_det.detect(frame)
    print(f"  Violation: {s_result.violation_detected}")
    print(f"  Confidence: {s_result.confidence:.2%}")
    print(f"  Children: {s_result.child_count}")
    print(f"  Adults: {s_result.adult_count}")
    print(f"  Ratio: {s_result.ratio:.2f}")
    print(f"  Required: {supervision_det.required_ratio:.2f}")
    print(f"  Details: {s_result.details}")
    print()

    # Run body language detector
    print("="*70)
    print("🧍 BODY LANGUAGE DETECTOR")
    print("="*70)
    bl_result = body_language_det.detect(frame)
    print(f"  Intimidation: {bl_result.intimidation_detected}")
    print(f"  Defensive Posture: {bl_result.defensive_posture_detected}")
    print(f"  Power Imbalance Score: {bl_result.power_imbalance_score:.2%}")
    print(f"  Confidence: {bl_result.confidence:.2%}")
    print(f"  Person Count: {len(bl_result.person_positions)}")
    print(f"  Details: {bl_result.details}")
    print()

    # Summary
    print("="*70)
    print("📊 SUMMARY")
    print("="*70)
    any_violation = (
        v_result.violence_detected or
        d_result.distress_detected or
        s_result.violation_detected or
        bl_result.intimidation_detected
    )

    if any_violation:
        print("🚨 VIOLATIONS DETECTED:")
        if v_result.violence_detected:
            print(f"  - Violence (conf: {v_result.confidence:.0%})")
        if d_result.distress_detected:
            print(f"  - Distress (conf: {d_result.confidence:.0%})")
        if s_result.violation_detected:
            print(f"  - Supervision (conf: {s_result.confidence:.0%})")
        if bl_result.intimidation_detected:
            print(f"  - Intimidation (conf: {bl_result.confidence:.0%})")
    else:
        print("✅ No violations detected by any detector")
        print("\n💡 Detection thresholds:")
        print(f"  - Violence: needs >0.5 score (current has motion={v_result.details})")
        print(f"  - Distress: needs >=0.5 distress_score (current max={d_result.max_distress_score:.2%})")
        print(f"  - Supervision: needs ratio <{supervision_det.required_ratio:.2f} (current={s_result.ratio:.2f})")
        print(f"  - Intimidation: needs score >=0.5 (current={bl_result.power_imbalance_score:.2%})")

    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_detectors.py <image_path>")
        print("\nExamples:")
        print("  python tools/testing/debug_detectors.py tests/images/test_classroom2.jpg")
        print("  python tools/testing/debug_detectors.py tests/images/test_violence.jpg")
        sys.exit(1)

    debug_image(sys.argv[1])
