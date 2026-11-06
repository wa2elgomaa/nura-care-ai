#!/usr/bin/env python3
"""
Test Person Tracking System

Tests the complete person tracking pipeline:
- Person detection
- Multi-object tracking
- ID consistency
- Per-person history

Usage:
    # Test with video file
    python3 tools/testing/test_person_tracking.py --video tests/videos/classroom_1.mp4

    # Test with webcam
    python3 tools/testing/test_person_tracking.py --camera 0

    # Save output video
    python3 tools/testing/test_person_tracking.py --video input.mp4 --output output.mp4
"""

import sys
import os
import argparse
import time
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

# Color palette for person IDs
COLORS = [
    (255, 0, 0),    # Blue
    (0, 255, 0),    # Green
    (0, 0, 255),    # Red
    (255, 255, 0),  # Cyan
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Yellow
    (128, 0, 255),  # Purple
    (255, 128, 0),  # Orange
    (0, 128, 255),  # Sky blue
    (128, 255, 0),  # Lime
]


def get_color(track_id):
    """Get consistent color for track ID"""
    return COLORS[track_id % len(COLORS)]


def draw_tracks(frame, tracks):
    """Draw bounding boxes and IDs on frame"""
    output = frame.copy()

    for track in tracks:
        track_id = track['id']
        bbox = track['bbox']
        conf = track['conf']

        # Get color for this ID
        color = get_color(track_id)

        # Draw bounding box
        x1, y1, x2, y2 = [int(v) for v in bbox]
        cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)

        # Draw ID label
        label = f"ID:{track_id} ({conf:.2f})"
        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)

        # Background for label
        cv2.rectangle(output,
                     (x1, y1 - label_size[1] - 10),
                     (x1 + label_size[0], y1),
                     color, -1)

        # Text
        cv2.putText(output, label, (x1, y1 - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Draw velocity arrow if significant
        velocity = track.get('velocity', [0, 0])
        if abs(velocity[0]) > 1 or abs(velocity[1]) > 1:
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            arrow_end = (int(cx + velocity[0] * 5), int(cy + velocity[1] * 5))
            cv2.arrowedLine(output, (cx, cy), arrow_end, color, 2)

    return output


def test_video(video_path, output_path=None, show=True):
    """Test tracking on video file"""

    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}PERSON TRACKING TEST - VIDEO{NC}")
    print(f"{BLUE}{'='*70}{NC}\n")

    print(f"Video: {video_path}")
    print()

    # Load tracker
    print(f"{YELLOW}Loading person tracker...{NC}")
    try:
        from nura_detectors.person_tracker import PersonTracker
        tracker = PersonTracker(detector_model='n')  # nano = fastest
        print(f"{GREEN}✓ Person tracker loaded{NC}\n")
    except Exception as e:
        print(f"{RED}✗ Failed to load tracker: {e}{NC}")
        return

    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"{RED}✗ Could not open video: {video_path}{NC}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"{CYAN}Video info:{NC}")
    print(f"  Resolution: {width}x{height}")
    print(f"  FPS: {fps}")
    print(f"  Frames: {total_frames}")
    print()

    # Video writer
    writer = None
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        print(f"Saving output to: {output_path}\n")

    # Statistics
    frame_count = 0
    total_time = 0
    active_ids = set()
    id_switches = 0
    prev_tracks = {}

    print(f"{YELLOW}Processing frames...{NC}")
    print(f"Press 'q' to quit, SPACE to pause\n")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Track persons
            start = time.time()
            tracks = tracker.update(frame)
            elapsed = (time.time() - start) * 1000
            total_time += elapsed

            # Count active IDs
            current_ids = set(t['id'] for t in tracks)
            active_ids.update(current_ids)

            # Detect ID switches (person disappears and reappears with different ID)
            for track in tracks:
                bbox = track['bbox']
                track_id = track['id']

                # Check if this bbox was previously tracked with different ID
                bbox_key = tuple([int(v) for v in bbox])
                if bbox_key in prev_tracks and prev_tracks[bbox_key] != track_id:
                    id_switches += 1

                prev_tracks[bbox_key] = track_id

            # Draw visualization
            vis_frame = draw_tracks(frame, tracks)

            # Add info overlay
            info_text = [
                f"Frame: {frame_count}/{total_frames}",
                f"People: {len(tracks)}",
                f"Total IDs: {len(active_ids)}",
                f"FPS: {1000/elapsed:.1f}",
                f"Track time: {elapsed:.1f}ms"
            ]

            y_offset = 30
            for text in info_text:
                cv2.putText(vis_frame, text, (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                y_offset += 25

            # Write frame
            if writer:
                writer.write(vis_frame)

            # Show frame
            if show:
                cv2.imshow('Person Tracking', vis_frame)
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    break
                elif key == ord(' '):
                    cv2.waitKey(0)  # Pause

            # Progress
            if frame_count % 30 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"  Progress: {progress:.1f}% | People: {len(tracks)} | "
                      f"Total IDs: {len(active_ids)} | Speed: {elapsed:.1f}ms")

    finally:
        cap.release()
        if writer:
            writer.release()
        if show:
            cv2.destroyAllWindows()

    # Summary
    print(f"\n{CYAN}{'='*70}{NC}")
    print(f"{CYAN}TRACKING SUMMARY{NC}")
    print(f"{CYAN}{'='*70}{NC}\n")

    avg_time = total_time / frame_count if frame_count > 0 else 0
    avg_fps = 1000 / avg_time if avg_time > 0 else 0

    print(f"Frames processed: {frame_count}")
    print(f"Total unique IDs: {len(active_ids)}")
    print(f"ID switches detected: {id_switches}")
    print(f"Average tracking time: {avg_time:.2f}ms")
    print(f"Average FPS: {avg_fps:.1f}")
    print()

    # Verdict
    if id_switches < frame_count * 0.01:  # < 1% switches
        print(f"{GREEN}✓ Good ID consistency (< 1% switches){NC}")
    else:
        print(f"{YELLOW}⚠ High ID switches ({id_switches}/{frame_count} = {100*id_switches/frame_count:.1f}%){NC}")

    if avg_time < 100:
        print(f"{GREEN}✓ Good performance (< 100ms){NC}")
    elif avg_time < 200:
        print(f"{YELLOW}⚠ Acceptable performance (< 200ms){NC}")
    else:
        print(f"{RED}✗ Slow performance (> 200ms){NC}")

    print()


def test_camera(camera_id=0):
    """Test tracking on live camera"""

    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}PERSON TRACKING TEST - CAMERA{NC}")
    print(f"{BLUE}{'='*70}{NC}\n")

    # Load tracker
    print(f"{YELLOW}Loading person tracker...{NC}")
    try:
        from nura_detectors.person_tracker import PersonTracker
        tracker = PersonTracker(detector_model='n')
        print(f"{GREEN}✓ Person tracker loaded{NC}\n")
    except Exception as e:
        print(f"{RED}✗ Failed to load tracker: {e}{NC}")
        return

    # Open camera
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"{RED}✗ Could not open camera {camera_id}{NC}")
        return

    print(f"{YELLOW}Camera opened. Press 'q' to quit{NC}\n")

    active_ids = set()
    frame_count = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Track persons
            start = time.time()
            tracks = tracker.update(frame)
            elapsed = (time.time() - start) * 1000

            # Update active IDs
            current_ids = set(t['id'] for t in tracks)
            active_ids.update(current_ids)

            # Draw visualization
            vis_frame = draw_tracks(frame, tracks)

            # Add info
            info_text = [
                f"Frame: {frame_count}",
                f"People: {len(tracks)}",
                f"Total IDs: {len(active_ids)}",
                f"FPS: {1000/elapsed:.1f}",
                f"Track time: {elapsed:.1f}ms"
            ]

            y_offset = 30
            for text in info_text:
                cv2.putText(vis_frame, text, (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                y_offset += 25

            cv2.imshow('Person Tracking - Camera', vis_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

    print(f"\n{CYAN}Processed {frame_count} frames, tracked {len(active_ids)} unique people{NC}")


def main():
    parser = argparse.ArgumentParser(description='Test person tracking system')

    parser.add_argument('--video', type=str, help='Path to video file')
    parser.add_argument('--camera', type=int, help='Camera device ID')
    parser.add_argument('--output', type=str, help='Output video path')
    parser.add_argument('--no-show', action='store_true', help='Do not show video window')

    args = parser.parse_args()

    if args.video:
        test_video(args.video, output_path=args.output, show=not args.no_show)
    elif args.camera is not None:
        test_camera(args.camera)
    else:
        print(f"{YELLOW}Usage:{NC}")
        print(f"  Test with video: python3 {sys.argv[0]} --video path/to/video.mp4")
        print(f"  Test with camera: python3 {sys.argv[0]} --camera 0")
        print(f"  Save output: python3 {sys.argv[0]} --video input.mp4 --output output.mp4")


if __name__ == '__main__':
    main()
