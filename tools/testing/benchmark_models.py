#!/usr/bin/env python3
"""
Benchmark Inference Speed: MViT vs ResNet50+GRU

Compares the two temporal violence detection models:
- MViT V2 (97.50% accuracy, PyTorch)
- ResNet50+GRU (95.83% accuracy, Keras)

Usage:
    python3 tools/testing/benchmark_models.py \
        --video tests/videos/fighting.mp4 \
        --iterations 10
"""
import sys
import argparse
import time
from pathlib import Path
import numpy as np
import cv2

# ANSI colors
BLUE = '\033[0;34m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
NC = '\033[0m'


def load_keras_model():
    """Load ResNet50+GRU model (baseline)"""
    try:
        import tensorflow as tf
        model_path = "models/temporal_violence.keras"
        model = tf.keras.models.load_model(model_path)
        print(f"{GREEN}✓ Loaded ResNet50+GRU model{NC}")
        return model, "keras"
    except Exception as e:
        print(f"{RED}✗ Failed to load Keras model: {e}{NC}")
        return None, None


def load_mvit_model():
    """Load MViT V2 model"""
    try:
        import torch
        from torchvision.models.video import mvit_v2_s

        model = mvit_v2_s(weights=None)

        # Replace classification head (400 -> 2 classes)
        import torch.nn as nn
        num_features = model.head[1].in_features
        model.head[1] = nn.Linear(num_features, 2)

        # Load trained weights
        checkpoint = torch.load("models/mvit_violence.pth", map_location="cpu")
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()

        print(f"{GREEN}✓ Loaded MViT V2 model{NC}")
        return model, "pytorch"
    except Exception as e:
        print(f"{RED}✗ Failed to load MViT model: {e}{NC}")
        return None, None


def load_video_frames(video_path, num_frames=20, target_size=(224, 224)):
    """Load frames from video"""
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"{RED}✗ Could not open video: {video_path}{NC}")
        return None

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames < num_frames:
        print(f"{YELLOW}⚠ Video has only {total_frames} frames, need {num_frames}{NC}")
        cap.release()
        return None

    # Sample frames uniformly
    frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)

    frames = []
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, target_size)
            frames.append(frame)

    cap.release()

    if len(frames) != num_frames:
        return None

    return np.array(frames)


def preprocess_for_keras(frames):
    """Preprocess frames for Keras model (ResNet50+GRU)"""
    # Normalize to [0, 1]
    frames = frames.astype(np.float32) / 255.0

    # Add batch dimension: (20, 224, 224, 3) -> (1, 20, 224, 224, 3)
    frames = np.expand_dims(frames, axis=0)

    return frames


def preprocess_for_pytorch(frames):
    """Preprocess frames for PyTorch model (MViT)"""
    import torch

    # Convert to tensor: (T, H, W, C) -> (C, T, H, W)
    frames = torch.from_numpy(frames).permute(3, 0, 1, 2).float()

    # Normalize (ImageNet stats)
    frames = frames / 255.0
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1, 1)
    frames = (frames - mean) / std

    # Add batch dimension: (C, T, H, W) -> (1, C, T, H, W)
    frames = frames.unsqueeze(0)

    return frames


def benchmark_keras_model(model, frames, iterations=10):
    """Benchmark Keras model inference speed"""
    import tensorflow as tf

    # Preprocess
    input_frames = preprocess_for_keras(frames)

    # Warmup
    _ = model.predict(input_frames, verbose=0)

    # Benchmark
    times = []
    predictions = []

    for i in range(iterations):
        start = time.time()
        pred = model.predict(input_frames, verbose=0)
        end = time.time()

        times.append((end - start) * 1000)  # Convert to ms
        predictions.append(pred[0])

    return times, predictions


def benchmark_pytorch_model(model, frames, iterations=10):
    """Benchmark PyTorch model inference speed"""
    import torch

    # Preprocess (only 16 frames for MViT)
    frames_subset = frames[:16]  # MViT uses 16 frames
    input_frames = preprocess_for_pytorch(frames_subset)

    # Warmup
    with torch.no_grad():
        _ = model(input_frames)

    # Benchmark
    times = []
    predictions = []

    for i in range(iterations):
        start = time.time()
        with torch.no_grad():
            pred = model(input_frames)
        end = time.time()

        times.append((end - start) * 1000)  # Convert to ms
        predictions.append(pred[0].numpy())

    return times, predictions


