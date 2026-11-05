#!/usr/bin/env python3
"""
Optimize MViT V2 Model

Applies various optimization techniques:
1. ONNX conversion (cross-platform, optimized runtime)
2. Dynamic quantization (INT8, reduces model size and speeds up CPU inference)
3. Static quantization (requires calibration data)

Usage:
    python3 tools/optimization/optimize_mvit.py \
        --model models/mvit_violence.pth \
        --output models/optimized/
"""
import sys
import argparse
import time
from pathlib import Path
import numpy as np

# ANSI colors
BLUE = '\033[0;34m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
NC = '\033[0m'


def load_mvit_model(model_path):
    """Load MViT V2 model"""
    try:
        import torch
        import torch.nn as nn
        from torchvision.models.video import mvit_v2_s

        model = mvit_v2_s(weights=None)

        # Replace classification head
        num_features = model.head[1].in_features
        model.head[1] = nn.Linear(num_features, 2)

        # Load trained weights
        checkpoint = torch.load(model_path, map_location="cpu")
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()

        print(f"{GREEN}✓ Loaded MViT V2 model{NC}")
        return model
    except Exception as e:
        print(f"{RED}✗ Failed to load model: {e}{NC}")
        return None


def create_dummy_input():
    """Create dummy input for export"""
    import torch

    # 16 frames, 224x224, 3 channels
    # Shape: (batch, channels, frames, height, width)
    dummy = torch.randn(1, 3, 16, 224, 224)
    return dummy


def export_to_onnx(model, output_path):
    """Export PyTorch model to ONNX format"""
    try:
        import torch

        print(f"\n{YELLOW}Converting to ONNX...{NC}")

        dummy_input = create_dummy_input()

        torch.onnx.export(
            model,
            dummy_input,
            output_path,
            export_params=True,
            opset_version=14,
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={
                'input': {0: 'batch_size'},
                'output': {0: 'batch_size'}
            }
        )

        # Get file size
        size_mb = Path(output_path).stat().st_size / (1024 * 1024)

        print(f"{GREEN}✓ ONNX model saved: {output_path}{NC}")
        print(f"  Size: {size_mb:.1f}MB")

        return True
    except Exception as e:
        print(f"{RED}✗ ONNX export failed: {e}{NC}")
        return False


def apply_dynamic_quantization(model, output_path):
    """Apply dynamic quantization (INT8)"""
    try:
        import torch

        print(f"\n{YELLOW}Applying dynamic quantization...{NC}")

        # Dynamic quantization - converts weights to INT8
        quantized_model = torch.quantization.quantize_dynamic(
            model,
            {torch.nn.Linear, torch.nn.Conv3d},
            dtype=torch.qint8
        )

        # Save quantized model
        torch.save({
            'model_state_dict': quantized_model.state_dict(),
            'quantized': True
        }, output_path)

        # Get file size
        size_mb = Path(output_path).stat().st_size / (1024 * 1024)

        print(f"{GREEN}✓ Quantized model saved: {output_path}{NC}")
        print(f"  Size: {size_mb:.1f}MB")

        return quantized_model
    except Exception as e:
        print(f"{RED}✗ Quantization failed: {e}{NC}")
        return None


def benchmark_model(model, name, iterations=10, is_onnx=False):
    """Benchmark model inference speed"""
    import torch

    print(f"\n{CYAN}Benchmarking {name}...{NC}")

    if is_onnx:
        return benchmark_onnx_model(model, iterations)

    # Create input
    dummy_input = create_dummy_input()

    # Warmup
    for _ in range(3):
        with torch.no_grad():
            _ = model(dummy_input)

    # Benchmark
    times = []
    for i in range(iterations):
        start = time.time()
        with torch.no_grad():
            _ = model(dummy_input)
        end = time.time()
        times.append((end - start) * 1000)

    avg_time = np.mean(times)
    std_time = np.std(times)
    min_time = np.min(times)

    print(f"  Avg: {avg_time:.2f}ms (±{std_time:.2f}ms)")
    print(f"  Min: {min_time:.2f}ms")

    return avg_time, min_time


def benchmark_onnx_model(onnx_path, iterations=10):
    """Benchmark ONNX model with ONNX Runtime"""
    try:
        import onnxruntime as ort
        import numpy as np

        # Create session
        sess = ort.InferenceSession(onnx_path)

        # Create input
        dummy_input = np.random.randn(1, 3, 16, 224, 224).astype(np.float32)

        # Warmup
        for _ in range(3):
            _ = sess.run(None, {'input': dummy_input})

        # Benchmark
        times = []
        for i in range(iterations):
            start = time.time()
            _ = sess.run(None, {'input': dummy_input})
            end = time.time()
            times.append((end - start) * 1000)

        avg_time = np.mean(times)
        std_time = np.std(times)
        min_time = np.min(times)

        print(f"  Avg: {avg_time:.2f}ms (±{std_time:.2f}ms)")
        print(f"  Min: {min_time:.2f}ms")

        return avg_time, min_time

    except ImportError:
        print(f"{YELLOW}  ⚠ onnxruntime not installed, skipping ONNX benchmark{NC}")
        print(f"    Install with: pip install onnxruntime")
        return None, None
    except Exception as e:
        print(f"{RED}  ✗ ONNX benchmark failed: {e}{NC}")
        return None, None


