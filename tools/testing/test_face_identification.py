#!/usr/bin/env python3
"""
Test Face Identification System

Tests the FaceIdentifier class with sample images.

Usage:
    # Test with sample enrollment
    python3 tools/testing/test_face_identification.py

    # Test with custom images
    python3 tools/testing/test_face_identification.py --enroll path/to/person1.jpg --test path/to/test.jpg
"""

import sys
import os
import argparse
import cv2
import numpy as np
from pathlib import Path

# Add package to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'packages' / 'nura-detectors' / 'src'))

# ANSI colors
BLUE = '\033[0;34m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
NC = '\033[0m'


def create_synthetic_face(name: str, size=(200, 200)) -> np.ndarray:
    """Create a synthetic face image for testing (when no real images available)"""
    # Create a colored rectangle with text as a placeholder
    colors = {
        'adam': (100, 150, 200),
        'noah': (150, 100, 200),
        'sarah': (200, 150, 100),
    }

    color = colors.get(name.lower(), (128, 128, 128))
    image = np.full((size[0], size[1], 3), color, dtype=np.uint8)

    # Add text
    cv2.putText(image, name.upper(), (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)

    return image


def test_face_identifier_without_db():
    """Test FaceIdentifier without database (in-memory only)"""
    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}FACE IDENTIFIER TEST (No Database){NC}")
    print(f"{BLUE}{'='*70}{NC}\n")

    # Try to import FaceIdentifier
    try:
        from nura_detectors import FaceIdentifier, FaceIdentity
        print(f"{GREEN}✓ FaceIdentifier imported successfully{NC}\n")
    except ImportError as e:
        print(f"{RED}✗ Failed to import FaceIdentifier: {e}{NC}")
        print(f"{YELLOW}Make sure face recognition dependencies are installed:{NC}")
        print(f"  pip install face-recognition insightface onnxruntime")
        return

    # Check which backend is available
    backend = "face_recognition"
    try:
        import face_recognition
        print(f"{GREEN}✓ face_recognition backend available{NC}")
    except ImportError:
        try:
            import insightface
            backend = "insightface"
            print(f"{GREEN}✓ insightface backend available{NC}")
        except ImportError:
            print(f"{RED}✗ No face recognition backend available{NC}")
            print(f"{YELLOW}Install one of:{NC}")
            print(f"  pip install face-recognition  # Easiest")
            print(f"  pip install insightface onnxruntime  # Best performance")
            return

    # Initialize FaceIdentifier (no database)
    print(f"\n{YELLOW}Initializing FaceIdentifier (backend={backend})...{NC}")
    try:
        identifier = FaceIdentifier(
            db_connection=None,  # No database
            backend=backend,
            min_confidence=0.6
        )
        print(f"{GREEN}✓ FaceIdentifier initialized{NC}\n")
    except Exception as e:
        print(f"{RED}✗ Failed to initialize FaceIdentifier: {e}{NC}")
        return

    # Test 1: Enroll synthetic persons
    print(f"{CYAN}TEST 1: Enrolling synthetic persons{NC}")
    print(f"{'-'*70}\n")

    persons = [
        {'id': 'adam_w', 'name': 'Adam Williams', 'display': 'Adam W.'},
        {'id': 'noah_m', 'name': 'Noah Martinez', 'display': 'Noah M.'},
        {'id': 'sarah_k', 'name': 'Sarah Kim', 'display': 'Sarah K.'},
    ]

    enrollment_images = {}

    for person in persons:
        # Create synthetic face image
        # In real use, this would be actual photos
        images = [
            create_synthetic_face(person['id'].split('_')[0]),
            create_synthetic_face(person['id'].split('_')[0]),
        ]
        enrollment_images[person['id']] = images

        print(f"Enrolling {person['display']}...")
        success = identifier.enroll_person(
            person_id=person['id'],
            full_name=person['name'],
            display_name=person['display'],
            enrollment_images=images
        )

        if success:
            print(f"  {GREEN}✓ Enrolled{NC}")
        else:
            print(f"  {RED}✗ Enrollment failed{NC}")

    print(f"\n{GREEN}✓ Enrolled {identifier.get_enrollment_count()} persons{NC}\n")

    # Test 2: Identify from test image
    print(f"{CYAN}TEST 2: Identification (synthetic test){NC}")
    print(f"{'-'*70}\n")

    print(f"{YELLOW}Note: Using synthetic faces for testing{NC}")
    print(f"{YELLOW}For real testing, use actual face photos{NC}\n")

    # Create test image with a "face"
    test_image = create_synthetic_face("adam")
    person_bbox = [0, 0, 200, 200]  # Full image

    print(f"Testing identification...")
    result = identifier.identify(test_image, person_bbox)

    if result:
        print(f"  {GREEN}✓ Identified: {result.display_name}{NC}")
        print(f"    Confidence: {result.confidence:.2%}")
        print(f"    Method: {result.method}")
        print(f"    Distance: {result.distance:.4f}")
    else:
        print(f"  {YELLOW}⚠ No match found (this is expected with synthetic faces){NC}")
        print(f"    Synthetic faces don't have real face features")

    print()

    # Test 3: Real image test (if available)
    print(f"{CYAN}TEST 3: Real image test{NC}")
    print(f"{'-'*70}\n")

    print(f"{YELLOW}To test with real images:{NC}")
    print(f"  1. Take 2-3 photos of a person (different angles)")
    print(f"  2. Run: python3 tools/testing/test_face_identification.py \\")
    print(f"          --enroll person1.jpg person2.jpg \\")
    print(f"          --test test.jpg")
    print()


