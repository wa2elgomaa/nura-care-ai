# Quick Testing Commands Reference

## 🧪 Test Current Hybrid System (Phase 1 + 2)

### Test on Images
```bash
# Test fast-path + YOLO pose + VLM
python3 tools/testing/quick_hybrid_test.py tests/images/test_violence.jpg
python3 tools/testing/quick_hybrid_test.py tests/images/test_classroom2.jpg
```

**Expected Results:**
- `test_violence.jpg`: 116ms, 100% confidence, fast_path
- `test_classroom2.jpg`: 15s, 72% confidence, hybrid (VLM validation)

---

## 🎬 Test Temporal RNN (Phase 3)

### Test on Video
```bash
# Test temporal detector on sample violent video
python3 tools/testing/test_temporal_integration.py \
  --video tests/data/Videos/FightingA_Part1/Fighting001_x264A.mp4 \
  --model models/temporal_test.h5

# Test on any video
python3 tools/testing/test_temporal_integration.py \
  --video <path-to-video> \
  --model models/temporal_test.h5
```

**Expected Results:**
- Violence probability: 45-55% (unreliable with small training set)
- Inference time: ~200ms
- Note: Model needs full training for accurate results

### Show Integration Status
```bash
# See what's integrated and what's pending
python3 tools/testing/test_temporal_integration.py --full-test
```

---

## 🎓 Train Better Model

### Quick Test (3 minutes)
```bash
python3 tools/training/train_temporal_detector.py \
  --violent tests/data/Videos/FightingA_Part1 \
  --normal tests/data/Videos/Normal_Videos_for_Event_Recognition/Normal_Videos_for_Event_Recognition \
  --epochs 5 \
  --max-videos 20 \
  --output models/temporal_test.h5
```

### Full Training (1-3 hours)
```bash
# Collect all fighting videos first
mkdir -p tests/data/Videos/all_fighting
find tests/data/Videos/FightingA_* -name "*.mp4" -exec cp {} tests/data/Videos/all_fighting/ \;

# Train on full dataset
python3 tools/training/train_temporal_detector.py \
  --violent tests/data/Videos/all_fighting \
  --normal tests/data/Videos/Normal_Videos_for_Event_Recognition/Normal_Videos_for_Event_Recognition \
  --epochs 15 \
  --max-videos 200 \
  --batch-size 16 \
  --output models/temporal_full.h5
```

---

## 🔄 Switch to Qwen2.5-VL (Recommended Upgrade)

### Step 1: Pull Model
```bash
# Choose model size
ollama pull qwen3-vl:8b-instruct   # Fast, good (recommended)
# ollama pull qwen2.5-vl:14b  # Balanced
# ollama pull qwen2.5-vl:32b  # Powerful, slow
```

### Step 2: Update Configuration
```bash
# Edit this file
nano services/nura-vlm/src/main.py

# Change line 38 from:
vlm_model: str = "llava:13b"

# To:
vlm_model: str = "qwen3-vl:8b-instruct"
```

### Step 3: Rebuild & Restart
```bash
docker compose -f compose.yaml -f compose.mac.yaml build nura-vlm
docker compose -f compose.yaml -f compose.mac.yaml up -d nura-vlm
```

### Step 4: Test
```bash
python3 tools/testing/quick_hybrid_test.py tests/images/test_violence.jpg
```

---

## 🔍 Check System Status

### Check Services
```bash
# Check if services are running
docker ps | grep -E "vlm|ollama"

# Check VLM service health
curl http://localhost:8001/health

# Check what VLM model is loaded
docker logs nura-nura-vlm-1 | grep "VLM Model"

# Check available Ollama models
curl http://localhost:11434/api/tags | jq '.models[].name'
```

### Check Models
```bash
# Check YOLO pose model
ls -lh yolov8n-pose.pt

# Check temporal RNN models
ls -lh models/temporal*.h5

# Check model summary
python3 << 'EOF'
import sys
sys.path.insert(0, 'packages/nura-detectors/src')
from nura_detectors.temporal_detector import TemporalViolenceDetector
detector = TemporalViolenceDetector(model_path="models/temporal_test.h5")
print(detector.get_model_summary())
EOF
```

---

## 🐛 Troubleshooting

### Services Not Running
```bash
# Restart all services
docker compose -f compose.yaml -f compose.mac.yaml restart

# View VLM logs
docker logs nura-nura-vlm-1 --tail 50

# View Ollama logs (native Mac)
ps aux | grep ollama
```

