#!/usr/bin/env python3
"""
Hybrid System Validation Suite
Comprehensive testing for 99% detection accuracy

Features:
- Video frame extraction (simulates camera feeds)
- Image dataset testing
- Ground truth labeling
- Accuracy metrics (precision, recall, F1)
- False positive/negative analysis
- Detailed reports

Usage:
    python tools/testing/hybrid_validation_suite.py --mode images
    python tools/testing/hybrid_validation_suite.py --mode videos --sample 10
    python tools/testing/hybrid_validation_suite.py --mode full --report
"""

import sys
import os
import json
import time
import base64
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import requests

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    print("⚠️  OpenCV not available - video frame extraction disabled")


@dataclass
class GroundTruth:
    """Ground truth label for test case"""
    has_violation: bool
    violation_type: str  # violence, distress, supervision, psychological_bullying, none
    severity: str  # low, medium, high
    description: str
    confidence: float = 1.0


@dataclass
class TestResult:
    """Test result with comparison to ground truth"""
    image_path: str
    ground_truth: GroundTruth
    predicted_violation: bool
    predicted_type: str
    predicted_severity: str
    predicted_confidence: float
    processing_time_ms: float
    source: str  # fast_path, vlm, hybrid
    correct: bool
    error_type: Optional[str] = None  # true_positive, false_positive, false_negative, true_negative