def main():
    parser = argparse.ArgumentParser(description='Optimize MViT V2 model')

    parser.add_argument('--model', default='models/mvit_violence.pth', help='Input model path')
    parser.add_argument('--output', default='models/optimized/', help='Output directory')
    parser.add_argument('--iterations', type=int, default=20, help='Benchmark iterations')

    args = parser.parse_args()

    print(f"{BLUE}{'='*60}{NC}")
    print(f"{BLUE}MViT V2 MODEL OPTIMIZATION{NC}")
    print(f"{BLUE}{'='*60}{NC}\n")

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load original model
    print("Loading original model...")
    original_model = load_mvit_model(args.model)

    if original_model is None:
        sys.exit(1)

    # Get original model size
    original_size = Path(args.model).stat().st_size / (1024 * 1024)
    print(f"  Original size: {original_size:.1f}MB\n")

    results = {}

    # Benchmark original model
    print(f"{CYAN}{'='*60}{NC}")
    print(f"{CYAN}1. ORIGINAL MODEL (Baseline){NC}")
    print(f"{CYAN}{'='*60}{NC}")
    orig_avg, orig_min = benchmark_model(original_model, "Original PyTorch", args.iterations)
    results['Original'] = {'avg': orig_avg, 'min': orig_min, 'size': original_size}

    # ONNX Export
    print(f"\n{CYAN}{'='*60}{NC}")
    print(f"{CYAN}2. ONNX EXPORT{NC}")
    print(f"{CYAN}{'='*60}{NC}")

    onnx_path = output_dir / "mvit_violence.onnx"
    if export_to_onnx(original_model, str(onnx_path)):
        onnx_size = Path(onnx_path).stat().st_size / (1024 * 1024)
        onnx_avg, onnx_min = benchmark_onnx_model(str(onnx_path), args.iterations)
        if onnx_avg:
            results['ONNX'] = {'avg': onnx_avg, 'min': onnx_min, 'size': onnx_size}

    # Dynamic Quantization
    print(f"\n{CYAN}{'='*60}{NC}")
    print(f"{CYAN}3. DYNAMIC QUANTIZATION (INT8){NC}")
    print(f"{CYAN}{'='*60}{NC}")

    quant_path = output_dir / "mvit_violence_quantized.pth"
    quantized_model = apply_dynamic_quantization(original_model, str(quant_path))
    if quantized_model:
        quant_size = Path(quant_path).stat().st_size / (1024 * 1024)
        quant_avg, quant_min = benchmark_model(quantized_model, "Quantized PyTorch", args.iterations)
        results['Quantized'] = {'avg': quant_avg, 'min': quant_min, 'size': quant_size}

    # Print summary
    print(f"\n{BLUE}{'='*60}{NC}")
    print(f"{BLUE}OPTIMIZATION SUMMARY{NC}")
    print(f"{BLUE}{'='*60}{NC}\n")

    print(f"{'Model':<20} {'Size':<15} {'Avg Time':<15} {'Min Time':<15} {'Speedup':<10}")
    print(f"{'-'*75}")

    for name, data in results.items():
        speedup = orig_avg / data['avg']
        size_reduction = (1 - data['size'] / original_size) * 100

        color = GREEN if speedup > 1.2 else YELLOW if speedup > 1.0 else NC

        size_str = f"{data['size']:.1f}MB"
        avg_str = f"{data['avg']:.2f}ms"
        min_str = f"{data['min']:.2f}ms"
        speedup_str = f"{speedup:.2f}x"

        print(f"{name:<20} {size_str:<15} {color}{avg_str:<15}{NC} {color}{min_str:<15}{NC} {color}{speedup_str:<10}{NC}")

    # Find best optimization
    print(f"\n{CYAN}Recommendations:{NC}")

    best_speed = min(results.items(), key=lambda x: x[1]['avg'])
    best_size = min(results.items(), key=lambda x: x[1]['size'])

    print(f"\n{GREEN}Best Speed:{NC} {best_speed[0]} ({best_speed[1]['avg']:.2f}ms)")
    print(f"{GREEN}Best Size:{NC} {best_size[0]} ({best_size[1]['size']:.1f}MB)")

    if best_speed[1]['avg'] < 200:
        print(f"\n{GREEN}✓ {best_speed[0]} meets <200ms target!{NC}")
        print(f"  Use: {output_dir / ('mvit_violence.onnx' if best_speed[0] == 'ONNX' else 'mvit_violence_quantized.pth')}")
    else:
        print(f"\n{YELLOW}⚠ No optimization brings inference below 200ms target{NC}")
        print(f"  Best achieved: {best_speed[1]['avg']:.2f}ms with {best_speed[0]}")
        print(f"  Consider: Hardware acceleration (GPU) or lighter architecture")


if __name__ == '__main__':
    main()
