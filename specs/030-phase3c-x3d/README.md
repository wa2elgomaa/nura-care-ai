# Phase 3C: X3D Architecture Integration

**Quick Reference Guide**

---

## 🎯 What is Phase 3C?

Optional upgrade to Phase 3A that replaces ResNet50+GRU with X3D architecture for potentially better accuracy and efficiency.

**Current:** ResNet50+GRU - 95.83% accuracy, 150ms inference  
**Target:** X3D-S - 96-97% accuracy, <200ms inference  
**Improvement:** +1-2% accuracy, 6x smaller model (3.8M vs 25M parameters)

---

## ⚡ Quick Decision Guide

### Should You Do Phase 3C?

**YES, if:**
- ✅ You want state-of-the-art temporal detection
- ✅ You need higher accuracy (>96%)
- ✅ You have 1-2 weeks for experimentation
- ✅ You're comfortable with PyTorch

**NO, if:**
- ❌ Current 95.83% accuracy is sufficient
- ❌ Don't want additional framework dependency
- ❌ Need to move to Phase 4 (person tracking) urgently
- ❌ CPU inference speed is critical (<150ms required)

**Recommendation:** Complete Phase 3B first, then evaluate based on distress detector results.

---

## 📋 What You'll Get

### Option 1: X3D is Better
- Switch to X3D as default
- **Benefits:** +1-2% accuracy, smaller model
- **Trade-off:** PyTorch dependency

### Option 2: Similar Performance  
- Keep both models as options
- **Benefits:** Flexibility for different scenarios
- **Trade-off:** Maintain two models

### Option 3: ResNet50+GRU is Better
- Keep current model
- **Benefits:** Validation our approach is already optimal
- **Trade-off:** None (just research time)

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install torch torchvision
git clone https://github.com/facebookresearch/SlowFast.git
cd SlowFast
pip install -r requirements.txt
python setup.py build develop
```

### 2. Download Pre-trained Model
```bash
wget https://dl.fbaipublicfiles.com/pyslowfast/x3d_models/x3d_s.pyth
```

### 3. Test Inference
```bash
python tools/testing/test_x3d_inference.py \
  --model x3d_s.pyth \
  --video tests/data/Videos/FightingA_Part11/Fighting003_x264A.mp4
```

### 4. Train on Our Data
```bash
python tools/training/train_x3d_detector.py \
  --train-csv datasets/x3d/train.csv \
  --val-csv datasets/x3d/val.csv \
  --pretrained x3d_s.pyth \
  --epochs 30 \
  --output models/x3d_violence.pyth
```

### 5. Compare with Baseline
```bash
python tools/testing/compare_temporal_models.py \
  --model1 models/temporal_violence.keras \
  --model2 models/x3d_violence.pyth \
  --test-dir datasets/videos