def print_results(name, times, predictions, accuracy):
    """Print benchmark results"""
    avg_time = np.mean(times)
    std_time = np.std(times)
    min_time = np.min(times)
    max_time = np.max(times)

    # Get prediction confidence
    pred_probs = [p[1] if len(p) == 2 else np.max(p) for p in predictions]
    avg_confidence = np.mean(pred_probs) * 100

    print(f"\n{CYAN}{'='*60}{NC}")
    print(f"{CYAN}{name}{NC}")
    print(f"{CYAN}{'='*60}{NC}")
    print(f"Accuracy:        {GREEN}{accuracy:.2f}%{NC}")
    print(f"Avg Time:        {YELLOW}{avg_time:.2f}ms{NC} (±{std_time:.2f}ms)")
    print(f"Min Time:        {GREEN}{min_time:.2f}ms{NC}")
    print(f"Max Time:        {RED}{max_time:.2f}ms{NC}")
    print(f"Avg Confidence:  {avg_confidence:.1f}%")
    print(f"Iterations:      {len(times)}")


def main():
    parser = argparse.ArgumentParser(description='Benchmark temporal violence detection models')

    parser.add_argument('--video', default='tests/videos/fighting.mp4', help='Test video path')
    parser.add_argument('--iterations', type=int, default=10, help='Number of inference iterations')

    args = parser.parse_args()

    print(f"{BLUE}{'='*60}{NC}")
    print(f"{BLUE}TEMPORAL VIOLENCE DETECTION - INFERENCE BENCHMARK{NC}")
    print(f"{BLUE}{'='*60}{NC}\n")

    # Load video
    print(f"Loading video: {args.video}")
    frames = load_video_frames(args.video, num_frames=20)

    if frames is None:
        print(f"{RED}✗ Failed to load video frames{NC}")
        sys.exit(1)

    print(f"{GREEN}✓ Loaded {len(frames)} frames from video{NC}\n")

    # Load models
    print("Loading models...")
    keras_model, keras_type = load_keras_model()
    mvit_model, mvit_type = load_mvit_model()

    if keras_model is None and mvit_model is None:
        print(f"{RED}✗ No models could be loaded{NC}")
        sys.exit(1)

    print()

    # Benchmark ResNet50+GRU (Keras)
    if keras_model is not None:
        print(f"{YELLOW}Benchmarking ResNet50+GRU (baseline)...{NC}")
        keras_times, keras_preds = benchmark_keras_model(keras_model, frames, args.iterations)
        print_results("ResNet50+GRU (Keras)", keras_times, keras_preds, 95.83)

    # Benchmark MViT V2 (PyTorch)
    if mvit_model is not None:
        print(f"\n{YELLOW}Benchmarking MViT V2...{NC}")
        mvit_times, mvit_preds = benchmark_pytorch_model(mvit_model, frames, args.iterations)
        print_results("MViT V2 (PyTorch)", mvit_times, mvit_preds, 97.50)

    # Comparison
    if keras_model is not None and mvit_model is not None:
        print(f"\n{BLUE}{'='*60}{NC}")
        print(f"{BLUE}COMPARISON{NC}")
        print(f"{BLUE}{'='*60}{NC}")

        keras_avg = np.mean(keras_times)
        mvit_avg = np.mean(mvit_times)

        speed_diff = mvit_avg - keras_avg
        speed_ratio = mvit_avg / keras_avg
        acc_diff = 97.50 - 95.83

        print(f"Accuracy Improvement:  {GREEN}+{acc_diff:.2f}%{NC} (MViT)")
        print(f"Speed Difference:      {YELLOW}{speed_diff:+.2f}ms{NC} (MViT {'slower' if speed_diff > 0 else 'faster'})")
        print(f"Speed Ratio:           {YELLOW}{speed_ratio:.2f}x{NC}")

        if mvit_avg < 200:
            print(f"\n{GREEN}✓ MViT meets <200ms target ({mvit_avg:.2f}ms){NC}")
        else:
            print(f"\n{RED}✗ MViT exceeds <200ms target ({mvit_avg:.2f}ms){NC}")

        print(f"\n{CYAN}Recommendation:{NC}")
        if speed_diff < 100 and acc_diff > 1:
            print(f"  {GREEN}→ Switch to MViT{NC} (Better accuracy, acceptable speed)")
        elif speed_diff > 200:
            print(f"  {YELLOW}→ Keep ResNet50+GRU{NC} (MViT too slow)")
        else:
            print(f"  {CYAN}→ Keep both available{NC} (Trade-off between speed and accuracy)")


if __name__ == '__main__':
    main()
