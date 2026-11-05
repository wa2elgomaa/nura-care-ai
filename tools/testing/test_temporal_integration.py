#!/usr/bin/env python3
"""
Test Temporal RNN Integration with Hybrid System
Tests the full pipeline: Fast-path → Temporal RNN → VLM
"""
import sys
import cv2
import time
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "nura-detectors" / "src"))

def test_temporal_on_video(video_path: str, model_path: str = "models/temporal_test.h5"):
    """
    Test temporal detector on a video file
    
    Args:
        video_path: Path to video file
        model_path: Path to trained temporal model
    """
    try:
        from nura_detectors.temporal_detector import TemporalViolenceDetector
    except ImportError as e:
        print(f"❌ Error importing temporal detector: {e}")
        print("Make sure TensorFlow is installed: pip3 install tensorflow")
        return
    
    print("╔══════════════════════════════════════════════════════════╗")
    print("║       TEMPORAL RNN DETECTOR TEST                         ║")
    print("╚══════════════════════════════════════════════════════════╝\n")
    
    # Check if model exists
    if not Path(model_path).exists():
        print(f"❌ Model not found: {model_path}")
        print("\nTrain a model first:")
        print("  python3 tools/training/train_temporal_detector.py \\")
        print("    --violent tests/data/Videos/FightingA_Part1 \\")
        print("    --normal tests/data/Videos/Normal_Videos_for_Event_Recognition/Normal_Videos_for_Event_Recognition \\")
        print("    --epochs 5 --max-videos 20 \\")
        print("    --output models/temporal_test.h5")
        return
    
    # Check if video exists
    if not Path(video_path).exists():
        print(f"❌ Video not found: {video_path}")
        return
    
    print(f"📹 Video: {video_path}")
    print(f"🎯 Model: {model_path}\n")
    
    # Load detector
    print("⏳ Loading temporal detector...")
    start = time.time()
    detector = TemporalViolenceDetector(
        sequence_length=20,
        model_path=model_path
    )
    load_time = time.time() - start
    print(f"✅ Detector loaded in {load_time:.2f}s\n")
    
    # Print model summary
    print("📋 Model Architecture:")
    print(detector.get_model_summary())
    print()
    
    # Process video
    print("🎬 Processing video frames...")
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        print(f"❌ Could not open video: {video_path}")
        return
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(f"   Total frames: {total_frames}")
    print(f"   FPS: {fps}")
    print(f"   Analyzing first 20 frames...\n")
    
    frame_count = 0
    start_time = time.time()
    
    while cap.isOpened() and frame_count < 20:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Add frame to detector
        ready = detector.add_frame(frame)
        frame_count += 1
        print(f"   Frame {frame_count}/20 added to buffer", end='\r')
        
        if ready:
            # Buffer is full, run inference
            print(f"\n\n✅ Buffer full (20 frames collected)")
            print("🧠 Running temporal analysis...\n")
            
            inference_start = time.time()
            result = detector.detect(ready_for_inference=True)
            inference_time = time.time() - inference_start
            
            # Display results
            print("╔══════════════════════════════════════════════════════════╗")
            print("║                   DETECTION RESULTS                       ║")
            print("╚══════════════════════════════════════════════════════════╝\n")
            
            print(f"🎯 Violence Detected: {'YES ⚠️' if result.violence_detected else 'NO ✅'}")
            print(f"📊 Probability: {result.violence_probability:.2%}")
            print(f"🔒 Confidence: {result.confidence:.2%}")
            print(f"📝 Details: {result.details}")
            print(f"⏱️  Inference Time: {inference_time*1000:.0f}ms")
            print(f"⏱️  Total Time: {(time.time() - start_time)*1000:.0f}ms")
            print()
            
            # Interpretation
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("INTERPRETATION:")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            if result.violence_probability > 0.7:
                print("🔴 HIGH RISK: Strong violence pattern detected")
                print("   → Immediate alert recommended")
            elif result.violence_probability > 0.5:
                print("🟡 MEDIUM RISK: Possible violence detected")
                print("   → Send to VLM for validation")
            elif result.violence_probability > 0.3:
                print("🟠 LOW RISK: Weak violence indicators")
                print("   → Monitor situation")
            else:
                print("🟢 NO RISK: Normal activity detected")
                print("   → No action needed")
            
            print()
            
            # Note about model accuracy
            if Path(model_path).name == "temporal_test.h5":
                print("⚠️  NOTE: This model was trained on only 37 videos (25% accuracy)")
                print("   For reliable predictions, train on full dataset (200+ videos)")
                print()
            
            break
    
    cap.release()
    
    if frame_count < 20:
        print(f"\n⚠️  Video too short: only {frame_count} frames")
        print("   Temporal detector needs 20 frames minimum")
    
    print("\n✅ Test complete!")


def test_hybrid_with_temporal():
    """
    Test full hybrid system with temporal detector integrated
    This simulates how the hybrid router would use temporal detection
    """
    print("\n" + "="*60)
    print("FULL HYBRID SYSTEM TEST (with Temporal RNN)")
    print("="*60 + "\n")
    
    print("📋 Detection Pipeline:")
    print("   1. Fast-path detectors (HOG, distress, supervision, body language)")
    print("   2. YOLOv8 Pose detector")
    print("   3. Temporal RNN (20-frame sequence)")
    print("   4. VLM validation (if medium confidence)")
    print()
    
    print("⚠️  INTEGRATION STATUS:")
    print("   ✅ Phase 1: Fast-path detectors - INTEGRATED")
    print("   ✅ Phase 2: YOLOv8 Pose - INTEGRATED")
    print("   ⏳ Phase 3: Temporal RNN - READY (not yet integrated)")
    print()
    
    print("🔧 To integrate temporal RNN into hybrid router:")
    print("   1. Edit: services/nura-vlm/src/hybrid_router.py")
    print("   2. Add temporal detector initialization")
    print("   3. Buffer frames per camera")
    print("   4. Run temporal analysis when buffer is full")
    print("   5. Use temporal result for routing decision")
    print()
    
    print("📄 See: INTEGRATION_GUIDE.md for step-by-step instructions")
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Temporal RNN Integration")
    parser.add_argument("--video", help="Path to video file (optional)")
    parser.add_argument("--model", default="models/temporal_test.h5", help="Path to trained model")
    parser.add_argument("--full-test", action="store_true", help="Show full hybrid integration test")
    
    args = parser.parse_args()
    
    if args.full_test:
        test_hybrid_with_temporal()
    elif args.video:
        test_temporal_on_video(args.video, args.model)
    else:
        # Default: test on a sample video from dataset
        print("No video specified. Testing on sample violent video...\n")
        
        sample_video = "tests/data/Videos/FightingA_Part1/Fighting001_x264A.mp4"
        if Path(sample_video).exists():
            test_temporal_on_video(sample_video, args.model)
        else:
            print(f"❌ Sample video not found: {sample_video}")
            print("\nUsage:")
            print(f"  python3 {sys.argv[0]} --video <path-to-video>")
            print(f"  python3 {sys.argv[0]} --full-test")
