#!/usr/bin/env python3
"""
VLM Image Testing Tool
Test any image with MLX-optimized VLM and save results

Usage:
    python test_vlm_image.py <image_path>
    python test_vlm_image.py tests/images/test_classroom1.jpg
    python test_vlm_image.py tests/images/*.jpg
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from PIL import Image as PILImage
import glob

# Suppres torch warning
import warnings
warnings.filterwarnings('ignore')


class VLMTester:
    """VLM testing tool with MLX"""

    def __init__(self, model_name="mlx-community/llava-1.5-7b-4bit"):
        self.model_name = model_name
        self.model = None
        self.processor = None
        self.results_dir = Path("test_results")
        self.results_dir.mkdir(exist_ok=True)

    def load_model(self):
        """Load MLX model"""
        if self.model is not None:
            return  # Already loaded

        print(f"Loading model: {self.model_name}")
        print("(This may take a moment on first run...)\n")

        try:
            from mlx_vlm import load
            start = time.time()
            self.model, self.processor = load(self.model_name)
            elapsed = time.time() - start
            print(f"✓ Model loaded in {elapsed:.1f}s\n")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("\nTrying to fix version compatibility...")
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "transformers==4.45.0"])
            print("\nPlease run the script again.")
            sys.exit(1)

    def analyze_image(self, image_path, prompt=None):
        """Analyze a single image"""

        if prompt is None:
            # Default childcare safety prompt
            prompt = """Analyze this childcare image for safety violations:

1. Are adults present supervising children?
2. Is there any physical aggression or violence?
3. Are any children in distress?
4. Are there any safety hazards?
5. What is the overall safety status?

Provide a detailed analysis."""

        # Load image
        try:
            image = PILImage.open(image_path).convert('RGB')
        except Exception as e:
            return {
                "error": f"Failed to load image: {e}",
                "image_path": str(image_path)
            }

        # Generate response
        try:
            from mlx_vlm import generate

            print(f"📸 Analyzing: {Path(image_path).name}")
            print(f"   Size: {image.size}")
            print(f"   Generating response...")

            start_time = time.time()

            # Try different parameter combinations for compatibility
            try:
                # Method 1: Direct call
                response = generate(
                    self.model,
                    self.processor,
                    prompt,
                    image,
                    max_tokens=500,
                    temperature=0.3
                )
            except Exception as e1:
                try:
                    # Method 2: Using image path
                    response = generate(
                        self.model,
                        self.processor,
                        prompt,
                        str(image_path),
                        max_tokens=500,
                        temperature=0.3
                    )
                except Exception as e2:
                    return {
                        "error": f"Generation failed: {e1}",
                        "image_path": str(image_path),
                        "attempts": [str(e1), str(e2)]
                    }

            elapsed = time.time() - start_time

            result = {
                "image_path": str(image_path),
                "image_name": Path(image_path).name,
                "image_size": image.size,
                "model": self.model_name,
                "prompt": prompt,
                "response": response,
                "processing_time_seconds": round(elapsed, 2),
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }

            print(f"   ✓ Completed in {elapsed:.2f}s\n")

            return result

        except Exception as e:
            return {
                "error": str(e),
                "image_path": str(image_path),
                "status": "failed"
            }

    def save_results(self, result, output_format="txt"):
        """Save results to file"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_name = Path(result["image_path"]).stem

        if output_format == "txt":
            output_file = self.results_dir / f"{image_name}_{timestamp}.txt"

            with open(output_file, 'w') as f:
                f.write("=" * 70 + "\n")
                f.write("VLM Image Analysis Results\n")
                f.write("=" * 70 + "\n\n")

                f.write(f"Image: {result.get('image_name', 'N/A')}\n")
                f.write(f"Path: {result.get('image_path', 'N/A')}\n")
                f.write(f"Size: {result.get('image_size', 'N/A')}\n")
                f.write(f"Model: {result.get('model', 'N/A')}\n")
                f.write(f"Timestamp: {result.get('timestamp', 'N/A')}\n")
                f.write(f"Processing Time: {result.get('processing_time_seconds', 'N/A')}s\n")
                f.write(f"Status: {result.get('status', 'N/A')}\n")
                f.write("\n" + "=" * 70 + "\n")
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
                f.write(f"Results saved: {output_file}\n")
                f.write("=" * 70 + "\n")

        elif output_format == "json":
            output_file = self.results_dir / f"{image_name}_{timestamp}.json"

            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)

        return output_file

    def test_images(self, image_paths, prompt=None, save_txt=True, save_json=False):
        """Test multiple images"""

        # Load model once
        self.load_model()

        # Expand wildcards
        all_paths = []
        for path in image_paths:
            if '*' in path:
                all_paths.extend(glob.glob(path))
            else:
                all_paths.append(path)

        all_paths = [p for p in all_paths if Path(p).exists()]

        if not all_paths:
            print("❌ No valid image paths found")
            return []

        print(f"Testing {len(all_paths)} image(s)...\n")
        print("=" * 70 + "\n")

        results = []

        for i, image_path in enumerate(all_paths, 1):
            print(f"[{i}/{len(all_paths)}]")

            result = self.analyze_image(image_path, prompt)
            results.append(result)

            # Save results
            if save_txt:
                txt_file = self.save_results(result, "txt")
                print(f"   📄 Saved: {txt_file}")

            if save_json:
                json_file = self.save_results(result, "json")
                print(f"   📄 Saved: {json_file}")

            print()

        # Summary
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)

        successful = sum(1 for r in results if r.get('status') == 'success')
        failed = len(results) - successful

        print(f"Total images: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")

        if successful > 0:
            times = [r['processing_time_seconds'] for r in results if 'processing_time_seconds' in r]
            avg_time = sum(times) / len(times)
            print(f"\nAverage processing time: {avg_time:.2f}s")

            # Calculate speedup
            current_time = 150  # Current Ollama average
            speedup = current_time / avg_time
            print(f"Current system average: ~{current_time}s")
            print(f"🚀 Speedup: {speedup:.0f}x faster!\n")

        print(f"Results saved in: {self.results_dir}/")
        print("=" * 70)

        return results


def main():
    """Main entry point"""

    print("=" * 70)
    print("VLM Image Testing Tool")
    print("=" * 70 + "\n")

    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  {sys.argv[0]} <image_path>")
        print(f"  {sys.argv[0]} tests/images/test_classroom1.jpg")
        print(f"  {sys.argv[0]} tests/images/*.jpg")
        print(f"  {sys.argv[0]} /path/to/image.jpg")
        print()

        # Test with default images if they exist
        default_images = [
            "tests/images/test_classroom1.jpg",
            "tests/images/test_classroom2.jpg",
            "tests/images/test_violence.jpg"
        ]

        existing = [p for p in default_images if Path(p).exists()]

        if existing:
            print(f"Found {len(existing)} test images. Test them? (y/n): ", end='')
            response = input().strip().lower()
            if response == 'y':
                image_paths = existing
            else:
                print("Exiting.")
                sys.exit(0)
        else:
            print("No images specified and no test images found.")
            sys.exit(1)
    else:
        image_paths = sys.argv[1:]

    # Create tester
    tester = VLMTester()

    # Custom prompt (optional)
    prompt = None  # Use default

    # You can customize the prompt here:
    # prompt = "Describe what you see in this image in detail."

    # Test images
    results = tester.test_images(
        image_paths,
        prompt=prompt,
        save_txt=True,
        save_json=True  # Also save JSON for easy parsing
    )

    print("\n✅ Testing complete!")


if __name__ == "__main__":
    main()
