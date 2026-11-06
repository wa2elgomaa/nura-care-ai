#!/usr/bin/env python3
"""
Benchmark Person Tracking Performance

Tests performance metrics:
- Inference speed (ms per frame)
- Throughput (FPS)
- Scalability (vs number of people)
- Memory usage

Usage:
    # Basic benchmark
    python3 tools/testing/benchmark_person_tracking.py

    # With specific video
    python3 tools/testing/benchmark_person_tracking.py --video tests/videos/classroom_1.mp4

    # Test different detector sizes
    python3 tools/testing/benchmark_person_tracking.py --model-size s  # n/s/m
"""

import sys
import os
import argparse
import time
import cv2
import numpy as np
from pathlib import Path
from collections import defaultdict

# Add package to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'packages' / 'nura-detectors' / 'src'))

# ANSI colors
BLUE = '\033[0;34m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
NC = '\033[0m'


def benchmark_detection_only(tracker, frames, iterations=10):
    """Benchmark just the detection component"""

    print(f"{YELLOW}Benchmarking detection only...{NC}")

    times = []
    person_counts = []

    for i in range(iterations):
        frame = frames[i % len(frames)]

        start = time.time()
        detections = tracker.detector.detect(frame)
        elapsed = (time.time() - start) * 1000

        times.append(elapsed)
        person_counts.append(len(detections))

    avg_time = np.mean(times)
    std_time = np.std(times)
    avg_people = np.mean(person_counts)

    print(f"  Detection time: {avg_time:.2f}ms (±{std_time:.2f}ms)")
    print(f"  Average people: {avg_people:.1f}")
    print()

    return {'avg': avg_time, 'std': std_time, 'avg_people': avg_people}


def benchmark_tracking_only(tracker, detections_list, iterations=10):
    """Benchmark just the tracking component"""

    print(f"{YELLOW}Benchmarking tracking only...{NC}")

    times = []
    track_counts = []

    # Reset tracker
    tracker.tracker = type(tracker.tracker)()

    for i in range(iterations):
        detections = detections_list[i % len(detections_list)]

        start = time.time()
        tracks = tracker.tracker.update(detections)
        elapsed = (time.time() - start) * 1000

        times.append(elapsed)
        track_counts.append(len(tracks))

    avg_time = np.mean(times)
    std_time = np.std(times)
    avg_tracks = np.mean(track_counts)

    print(f"  Tracking time: {avg_time:.2f}ms (±{std_time:.2f}ms)")
    print(f"  Average tracks: {avg_tracks:.1f}")
    print()

    return {'avg': avg_time, 'std': std_time, 'avg_tracks': avg_tracks}


def benchmark_end_to_end(tracker, frames, iterations=10):
    """Benchmark complete pipeline"""

    print(f"{YELLOW}Benchmarking end-to-end...{NC}")

    times = []
    track_counts = []

    # Reset tracker
    from nura_detectors.person_tracker import ByteTracker
    tracker.tracker = ByteTracker()

    for i in range(iterations):
        frame = frames[i % len(frames)]

        start = time.time()
        tracks = tracker.update(frame)
        elapsed = (time.time() - start) * 1000

        times.append(elapsed)
        track_counts.append(len(tracks))

    avg_time = np.mean(times)
    std_time = np.std(times)
    min_time = np.min(times)
    max_time = np.max(times)
    avg_tracks = np.mean(track_counts)

    print(f"  Total time: {avg_time:.2f}ms (±{std_time:.2f}ms)")
    print(f"  Min time: {min_time:.2f}ms")
    print(f"  Max time: {max_time:.2f}ms")
    print(f"  Average tracks: {avg_tracks:.1f}")
    print(f"  FPS: {1000/avg_time:.1f}")
    print()

    return {
        'avg': avg_time,
        'std': std_time,
        'min': min_time,
        'max': max_time,
        'avg_tracks': avg_tracks,
        'fps': 1000/avg_time
    }


