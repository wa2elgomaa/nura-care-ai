# Phase 3C: X3D Architecture - Kickoff Summary

**Started:** 2026-11-05 (Evening)  
**Status:** 🟡 Setup in progress  
**Decision:** Proceed with X3D integration

---

## 🎯 Session Summary

### Completed Today

**Phase 3A:** ✅ COMPLETE
- Temporal violence detection: 95.83% accuracy
- Model: ResNet50+GRU (20-frame sequences)
- Integrated into hybrid router

**Phase 3B:** ✅ COMPLETE (with caveats)
- Enhanced distress detector trained
- Result: 39.31% accuracy (7-class)
- Top-3 accuracy: 93.76% (excellent!)
- **Decision:** Retrain as binary or use top-3 predictions (later)

**VLM Optimization:** ✅ COMPLETE
- Switched: LLaVA 13B → Qwen3-VL 8B
- Expected speedup: 50% faster validation

**OUC-CGE Research:** ✅ COMPLETE
- Analyzed classroom engagement repository
- Extracted X3D insights
- Created comprehensive research document

**Phase 3C Specification:** ✅ COMPLETE
- Full 20-page implementation spec
- Quick reference guide
- Decision matrices and benchmarks

### Phase 3C: Starting Now

**Goal:** Evaluate X3D architecture to potentially improve from 95.83% → 96-97% accuracy

**Current Status:**
- ✅ PyTorch 2.8.0 installed
- 🟡 SlowFast framework cloning (alternative approach needed)
- 🟡 X3D-S model downloading
- 📋 Implementation plan ready

---

## 🚀 Phase 3C Quick Plan

### Simplified Approach (Without Full SlowFast)

Instead of full SlowFast framework, we'll:
1. ✅ Use PyTorch directly
2. ✅ Implement X3D architecture from scratch (lightweight)
3. ✅ Download pre-trained weights
4. ✅ Fine-tune on our violence dataset

**Why This Works:**
- Faster setup (no framework dependency issues)
- More control over implementation
- Easier integration with our TensorFlow stack (via ONNX)
- Learn X3D architecture deeply

---

## 📋 Revised Implementation Steps

### Step 1: X3D Architecture Implementation (Tomorrow)
```python
# packages/nura-detectors/src/nura_detectors/x3d_model.py
# Implement lightweight X3D-S architecture
# - Stem layer
# - 4 stages with progressive expansion
# - Classification head
```

### Step 2: Load Pre-trained Weights
```python
# Convert SlowFast pre-trained weights to our implementation
# models/x3d/x3d_s.pyth → models/x3d/x3d_s_converted.pth
```

### Step 3: Dataset Preparation  
```python
# Convert our violence dataset to X3D format
# - 13 frames per clip
# - 224x224 resolution
# - Uniform sampling
```

### Step 4: Fine-tuning
```bash
python3 tools/training/train_x3d_violence.py \
  --dataset datasets/x3d \
  --pretrained models/x3d/x3d_s_converted.pth \
  --epochs 30 \
  --output models/x3d_violence.pth
```

### Step 5: Evaluation & Comparison
```bash
python3 tools/testing/compare_models.py \
  --baseline models/temporal_violence.keras \
  --x3d models/x3d_violence.pth \
  --test-videos datasets/videos/test/
```

---

## 🎯 Success Criteria

**Go/No-Go Decision Points:**

✅ **After Step 1** (Architecture Implementation):
- Can we implement X3D-S in <500 lines?
- Does it run on CPU in <300ms?

✅ **After Step 3** (Fine-tuning):
- Training accuracy >96%?
- Validation accuracy >95%?

✅ **After Step 5** (Evaluation):
- X3D accuracy > ResNet50+GRU + 1%?
- Inference speed <200ms?

**Final Decision:**
```
IF X3D better AND speed acceptable:
    → Deploy X3D
ELIF similar performance:
    → Keep both as options
ELSE:
    → Keep ResNet50+GRU
```

---

## 💡 Alternative: Quick Benchmark First

**Before Full Implementation:**

Option A: Use pre-trained X3D via ONNX Runtime
```bash
# Convert X3D-S to ONNX
# Test inference speed on our hardware
# If fast enough, proceed with full implementation
```

Option B: Use X3D from torchvision (if available)
```python
import torchvision.models.video as models
# Check if X3D is available in torchvision
```

**Recommendation:** Try Option B first (quickest validation)

---

## 📊 Current System State

**Models Trained:**
- ✅ Temporal violence: `models/temporal_violence.keras` (95.83%)
- ✅ Distress classifier: `models/distress_classifier.keras` (39.31%, needs work)
- 🟡 X3D violence: To be trained

**VLM Service:**
- ✅ Running on Qwen3-VL 8B
- ✅ Temporal detector enabled
- ✅ VLM validation working

**Datasets Organized:**
- ✅ 450 violence videos
- ✅ 61,732 facial expression images
- ✅ Manifests ready

---

## 🕐 Estimated Timeline

**Phase 3C Simplified:**
- Tomorrow: X3D architecture implementation (4-6 hours)
- Day 2: Dataset prep + training (6-8 hours)
- Day 3: Evaluation + integration (4-6 hours)
- **Total: 3 days** (vs original 1-2 weeks)

**Why Faster:**
- Skip full SlowFast framework
- Lightweight implementation
- Focus on X3D-S only (not all variants)
- Reuse existing data pipeline

---

## 🤔 Decision Point

**Two Paths Forward:**

### Path A: X3D Now (3 days)
- Implement X3D architecture
- Train on violence dataset
- Compare with baseline
- **Pro:** Potential accuracy improvement
- **Con:** 3 days before Phase 4

### Path B: Phase 4 First (Strategic)
- Move to person tracking
- Come back to X3D later if needed
- **Pro:** New capability sooner
- **Con:** Miss potential accuracy gain

**Current Choice:** Starting Path A (X3D now) per user request

---

## 📝 Next Session Actions

1. ✅ Check if X3D model download completed
2. ✅ Implement lightweight X3D-S architecture
3. ✅ Test inference speed on sample video
4. ✅ Make go/no-go decision on full implementation

---

## 🎓 Today's Learnings

**What Worked:**
- ✅ Temporal detector (95.83%) exceeded expectations
- ✅ VLM optimization simple and effective
- ✅ Comprehensive research before implementation
- ✅ Clear specifications reduce implementation risk

**What Didn't:**
- ❌ Multi-class emotion detection (39% vs 85% target)
- ❌ Transfer learning needs more tuning
- ⚠️ 7-class problem much harder than 2-class

**Adjustments:**
- Binary distress classifier instead of 7-class
- Top-K predictions more useful than single class
- Simpler X3D integration (skip full framework)

---

## 📊 Progress Tracker

**Phase 3 Overall:**
- ✅ 3A: Temporal detection (COMPLETE - 95.83%)
- ⚠️ 3B: Distress detection (TRAINED - needs rework)
- 🟡 3C: X3D architecture (IN PROGRESS)

**Next Major Milestone:**
- Phase 4: Person tracking (DeepSORT/ByteTrack)

---

**Status:** Ready to implement X3D tomorrow morning  
**Blocked:** None  
**Risk:** X3D may not be significantly better than current 95.83%  
**Mitigation:** Quick benchmark before full implementation
