#!/usr/bin/env python3
"""
Simple Inference Speed Benchmark

Compares inference speed of:
- MViT V2 (PyTorch, 97.50% accuracy)
- ResNet50+GRU reference (estimated from training logs)

Usage:
    python3 tools/testing/benchmark_speed.py --iterations 10
"""
import sys
import argparse
import time
import numpy as np
import cv2

# ANSI colors
BLUE = '\033[0;34m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
NC = '\033[0m'


def load_mvit_model():
    """Load MViT V2 model"""
    try:
        import torch
        from torchvision.models.video import mvit_v2_s
        import torch.nn as nn

        model = mvit_v2_s(weights=None)

        # Replace classification head (400 -> 2 classes)
        num_features = model.head[1].in_features
        model.head[1] = nn.Linear(num_features, 2)

        # Load trained weights
        checkpoint = torch.load("models/mvit_violence.pth", map_location="cpu")
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()

        print(f"{GREEN}✓ Loaded MViT V2 model{NC}")
        return model
    except Exception as e:
        print(f"{RED}✗ Failed to load MViT model: {e}{NC}")
        return None


def create_dummy_input():
    """Create dummy video input (16 frames, 224x224x3)"""
    import torch

    # Random frames
    frames = np.random.randint(0, 255, (16, 224, 224, 3), dtype=np.uint8)

    # Convert to tensor: (T, H, W, C) -> (C, T, H, W)
    frames = torch.from_numpy(frames).permute(3, 0, 1, 2).float()

    # Normalize (ImageNet stats)
    frames = frames / 255.0
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1, 1)
    frames = (frames - mean) / std

    # Add batch dimension
    frames = frames.unsqueeze(0)

    return frames


def benchmark_mvit(model, iterations=10):
    """Benchmark MViT V2 inference speed"""
    import torch

    # Create input
    input_frames = create_dummy_input()

    # Warmup (5 iterations)
    print(f"{YELLOW}Warming up...{NC}")
    for _ in range(5):
        with torch.no_grad():
            _ = model(input_frames)

    # Benchmark
    print(f"{YELLOW}Running {iterations} iterations...{NC}")
    times = []

    for i in range(iterations):
        start = time.time()
        with torch.no_grad():
            pred = model(input_frames)
        end = time.time()

        times.append((end - start) * 1000)  # Convert to ms
        print(f"  Run {i+1}: {times[-1]:.2f}ms")

    return times


def print_results(times):
    """Print benchmark results"""
    avg_time = np.mean(times)
    std_time = np.std(times)
    min_time = np.min(times)
    max_time = np.max(times)
    median_time = np.median(times)

    print(f"\n{CYAN}{'='*60}{NC}")
    print(f"{CYAN}MViT V2 INFERENCE BENCHMARK{NC}")
    print(f"{CYAN}{'='*60}{NC}")
    print(f"Model Accuracy:  {GREEN}97.50%{NC}")
    print(f"Avg Time:        {YELLOW}{avg_time:.2f}ms{NC} (±{std_time:.2f}ms)")
    print(f"Median Time:     {YELLOW}{median_time:.2f}ms{NC}")
    print(f"Min Time:        {GREEN}{min_time:.2f}ms{NC}")
    print(f"Max Time:        {RED}{max_time:.2f}ms{NC}")
    print(f"Iterations:      {len(times)}")

    if avg_time < 200:
        print(f"\n{GREEN}✓ Meets <200ms target{NC}")
    else:
        print(f"\n{RED}✗ Exceeds <200ms target{NC}")


def main():
    parser = argparse.ArgumentParser(description='Benchmark MViT inference speed')
    parser.add_argument('--iterations', type=int, default=10, help='Number of iterations')
    args = parser.parse_args()

    print(f"{BLUE}{'='*60}{NC}")
    print(f"{BLUE}MViT V2 INFERENCE SPEED BENCHMARK{NC}")
    print(f"{BLUE}{'='*60}{NC}\n")

    # Load model
    print("Loading MViT V2 model...")
    model = load_mvit_model()

    if model is None:
        print(f"{RED}✗ Failed to load model{NC}")
        sys.exit(1)

    print()

    # Benchmark
    times = benchmark_mvit(model, args.iterations)

    # Results
    print_results(times)

    # Comparison with baseline
    print(f"\n{BLUE}{'='*60}{NC}")
    print(f"{BLUE}COMPARISON WITH BASELINE{NC}")
    print(f"{BLUE}{'='*60}{NC}")

    resnet_time = 150  # ResNet50+GRU baseline (from prior testing)
    resnet_acc = 95.83
    mvit_time = np.mean(times)
    mvit_acc = 97.50

    print(f"\n{'Model':<20} {'Accuracy':<15} {'Speed':<15}")
    print(f"{'-'*50}")
    print(f"{'ResNet50+GRU':<20} {f'{resnet_acc:.2f}%':<15} {f'~{resnet_time:.0f}ms':<15}")
    print(f"{'MViT V2':<20} {f'{mvit_acc:.2f}%':<15} {f'{mvit_time:.0f}ms':<15}")

    acc_gain = mvit_acc - resnet_acc
    speed_diff = mvit_time - resnet_time

    print(f"\n{CYAN}Improvement:{NC}")
    print(f"  Accuracy: {GREEN}+{acc_gain:.2f}%{NC}")
    print(f"  Speed:    {YELLOW if speed_diff > 0 else GREEN}{speed_diff:+.0f}ms{NC} ({'slower' if speed_diff > 0 else 'faster'})")

    print(f"\n{CYAN}Recommendation:{NC}")
    if mvit_time < 200 and acc_gain > 1:
        print(f"  {GREEN}✓ Switch to MViT V2{NC}")
        print(f"    - Better accuracy (+{acc_gain:.2f}%)")
        print(f"    - Acceptable speed ({mvit_time:.0f}ms < 200ms target)")
    elif speed_diff > 100:
        print(f"  {YELLOW}⚠ Keep ResNet50+GRU{NC}")
        print(f"    - MViT is {speed_diff:.0f}ms slower")
        print(f"    - Accuracy gain (+{acc_gain:.2f}%) may not justify speed cost")
    else:
        print(f"  {CYAN}→ Deploy both models{NC}")
        print(f"    - Use ResNet50+GRU for real-time (faster)")
        print(f"    - Use MViT for batch/offline (more accurate)")


if __name__ == '__main__':
    main()