def benchmark_scalability(tracker, base_frame, max_people=10):
    """Test how performance scales with number of people"""

    print(f"{YELLOW}Benchmarking scalability (vs number of people)...{NC}")

    results = []

    # Create synthetic scenarios with different person counts
    for n_people in range(1, max_people + 1):
        # Get n detections
        detections = tracker.detector.detect(base_frame)

        # If no detections, create synthetic ones
        if len(detections) == 0:
            print(f"{YELLOW}  No people detected in frame, creating synthetic detections{NC}")
            h, w = base_frame.shape[:2]
            # Create synthetic detections with random positions
            for i in range(n_people):
                x1 = np.random.randint(0, w // 2)
                y1 = np.random.randint(0, h // 2)
                x2 = x1 + np.random.randint(50, 150)
                y2 = y1 + np.random.randint(100, 300)
                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'conf': 0.9,
                    'class': 0
                })
        elif len(detections) < n_people:
            # Duplicate some detections if needed
            original_count = len(detections)
            while len(detections) < n_people:
                detections.append(detections[len(detections) % original_count].copy())

        detections = detections[:n_people]

        # Benchmark tracking with this many people
        times = []
        for _ in range(10):
            start = time.time()
            tracks = tracker.tracker.update(detections)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)

        avg_time = np.mean(times)
        results.append({'people': n_people, 'time': avg_time})

        print(f"  {n_people} people: {avg_time:.2f}ms")

    print()
    return results


def load_test_frames(video_path, num_frames=30):
    """Load frames from video for benchmarking"""

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"{RED}✗ Could not open video: {video_path}{NC}")
        return None

    frames = []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Sample frames uniformly
    frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)

    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            frames.append(frame)

    cap.release()

    print(f"{GREEN}✓ Loaded {len(frames)} frames from video{NC}\n")
    return frames


