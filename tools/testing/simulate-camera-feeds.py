#!/usr/bin/env python3
"""
Simulate Live Camera Feeds for Testing
Streams videos from tests/data/ to the VLM API simulating real-time camera feeds
"""
import cv2
import base64
import requests
import json
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from threading import Thread
import queue

# Configuration
VLM_API_URL = "http://localhost:8001/analyze/hybrid"
DEFAULT_FPS = 30  # Simulate real-time playback

# ANSI colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
MAGENTA = '\033[0;35m'
CYAN = '\033[0;36m'
NC = '\033[0m'  # No Color


class CameraFeedSimulator:
    """Simulates a camera feed from a video file"""

    def __init__(self, camera_id, video_path, fps=30, loop=False):
        self.camera_id = camera_id
        self.video_path = video_path
        self.fps = fps
        self.loop = loop
        self.frame_interval = 1.0 / fps
        self.violations = []
        self.frame_count = 0
        self.violation_count = 0
        self.running = False

    def send_frame(self, frame):
        """Send frame to VLM API"""
        # Encode frame to JPEG
        success, buffer = cv2.imencode('.jpg', frame)
        if not success:
            return None

        # Convert to base64
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        # Send to API
        try:
            response = requests.post(
                VLM_API_URL,
                json={
                    'image_base64': image_base64,
                    'camera_id': self.camera_id
                },
                timeout=30
            )

            if response.ok:
                return response.json()
            else:
                print(f"{RED}[{self.camera_id}] API error: {response.status_code}{NC}")
                return None

        except Exception as e:
            print(f"{RED}[{self.camera_id}] Error: {e}{NC}")
            return None

    def run(self):
        """Simulate camera feed"""
        self.running = True

        while self.running:
            cap = cv2.VideoCapture(str(self.video_path))

            if not cap.isOpened():
                print(f"{RED}[{self.camera_id}] Failed to open video{NC}")
                break

            print(f"{CYAN}[{self.camera_id}] Starting stream: {self.video_path.name}{NC}")

            while self.running:
                start_time = time.time()

                ret, frame = cap.read()
                if not ret:
                    if self.loop:
                        print(f"{YELLOW}[{self.camera_id}] Looping video...{NC}")
                        break  # Restart video
                    else:
                        self.running = False
                        break

                # Send frame to API
                result = self.send_frame(frame)

                if result:
                    self.frame_count += 1

                    # Log violations
                    if result.get('violation_detected'):
                        self.violation_count += 1
                        violation_type = result.get('violation_type', 'unknown')
                        confidence = result.get('confidence', 0)
                        source = result.get('source', 'unknown')

                        timestamp = datetime.now().strftime('%H:%M:%S')
                        print(f"{RED}[{self.camera_id}] {timestamp} - VIOLATION: {violation_type} "
                              f"({confidence:.0%}) [{source}]{NC}")

                        self.violations.append({
                            'timestamp': timestamp,
                            'frame': self.frame_count,
                            'type': violation_type,
                            'confidence': confidence,
                            'source': source
                        })

                # Simulate real-time by waiting
                elapsed = time.time() - start_time
                sleep_time = max(0, self.frame_interval - elapsed)
                time.sleep(sleep_time)

            cap.release()

            if not self.loop:
                break

        print(f"{CYAN}[{self.camera_id}] Stream ended - Frames: {self.frame_count}, "
              f"Violations: {self.violation_count}{NC}")

    def stop(self):
        """Stop the camera feed"""
        self.running = False


def simulate_multi_camera(video_paths, fps=30, loop=False):
    """Simulate multiple camera feeds simultaneously"""

    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}Multi-Camera Feed Simulation{NC}")
    print(f"{BLUE}{'='*70}{NC}\n")

    print(f"Cameras: {len(video_paths)}")
    print(f"FPS: {fps}")
    print(f"Loop: {loop}")
    print()

    # Create camera simulators
    cameras = []
    threads = []

    for i, video_path in enumerate(video_paths):
        camera_id = f"camera-{i+1}"
        camera = CameraFeedSimulator(camera_id, video_path, fps=fps, loop=loop)
        cameras.append(camera)

        # Start each camera in its own thread
        thread = Thread(target=camera.run, daemon=True)
        threads.append(thread)
        thread.start()

    try:
        # Wait for all threads to complete
        for thread in threads:
            thread.join()

    except KeyboardInterrupt:
        print(f"\n{YELLOW}Stopping all cameras...{NC}")
        for camera in cameras:
            camera.stop()

        # Wait for threads to finish
        for thread in threads:
            thread.join(timeout=2)

    # Summary
    print(f"\n{BLUE}{'='*70}{NC}")
    print(f"{BLUE}Simulation Complete{NC}")
    print(f"{BLUE}{'='*70}{NC}\n")

    total_frames = sum(c.frame_count for c in cameras)
    total_violations = sum(c.violation_count for c in cameras)

    print(f"Total Frames Processed: {total_frames}")
    print(f"Total Violations: {total_violations}")
    print()

    for camera in cameras:
        print(f"{CYAN}[{camera.camera_id}]{NC} {camera.video_path.name}")
        print(f"  Frames: {camera.frame_count}, Violations: {camera.violation_count}")
        if camera.violations:
            print(f"  Last 5 violations:")
            for v in camera.violations[-5:]:
                print(f"    {v['timestamp']} - {v['type']} ({v['confidence']:.0%})")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Simulate live camera feeds from video files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single camera
  python3 tools/testing/simulate-camera-feeds.py tests/data/Videos/FightingA_Part1/Fighting013_x264A.mp4

  # Multiple cameras
  python3 tools/testing/simulate-camera-feeds.py \\
    tests/data/Videos/FightingA_Part1/Fighting013_x264A.mp4 \\
    tests/data/Videos/Normal_Videos_for_Event_Recognition/Normal_Videos_for_Event_Recognition/Normal_Videos_100_x264.mp4

  # Loop videos continuously
  python3 tools/testing/simulate-camera-feeds.py --loop tests/data/Videos/FightingA_Part1/*.mp4

  # Slower playback (15 FPS)
  python3 tools/testing/simulate-camera-feeds.py --fps 15 tests/data/Videos/FightingA_Part1/Fighting013_x264A.mp4

  # All fighting videos
  find tests/data/Videos -name "*Fighting*.mp4" -exec python3 tools/testing/simulate-camera-feeds.py --fps 30 {} +
        """
    )

    parser.add_argument(
        'videos',
        nargs='+',
        help='Video file(s) to use as camera feeds'
    )

    parser.add_argument(
        '--fps',
        type=int,
        default=30,
        help='Frames per second for playback (default: 30)'
    )

    parser.add_argument(
        '--loop',
        action='store_true',
        help='Loop videos continuously'
    )

    args = parser.parse_args()

    # Validate video files
    video_paths = []
    for video in args.videos:
        path = Path(video)
        if not path.exists():
            print(f"{RED}Error: Video not found: {video}{NC}")
            sys.exit(1)
        video_paths.append(path)

    # Check if API is running
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if not response.ok:
            print(f"{RED}Error: VLM service not responding{NC}")
            print(f"{YELLOW}Start with: ./start.sh{NC}")
            sys.exit(1)
    except:
        print(f"{RED}Error: Cannot connect to VLM service{NC}")
        print(f"{YELLOW}Start with: ./start.sh{NC}")
        sys.exit(1)

    # Run simulation
    simulate_multi_camera(video_paths, fps=args.fps, loop=args.loop)


if __name__ == '__main__':
    main()