```

---

## 📊 X3D Model Variants

| Variant | Frames | Accuracy (Kinetics) | Params | FLOPs | Use Case |
|---------|--------|---------------------|--------|-------|----------|
| **X3D-XS** | 4 | 68.7% | 3.8M | 0.60G | Mobile/Edge |
| **X3D-S** ⭐ | 13 | 73.1% | 3.8M | 1.96G | **Recommended** |
| **X3D-M** | 16 | 75.1% | 3.8M | 4.73G | High accuracy |
| **X3D-L** | 16 | 76.9% | 6.2M | 18.37G | Maximum accuracy |

⭐ **X3D-S is recommended** for best balance of accuracy and speed.

---

## ⏱️ Timeline

**Phase 3C-1:** Setup & Research (2-3 days)  
**Phase 3C-2:** Data Preparation (2-3 days)  
**Phase 3C-3:** Training (3-5 days)  
**Phase 3C-4:** Integration (2-3 days)  
**Phase 3C-5:** Evaluation (2-3 days)  

**Total:** 10-15 days (~2 weeks)

---

## 🎯 Success Criteria

**Must Have:**
- ✅ X3D trained on our dataset
- ✅ Inference speed measured
- ✅ Accuracy compared with baseline

**Should Have:**
- ✅ Accuracy ≥ 96%
- ✅ Speed < 200ms
- ✅ Model size < 20MB

---

## 📁 Key Files

**Specification:**
- `specs/030-phase3c-x3d/spec.md` - Full specification (this is detailed)
- `specs/030-phase3c-x3d/README.md` - This quick reference

**Implementation (To Be Created):**
- `packages/nura-detectors/src/nura_detectors/x3d_detector.py`
- `tools/training/train_x3d_detector.py`
- `tools/testing/compare_temporal_models.py`
- `configs/Violence/X3D_S.yaml`

**Models:**
- `models/x3d_s.pyth` - Pre-trained (Kinetics)
- `models/x3d_violence.pyth` - Fine-tuned (our data)

---

## 🔧 Configuration

**Enable X3D in .env:**
```bash
# Temporal Detection Model Selection
USE_X3D_TEMPORAL=true              # false = ResNet50+GRU, true = X3D
X3D_MODEL_PATH=models/x3d_violence.pyth
X3D_NUM_FRAMES=13                  # 13 frames at 6fps = ~2 seconds
X3D_CONFIDENCE_THRESHOLD=0.7
```

---

## 📊 Expected Results

**Baseline (ResNet50+GRU):**
- Accuracy: 95.83%
- FP Rate: 8.3%
- FN Rate: 8.3%
- Speed: 150ms
- Size: 25MB

**Target (X3D-S):**
- Accuracy: 96-97%
- FP Rate: 5-7%
- FN Rate: 5-7%
- Speed: 150-200ms
- Size: 15MB

**Improvement:**
- +1-2% accuracy
- -2-3% false positives
- 6x smaller model
- Acceptable speed trade-off

---

## 🤔 FAQ

**Q: Do I need a GPU?**  
A: No, but it helps. X3D can run on CPU (M4 Max) in 150-200ms. GPU would be faster.

**Q: Will this replace ResNet50+GRU?**  
A: Only if X3D is measurably better (>1% accuracy improvement). Otherwise, we keep both as options.

**Q: What about the current temporal detector?**  
A: It stays! We never delete working code. X3D would be an alternative, not a replacement.

**Q: Is this required?**  
A: No, this is optional. Phase 3A is complete and working well (95.83%). This is about optimization.

**Q: When should I do this?**  
A: After Phase 3B completes. Or skip to Phase 4 (person tracking) if speed to market is more important.

**Q: What if X3D is worse?**  
A: Then we learned that our approach is already optimal. Research time well spent.

---

## 🎓 Learning Resources

**Papers:**
- [X3D Paper (CVPR 2020)](https://arxiv.org/abs/2004.04730)
- [SlowFast Paper (ICCV 2019)](https://arxiv.org/abs/1812.03982)

**Code:**
- [PySlowFast GitHub](https://github.com/facebookresearch/SlowFast)
- [Model Zoo](https://github.com/facebookresearch/SlowFast/blob/main/MODEL_ZOO.md)

**Tutorials:**
- [SlowFast Tutorial](https://github.com/facebookresearch/SlowFast/blob/main/GETTING_STARTED.md)
- [X3D README](https://github.com/facebookresearch/SlowFast/tree/main/projects/x3d)

---

## ✅ Checklist

### Before You Start
- [ ] Phase 3A complete (95.83% baseline)
- [ ] Phase 3B complete (distress detector)
- [ ] 1-2 weeks available
- [ ] Decision to proceed

### What You Need
- [ ] PyTorch installed
- [ ] SlowFast framework set up
- [ ] Pre-trained X3D model downloaded
- [ ] Dataset in X3D format

### What You'll Build
- [ ] X3D detector wrapper
- [ ] Training pipeline
- [ ] Comparison framework
- [ ] Integration into hybrid router

### What You'll Decide
- [ ] Is X3D better than ResNet50+GRU?
- [ ] Should we switch or keep both?
- [ ] Document decision and rationale

---

## 💡 Pro Tips

1. **Start with X3D-S** - Best balance, if not good enough try X3D-M
2. **Use ONNX Runtime** - Better CPU performance than raw PyTorch
3. **Quantize the model** - INT8 quantization can double inference speed
4. **Test on real videos** - Kinetics accuracy doesn't guarantee our accuracy
5. **Compare fairly** - Use same test set as Phase 3A (same 48 videos)

---

## 🚦 Decision Tree

```
┌─────────────────────────────┐
│ Phase 3A Complete (95.83%)  │
└─────────────┬───────────────┘
              │
              ▼
        Need >96% accuracy?
              │
        ┌─────┴─────┐
        │           │
       Yes         No
        │           │
        ▼           ▼
   Do Phase 3C   Skip to Phase 4
        │
        ▼
   X3D > 96%?
        │
   ┌────┴────┐
   │         │
  Yes       No
   │         │
   ▼         ▼
Switch to  Keep
  X3D    ResNet50+GRU
```

---

**Next Steps:**
1. Review this specification
2. Decide: Do Phase 3C now, later, or skip?
3. If now: Start with Phase 3C-1 (Setup)
4. If later: Bookmark this spec, proceed to Phase 4
5. If skip: Archive as research, stay with ResNet50+GRU

**Questions?** Review the full spec: `specs/030-phase3c-x3d/spec.md`