### Missing Dependencies
```bash
# Install all Python dependencies
pip3 install opencv-python tensorflow scikit-learn tqdm requests Pillow

# Verify installation
python3 -c "import cv2, tensorflow as tf; print('OK')"
```

### Model Not Found
```bash
# Check if model exists
ls -lh models/temporal_test.h5

# If not, train it
python3 tools/training/train_temporal_detector.py \
  --violent tests/data/Videos/FightingA_Part1 \
  --normal tests/data/Videos/Normal_Videos_for_Event_Recognition/Normal_Videos_for_Event_Recognition \
  --epochs 5 --max-videos 20 \
  --output models/temporal_test.h5
```

---

## 📊 Compare Performance

### Measure Speed
```bash
# Fast-path only (Phase 1)
time python3 tools/testing/quick_hybrid_test.py tests/images/test_violence.jpg

# With temporal (Phase 3) - once integrated
time python3 tools/testing/test_temporal_integration.py \
  --video tests/data/Videos/FightingA_Part1/Fighting001_x264A.mp4
```

### Expected Timings
- Fast-path heuristics: ~95ms
- YOLO pose: ~100ms
- Temporal RNN: ~200ms (20 frames)
- VLM (LLaVA 13B): ~15s
- VLM (Qwen2.5-VL 7B): ~8-12s

---

## 🎯 Common Test Scenarios

### Scenario 1: Quick Validation
```bash
# Test on known violation image
python3 tools/testing/quick_hybrid_test.py tests/images/test_violence.jpg
# Expected: Fast detection, 100% confidence
```

### Scenario 2: Ambiguous Case
```bash
# Test on subtle psychological bullying
python3 tools/testing/quick_hybrid_test.py tests/images/test_classroom2.jpg
# Expected: VLM validation, 72% confidence, 15s processing
```

### Scenario 3: Video Sequence
```bash
# Test temporal analysis
python3 tools/testing/test_temporal_integration.py \
  --video tests/data/Videos/FightingA_Part1/Fighting001_x264A.mp4
# Expected: Temporal pattern detected, ~200ms
```

### Scenario 4: Performance Benchmark
```bash
# Run full comparison
python3 tools/testing/test_hybrid_system.py
# Compares VLM-only vs Hybrid on all test images
```

---

## 📁 Quick File Reference

### Code
- `services/nura-vlm/src/main.py` - VLM service, model configuration
- `services/nura-vlm/src/hybrid_router.py` - Routing logic
- `packages/nura-detectors/src/nura_detectors/*.py` - All detectors

### Models
- `yolov8n-pose.pt` - YOLO pose model (6.2 MB)
- `models/temporal_test.h5` - Temporal RNN test model (1.2 MB, 25% acc)
- `models/temporal_full.h5` - Temporal RNN full model (to be trained, 78% acc)

### Test Scripts
- `tools/testing/quick_hybrid_test.py` - Main test script
- `tools/testing/test_temporal_integration.py` - Temporal RNN test
- `tools/testing/test_hybrid_system.py` - Full comparison
- `tools/training/train_temporal_detector.py` - Train temporal model

### Documentation
- `QUICK_START.md` - Getting started guide
- `MODEL_ARCHITECTURE.md` - Model overview, Qwen2.5-VL upgrade
- `TRAINING_SUMMARY.md` - Phase 3 training results
- `PHASE2_ML_DETECTORS.md` - YOLO pose implementation
- `TESTING_COMMANDS.md` - This file

---

## 💡 Pro Tips

1. **Start with quick test:** `quick_hybrid_test.py` tests current production system
2. **Train full model:** Small test model (25% acc) is unreliable - train on 200+ videos
3. **Switch to Qwen2.5-VL:** Better performance, faster, native video support
4. **Monitor logs:** `docker logs nura-nura-vlm-1 -f` to see real-time processing
5. **Test incrementally:** Test each phase separately before full integration

---

## 🚀 Next Steps

1. ✅ Test current system: `quick_hybrid_test.py`
2. ⏳ Switch to Qwen2.5-VL: Follow upgrade steps above
3. ⏳ Train full temporal model: 200+ videos, 1-3 hours
4. ⏳ Integrate temporal into hybrid: Edit `hybrid_router.py`
5. ⏳ Create video test suite: Label 50+ videos for validation
