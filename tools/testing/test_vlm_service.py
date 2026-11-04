#!/usr/bin/env python3
"""
VLM Service Testing Tool
Test images with the running VLM service and save results

Usage:
    python tools/testing/test_vlm_service.py <image_path>
    python tools/testing/test_vlm_service.py tests/images/test_classroom1.jpg
    python tools/testing/test_vlm_service.py "path/to/your/image.jpg"

Results saved to: test_results/
"""

import sys
import time
import json
import base64
import requests
from pathlib import Path
from datetime import datetime


def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')


def test_vlm_service(image_path, vlm_url="http://localhost:8001", prompt=None):
    """Test VLM service with an image"""

    image_path = Path(image_path)

    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        return None

    # Default prompt for childcare safety
    if prompt is None:
        prompt = """Analyze this childcare image for safety violations:

1. Supervision: Are adults present supervising children? What is the ratio?
2. Physical Safety: Is there any physical aggression, violence, or dangerous behavior?
3. Child Wellbeing: Are any children in distress, crying, or showing signs of injury?
4. Environment: Are there any safety hazards visible (sharp objects, unsafe equipment)?
5. Severity: If violations exist, classify as LOW, MEDIUM, or HIGH severity.

Provide a detailed analysis."""

    print("=" * 70)
    print(f"Testing VLM Service")
    print("=" * 70)
    print(f"Image: {image_path.name}")
    print(f"Path: {image_path}")
    print(f"VLM URL: {vlm_url}")
    print(f"Prompt: {prompt[:100]}...")
    print()

    # Encode image
    print("📸 Encoding image...")
    try:
        image_b64 = encode_image(image_path)
        print(f"   ✓ Image encoded ({len(image_b64)} bytes)")
    except Exception as e:
        print(f"   ❌ Error encoding image: {e}")
        return None

    # Prepare request
    payload = {
        "image_base64": image_b64,
        "prompt": prompt
    }

    # Send request
    print("\n🤖 Sending to VLM service...")
    print("   (This may take 30-180 seconds depending on your setup)")

    start_time = time.time()

    try:
        response = requests.post(
            f"{vlm_url}/analyze",
            json=payload,
            timeout=300  # 5 minutes max
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            result = response.json()

            print(f"\n✅ Analysis complete in {elapsed:.1f}s")
            print()
            print("=" * 70)
            print("ANALYSIS RESULT")
            print("=" * 70)
            print()
            print(result.get('analysis', 'No analysis returned'))
            print()
            print("=" * 70)

            # Save results
            save_result(image_path, result, elapsed, prompt)

            return result
        else:
            print(f"\n❌ Error: HTTP {response.status_code}")
            print(f"   {response.text}")
            return None

    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"\n⏱️  Request timed out after {elapsed:.1f}s")
        print("   Try increasing VLM_TIMEOUT in .env")
        return None
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection refused to {vlm_url}")
        print("   Make sure the VLM service is running:")
        print("   docker compose ps | grep vlm")
        return None
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ Error after {elapsed:.1f}s: {e}")
        return None


def save_result(image_path, result, elapsed_time, prompt):
    """Save result to files"""

    results_dir = Path("test_results")
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_name = Path(image_path).stem

    # Save as TXT
    txt_file = results_dir / f"{image_name}_{timestamp}.txt"

    with open(txt_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("VLM Service Analysis Results\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Image: {Path(image_path).name}\n")
        f.write(f"Path: {image_path}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Processing Time: {elapsed_time:.1f}s\n\n")

        f.write("=" * 70 + "\n")
        f.write("PROMPT\n")
        f.write("=" * 70 + "\n\n")
        f.write(prompt + "\n\n")

        f.write("=" * 70 + "\n")
        f.write("ANALYSIS\n")
        f.write("=" * 70 + "\n\n")
        f.write(result.get('analysis', 'No analysis returned') + "\n\n")

        f.write("=" * 70 + "\n")

    # Save as JSON
    json_file = results_dir / f"{image_name}_{timestamp}.json"

    full_result = {
        "image_path": str(image_path),
        "image_name": Path(image_path).name,
        "timestamp": datetime.now().isoformat(),
        "processing_time_seconds": round(elapsed_time, 1),
        "prompt": prompt,
        "analysis": result.get('analysis', ''),
        "model": result.get('model', 'unknown'),
        "status": "success"
    }

    with open(json_file, 'w') as f:
        json.dump(full_result, f, indent=2)

    print(f"\n📄 Results saved:")
    print(f"   TXT: {txt_file}")
    print(f"   JSON: {json_file}")


def test_service_health(vlm_url="http://localhost:8001"):
    """Test if VLM service is healthy"""

    try:
        response = requests.get(f"{vlm_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ VLM service is healthy at {vlm_url}")
            return True
        else:
            print(f"⚠️  VLM service returned HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to VLM service at {vlm_url}")
        print("\nTroubleshooting:")
        print("1. Check if service is running:")
        print("   docker compose ps | grep vlm")
        print("\n2. Check logs:")
        print("   docker compose logs nura-vlm")
        print("\n3. If using Mac, ensure native Ollama is running:")
        print("   ollama ps")
        return False
    except Exception as e:
        print(f"❌ Error checking health: {e}")
        return False


def main():
    """Main function"""

    if len(sys.argv) < 2:
        print("Usage: python test_vlm_service.py <image_path>")
        print("\nExamples:")
        print("  python tools/testing/test_vlm_service.py tests/images/test_classroom1.jpg")
        print("  python tools/testing/test_vlm_service.py path/to/your/image.jpg")
        print("\nCustom prompt:")
        print('  python tools/testing/test_vlm_service.py image.jpg "Describe this image"')
        sys.exit(1)

    image_path = sys.argv[1]
    custom_prompt = sys.argv[2] if len(sys.argv) > 2 else None

    # Check service health first
    print("\nChecking VLM service health...")
    if not test_service_health():
        sys.exit(1)

    print()

    # Test with image
    result = test_vlm_service(image_path, prompt=custom_prompt)

    if result:
        print("\n✅ Test completed successfully!")
        print(f"\nResults saved in: test_results/")
    else:
        print("\n❌ Test failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