def main():
    parser = argparse.ArgumentParser(description='Benchmark person tracking performance')

    parser.add_argument('--video', type=str,
                       default='tests/videos/classroom_1.mp4',
                       help='Path to test video')
    parser.add_argument('--model-size', type=str, default='n',
                       choices=['n', 's', 'm'],
                       help='YOLO model size (n=nano, s=small, m=medium)')
    parser.add_argument('--iterations', type=int, default=30,
                       help='Number of iterations for each test')

    args = parser.parse_args()

    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}PERSON TRACKING PERFORMANCE BENCHMARK{NC}")
    print(f"{BLUE}{'='*70}{NC}\n")

    # Load frames
    print(f"Loading test frames from: {args.video}")
    frames = load_test_frames(args.video, num_frames=args.iterations)

    if not frames:
        return 1

    # Load tracker
    print(f"{YELLOW}Loading person tracker (model: yolov8{args.model_size})...{NC}")
    try:
        from nura_detectors.person_tracker import PersonTracker
        tracker = PersonTracker(detector_model=args.model_size)
        print(f"{GREEN}✓ Tracker loaded{NC}\n")
    except Exception as e:
        print(f"{RED}✗ Failed to load tracker: {e}{NC}")
        return 1

    # Warmup
    print(f"{YELLOW}Warming up...{NC}")
    for _ in range(5):
        tracker.update(frames[0])
    print(f"{GREEN}✓ Warmup complete{NC}\n")

    # Run benchmarks
    print(f"{CYAN}{'='*70}{NC}")
    print(f"{CYAN}1. DETECTION BENCHMARK{NC}")
    print(f"{CYAN}{'='*70}{NC}\n")

    detection_results = benchmark_detection_only(tracker, frames, args.iterations)

    # Get detections for tracking-only benchmark
    print(f"{YELLOW}Collecting detections for tracking benchmark...{NC}")
    detections_list = [tracker.detector.detect(f) for f in frames[:args.iterations]]
    print(f"{GREEN}✓ Collected {len(detections_list)} detection sets{NC}\n")

    print(f"{CYAN}{'='*70}{NC}")
    print(f"{CYAN}2. TRACKING BENCHMARK{NC}")
    print(f"{CYAN}{'='*70}{NC}\n")

    tracking_results = benchmark_tracking_only(tracker, detections_list, args.iterations)

    print(f"{CYAN}{'='*70}{NC}")
    print(f"{CYAN}3. END-TO-END BENCHMARK{NC}")
    print(f"{CYAN}{'='*70}{NC}\n")

    e2e_results = benchmark_end_to_end(tracker, frames, args.iterations)

    print(f"{CYAN}{'='*70}{NC}")
    print(f"{CYAN}4. SCALABILITY BENCHMARK{NC}")
    print(f"{CYAN}{'='*70}{NC}\n")

    scalability_results = benchmark_scalability(tracker, frames[0], max_people=10)

    # Summary
    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}BENCHMARK SUMMARY{NC}")
    print(f"{BLUE}{'='*70}{NC}\n")

    print(f"{'Component':<20} {'Avg Time':<15} {'Throughput':<15} {'Notes':<20}")
    print(f"{'-'*70}")

    det_fps = 1000 / detection_results['avg'] if detection_results['avg'] > 0 else 0
    track_fps = 1000 / tracking_results['avg'] if tracking_results['avg'] > 0 else 0

    
    # Pre-format strings to avoid f-string backslash issues
    det_time_str = f"{detection_results['avg']:.2f}ms"
    det_fps_str = f"{det_fps:.1f} FPS"
    det_people_str = f"{detection_results['avg_people']:.1f} people avg"
    
    track_time_str = f"{tracking_results['avg']:.2f}ms"
    track_fps_str = f"{track_fps:.1f} FPS"
    track_tracks_str = f"{tracking_results['avg_tracks']:.1f} tracks avg"
    
    e2e_time_str = f"{e2e_results['avg']:.2f}ms"
    e2e_fps_str = f"{e2e_results['fps']:.1f} FPS"
    e2e_tracks_str = f"{e2e_results['avg_tracks']:.1f} tracks avg"
    
    print(f"{'Detection':<20} {det_time_str:<15} {det_fps_str:<15} {det_people_str:<20}")
    print(f"{'Tracking':<20} {track_time_str:<15} {track_fps_str:<15} {track_tracks_str:<20}")
    print(f"{'Total (E2E)':<20} {e2e_time_str:<15} {e2e_fps_str:<15} {e2e_tracks_str:<20}")
    print()

    # Performance targets
    print(f"{CYAN}Performance Analysis:{NC}\n")

    target_e2e = 200  # ms
    target_fps = 5    # for 10 cameras

    if e2e_results['avg'] < target_e2e:
        print(f"{GREEN}✓ Meets <200ms target ({e2e_results['avg']:.2f}ms){NC}")
    else:
        print(f"{RED}✗ Exceeds 200ms target ({e2e_results['avg']:.2f}ms){NC}")

    if e2e_results['fps'] > target_fps:
        print(f"{GREEN}✓ Good throughput for multi-camera ({e2e_results['fps']:.1f} FPS){NC}")
    else:
        print(f"{YELLOW}⚠ Low throughput ({e2e_results['fps']:.1f} FPS){NC}")

    # Overhead calculation
    overhead = e2e_results['avg'] - detection_results['avg']
    overhead_pct = (overhead / detection_results['avg']) * 100

    print(f"\nTracking overhead: {overhead:.2f}ms ({overhead_pct:.1f}% of detection time)")

    if overhead < 50:
        print(f"{GREEN}✓ Low tracking overhead (<50ms){NC}")
    else:
        print(f"{YELLOW}⚠ High tracking overhead (>50ms){NC}")

    # Scalability
    print(f"\n{CYAN}Scalability:{NC}")
    if scalability_results:
        time_1 = scalability_results[0]['time']
        time_10 = scalability_results[-1]['time']
        increase = ((time_10 - time_1) / time_1) * 100

        print(f"  1 person: {time_1:.2f}ms")
        print(f"  10 people: {time_10:.2f}ms")
        print(f"  Increase: +{increase:.1f}%")

        if increase < 100:
            print(f"{GREEN}✓ Good scalability (<100% increase for 10x people){NC}")
        else:
            print(f"{YELLOW}⚠ Poor scalability (>{increase:.0f}% increase){NC}")

    # Recommendation
    print(f"\n{CYAN}{'='*70}{NC}")
    print(f"{CYAN}RECOMMENDATION{NC}")
    print(f"{CYAN}{'='*70}{NC}\n")

    if e2e_results['avg'] < 100:
        print(f"{GREEN}Excellent performance! Can handle 10+ FPS per camera.{NC}")
        print(f"Suitable for 10-15 cameras with light sampling (2-5 FPS).")
    elif e2e_results['avg'] < 200:
        print(f"{YELLOW}Good performance. Can handle 5 FPS per camera.{NC}")
        print(f"Suitable for 5-10 cameras with moderate sampling.")
    else:
        print(f"{RED}Slow performance. Recommend GPU or lighter model.{NC}")
        print(f"Consider: YOLOv8n (nano) or GPU acceleration.")

    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
