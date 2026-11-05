#!/bin/bash
# Test the hybrid detection system with test images
# Run: ./test-images.sh

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Testing Hybrid Detection System                     ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Check if service is running
if ! curl -s http://localhost:8001/health >/dev/null 2>&1; then
    echo -e "${RED}✗ VLM Service not running${NC}"
    echo -e "${YELLOW}Start with: ./start.sh${NC}"
    exit 1
fi

python3 << 'EOF'
import base64
import requests
import json
import time
import sys

def test_image(image_path, camera_id, expected_violation):
    print(f"\n{'='*70}")
    print(f"Testing: {image_path}")
    print(f"Expected: {'VIOLATION' if expected_violation else 'NO VIOLATION'}")
    print(f"{'='*70}")

    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"✗ Image not found: {image_path}")
        return False

    start = time.time()
    try:
        response = requests.post(
            'http://localhost:8001/analyze/hybrid',
            json={'image_base64': image_data, 'camera_id': camera_id},
            timeout=120
        )
        elapsed = time.time() - start

        if response.ok:
            result = response.json()
            violation = result["violation_detected"]
            match = "✓ CORRECT" if violation == expected_violation else "✗ WRONG"

            print(f"\n{match}")
            print(f"  Violation detected: {violation}")
            print(f"  Type: {result['violation_type']}")
            print(f"  Confidence: {result['confidence']:.2%}")
            print(f"  Source: {result['source']}")
            print(f"  Processing time: {result['processing_time_ms']:.0f}ms ({elapsed:.2f}s total)")
            print(f"  Details: {result['details']}")

            if 'fast_path_summary' in result and result['fast_path_summary']:
                fps = result['fast_path_summary']
                print(f"  Fast-path results:")
                print(f"    - Violence: {fps.get('violence_detected', False)}")
                print(f"    - Distress: {fps.get('distress_detected', False)}")
                print(f"    - Supervision: {fps.get('supervision_violation', False)}")
                print(f"    - Intimidation: {fps.get('intimidation_detected', False)}")

            return violation == expected_violation
        else:
            print(f"\n✗ ERROR: {response.status_code}")
            print(f"  {response.text}")
            return False

    except Exception as e:
        elapsed = time.time() - start
        print(f"\n✗ FAILED after {elapsed:.2f}s")
        print(f"  Error: {e}")
        return False

# Test images
print("\nTESTING FALSE POSITIVE FIX - Multi-Detector Consensus + VLM Validation")
print("="*70)

test1 = test_image('tests/images/test_classroom1.jpg', 'test_classroom1', expected_violation=False)
test2 = test_image('tests/images/test_classroom2.jpg', 'test_classroom2', expected_violation=True)
test3 = test_image('tests/images/test_violence.jpg', 'test_violence', expected_violation=True)

print(f"\n{'='*70}")
print("RESULTS SUMMARY")
print(f"{'='*70}")
print(f"test_classroom1.jpg (peaceful):      {'✓ PASS' if test1 else '✗ FAIL'}")
print(f"test_classroom2.jpg (confrontation): {'✓ PASS' if test2 else '✗ FAIL'}")
print(f"test_violence.jpg (violence):        {'✓ PASS' if test3 else '✗ FAIL'}")
print(f"\nOverall: {'✓ ALL TESTS PASSED' if all([test1, test2, test3]) else '✗ SOME TESTS FAILED'}")
print(f"{'='*70}\n")

sys.exit(0 if all([test1, test2, test3]) else 1)
EOF
