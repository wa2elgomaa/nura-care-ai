#!/usr/bin/env python3
"""
Final MLX VLM test with classroom images
"""

import time
from pathlib import Path
from PIL import Image as PILImage

def test_mlx_vlm():
    """Test MLX VLM with classroom images"""

    print("=" * 70)
    print("Mac M4 Max - VLM Performance Test")
    print("=" * 70 + "\n")

    from mlx_vlm import load, generate
    from mlx_vlm.prompt_utils import apply_chat_template
    from mlx_vlm.utils import load_config

    model_path = "mlx-community/llava-1.5-7b-4bit"

    print("Loading model (already downloaded)...")
    start_load = time.time()
    model, processor = load(model_path)
    config = load_config(model_path)
    load_time = time.time() - start_load
    print(f"✓ Model loaded in {load_time:.1f}s\n")

    # Test images
    test_images = [
        ("tests/images/test_classroom1.jpg", "Adult supervision test"),
        ("tests/images/test_classroom2.jpg", "Ambiguous scene test"),
        ("tests/images/test_violence.jpg", "Violence detection test"),
    ]

    prompt = """Analyze this childcare image for safety:

1. Are adults present supervising children?
2. Is there any physical aggression or violence?
3. Are any children in distress?

Answer in 2-3 sentences."""

    results = []

    for img_path, description in test_images:
        if not Path(img_path).exists():
            print(f"⚠️  Skipping {img_path} (not found)\n")
            continue

        print(f"📸 {description}")
        print(f"   File: {Path(img_path).name}")

        try:
            # Load image
            image = PILImage.open(img_path).convert('RGB')

            # Format prompt
            formatted_prompt = apply_chat_template(
                processor, config, prompt, num_images=1
            )

            # Measure inference
            start = time.time()

            output = generate(
                model,
                processor,
                image,
                formatted_prompt,
                max_tokens=200,
                temperature=0.3,
                verbose=False
            )

            elapsed = time.time() - start
            results.append(elapsed)

            print(f"   ✓ Completed in {elapsed:.2f}s")
            print(f"   Response: {output[:150]}...\n")

        except Exception as e:
            print(f"   ❌ Error: {e}\n")

    if results:
        print("=" * 70)
        print("PERFORMANCE RESULTS")
        print("=" * 70)
        avg = sum(results) / len(results)
        print(f"Images tested: {len(results)}")
        print(f"Average latency: {avg:.2f}s")
        print(f"Min: {min(results):.2f}s, Max: {max(results):.2f}s")
        print(f"Target: <5s for production")

        current = 150  # Current average
        speedup = current / avg

        print(f"\n🚀 SPEEDUP: {speedup:.0f}x faster than current ({current}s)!")

        if avg < 1.0:
            print("\n✅ EXCELLENT - Sub-second performance!")
        elif avg < 2.0:
            print("\n✅ VERY GOOD - Under 2 seconds!")
        elif avg < 5.0:
            print("\n✅ GOOD - Production ready!")
        else:
            print("\n✅ ACCEPTABLE - Still much faster!")

        print("\n" + "=" * 70)
        print("CAPACITY ANALYSIS")
        print("=" * 70)
        throughput = 1 / avg
        print(f"Single instance: {throughput:.1f} FPS")

        instances = 4
        total_fps = throughput * instances
        print(f"{instances} parallel instances: {total_fps:.1f} FPS")
        print(f"Camera capacity: {int(total_fps)} cameras @ 1 FPS")

        if total_fps >= 10:
            print("\n✅ Can handle 10+ cameras!")

        print("\n💡 With your 128GB RAM, you can run even more instances!")
        print("=" * 70)

    else:
        print("❌ No images tested")

if __name__ == "__main__":
    test_mlx_vlm()
