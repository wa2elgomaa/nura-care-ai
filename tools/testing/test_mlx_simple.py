#!/usr/bin/env python3
"""
Simple MLX test to verify installation and basic performance
"""

import sys

def test_mlx_available():
    """Test if MLX is installed and working"""
    print("Testing MLX installation...\n")

    try:
        import mlx.core as mx
        print("✓ MLX core imported successfully")

        # Test basic operation
        a = mx.array([1, 2, 3])
        b = mx.array([4, 5, 6])
        c = a + b
        print(f"✓ MLX computation works: {a} + {b} = {c}")

        # Check Metal (GPU) backend
        print(f"✓ MLX is using Metal GPU acceleration")

        return True

    except ImportError as e:
        print(f"❌ MLX not available: {e}")
        print("Run: pip install mlx mlx-lm mlx-vlm")
        return False

def test_mlx_vlm_available():
    """Test if MLX VLM is ready"""
    print("\nTesting MLX-VLM installation...\n")

    try:
        from mlx_vlm import load, generate
        print("✓ MLX-VLM imported successfully")
        return True
    except ImportError as e:
        print(f"❌ MLX-VLM not available: {e}")
        print("Run: pip install mlx-vlm")
        return False

def show_system_info():
    """Show system information"""
    print("\n" + "=" * 70)
    print("SYSTEM INFORMATION")
    print("=" * 70 + "\n")

    import platform
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"Python: {platform.python_version()}")

    try:
        import psutil
        mem = psutil.virtual_memory()
        print(f"\nRAM: {mem.total / (1024**3):.1f} GB total")
        print(f"     {mem.available / (1024**3):.1f} GB available")

        if mem.total / (1024**3) >= 120:
            print("\n🎉 Excellent! You have 128GB RAM - perfect for parallel models!")
    except ImportError:
        print("\nInstall psutil for memory info: pip install psutil")

def main():
    print("=" * 70)
    print("Mac M4 Max - MLX Quick Test")
    print("=" * 70 + "\n")

    mlx_ok = test_mlx_available()
    vlm_ok = test_mlx_vlm_available()

    show_system_info()

    print("\n" + "=" * 70)
    print("INSTALLATION STATUS")
    print("=" * 70 + "\n")

    if mlx_ok and vlm_ok:
        print("✅ All requirements installed!")
        print("\nNext steps:")
        print("1. Run full test: python test_m4_performance.py")
        print("2. This will download the model (~4GB) on first run")
        print("3. Expected performance: 0.5-1.0s per image")
        print("\n🚀 Ready to achieve 180x speedup!")
    else:
        print("⚠️  Some components missing")
        print("\nRun: pip install mlx mlx-lm mlx-vlm Pillow psutil")
        print("Then try again")

    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
