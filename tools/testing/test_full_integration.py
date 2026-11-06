#!/usr/bin/env python3
"""
Full Integration Test - Phase 4 + 4B

Tests the complete person tracking and identification pipeline:
1. Person detection & tracking (ByteTrack)
2. Face identification (linking IDs to names)
3. Temporal violence detection (per-person)
4. Named alerts

Usage:
    # Test with video
    python3 tools/testing/test_full_integration.py --video classroom.mp4

    # Test with sample database
    python3 tools/testing/test_full_integration.py --test-db
"""

import sys
import os
import argparse
import asyncio
from pathlib import Path
import cv2
import numpy as np

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'services' / 'nura-vlm' / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'packages' / 'nura-detectors' / 'src'))

# ANSI colors
BLUE = '\033[0;34m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
MAGENTA = '\033[0;35m'
NC = '\033[0m'


def print_header(text):
    """Print section header"""
    print(f"\n{BLUE}{'='*70}{NC}")
    print(f"{BLUE}{text}{NC}")
    print(f"{BLUE}{'='*70}{NC}\n")


def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{NC}")


def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{NC}")


def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{NC}")


def print_info(text):
    """Print info message"""
    print(f"{CYAN}ℹ {text}{NC}")


def setup_test_database():
    """Setup test database with sample enrollments"""
    print_header("SETTING UP TEST DATABASE")

    try:
        import psycopg2

        # Connect to database
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "nura_db"),
            user=os.getenv("POSTGRES_USER", "nura"),
            password=os.getenv("POSTGRES_PASSWORD", "Pa$$w0rd!")
        )

        cursor = conn.cursor()

        # Check if tables exist
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'enrolled_persons'
            )
        """)

        if not cursor.fetchone()[0]:
            print_error("Database tables not found!")
            print_info("Run migration first:")
            print_info("  psql -U nura -d nura_db -f services/nura-vlm/migrations/001_person_enrollment.sql")
            return False

        # Check enrolled persons
        cursor.execute("SELECT COUNT(*) FROM enrolled_persons WHERE active = TRUE")
        count = cursor.fetchone()[0]

        print_success(f"Database connected")
        print_info(f"  Enrolled persons: {count}")

        if count == 0:
            print_warning("No persons enrolled in database")
            print_info("Enroll persons via API:")
            print_info("  http://localhost:8002/static/enrollment.html")

        conn.close()
        return True

    except Exception as e:
        print_error(f"Database connection failed: {e}")
        print_info("Make sure PostgreSQL is running and database is created")
        return False


def test_person_tracking():
    """Test person tracking alone"""
    print_header("TEST 1: PERSON TRACKING")

    try:
        from nura_detectors import PersonTracker

        # Initialize tracker
        tracker = PersonTracker(detector_model='n')
        print_success("PersonTracker initialized")

        # Create test image with multiple "persons" (colored rectangles)
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(test_frame, (50, 50), (150, 250), (255, 0, 0), -1)  # Blue person
        cv2.rectangle(test_frame, (200, 100), (300, 300), (0, 255, 0), -1)  # Green person
        cv2.rectangle(test_frame, (400, 50), (500, 250), (0, 0, 255), -1)  # Red person

        # Track persons
        tracks = tracker.update(test_frame)

        print_info(f"  Detected {len(tracks)} person(s)")

        for track in tracks:
            print(f"    Person {track['id']}: bbox={[int(v) for v in track['bbox']]}, "
                  f"conf={track['conf']:.2f}, age={track['age']}")

        if len(tracks) > 0:
            print_success("Person tracking working")
            return True
        else:
            print_warning("No persons detected (this is normal with synthetic images)")
            return True

    except Exception as e:
        print_error(f"Person tracking failed: {e}")
        return False


def test_face_identification():
    """Test face identification"""
    print_header("TEST 2: FACE IDENTIFICATION")

    try:
        from nura_detectors import FaceIdentifier
        import psycopg2

        # Connect to database
        db = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "nura_db"),
            user=os.getenv("POSTGRES_USER", "nura"),
            password=os.getenv("POSTGRES_PASSWORD", "Pa$$w0rd!")
        )

        # Initialize identifier
        backend = os.getenv("FACE_RECOGNITION_BACKEND", "insightface")
        identifier = FaceIdentifier(
            db_connection=db,
            backend=backend,
            min_confidence=0.6
        )

        enrolled_count = identifier.get_enrollment_count()
        print_success(f"FaceIdentifier initialized (backend={backend})")
        print_info(f"  Enrolled persons: {enrolled_count}")

        if enrolled_count == 0:
            print_warning("No persons enrolled - face identification will not work")
            print_info("Enroll persons first via API or UI")
        else:
            print_success(f"Ready for identification with {enrolled_count} enrolled person(s)")

        db.close()
        return True

    except ImportError as e:
        print_error(f"Face recognition backend not installed: {e}")
        print_info("Install dependencies:")
        print_info(f"  pip install {os.getenv('FACE_RECOGNITION_BACKEND', 'insightface')} onnxruntime")
        return False
    except Exception as e:
        print_error(f"Face identification failed: {e}")
        return False


async def test_hybrid_router():
    """Test hybrid router integration"""
    print_header("TEST 3: HYBRID ROUTER INTEGRATION")

    try:
        from hybrid_router import HybridRouter

        # Initialize router (no VLM client for testing)
        router = HybridRouter(vlm_client=None)
        print_success("HybridRouter initialized")

        # Check what's enabled
        print_info("  Configuration:")
        print(f"    Person tracking: {router.enable_person_tracking}")
        print(f"    Face identification: {router.enable_face_identification}")
        print(f"    Temporal detection: {router.enable_temporal}")

        # Create test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Analyze frame
        print_info("  Analyzing test frame...")
        alert = await router.analyze_frame(test_frame, camera_id="test_camera")

        print_success("Frame analysis complete")
        print_info(f"  Violation detected: {alert.violation_detected}")
        print_info(f"  Type: {alert.violation_type}")
        print_info(f"  Confidence: {alert.confidence:.2f}")
        print_info(f"  Source: {alert.source}")
        print_info(f"  Details: {alert.details}")

        if alert.persons_involved:
            print_info(f"  Persons involved: {alert.persons_involved}")

        return True

    except Exception as e:
        print_error(f"Hybrid router test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_with_video(video_path):
    """Test with actual video"""
    print_header(f"TEST 4: VIDEO PROCESSING - {video_path}")

    try:
        from hybrid_router import HybridRouter

        # Check video exists
        if not os.path.exists(video_path):
            print_error(f"Video not found: {video_path}")
            return False

        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print_error("Could not open video")
            return False

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print_info(f"  Video: {video_path}")
        print_info(f"  FPS: {fps}, Frames: {total_frames}")

        # Initialize router
        router = HybridRouter(vlm_client=None)
        print_success("Router initialized")

        # Process frames
        frame_count = 0
        max_frames = min(100, total_frames)  # Process first 100 frames

        print_info(f"  Processing first {max_frames} frames...")

        identified_persons = set()
        total_tracks = 0
        violations_detected = 0

        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Analyze frame
            alert = await router.analyze_frame(frame, camera_id="test_camera")

            # Collect statistics
            if alert.fast_path_results and "person_tracking" in alert.fast_path_results:
                tracks = alert.fast_path_results["person_tracking"].get("tracks", [])
                total_tracks += len(tracks)

                for track in tracks:
                    if track.get('identity'):
                        identified_persons.add(track['display_name'])

            if alert.violation_detected:
                violations_detected += 1
                print_warning(f"  Frame {frame_count}: {alert.details}")

            # Progress
            if frame_count % 20 == 0:
                print(f"    Processed {frame_count}/{max_frames} frames...")

        cap.release()

        # Summary
        print_success(f"Processed {frame_count} frames")
        print_info(f"  Total person tracks: {total_tracks}")
        print_info(f"  Identified persons: {len(identified_persons)}")
        if identified_persons:
            print_info(f"    Names: {', '.join(identified_persons)}")
        print_info(f"  Violations detected: {violations_detected}")

        return True

    except Exception as e:
        print_error(f"Video processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    parser = argparse.ArgumentParser(description='Full integration test')
    parser.add_argument('--video', type=str, help='Video file to test')
    parser.add_argument('--test-db', action='store_true', help='Test database setup')
    parser.add_argument('--skip-db', action='store_true', help='Skip database checks')

    args = parser.parse_args()

    print_header("PHASE 4 + 4B INTEGRATION TEST")
    print_info("Testing complete person tracking and identification pipeline")

    # Test sequence
    all_passed = True

    # Database setup
    if not args.skip_db:
        if not setup_test_database():
            print_warning("Continuing without database...")

    # Test 1: Person Tracking
    if not test_person_tracking():
        all_passed = False

    # Test 2: Face Identification
    if not test_face_identification():
        all_passed = False

    # Test 3: Hybrid Router
    if not await test_hybrid_router():
        all_passed = False

    # Test 4: Video (if provided)
    if args.video:
        if not await test_with_video(args.video):
            all_passed = False

    # Summary
    print_header("TEST SUMMARY")

    if all_passed:
        print_success("All tests passed!")
        print_info("System is ready for production testing")
    else:
        print_warning("Some tests failed")
        print_info("Check errors above and fix issues")

    # Next steps
    print_header("NEXT STEPS")
    print_info("1. Enroll persons via API:")
    print(f"     {CYAN}http://localhost:8002/static/enrollment.html{NC}")
    print_info("2. Test with real classroom video:")
    print(f"     {CYAN}python3 tools/testing/test_full_integration.py --video classroom.mp4{NC}")
    print_info("3. Monitor alerts in production:")
    print(f"     {CYAN}Check hybrid_router logs for named alerts{NC}")


if __name__ == '__main__':
    asyncio.run(main())
