#!/usr/bin/env python3
"""
Quick Hybrid Test Script
Test a single image with the hybrid endpoint

Usage:
    python tools/testing/quick_hybrid_test.py <image_path>
    python tools/testing/quick_hybrid_test.py tests/images/test_classroom2.jpg
"""
import sys
import base64
import requests
import json
from pathlib import Path


def test_hybrid(image_path, vlm_url="http://localhost:8001"):
    """Test hybrid endpoint with an image"""

    print(f"\n{'='*70}")
    print(f"🧪 HYBRID FAST-PATH TEST")
    print(f"{'='*70}")
    print(f"Image: {Path(image_path).name}")
    print(f"URL: {vlm_url}/analyze/hybrid")
    print()

    # Load and encode image
    try:
        with open(image_path, 'rb') as f:
            image_b64 = base64.b64encode(f.read()).decode('utf-8')
        print(f"✓ Image loaded ({len(image_b64)} bytes)")
    except FileNotFoundError:
        print(f"❌ Image not found: {image_path}")
        return

    # Test hybrid endpoint
    print(f"\n🔍 Analyzing with hybrid fast-path...")

    try:
        response = requests.post(
            f"{vlm_url}/analyze/hybrid",
            json={"image_base64": image_b64},
            timeout=60
        )

        if response.status_code != 200:
            print(f"\n❌ Error {response.status_code}")
            print(f"   {response.text}")
            return

        result = response.json()

        # Display results
        print(f"\n{'='*70}")
        print(f"📊 RESULTS")
        print(f"{'='*70}")

        # Main findings
        print(f"\n🎯 Detection:")
        print(f"   Violation: {result['violation_detected']}")
        print(f"   Type: {result['violation_type']}")
        print(f"   Severity: {result['severity']}")
        print(f"   Confidence: {result['confidence']:.1%}")

        # Performance
        print(f"\n⚡ Performance:")
        print(f"   Processing Time: {result['processing_time_ms']:.0f}ms")
        print(f"   Source: {result['source']}")
        print(f"   Immediate Action: {result['immediate_action_required']}")

        # Details
        print(f"\n📝 Details:")
        print(f"   {result['details']}")

        # Fast-path breakdown
        if result.get('fast_path_results'):
            print(f"\n🔬 Fast-Path Detectors:")
            fp = result['fast_path_results']
            print(f"   Violence: {'✓ DETECTED' if fp.get('violence_detected') else '✗ Not detected'}")
            print(f"   Distress: {'✓ DETECTED' if fp.get('distress_detected') else '✗ Not detected'}")
            print(f"   Supervision Violation: {'✓ DETECTED' if fp.get('supervision_violation') else '✗ Not detected'}")
            print(f"   Intimidation/Bullying: {'✓ DETECTED' if fp.get('intimidation_detected') else '✗ Not detected'}")

        # VLM result if hybrid was used
        if result.get('vlm_result'):
            print(f"\n🤖 VLM Validation:")
            print(f"   {result['vlm_result'][:200]}...")

        print(f"\n{'='*70}")

        # Interpretation
        if result['violation_detected']:
            emoji = "🚨" if result['severity'] == 'high' else "⚠️"
            print(f"\n{emoji} ALERT: {result['violation_type'].upper()} violation detected!")
        else:
            print(f"\n✅ No violations detected")

        print(f"\n{'='*70}\n")

    except requests.exceptions.Timeout:
        print(f"\n⏱️  Request timed out (>60s)")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection failed to {vlm_url}")
        print(f"   Make sure the VLM service is running:")
        print(f"   docker ps | grep vlm")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_hybrid_test.py <image_path>")
        print("\nExamples:")
        print("  python tools/testing/quick_hybrid_test.py tests/images/test_classroom2.jpg")
        print("  python tools/testing/quick_hybrid_test.py tests/images/test_violence.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    test_hybrid(image_path)


if __name__ == "__main__":
    main()