def test_with_real_images(enroll_images: list, test_image_path: str):
    """Test with real images"""
    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}FACE IDENTIFIER TEST (Real Images){NC}")
    print(f"{BLUE}{'='*70}{NC}\n")

    try:
        from nura_detectors import FaceIdentifier
    except ImportError as e:
        print(f"{RED}✗ Failed to import FaceIdentifier: {e}{NC}")
        return

    # Detect backend
    backend = "face_recognition"
    try:
        import face_recognition
    except ImportError:
        try:
            import insightface
            backend = "insightface"
        except ImportError:
            print(f"{RED}✗ No face recognition backend available{NC}")
            return

    # Initialize
    identifier = FaceIdentifier(db_connection=None, backend=backend)

    # Load enrollment images
    enrollment_imgs = []
    for img_path in enroll_images:
        img = cv2.imread(img_path)
        if img is not None:
            enrollment_imgs.append(img)
        else:
            print(f"{YELLOW}⚠ Could not load {img_path}{NC}")

    if not enrollment_imgs:
        print(f"{RED}✗ No valid enrollment images{NC}")
        return

    # Enroll person
    print(f"Enrolling person with {len(enrollment_imgs)} images...")
    success = identifier.enroll_person(
        person_id="test_person",
        full_name="Test Person",
        display_name="Test P.",
        enrollment_images=enrollment_imgs
    )

    if not success:
        print(f"{RED}✗ Enrollment failed{NC}")
        return

    print(f"{GREEN}✓ Enrolled successfully{NC}\n")

    # Load test image
    test_img = cv2.imread(test_image_path)
    if test_img is None:
        print(f"{RED}✗ Could not load test image: {test_image_path}{NC}")
        return

    # Identify
    h, w = test_img.shape[:2]
    person_bbox = [0, 0, w, h]  # Full image as person ROI

    print(f"Identifying from test image...")
    result = identifier.identify(test_img, person_bbox)

    if result:
        print(f"{GREEN}✓ Identified: {result.display_name}{NC}")
        print(f"  Confidence: {result.confidence:.2%}")
        print(f"  Distance: {result.distance:.4f}")
    else:
        print(f"{YELLOW}⚠ No match found{NC}")
        print(f"  Possible reasons:")
        print(f"    - No face detected in test image")
        print(f"    - Face too small or low quality")
        print(f"    - Confidence below threshold (0.6)")


def main():
    parser = argparse.ArgumentParser(description='Test face identification system')

    parser.add_argument('--enroll', nargs='+', help='Enrollment images')
    parser.add_argument('--test', type=str, help='Test image path')

    args = parser.parse_args()

    if args.enroll and args.test:
        test_with_real_images(args.enroll, args.test)
    else:
        test_face_identifier_without_db()


if __name__ == '__main__':
    main()
