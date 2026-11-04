#!/usr/bin/env python3
"""
Simple image testing with Ollama (current system) for comparison
This bypasses MLX version issues and uses your existing setup
"""

import sys
import time
import json
import base64
from pathlib import Path
from datetime import datetime
import requests

def test_with_ollama(image_path, prompt=None):
    """Test image with current Ollama setup"""

    if prompt is None:
        prompt = """Analyze this childcare image for safety:

1. Are adults present supervising children?
2. Is there any physical aggression or violence?
3. Are any children in distress?
4. Are there any safety hazards?

Answer in detail."""

    print(f"📸 Testing: {Path(image_path).name}")
    print(f"   Using: Current Ollama system (for comparison)")

    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    # Call VLM service
    url = "http://localhost:8001/analyze"

    try:
        print(f"   Sending request...")
        start = time.time()

        response = requests.post(
            url,
            json={
                "camera_id": "test",
                "image_base64": image_data,
                "prompt": prompt
            },
            timeout=300
        )

        elapsed = time.time() - start

        if response.status_code == 200:
            result = response.json()

            print(f"   ✓ Completed in {elapsed:.1f}s")

            return {
                "image_path": str(image_path),
                "processing_time": elapsed,
                "result": result,
                "status": "success"
            }
        else:
            print(f"   ❌ Error: {response.status_code}")
            return {
                "image_path": str(image_path),
                "error": f"HTTP {response.status_code}",
                "status": "failed"
            }

    except requests.exceptions.Timeout:
        elapsed = time.time() - start
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
    txt_file = Path(output_dir) / f"{image_name}_{timestamp}.txt"

    with open(txt_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("VLM Image Analysis Results (Ollama System)\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Image: {Path(result['image_path']).name}\n")
        f.write(f"Path: {result['image_path']}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Processing Time: {result.get('processing_time', 'N/A'):.1f}s\n")
        f.write(f"Status: {result.get('status', 'N/A')}\n\n")

        f.write("=" * 70 + "\n")
        f.write("RESULT\n")
        f.write("=" * 70 + "\n\n")

        if 'error' in result:
            f.write(f"ERROR: {result['error']}\n")
        elif 'result' in result:
            f.write(json.dumps(result['result'], indent=2))
            f.write("\n")

        f.write("\n" + "=" * 70 + "\n")

    # JSON file
    json_file = Path(output_dir) / f"{image_name}_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(result, f, indent=2)

    return txt_file, json_file

def main():
    """Main function"""

    print("=" * 70)
    print("Image Testing Tool (Ollama Current System)")
    print("=" * 70 + "\n")

    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  {sys.argv[0]} <image_path>")
        print(f"\nExample:")
        print(f"  {sys.argv[0]} tests/images/test_classroom1.jpg")
        sys.exit(1)

    image_path = sys.argv[1]

    if not Path(image_path).exists():
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)

    # Test image
    result = test_with_ollama(image_path)

    # Save results
    txt_file, json_file = save_result(result)

    print(f"\n   📄 Saved: {txt_file}")
    print(f"   📄 Saved: {json_file}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if result['status'] == 'success':
        print(f"✅ Success")
        print(f"Processing time: {result['processing_time']:.1f}s")
        print(f"\nNote: Current system is SLOW (2-3 minutes expected)")
        print(f"MLX optimization will be 100x+ faster!")
    elif result['status'] == 'timeout':
        print(f"⏱️  Timeout - image processing took too long")
        print(f"This is the problem we're solving with MLX!")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")

    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
