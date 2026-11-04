#!/usr/bin/env python3
"""
Test Hybrid Fast-Path + VLM System

Compares:
1. VLM-only analysis (old approach)
2. Hybrid fast-path + VLM analysis (new approach)

Tests with the same images that showed 0% detection rate.
"""
import requests
import base64
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class HybridSystemTester:
    """Test hybrid system vs VLM-only"""

    def __init__(self, vlm_url: str = "http://localhost:8001"):
        self.vlm_url = vlm_url
        self.results = []

    def load_image_b64(self, image_path: str) -> str:
        """Load image and encode as base64"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def test_vlm_only(self, image_path: str, prompt: str) -> Dict:
        """Test with VLM-only approach (old)"""
        print(f"\n{'='*70}")
        print(f"VLM-ONLY TEST: {Path(image_path).name}")
        print(f"{'='*70}")

        image_b64 = self.load_image_b64(image_path)

        payload = {
            "image_base64": image_b64,
            "prompt": prompt
        }

        start_time = time.time()

        try:
            response = requests.post(
                f"{self.vlm_url}/analyze",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()

            elapsed_ms = (time.time() - start_time) * 1000

            print(f"\n✓ Completed in {elapsed_ms:.0f}ms")
            print(f"\nAnalysis:")
            print(result['analysis'][:500])
            if len(result['analysis']) > 500:
                print("... (truncated)")

            return {
                "success": True,
                "elapsed_ms": elapsed_ms,
                "analysis": result['analysis'],
                "adults_detected": result.get('adults_detected'),
                "children_count": result.get('children_count'),
                "safety_concern": result.get('safety_concern')
            }

        except Exception as e:
            print(f"\n✗ Error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def test_hybrid(self, image_path: str) -> Dict:
        """Test with hybrid fast-path + VLM approach (new)"""
        print(f"\n{'='*70}")
        print(f"HYBRID TEST: {Path(image_path).name}")
        print(f"{'='*70}")

        image_b64 = self.load_image_b64(image_path)

        payload = {
            "image_base64": image_b64
        }

        start_time = time.time()

        try:
            response = requests.post(
                f"{self.vlm_url}/analyze/hybrid",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()

            elapsed_ms = (time.time() - start_time) * 1000

            print(f"\n✓ Completed in {elapsed_ms:.0f}ms")
            print(f"\nResults:")
            print(f"  Violation Detected: {result['violation_detected']}")
            print(f"  Type: {result['violation_type']}")
            print(f"  Severity: {result['severity']}")
            print(f"  Confidence: {result['confidence']:.2f}")
            print(f"  Source: {result['source']}")
            print(f"  Immediate Action: {result['immediate_action_required']}")
            print(f"\nDetails:")
            print(f"  {result['details']}")

            # Show fast-path results
            if result.get('fast_path_results'):
                print(f"\nFast-Path Detections:")
                fp = result['fast_path_results']

                if fp.get('violence', {}).get('violence_detected'):
                    v = fp['violence']
                    print(f"  Violence: {v['action_type']} (conf: {v['confidence']:.2f})")
                    print(f"    {v['details']}")

                if fp.get('distress', {}).get('distress_detected'):
                    d = fp['distress']
                    print(f"  Distress: {d['emotion']} (conf: {d['confidence']:.2f})")
                    print(f"    {d['details']}")

                if fp.get('supervision', {}).get('violation_detected'):
                    s = fp['supervision']
                    print(f"  Supervision: {s['adult_count']} adults : {s['child_count']} children")
                    print(f"    Ratio: {s['ratio']:.2f} (required: {s['required_ratio']:.2f})")

            # Show VLM result if used
            if result.get('vlm_result'):
                print(f"\nVLM Validation:")
                print(f"  {result['vlm_result'][:300]}")
                if len(result['vlm_result']) > 300:
                    print("  ... (truncated)")

            return {
                "success": True,
                "elapsed_ms": elapsed_ms,
                "violation_detected": result['violation_detected'],
                "violation_type": result['violation_type'],
                "severity": result['severity'],
                "confidence": result['confidence'],
                "source": result['source'],
                "immediate_action": result['immediate_action_required'],
                "fast_path_results": result.get('fast_path_results'),
                "vlm_result": result.get('vlm_result')
            }

        except Exception as e:
            print(f"\n✗ Error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def compare_approaches(self, image_path: str, description: str):
        """Compare VLM-only vs Hybrid for the same image"""
        print(f"\n{'#'*70}")
        print(f"# TEST CASE: {description}")
        print(f"# Image: {Path(image_path).name}")
        print(f"{'#'*70}")

        # Generic prompt for VLM-only
        vlm_prompt = """Analyze this childcare image for safety violations:

