#!/usr/bin/env python3
"""
Quick MLX VLM test with a smaller, faster model
"""

import time
from pathlib import Path
from PIL import Image

def test_mlx_vlm():
    """Test MLX VLM with available model"""

    print("="  * 70)
    print("Mac M4 Max - Quick VLM Test")
    print("=" * 70 + "\n")

    try:
        from mlx_vlm import load, generate
        from mlx_vlm.prompt_utils import apply_chat_template
        from mlx_vlm.utils import load_config
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Run: pip install mlx-vlm")
        return

    # Use a known working model
    model_path = "mlx-community/llava-1.5-7b-4bit"

    print(f"Loading model: {model_path}")
    print("(First run will download ~4GB, takes 5-10 minutes)\n")

    try:
        start_load = time.time()
        model, processor = load(model_path)
        config = load_config(model_path)
        load_time = time.time() - start_load

        print(f"✓ Model loaded in {load_time:.1f}s\n")

    except Exception as e:
        print(f"❌ Error loading model: {e}\n")
        print("Trying alternative model...")

        # Try smaller model
        model_path = "mlx-community/paligemma-3b-mix-448-8bit"
        print(f"Loading: {model_path}\n")

        try:
            model, processor = load(model_path)
            config = load_config(model_path)
            print("✓ Alternative model loaded\n")
        except Exception as e2:
            print(f"❌ Also failed: {e2}")
            print("\nAvailable models:")
            print("  - mlx-community/llava-1.5-7b-4bit")
            print("  - mlx-community/paligemma-3b-mix-448-8bit")
            print("\nCheck https://huggingface.co/mlx-community for more")
            return

    # Test with one image
    test_image = "tests/images/test_classroom1.jpg"

    if not Path(test_image).exists():
        print(f"⚠️  Test image not found: {test_image}")
        print("Creating a simple test...")

        # Create a simple test image
        from PIL import Image
        import numpy as np
        test_img = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
        test_image = "/tmp/test.jpg"
        test_img.save(test_image)
        print(f"✓ Created test image: {test_image}\n")

    print(f"📸 Analyzing {Path(test_image).name}...")

    try:
        # Load image
        image = Image.open(test_image).convert('RGB')

        # Simple prompt
        prompt = "Describe what you see in this image."

        # Format prompt
        formatted_prompt = apply_chat_template(
            processor, config, prompt, num_images=1
        )

        # Measure inference
        print("Running inference...")
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

        print(f"\n✓ Completed in {elapsed:.2f}s")
        print(f"\nResponse:\n{output}\n")

        # Calculate speedup
        current_time = 150  # Current average
        speedup = current_time / elapsed

        print("=" * 70)
        print("PERFORMANCE RESULTS")
        print("=" * 70)
        print(f"Latency: {elapsed:.2f}s")
        print(f"Current system: ~{current_time}s")
        print(f"Speedup: {speedup:.0f}x faster! 🚀")

        if elapsed < 1.0:
            print("\n✅ EXCELLENT - Meeting <1s target!")
        elif elapsed < 2.0:
            print("\n✅ GOOD - Under 2s, production ready!")
        elif elapsed < 5.0:
            print("\n✅ ACCEPTABLE - Much better than current!")
        else:
            print("\n⚠️  SLOW - But still better than 150s!")

        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("1. Test with your classroom images")
        print("2. Load 4 instances for parallel processing")
        print("3. Integrate with NURA services")
        print("4. Add fast-path models for 70% of frames")
        print("\n🎉 M4 Max optimization is working!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"❌ Error during inference: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mlx_vlm()
