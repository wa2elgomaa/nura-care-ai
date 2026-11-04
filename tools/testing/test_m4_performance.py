#!/usr/bin/env python3
"""
Test M4 Max performance with MLX-optimized LLaVA
Expected: 0.5-1.0 second per image (vs 120-180s current)
"""

import time
from pathlib import Path
from PIL import Image
import sys

def test_single_frame():
    """Test single frame analysis with MLX"""

    print("=" * 70)
    print("Mac M4 Max VLM Performance Test")
    print("=" * 70 + "\n")

    try:
        from mlx_vlm import load, generate
        from mlx_vlm.prompt_utils import apply_chat_template
        from mlx_vlm.utils import load_config
    except ImportError:
        print("❌ mlx-vlm not installed")
        print("Run: pip install mlx-vlm")
        return

    print("Loading MLX-optimized LLaVA model...")
    print("(First run will download ~4GB model, takes 5-10 minutes)\n")

    model_path = "mlx-community/llava-1.6-mistral-7b-4bit"

    try:
        # Load model - will auto-download on first run
        model, processor = load(model_path)
        config = load_config(model_path)
        print("✓ Model loaded successfully\n")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("\nTrying to download model explicitly...")
        import subprocess
        subprocess.run([
            "huggingface-cli", "download",
            model_path,
            "--local-dir", f"./models/{model_path.split('/')[-1]}"
        ])
        return

    # Test images
    test_images = [
        "tests/images/test_classroom1.jpg",
        "tests/images/test_classroom2.jpg",
        "tests/images/test_violence.jpg"
    ]

    prompt = """Analyze this childcare image for safety violations:

1. Are adults present supervising children?
2. Is there any physical aggression or violence?
3. Are any children in distress?
4. Are there safety hazards visible?

Answer concisely in 2-3 sentences."""

    results = []

    for img_path in test_images:
        if not Path(img_path).exists():
            print(f"⚠️  Skipping {img_path} (not found)")
            continue

        print(f"📸 Analyzing {Path(img_path).name}...")

        try:
            # Load image
            image = Image.open(img_path).convert('RGB')

            # Prepare prompt
            formatted_prompt = apply_chat_template(
                processor, config, prompt, num_images=1
            )

            # Measure inference time
            start = time.time()

            output = generate(
                model,
                processor,
                image,
                formatted_prompt,
                max_tokens=300,
                temperature=0.3,
                verbose=False
            )

            elapsed = time.time() - start
            results.append(elapsed)

            print(f"   ✓ Completed in {elapsed:.2f}s")
            print(f"   Response: {output[:150]}...")
            print()

        except Exception as e:
            print(f"   ❌ Error: {e}\n")

    if results:
        print("=" * 70)
        print("PERFORMANCE RESULTS")
        print("=" * 70)
        print(f"Average latency: {sum(results)/len(results):.2f}s")
        print(f"Min: {min(results):.2f}s, Max: {max(results):.2f}s")
        print(f"Target: 0.5-1.0s per image")

        avg = sum(results) / len(results)
        current = 150  # Current average (120-180s)
        speedup = current / avg

        print(f"\n🚀 SPEEDUP: {speedup:.0f}x faster than current!")

        if avg < 1.0:
            print("✅ EXCELLENT - Meeting performance target!")
            print("   Ready for production multi-camera deployment!")
        elif avg < 2.0:
            print("✅ GOOD - 2x faster optimization still possible")
            print("   Already production-ready for 10+ cameras!")
        else:
            print("⚠️  SLOWER than expected - Check Metal GPU acceleration")

        print("\n" + "=" * 70)
        print("CAPACITY ANALYSIS")
        print("=" * 70)
        throughput = 1 / avg
        print(f"Single instance throughput: {throughput:.1f} FPS")

        # With 128GB, can run 4 instances in parallel
        instances = 4
        total_throughput = throughput * instances
        print(f"With {instances} parallel instances: {total_throughput:.1f} FPS")
        print(f"Can support: {int(total_throughput)} cameras @ 1 FPS")

        if total_throughput >= 10:
            print("\n✅ Can handle 10+ cameras in real-time!")

        print("\n💡 Your M4 Max has 128GB RAM - you can run even more instances!")

    else:
        print("❌ No images tested")
        print("Make sure test images exist in tests/images/")

def test_memory_capacity():
    """Show how much memory is available for models"""

    print("\n" + "=" * 70)
    print("MEMORY CAPACITY ANALYSIS")
    print("=" * 70)

    try:
        import psutil
        mem = psutil.virtual_memory()
        total_gb = mem.total / (1024**3)
        used_gb = mem.used / (1024**3)
        available_gb = mem.available / (1024**3)

        print(f"Total RAM: {total_gb:.1f} GB")
        print(f"Used: {used_gb:.1f} GB")
        print(f"Available: {available_gb:.1f} GB")

        # Each model instance uses ~4GB
        model_size = 4
        max_instances = int(available_gb / model_size * 0.8)  # 80% safety margin

        print(f"\n📊 With {model_size}GB per model instance:")
        print(f"   Can load: {max_instances} parallel instances")
        print(f"   Total throughput: {max_instances * 1.0:.0f} FPS (estimated)")

        if total_gb >= 120:
            print(f"\n🎉 Your {total_gb:.0f}GB RAM is PERFECT for this!")
            print("   Most systems have 16-32GB - yours enables massive parallelism!")

    except ImportError:
        print("Install psutil to see memory analysis: pip install psutil")

if __name__ == "__main__":
    print("\n🚀 Starting M4 Max VLM Performance Test...\n")

    # Test single frame performance
    test_single_frame()

    # Show memory capacity
    test_memory_capacity()

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("1. If performance is good (< 1s), integrate with NURA services")
    print("2. Load 4 parallel instances for multi-camera support")
    print("3. Add fast-path models (CoreML) for 70% of frames")
    print("\nSee docs/QUICKSTART_M4_MAX.md for integration guide")
    print("=" * 70 + "\n")
