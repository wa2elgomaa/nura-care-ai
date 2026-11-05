#!/usr/bin/env python3
"""
Camera Frame Simulator
Simulates real-time camera feeds for testing before hardware integration

Features:
- Load images/videos and stream as frames
- Simulate multiple cameras
- Add realistic delays/noise
- Test frame rate handling
- Batch processing simulation

Usage:
    # Simulate single camera from video
    python tools/testing/camera_frame_simulator.py --video tests/data/Videos/Fighting/fight01.mp4

    # Simulate from image directory
    python tools/testing/camera_frame_simulator.py --dir tests/images --fps 2

    # Simulate multiple cameras
    python tools/testing/camera_frame_simulator.py --cameras 4 --dir tests/images
"""

import sys
import os
import time
import base64
import argparse
from pathlib import Path
from typing import List, Generator, Optional
from dataclasses import dataclass
import requests
from datetime import datetime

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    print("⚠️  OpenCV not available - install with: pip install opencv-python")


@dataclass
class CameraFrame:
    """Single camera frame"""
    camera_id: str
    frame_number: int
    timestamp: datetime
    image_data: bytes
    image_b64: str


class CameraSimulator:
    """Simulates camera feed for testing"""

    def __init__(self, camera_id: str = "cam001", fps: int = 1):
        self.camera_id = camera_id
        self.fps = fps
        self.frame_interval = 1.0 / fps
        self.frame_count = 0

    def stream_from_video(self, video_path: str) -> Generator[CameraFrame, None, None]:
        """Stream frames from video file"""
        if not HAS_CV2:
            print("❌ OpenCV required for video streaming")
            return

        cap = cv2.VideoCapture(str(video_path))
        video_fps = cap.get(cv2.CAP_PROP_FPS)

        # Calculate frame skip to match target FPS
        skip_frames = int(video_fps / self.fps) if self.fps < video_fps else 1

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Skip frames to match target FPS
            for _ in range(skip_frames - 1):
                cap.read()

            # Encode frame
            _, buffer = cv2.imencode('.jpg', frame)
            image_data = buffer.tobytes()
            image_b64 = base64.b64encode(image_data).decode('utf-8')

            yield CameraFrame(
                camera_id=self.camera_id,
                frame_number=self.frame_count,
                timestamp=datetime.now(),
                image_data=image_data,
                image_b64=image_b64
            )

            self.frame_count += 1
            time.sleep(self.frame_interval)

        cap.release()

    def stream_from_images(self, image_dir: str) -> Generator[CameraFrame, None, None]:
        """Stream frames from image directory"""
        image_paths = sorted(Path(image_dir).glob("*.jpg")) + sorted(Path(image_dir).glob("*.png"))

        for img_path in image_paths:
            with open(img_path, 'rb') as f:
                image_data = f.read()
                image_b64 = base64.b64encode(image_data).decode('utf-8')

            yield CameraFrame(
                camera_id=self.camera_id,
                frame_number=self.frame_count,
                timestamp=datetime.now(),
                image_data=image_data,
                image_b64=image_b64
            )

            self.frame_count += 1
            time.sleep(self.frame_interval)

    def stream_single_image_loop(self, image_path: str, duration_s: int = 60) -> Generator[CameraFrame, None, None]:
        """Stream same image repeatedly (for testing)"""
        with open(image_path, 'rb') as f:
            image_data = f.read()
            image_b64 = base64.b64encode(image_data).decode('utf-8')

        start_time = time.time()

        while time.time() - start_time < duration_s:
            yield CameraFrame(
                camera_id=self.camera_id,
                frame_number=self.frame_count,
                timestamp=datetime.now(),
                image_data=image_data,
                image_b64=image_b64
            )

            self.frame_count += 1
            time.sleep(self.frame_interval)


class MultiCameraSimulator:
    """Simulates multiple camera feeds"""

    def __init__(self, num_cameras: int = 4, fps: int = 1):
        self.cameras = [
            CameraSimulator(camera_id=f"cam{i:03d}", fps=fps)
            for i in range(num_cameras)
        ]

    def stream_all(self, image_dir: str) -> Generator[List[CameraFrame], None, None]:
        """Stream from all cameras simultaneously"""
        # Get image files for each camera
        all_images = list(Path(image_dir).glob("*.jpg")) + list(Path(image_dir).glob("*.png"))

        # Distribute images across cameras
        camera_images = [all_images[i::len(self.cameras)] for i in range(len(self.cameras))]

        # Stream in round-robin
        max_frames = max(len(imgs) for imgs in camera_images)

        for frame_idx in range(max_frames):
            frames = []

            for cam_idx, camera in enumerate(self.cameras):
                if frame_idx < len(camera_images[cam_idx]):
                    img_path = camera_images[cam_idx][frame_idx]

                    with open(img_path, 'rb') as f:
                        image_data = f.read()
                        image_b64 = base64.b64encode(image_data).decode('utf-8')

                    frames.append(CameraFrame(
                        camera_id=camera.camera_id,
                        frame_number=frame_idx,
                        timestamp=datetime.now(),
                        image_data=image_data,
                        image_b64=image_b64
                    ))

            if frames:
                yield frames
                time.sleep(1.0 / self.cameras[0].fps)