1. Supervision: Are adults present supervising children? What is the ratio?
2. Physical Safety: Is there any physical aggression, violence, or dangerous behavior?
3. Child Wellbeing: Are any children in distress, crying, or showing signs of injury?
4. Environment: Are there any safety hazards visible (sharp objects, unsafe equipment)?
5. Severity: If violations exist, classify as LOW, MEDIUM, or HIGH severity.

Provide a detailed analysis."""

        # Test both approaches
        vlm_result = self.test_vlm_only(image_path, vlm_prompt)
        hybrid_result = self.test_hybrid(image_path)

        # Compare
        print(f"\n{'='*70}")
        print(f"COMPARISON")
        print(f"{'='*70}")

        if vlm_result.get('success') and hybrid_result.get('success'):
            print(f"\nPerformance:")
            print(f"  VLM-only: {vlm_result['elapsed_ms']:.0f}ms")
            print(f"  Hybrid:   {hybrid_result['elapsed_ms']:.0f}ms")
            speedup = vlm_result['elapsed_ms'] / hybrid_result['elapsed_ms']
            print(f"  Speedup:  {speedup:.1f}x {'FASTER' if speedup > 1 else 'SLOWER'}")

            print(f"\nDetection:")
            print(f"  VLM-only safety concern: {vlm_result.get('safety_concern', 'Unknown')}")
            print(f"  Hybrid violation detected: {hybrid_result['violation_detected']}")
            print(f"  Hybrid violation type: {hybrid_result['violation_type']}")
            print(f"  Hybrid severity: {hybrid_result['severity']}")

        # Store for summary
        self.results.append({
            "image": Path(image_path).name,
            "description": description,
            "vlm": vlm_result,
            "hybrid": hybrid_result
        })

    def save_summary(self, output_dir: str = "test_results"):
        """Save comparison summary"""
        Path(output_dir).mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON summary
        json_file = Path(output_dir) / f"hybrid_comparison_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        # Human-readable summary
        txt_file = Path(output_dir) / f"hybrid_comparison_{timestamp}.txt"
        with open(txt_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("HYBRID SYSTEM COMPARISON SUMMARY\n")
            f.write("="*70 + "\n\n")
            f.write(f"Test Date: {datetime.now().isoformat()}\n")
            f.write(f"Total Tests: {len(self.results)}\n\n")

            for i, result in enumerate(self.results, 1):
                f.write(f"\n{'='*70}\n")
                f.write(f"Test {i}: {result['description']}\n")
                f.write(f"Image: {result['image']}\n")
                f.write(f"{'='*70}\n\n")

                if result['vlm'].get('success'):
                    f.write(f"VLM-Only:\n")
                    f.write(f"  Time: {result['vlm']['elapsed_ms']:.0f}ms\n")
                    f.write(f"  Safety Concern: {result['vlm'].get('safety_concern', 'Unknown')}\n\n")

                if result['hybrid'].get('success'):
                    f.write(f"Hybrid:\n")
                    f.write(f"  Time: {result['hybrid']['elapsed_ms']:.0f}ms\n")
                    f.write(f"  Violation: {result['hybrid']['violation_detected']}\n")
                    f.write(f"  Type: {result['hybrid']['violation_type']}\n")
                    f.write(f"  Severity: {result['hybrid']['severity']}\n")
                    f.write(f"  Confidence: {result['hybrid']['confidence']:.2f}\n")
                    f.write(f"  Source: {result['hybrid']['source']}\n\n")

        print(f"\n{'='*70}")
        print(f"Results saved:")
        print(f"  JSON: {json_file}")
        print(f"  TXT:  {txt_file}")
        print(f"{'='*70}")


def main():
    """Run hybrid system tests"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║           HYBRID SYSTEM TEST: VLM-Only vs Fast-Path           ║
╚════════════════════════════════════════════════════════════════╝

Testing the hybrid fast-path architecture against VLM-only approach.

Goal: Prove that hybrid system fixes the 0% detection rate problem
      while improving performance.
""")

    tester = HybridSystemTester()

    # Test cases (same images that failed with VLM-only)
    test_cases = [
        {
            "path": "tests/images/test_violence.jpg",
            "description": "Child hitting another with pencil (previously missed)"
        },
        {
            "path": "tests/images/test_classroom2.jpg",
            "description": "Physical confrontation between children (previously missed)"
        },
        {
            "path": "tests/images/test_classroom1.jpg",
            "description": "Normal classroom activity (should be no violation)"
        }
    ]

    for test_case in test_cases:
        try:
            tester.compare_approaches(
                test_case["path"],
                test_case["description"]
            )
        except Exception as e:
            print(f"\n✗ Test failed: {e}")

    # Save summary
    tester.save_summary()

    print(f"\n{'='*70}")
    print("Testing complete!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
