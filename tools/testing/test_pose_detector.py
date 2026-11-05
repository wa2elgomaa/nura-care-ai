#!/usr/bin/env python3
"""
Test Pose Detector vs Old HOG Detector
Compare accuracy improvement
"""
import sys
import cv2
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "nura-detectors" / "src"))

from nura_detectors import BodyLanguageDetector, PoseBodyLanguageDetector

def test_image(image_path, expected_violation=True):
    """Test both detectors on an image"""
    print(f"\n{'='*70}")
    print(f"Testing: {Path(image_path).name}")
    print(f"Expected: {'VIOLATION' if expected_violation else 'NO VIOLATION'}")
    print(f"{'='*70}\n")

    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Could not load {image_path}")
        return

    # Test old HOG detector
    print("🔧 OLD DETECTOR (HOG-based):")
    old_detector = BodyLanguageDetector()
    old_result = old_detector.detect(img)
    print(f"   Intimidation: {old_result.intimidation_detected}")
    print(f"   Score: {old_result.power_imbalance_score:.2f}")
    print(f"   Details: {old_result.details}")

    old_correct = old_result.intimidation_detected == expected_violation
    print(f"   Result: {'✅ CORRECT' if old_correct else '❌ WRONG'}")

    # Test new pose detector
    print("\n⭐ NEW DETECTOR (YOLOv8 Pose):")
    new_detector = PoseBodyLanguageDetector(model_size='n')
    new_result = new_detector.detect(img)
    print(f"   Intimidation: {new_result.intimidation_detected}")
    print(f"   Defensive: {new_result.defensive_posture_detected}")
    print(f"   Aggressive: {new_result.aggressive_posture_detected}")
    print(f"   Score: {new_result.power_imbalance_score:.2f}")
    print(f"   People: {new_result.person_count}")
    print(f"   Details: {new_result.details}")

    new_correct = new_result.intimidation_detected == expected_violation
    print(f"   Result: {'✅ CORRECT' if new_correct else '❌ WRONG'}")

    # Comparison
    print(f"\n📊 COMPARISON:")
    if not old_correct and new_correct:
        print(f"   🎉 IMPROVEMENT! New detector fixed the issue!")
    elif old_correct and not new_correct:
        print(f"   ⚠️  REGRESSION! New detector worse than old!")
    elif old_correct and new_correct:
        print(f"   ✅ Both correct")
    else:
        print(f"   ❌ Both wrong - need more tuning")

    return old_correct, new_correct


def main():
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║       POSE DETECTOR vs HOG DETECTOR COMPARISON           ║")
    print("╚═══════════════════════════════════════════════════════════╝")

    test_cases = [
        ("tests/images/test_classroom2.jpg", True, "Confrontation - should detect"),
        ("tests/images/test_violence.jpg", True, "Intimidation - should detect"),
        ("tests/images/test_classroom1.jpg", False, "Normal - should NOT detect"),
    ]

    results = []
    for image_path, expected, description in test_cases:
        if Path(image_path).exists():
            old_correct, new_correct = test_image(image_path, expected)
            results.append({
                'image': Path(image_path).name,
                'description': description,
                'old_correct': old_correct,
                'new_correct': new_correct
            })

    # Summary
    print("\n\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)

    old_accuracy = sum(1 for r in results if r['old_correct']) / len(results) * 100
    new_accuracy = sum(1 for r in results if r['new_correct']) / len(results) * 100

    print(f"\nOLD HOG Detector: {old_accuracy:.0f}% accuracy ({sum(1 for r in results if r['old_correct'])}/{len(results)})")
    print(f"NEW Pose Detector: {new_accuracy:.0f}% accuracy ({sum(1 for r in results if r['new_correct'])}/{len(results)})")
    print(f"\nImprovement: {new_accuracy - old_accuracy:+.0f} percentage points")

    if new_accuracy > old_accuracy:
        print("\n🎉 Pose detector is BETTER!")
    elif new_accuracy == old_accuracy:
        print("\n➡️  Same accuracy (need more test cases)")
    else:
        print("\n⚠️  Pose detector needs tuning")

    print("\n" + "="*70)


if __name__ == "__main__":
    main()