def test_hybrid_endpoint(frame: CameraFrame, vlm_url: str = "http://localhost:8001") -> dict:
    """Test frame with hybrid endpoint"""
    try:
        response = requests.post(
            f"{vlm_url}/analyze/hybrid",
            json={
                "image_base64": frame.image_b64,
                "camera_id": frame.camera_id
            },
            timeout=60
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Camera Frame Simulator")
    parser.add_argument("--video", type=str, help="Path to video file")
    parser.add_argument("--dir", type=str, help="Path to image directory")
    parser.add_argument("--image", type=str, help="Path to single image (loop)")
    parser.add_argument("--fps", type=int, default=1, help="Frames per second")
    parser.add_argument("--cameras", type=int, default=1, help="Number of cameras to simulate")
    parser.add_argument("--duration", type=int, default=60, help="Duration in seconds (for single image loop)")
    parser.add_argument("--test", action="store_true", help="Test with hybrid endpoint")
    parser.add_argument("--url", default="http://localhost:8001", help="VLM service URL")
    parser.add_argument("--save-frames", type=str, help="Directory to save extracted frames")

    args = parser.parse_args()

    print("╔═══════════════════════════════════════════════════════════╗")
    print("║           CAMERA FRAME SIMULATOR                         ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()
    print(f"Cameras: {args.cameras}")
    print(f"FPS: {args.fps}")
    print(f"Testing: {'Yes' if args.test else 'No'}")
    print()

    if args.cameras == 1:
        # Single camera simulation
        simulator = CameraSimulator(camera_id="cam001", fps=args.fps)

        if args.video:
            print(f"📹 Streaming from video: {args.video}")
            frame_generator = simulator.stream_from_video(args.video)

        elif args.dir:
            print(f"📂 Streaming from directory: {args.dir}")
            frame_generator = simulator.stream_from_images(args.dir)

        elif args.image:
            print(f"🖼️  Looping single image: {args.image}")
            frame_generator = simulator.stream_single_image_loop(args.image, args.duration)

        else:
            print("❌ Provide --video, --dir, or --image")
            return

        # Process frames
        violation_count = 0
        total_frames = 0

        try:
            for frame in frame_generator:
                total_frames += 1
                print(f"\r[{frame.camera_id}] Frame {frame.frame_number:04d}", end="", flush=True)

                # Save frame if requested
                if args.save_frames:
                    save_dir = Path(args.save_frames)
                    save_dir.mkdir(parents=True, exist_ok=True)
                    frame_path = save_dir / f"{frame.camera_id}_frame_{frame.frame_number:04d}.jpg"

                    with open(frame_path, 'wb') as f:
                        f.write(frame.image_data)

                # Test with hybrid endpoint
                if args.test:
                    result = test_hybrid_endpoint(frame, args.url)

                    if result.get('violation_detected'):
                        violation_count += 1
                        print(f"\n  🚨 VIOLATION: {result['violation_type']} "
                              f"({result['confidence']:.0%}) - {result['processing_time_ms']:.0f}ms")

        except KeyboardInterrupt:
            print("\n\n⏹️  Stopped by user")

        print(f"\n\n{'='*60}")
        print(f"Total Frames: {total_frames}")
        if args.test:
            print(f"Violations Detected: {violation_count}")
            print(f"Detection Rate: {violation_count/total_frames:.1%}" if total_frames > 0 else "N/A")

    else:
        # Multi-camera simulation
        if not args.dir:
            print("❌ Multi-camera mode requires --dir")
            return

        print(f"📹 Streaming from {args.cameras} cameras")
        multi_sim = MultiCameraSimulator(num_cameras=args.cameras, fps=args.fps)

        violation_counts = {f"cam{i:03d}": 0 for i in range(args.cameras)}
        frame_counts = {f"cam{i:03d}": 0 for i in range(args.cameras)}

        try:
            for frame_batch in multi_sim.stream_all(args.dir):
                for frame in frame_batch:
                    frame_counts[frame.camera_id] += 1
                    print(f"\r[{frame.camera_id}] Frame {frame.frame_number:04d}", end="  ", flush=True)

                    if args.test:
                        result = test_hybrid_endpoint(frame, args.url)

                        if result.get('violation_detected'):
                            violation_counts[frame.camera_id] += 1
                            print(f"\n  🚨 [{frame.camera_id}] VIOLATION: {result['violation_type']}")

        except KeyboardInterrupt:
            print("\n\n⏹️  Stopped by user")

        print(f"\n\n{'='*60}")
        print("MULTI-CAMERA SUMMARY")
        print(f"{'='*60}")

        for cam_id in sorted(frame_counts.keys()):
            frames = frame_counts[cam_id]
            violations = violation_counts[cam_id]
            print(f"{cam_id}: {frames} frames, {violations} violations")


if __name__ == "__main__":
    main()
