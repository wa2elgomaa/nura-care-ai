# 🎬 NURA AI Demo

Single script to test any image or video through the AI pipeline.

## Quick Start

```bash
# Test crying detection
./demo.sh crying

# Test happy child
./demo.sh smiling

# Test video
./demo.sh video

# Test your own file
./demo.sh path/to/your/image.jpg
```

## What It Does

Simulates camera feed analysis:
1. Loads image/video
2. Sends to AI pipeline
3. Analyzes with 4 detectors (violence, distress, body language, supervision)
4. Shows results with colored output
5. Saves annotated frame to `demo_output.jpg`

## Prerequisites

```bash
# Start VLM service first
./runner/run_vlm_service.sh
```

## Examples

```bash
# Test crying image
./demo.sh "tests/data/ToddlerActions/train/Toddler crying/image.jpg"

# Test classroom video
./demo.sh tests/videos/classroom_1.mp4

# Quick shortcuts
./demo.sh crying    # Auto-picks crying image
./demo.sh smiling   # Auto-picks smiling image
./demo.sh video     # Uses classroom_1.mp4
```

## Output

```
🤖 AI Analysis Results
Detector       Score  Detected
Violence       0.023  ✅ NO
Distress       0.840  🔴 YES   ← Alert!
Body Language  0.012  ✅ NO
Supervision    0.420  ✅ NO

⚠️ Alert Generated
Type: distress
Confidence: 84%

✓ Annotated output: demo_output.jpg
```

## Documentation

See `docs/` folder for detailed guides:
- Training results
- Session summary
- Full documentation

## Tools Location

- `demo.sh` - This demo script
- `tools/` - Advanced testing tools
- `runner/` - Service management
- `training/` - Model training
