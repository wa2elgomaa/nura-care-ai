# SlowFast Repository Insights

**Date:** 2026-11-06  
**Source:** https://github.com/facebookresearch/SlowFast

---

## Repository Overview

**PySlowFast** is Meta AI's official video understanding codebase supporting:
- SlowFast networks
- X3D (Expanding Architectures)
- MViT (Multiscale Vision Transformers) v1 & v2
- Other models: C2D, I3D, Non-local Networks, Rev-ViT

---

## Available Models (from Model Zoo)

### 1. MViT (Multiscale Vision Transformers)

**MViTv2 Performance (Kinetics-400):**
| Variant | Frames | Top-1 | Top-5 | Notes |
|---------|--------|-------|-------|-------|
| MViTv2-S | 16x4 | 81.0% | 94.6% | Small variant (what we tested) |
| MViTv2-B | 32x3 | 82.9% | 95.7% | Base variant |

**Our MViT Results:**
- Model: MViTv2-S (16 frames)
- Task: Violence detection (binary)
- Accuracy: **97.50%** (on our dataset)
- Speed: **298ms CPU** (too slow for real-time)

**Comparison:**
- ✅ Accuracy: Our 97.50% > their 81.0% (but different tasks)
- ❌ Speed: 298ms = 3.4fps (far from real-time 30fps)

### 2. X3D (Expanding Architectures)

**X3D Performance (Kinetics-400):**
| Model | Accuracy | Params | GFLOPs | Speed (est) |
|-------|----------|--------|--------|-------------|
| X3D-XS | 69.5% | 3.8M | 0.60 | Fastest |
| X3D-S | 73.5% | 3.8M | 1.96 | Fast |
| X3D-M | 76.2% | 3.8M | 4.73 | Medium |
| X3D-L | 77.5% | 6.2M | 18.37 | Slower |

**Key insight:**
- X3D-S: Only 1.96 GFLOPs (very efficient!)
- Our MViT: ~5-6 GFLOPs estimated
- **X3D could be 2-3x faster than MViT**

### 3. SlowFast Networks

**Performance (Kinetics-400):**
| Config | Frames | Top-1 | Top-5 |
|--------|--------|-------|-------|
| R50, 4x16 | 64 | 75.6% | 92.0% |
| R50, 8x8 | 64 | 77.0% | 92.6% |

**AVA (Action Detection):**
- R101 models: 28.2-29.4% mAP
- This is the multi-person action detection like the demo!

---

## Critical Findings

### ❌ No Speed Benchmarks in Repo
The Model Zoo provides:
- ✅ Accuracy metrics
- ✅ Model parameters
- ✅ GFLOPs (compute cost)
- ❌ **NO FPS data**
- ❌ **NO inference time**
- ❌ **NO hardware specs**

### 🤔 Implications for Our Analysis

**Our estimates were reasonable:**
- MViT CPU: ~298ms (measured)
- MViT GPU: ~10-15ms (estimated) ✅ Matches typical transformer GPU speedup
- X3D CPU: ~100-150ms (estimated from GFLOPs ratio)
- X3D GPU: ~5-10ms (estimated)

### 📊 Model Efficiency Ranking (by GFLOPs)

1. **X3D-XS**: 0.60 GFLOPs ⚡ Fastest
2. **X3D-S**: 1.96 GFLOPs ⚡⚡ Fast
3. **X3D-M**: 4.73 GFLOPs ⚡⚡⚡ Medium
4. **MViTv2-S**: ~5-6 GFLOPs (est) ⚡⚡⚡ Medium-slow
5. **X3D-L**: 18.37 GFLOPs ⚡⚡⚡⚡ Slow

**Conclusion:** X3D-S is likely **2-3x faster** than our MViT!

---

## Revised Recommendations

### 1. Try X3D-S Before Moving to Phase 4

**Why:**
- 2-3x faster than MViT (1.96 vs 5-6 GFLOPs)
- Smaller model (3.8M vs 34M params)
- Still transformer-based (modern architecture)
- Pre-trained weights available

