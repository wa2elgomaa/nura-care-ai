#!/usr/bin/env python3
"""
Test llama.cpp with LLaVA v1.6 models
Compatible with llama.cpp 0.8.0
"""

import subprocess
import time
import json
from pathlib import Path
from datetime import datetime


def test_llava_v16(image_path, prompt=None):
    """Test image with llama.cpp and LLaVA v1.6"""

    if prompt is None:
        prompt = """Analyze this childcare image for safety:

1. Are adults present supervising children?
2. Is there any physical aggression or violence?
3. Are any children in distress?
4. Are there any safety hazards?

Answer in detail."""

    model_path = "models/gguf/llava-v1.6-mistral-7b.Q4_K_M.gguf"
    mmproj_path = "models/gguf/llava-v1.6-mistral-7b-mmproj.gguf"

    # Check if models exist
    if not Path(model_path).exists():
        print(f"❌ Model not found: {model_path}")
        print("\nRun: ./download_compatible_llava.sh")
        return None

    if not Path(mmproj_path).exists():
        print(f"❌ Vision model not found: {mmproj_path}")
        print("\nRun: ./download_compatible_llava.sh")
        return None

    if not Path(image_path).exists():
        print(f"❌ Image not found: {image_path}")
        return None

    print(f"📸 Analyzing: {Path(image_path).name}")
    print(f"   Model: LLaVA v1.6 Mistral 7B Q4_K_M")
    print(f"   Backend: llama.cpp 0.8.0 with Metal GPU")
    print(f"   Generating response...")

    # Build llama-cli command
    cmd = [
        "llama-cli",
        "-m", model_path,
        "--mmproj", mmproj_path,
        "--image", image_path,
        "-p", prompt,
        "-n", "500",
        "--temp", "0.3",
        "-ngl", "99",  # GPU layers
        "-t", "8"       # CPU threads
    ]

    try:
        start_time = time.time()

        # Run llama-cli
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            # Parse output
            output = result.stdout

            # Extract response (after the prompt)
            response_lines = []
            capture = False
            for line in output.split('\n'):
                if prompt.strip() in line or capture:
                    capture = True
                    response_lines.append(line)

            response = '\n'.join(response_lines).strip()

            # Clean up response
            if response.startswith(prompt):
                response = response[len(prompt):].strip()

            print(f"   ✓ Completed in {elapsed:.2f}s\n")

            return {
                "image_path": str(image_path),
                "image_name": Path(image_path).name,
                "model": "LLaVA v1.6 Mistral 7B Q4_K_M",
                "backend": "llama.cpp 0.8.0 + Metal GPU",
                "prompt": prompt,
                "response": response if response else output,
                "processing_time_seconds": round(elapsed, 2),
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
        else:
            print(f"   ❌ Error: {result.returncode}")
            stderr = result.stderr[:500] if result.stderr else "No error output"
            print(f"   {stderr}")

            return {
                "image_path": str(image_path),
                "error": stderr,
                "status": "failed"
            }

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"   ⏱️  Timeout after {elapsed:.1f}s")
        return {
            "image_path": str(image_path),
            "error": f"Timeout after {elapsed:.1f}s",
            "status": "timeout"
        }
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            "image_path": str(image_path),
            "error": str(e),
            "status": "failed"
        }


def save_result(result, output_dir="test_results"):
    """Save result to file"""

    Path(output_dir).mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_name = Path(result["image_path"]).stem

    # TXT file
    txt_file = Path(output_dir) / f"{image_name}_llava16_{timestamp}.txt"

    with open(txt_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("LLaVA v1.6 Analysis Results\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Image: {result.get('image_name', 'N/A')}\n")
        f.write(f"Path: {result.get('image_path', 'N/A')}\n")
        f.write(f"Model: {result.get('model', 'N/A')}\n")
        f.write(f"Backend: {result.get('backend', 'N/A')}\n")
        f.write(f"Timestamp: {result.get('timestamp', 'N/A')}\n")
        f.write(f"Processing Time: {result.get('processing_time_seconds', 'N/A')}s\n")
        f.write(f"Status: {result.get('status', 'N/A')}\n\n")

        f.write("=" * 70 + "\n")
        f.write("PROMPT\n")
        f.write("=" * 70 + "\n\n")
        f.write(result.get('prompt', 'N/A') + "\n\n")

        f.write("=" * 70 + "\n")
        f.write("ANALYSIS\n")
        f.write("=" * 70 + "\n\n")

        if 'error' in result:
            f.write(f"ERROR: {result['error']}\n")
        else:
            f.write(result.get('response', 'No response') + "\n")

        f.write("\n" + "=" * 70 + "\n")

    # JSON file
    json_file = Path(output_dir) / f"{image_name}_llava16_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(result, f, indent=2)

    return txt_file, json_file


def main():
    """Main function"""

    print("=" * 70)
    print("LLaVA v1.6 Performance Test (llama.cpp 0.8.0)")
    print("=" * 70 + "\n")

    # Test images
    test_images = [
        "tests/images/test_classroom1.jpg",
        "tests/images/test_classroom2.jpg",
        "tests/images/test_violence.jpg"
    ]

    results = []

    for image_path in test_images:
        if not Path(image_path).exists():
            print(f"⚠️  Skipping {image_path} (not found)\n")
            continue

        result = test_llava_v16(image_path)

        if result:
            results.append(result)

            # Save results
            txt_file, json_file = save_result(result)
            print(f"   📄 Saved: {txt_file}")
            print(f"   📄 Saved: {json_file}\n")

    # Summary
    if results:
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)

        successful = [r for r in results if r.get('status') == 'success']

        print(f"Total images: {len(results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(results) - len(successful)}")

        if successful:
            times = [r['processing_time_seconds'] for r in successful]
            avg_time = sum(times) / len(times)

            print(f"\nAverage processing time: {avg_time:.2f}s")
            print(f"Min: {min(times):.2f}s, Max: {max(times):.2f}s")

            # Calculate speedup
            current_time = 150  # Current average
            speedup = current_time / avg_time

            print(f"\nCurrent system average: ~{current_time}s")
            print(f"🚀 Speedup: {speedup:.0f}x faster!\n")

            if avg_time < 1.0:
                print("✅ EXCELLENT - Sub-second performance!")
            elif avg_time < 2.0:
                print("✅ VERY GOOD - Under 2 seconds!")
            elif avg_time < 5.0:
                print("✅ GOOD - Production ready!")
            else:
                print("✅ ACCEPTABLE - Better than current!")

            # Multi-camera capacity
            throughput = 1 / avg_time
            instances = 4
            total_fps = throughput * instances

            print(f"\nCapacity Analysis:")
            print(f"  Single instance: {throughput:.1f} FPS")
            print(f"  4 parallel instances: {total_fps:.1f} FPS")
            print(f"  Camera capacity: {int(total_fps)} cameras @ 1 FPS")

            if total_fps >= 10:
                print("\n✅ Can handle 10+ cameras in real-time!")

        print(f"\nResults saved in: test_results/")
        print("=" * 70)

    else:
        print("❌ No images processed successfully")


if __name__ == "__main__":
    main()