class HybridTester:
    """Comprehensive hybrid system tester"""

    def __init__(self, vlm_url: str = "http://localhost:8001"):
        self.vlm_url = vlm_url
        self.results: List[TestResult] = []

    def test_image(self, image_path: str, ground_truth: GroundTruth) -> TestResult:
        """Test single image with hybrid endpoint"""
        try:
            # Load and encode image
            with open(image_path, 'rb') as f:
                image_b64 = base64.b64encode(f.read()).decode('utf-8')

            # Call hybrid endpoint
            start_time = time.time()
            response = requests.post(
                f"{self.vlm_url}/analyze/hybrid",
                json={"image_base64": image_b64},
                timeout=60
            )
            elapsed_ms = (time.time() - start_time) * 1000

            if response.status_code != 200:
                return TestResult(
                    image_path=image_path,
                    ground_truth=ground_truth,
                    predicted_violation=False,
                    predicted_type="error",
                    predicted_severity="low",
                    predicted_confidence=0.0,
                    processing_time_ms=elapsed_ms,
                    source="error",
                    correct=False,
                    error_type="error"
                )

            result = response.json()

            # Determine correctness
            predicted_violation = result['violation_detected']
            correct = (predicted_violation == ground_truth.has_violation)

            # Classify error type
            if ground_truth.has_violation and predicted_violation:
                error_type = "true_positive"
            elif not ground_truth.has_violation and not predicted_violation:
                error_type = "true_negative"
            elif ground_truth.has_violation and not predicted_violation:
                error_type = "false_negative"
            else:  # not ground_truth.has_violation and predicted_violation
                error_type = "false_positive"

            return TestResult(
                image_path=image_path,
                ground_truth=ground_truth,
                predicted_violation=predicted_violation,
                predicted_type=result['violation_type'],
                predicted_severity=result['severity'],
                predicted_confidence=result['confidence'],
                processing_time_ms=result['processing_time_ms'],
                source=result['source'],
                correct=correct,
                error_type=error_type
            )

        except Exception as e:
            print(f"❌ Error testing {image_path}: {e}")
            return TestResult(
                image_path=image_path,
                ground_truth=ground_truth,
                predicted_violation=False,
                predicted_type="error",
                predicted_severity="low",
                predicted_confidence=0.0,
                processing_time_ms=0.0,
                source="error",
                correct=False,
                error_type="error"
            )

    def extract_frames_from_video(
        self,
        video_path: str,
        num_frames: int = 5,
        output_dir: Optional[Path] = None
    ) -> List[str]:
        """Extract frames from video to simulate camera feed"""
        if not HAS_CV2:
            print("❌ OpenCV required for video frame extraction")
            return []

        if output_dir is None:
            output_dir = Path("test_results/video_frames")
        output_dir.mkdir(parents=True, exist_ok=True)

        cap = cv2.VideoCapture(str(video_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if total_frames == 0:
            print(f"⚠️  Could not read video: {video_path}")
            return []

        # Sample frames evenly across video
        frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)

        extracted_frames = []
        video_name = Path(video_path).stem

        for idx, frame_num in enumerate(frame_indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()

            if ret:
                frame_path = output_dir / f"{video_name}_frame_{idx:03d}.jpg"
                cv2.imwrite(str(frame_path), frame)
                extracted_frames.append(str(frame_path))

        cap.release()
        return extracted_frames

    def calculate_metrics(self) -> Dict:
        """Calculate precision, recall, F1, accuracy"""
        if not self.results:
            return {}

        tp = sum(1 for r in self.results if r.error_type == "true_positive")
        fp = sum(1 for r in self.results if r.error_type == "false_positive")
        fn = sum(1 for r in self.results if r.error_type == "false_negative")
        tn = sum(1 for r in self.results if r.error_type == "true_negative")

        total = tp + fp + fn + tn
        accuracy = (tp + tn) / total if total > 0 else 0

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        avg_time = np.mean([r.processing_time_ms for r in self.results])

        return {
            "total_tests": total,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives": tn,
            "avg_processing_time_ms": avg_time
        }

    def generate_report(self, output_path: Optional[Path] = None) -> str:
        """Generate detailed test report"""
        metrics = self.calculate_metrics()

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"test_results/hybrid_validation_{timestamp}.txt")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = []
        report.append("=" * 70)
        report.append("HYBRID SYSTEM VALIDATION REPORT")
        report.append("=" * 70)
        report.append(f"Date: {datetime.now().isoformat()}")
        report.append(f"Total Tests: {metrics['total_tests']}")
        report.append("")

        report.append("ACCURACY METRICS")
        report.append("-" * 70)
        report.append(f"Overall Accuracy: {metrics['accuracy']:.2%}")
        report.append(f"Precision: {metrics['precision']:.2%}")
        report.append(f"Recall: {metrics['recall']:.2%}")
        report.append(f"F1 Score: {metrics['f1_score']:.2%}")
        report.append("")

        report.append("CONFUSION MATRIX")
        report.append("-" * 70)
        report.append(f"True Positives:  {metrics['true_positives']}")
        report.append(f"False Positives: {metrics['false_positives']}")
        report.append(f"False Negatives: {metrics['false_negatives']}")
        report.append(f"True Negatives:  {metrics['true_negatives']}")
        report.append("")

        report.append("PERFORMANCE")
        report.append("-" * 70)
        report.append(f"Average Processing Time: {metrics['avg_processing_time_ms']:.0f}ms")
        report.append("")

        # False positives
        false_positives = [r for r in self.results if r.error_type == "false_positive"]
        if false_positives:
            report.append("FALSE POSITIVES (Need to Fix)")
            report.append("-" * 70)
            for r in false_positives:
                report.append(f"  {Path(r.image_path).name}")
                report.append(f"    Expected: No violation")
                report.append(f"    Got: {r.predicted_type} ({r.predicted_confidence:.0%})")
                report.append("")

        # False negatives
        false_negatives = [r for r in self.results if r.error_type == "false_negative"]
        if false_negatives:
            report.append("FALSE NEGATIVES (Missed Detections)")
            report.append("-" * 70)
            for r in false_negatives:
                report.append(f"  {Path(r.image_path).name}")
                report.append(f"    Expected: {r.ground_truth.violation_type}")
                report.append(f"    Got: No violation")
                report.append(f"    Description: {r.ground_truth.description}")
                report.append("")

        report.append("=" * 70)
        report.append(f"TARGET: 99% Accuracy")
        report.append(f"CURRENT: {metrics['accuracy']:.2%}")
        report.append(f"GAP: {(0.99 - metrics['accuracy']) * 100:.1f} percentage points")
        report.append("=" * 70)

        report_text = "\n".join(report)

        # Save to file
        with open(output_path, 'w') as f:
            f.write(report_text)

        # Also save JSON
        json_path = output_path.with_suffix('.json')
        with open(json_path, 'w') as f:
            json.dump({
                "metrics": metrics,
                "results": [asdict(r) for r in self.results]
            }, f, indent=2, default=str)

        print(f"\n✅ Report saved:")
        print(f"   TXT: {output_path}")
        print(f"   JSON: {json_path}")

        return report_text


# Predefined test cases with ground truth
CHILDCARE_TEST_CASES = [
    # Existing test images
    ("tests/images/test_violence.jpg", GroundTruth(
        has_violation=True,
        violation_type="psychological_bullying",
        severity="high",
        description="Child intimidation with physical contact and power imbalance"
    )),
    ("tests/images/test_classroom2.jpg", GroundTruth(
        has_violation=True,
        violation_type="psychological_bullying",
        severity="medium",
        description="Physical confrontation between children, defensive posture"
    )),
    ("tests/images/test_classroom1.jpg", GroundTruth(
        has_violation=False,
        violation_type="none",
        severity="low",
        description="Normal classroom activity, children at desks"
    )),
]


def main():
    parser = argparse.ArgumentParser(description="Hybrid System Validation Suite")
    parser.add_argument("--mode", choices=["images", "videos", "full"], default="images",
                        help="Test mode: images, videos, or full suite")
    parser.add_argument("--sample", type=int, default=10,
                        help="Number of video frames to extract per video")
    parser.add_argument("--report", action="store_true",
                        help="Generate detailed report")
    parser.add_argument("--url", default="http://localhost:8001",
                        help="VLM service URL")
    parser.add_argument("--dataset", type=str,
                        help="Path to additional test images (directory)")

    args = parser.parse_args()

    print("╔═══════════════════════════════════════════════════════════╗")
    print("║        HYBRID SYSTEM VALIDATION SUITE                    ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()

    tester = HybridTester(vlm_url=args.url)

    # Test predefined images
    print("📸 Testing predefined childcare images...")
    for image_path, ground_truth in CHILDCARE_TEST_CASES:
        if not Path(image_path).exists():
            print(f"⚠️  Skipping {image_path} (not found)")
            continue

        print(f"  Testing: {Path(image_path).name}...", end=" ")
        result = tester.test_image(image_path, ground_truth)

        if result.correct:
            print(f"✅ CORRECT ({result.processing_time_ms:.0f}ms)")
        else:
            print(f"❌ {result.error_type.upper()} ({result.processing_time_ms:.0f}ms)")

        tester.results.append(result)

    # Test additional dataset if provided
    if args.dataset and Path(args.dataset).exists():
        print(f"\n📂 Testing additional dataset: {args.dataset}")
        image_files = list(Path(args.dataset).glob("*.jpg")) + list(Path(args.dataset).glob("*.png"))

        for img_path in image_files[:20]:  # Limit to 20 for now
            # You'll need to label these manually or use a labeling tool
            # For now, assume they need manual review
            print(f"  ⚠️  {img_path.name} - needs ground truth label")

    # Video frame extraction
    if args.mode in ["videos", "full"] and HAS_CV2:
        print(f"\n🎥 Extracting frames from videos (sample={args.sample})...")
        video_dir = Path("tests/data/Videos/FightingA_Part1")

        if video_dir.exists():
            video_files = list(video_dir.glob("*.mp4"))[:3]  # Test 3 videos

            for video_path in video_files:
                print(f"  Processing: {video_path.name}...")
                frames = tester.extract_frames_from_video(
                    str(video_path),
                    num_frames=args.sample
                )
                print(f"    Extracted {len(frames)} frames")

                # Test frames (assuming violence dataset)
                for frame_path in frames:
                    ground_truth = GroundTruth(
                        has_violation=True,
                        violation_type="violence",
                        severity="high",
                        description="Fighting scene from RWF-2000 dataset"
                    )
                    result = tester.test_image(frame_path, ground_truth)
                    tester.results.append(result)

    # Calculate and display metrics
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    metrics = tester.calculate_metrics()

    print(f"Total Tests: {metrics['total_tests']}")
    print(f"Accuracy: {metrics['accuracy']:.2%}")
    print(f"Precision: {metrics['precision']:.2%}")
    print(f"Recall: {metrics['recall']:.2%}")
    print(f"F1 Score: {metrics['f1_score']:.2%}")
    print()
    print(f"True Positives: {metrics['true_positives']}")
    print(f"False Positives: {metrics['false_positives']}")
    print(f"False Negatives: {metrics['false_negatives']}")
    print(f"True Negatives: {metrics['true_negatives']}")
    print()
    print(f"Avg Processing Time: {metrics['avg_processing_time_ms']:.0f}ms")

    # Generate report
    if args.report or metrics['accuracy'] < 0.99:
        print("\n📊 Generating detailed report...")
        report = tester.generate_report()
        print("\n" + report)

    # Recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS FOR 99% ACCURACY")
    print("=" * 70)

    if metrics['false_positives'] > 0:
        print("❌ Reduce False Positives:")
        print("   - Tighten detector thresholds")
        print("   - Require more indicators for detection")
        print("   - Add more negative examples to training")

    if metrics['false_negatives'] > 0:
        print("❌ Reduce False Negatives:")
        print("   - Lower detection thresholds")
        print("   - Add more detector types")
        print("   - Improve VLM prompts")
        print("   - Use better ML models (YOLO, I3D)")

    print("\n✅ Next Steps:")
    print("   1. Label more test images with ground truth")
    print("   2. Create childcare-specific test dataset (50-100 images)")
    print("   3. Test various scenarios: supervision, distress, violence")
    print("   4. Iterate on detector thresholds")
    print("   5. Re-run validation suite until 99% accuracy")


if __name__ == "__main__":
    main()