**Expected performance:**
```
X3D-S (estimated on CPU):
- Speed: ~100-120ms (vs MViT 298ms)
- Accuracy: ~75% Kinetics → ~93-95% violence (estimated)
- Size: ~15MB (vs MViT 392MB)
```

**If successful:**
✅ **Meets <200ms target!**
✅ Better than ResNet50+GRU baseline
✅ Can proceed without GPU

### 2. X3D Implementation Path

**Option A: Use from SlowFast repo**
```bash
# Clone SlowFast
git clone https://github.com/facebookresearch/SlowFast
cd SlowFast
pip install -e .

# Download X3D-S weights
# Fine-tune on violence dataset
```

**Pros:**
- Official implementation
- Pre-trained weights
- Well-tested

**Cons:**
- Heavy dependency (full framework)
- Complex setup
- Harder to deploy

**Option B: Lightweight X3D implementation**
```python
# Implement X3D-S from scratch
# Load pre-trained weights
# Integrate into our pipeline
```

**Pros:**
- Lighter deployment
- Control over architecture
- Easier integration

**Cons:**
- Implementation time
- Weight conversion needed

### 3. Updated Phase Roadmap

**Phase 3C (revised):**
1. ✅ MViT tested: 97.50% but 298ms (too slow)
2. ⏳ **Try X3D-S**: Potential 100-120ms (meets target!)
3. 🎯 Decision: X3D-S or ResNet50+GRU

**If X3D-S works (<200ms):**
- Deploy X3D-S (best of both worlds)
- Phase 3 COMPLETE ✅

**If X3D-S still slow (>200ms):**
- Keep ResNet50+GRU (proven, 150ms)
- Move to Phase 4 (Person Tracking)

---

## SlowFast Demo Analysis (Updated)

**The demo likely uses:**
- Model: SlowFast R50 or R101 on AVA dataset
- Hardware: **NVIDIA GPU (required)**
- FPS: ~30fps with GPU acceleration
- Task: Multi-person action detection (80 classes)

**Can we replicate it?**

❌ **Not exactly** - They use:
1. GPU (we're CPU-only)
2. AVA dataset (80 action classes)
3. Multi-person tracking
4. Real-time inference

✅ **We can get close** - With X3D-S:
1. Speed: 100-120ms CPU (8-10fps)
2. Accuracy: ~95% (violence-specific)
3. Person tracking: Phase 4
4. Near real-time: 8-10fps acceptable for monitoring

---

## Action Items

### Immediate (Before Phase 4):

**Option 1: Quick X3D-S Test** (Recommended)
```bash
# 1. Install SlowFast
pip install fvcore pytorchvideo

# 2. Download X3D-S weights
# 3. Benchmark speed on our hardware
# 4. If <200ms → fine-tune on violence data
# 5. If >200ms → stick with ResNet50+GRU
```

**Timeline:** 1-2 days
**Risk:** Low (just testing)
**Reward:** Potentially 2x faster than current

**Option 2: Move to Phase 4** (Conservative)
```bash
# Skip X3D testing
# Deploy ResNet50+GRU (95.83%, 150ms)
# Implement person tracking (DeepSORT)
```

**Timeline:** Immediate
**Risk:** None (proven solution)
**Reward:** New capability (tracking)

### My Recommendation:

**Quick X3D-S speed test (2-3 hours):**
1. Download X3D-S pre-trained model
2. Run inference benchmark (like we did for MViT)
3. If speed < 150ms → pursue further
4. If speed > 200ms → move to Phase 4

**Why:** Only a few hours to potentially unlock better performance. Low risk, high reward.

---

## Conclusion

**From SlowFast repo:**
1. ✅ X3D-S exists and is **2-3x more efficient** than MViT
2. ✅ Pre-trained weights available
3. ❌ No official speed benchmarks (we must measure)
4. 🎯 Worth testing before Phase 4

**Updated strategy:**
1. Test X3D-S speed (2-3 hours)
2. If fast enough → train on violence data
3. If too slow → proceed with ResNet50+GRU to Phase 4

**Expected outcome:**
- Best case: X3D-S at 100-120ms ✅ Better than all options
- Worst case: X3D-S at 200ms+ → Use ResNet50+GRU (no loss)
