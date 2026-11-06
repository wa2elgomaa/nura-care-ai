# Model Alternatives Analysis - Updated

**Date:** 2026-11-06  
**Source:** SlowFast Model Comparison Table

---

## Models Ranked for Our Use Case

Based on the SlowFast comparison table, here's the ranking for **real-time childcare monitoring on CPU**:

### 🥇 1. TSM (Temporal Shift Module) - **BEST FIT**

**Why it's perfect for us:**
- ✅ **Hardware-friendly** (designed for edge devices)
- ✅ **Real-time streaming** (exactly what we need!)
- ✅ **2D CNN with temporal shift** (much lighter than 3D convolutions)
- ✅ **Edge device optimized** (works great on CPU)

**Architecture:**
```
TSM = 2D CNN + Temporal Shift
- Uses regular 2D convolutions (fast!)
- Shifts channels temporally (no extra compute)
- Achieves temporal modeling without 3D convs
```

**Expected Performance (estimated):**
- Speed: **50-80ms CPU** (3-5x faster than MViT!)
- Accuracy: ~90-95% (good for violence detection)
- Size: ~10-20MB
- **Should easily meet <200ms target!**

**Papers show:**
- TSM ResNet50: 74.7% on Kinetics (similar to SlowFast)
- Real-time on mobile devices (~30fps on phone GPU)
- Very CPU-friendly architecture

---

### 🥈 2. X3D-S - **SECOND BEST**

**Why it's good:**
- ✅ Highly optimized efficiency
- ✅ Low-latency environments
- ✅ Lightweight CNN (1.96 GFLOPs)

**Expected Performance:**
- Speed: ~100-120ms CPU
- Accuracy: ~93-95%
- Size: ~15MB

**Use case:** Constrained environments (us!)

---

### 🥉 3. I3D - **GOOD FOR SMALL DATASETS**

**Why it's interesting:**
- ✅ Better on small datasets (we have 240 videos)
- ✅ Good transfer learning
- ✅ 3D Inflated convolutions

**Expected Performance:**
- Speed: ~200-300ms CPU
- Accuracy: ~95-97%
- Size: ~100MB

**Trade-off:** Slower but might train better on our limited data

---

### ❌ Not Suitable for Us

**VideoMAE** - Transformer (ViT)
- ❌ SOTA accuracy but heavy
- ❌ Large datasets needed
- ❌ Cloud workloads only

**TimeSformer** - Transformer (ViT)
- ❌ Factorized attention (complex)
- ❌ High-accuracy but slow
- ❌ GPU required

**SlowOnly** - CNN (Single Stream)
- ⚠️ Drop-in for SlowFast pipelines
- ⚠️ Lower cost but moderate speed

**MViT** - We already tested
- ❌ 298ms CPU (too slow)
- ✅ 97.50% accuracy (good)

---

## Updated Recommendation

### **NEW PLAN: Test TSM first, then X3D**

**Phase 3C (Revised Again):**

1. ✅ MViT tested: 97.50% @ 298ms (too slow)
2. 🎯 **Test TSM ResNet50**: Expected ~50-80ms (fastest!)
3. 🎯 **Test X3D-S** (if TSM not available): Expected ~100-120ms
4. 🎯 **Test I3D** (if others fail): Expected ~200ms

**Priority Order:**
```
1st: TSM (best for real-time edge)
2nd: X3D-S (optimized efficiency)
3rd: I3D (good for small data)
Fallback: ResNet50+GRU (current, proven)
```

---

## TSM Implementation Options

### Option 1: Use from Official TSM Repo
```bash
# Clone TSM repository
git clone https://github.com/mit-han-lab/temporal-shift-module
cd temporal-shift-module

# Download pre-trained weights
# TSM ResNet50 on Kinetics
```

**Pros:**
- Official implementation
- Pre-trained weights
- Well-tested

**Cons:**
- Another framework dependency
- Setup complexity

### Option 2: Use PyTorchVideo (Meta's Library)
```bash
# PyTorchVideo has TSM built-in!
pip install pytorchvideo

# Load TSM model
from pytorchvideo.models import create_tsm
model = create_tsm(model_name='tsm_resnet50')
```

**Pros:**
- Clean API
- Same team as SlowFast
- Easy integration

**Cons:**
- Need to check if weights available

### Option 3: Lightweight TSM from Scratch
```python
# Implement TSM module (very simple!)
class TemporalShift(nn.Module):
    def __init__(self, n_div=8):
        super().__init__()
        self.n_div = n_div
    
    def forward(self, x):
        # Shift channels temporally
        # Very lightweight operation!
        ...
```

**Pros:**
- Full control
- Minimal dependencies
- Easy to deploy

**Cons:**
- Need to port weights

---

## Quick Speed Comparison (Estimated)

| Model | CPU Speed | GPU Speed | Accuracy | Best For |
|-------|-----------|-----------|----------|----------|
| **TSM ResNet50** | **50-80ms** | 5-10ms | ~90-95% | **Real-time edge** ✅ |
| **X3D-S** | 100-120ms | 8-12ms | ~93-95% | Low-latency |
| **I3D** | 200-300ms | 15-20ms | ~95-97% | Small datasets |
| **ResNet50+GRU** | 150ms | ~10ms | 95.83% | Current baseline |
| **MViT V2** | 298ms | 15-20ms | 97.50% | High accuracy |

**Winner for CPU real-time: TSM ResNet50!**

---

## Action Plan

### Immediate Next Steps:

**Option A: Quick TSM Test** (Highly Recommended!)
```bash
# 1. Install pytorchvideo
pip install pytorchvideo fvcore

# 2. Load TSM ResNet50
# 3. Benchmark speed (expect 50-80ms!)
# 4. If confirmed → fine-tune on violence data
```

**Timeline:** 2-4 hours
**Expected:** 50-80ms (meets <200ms easily!)
**Risk:** Very low

**Option B: Test Both TSM + X3D**
```bash
# 1. Test TSM speed
# 2. Test X3D speed
# 3. Compare both
# 4. Pick faster one
```

**Timeline:** 4-6 hours
**Expected:** Find best option
**Risk:** Low

**Option C: Skip to Phase 4**
```bash
# Use ResNet50+GRU (150ms, proven)
# Move to person tracking
```

**Timeline:** Immediate
**Risk:** None (conservative)

---

## Why TSM is Exciting

**From the paper (MIT Han Lab):**
1. "Zero-cost temporal modeling" - temporal shift is nearly free!
2. "Real-time on mobile" - runs at 30fps on phones
3. "Plug-and-play" - works with any 2D CNN
4. "State-of-the-art efficiency" - best speed/accuracy trade-off

**Architecture advantage:**
```
3D Convolution (I3D, X3D):
- 3x3x3 kernel = 27 multiplications
- Slow on CPU

2D Convolution + Temporal Shift (TSM):
- 3x3 kernel = 9 multiplications
- Temporal shift = channel reordering (free!)
- 3x faster!
```

**This could be the solution we've been looking for!**

---

## Recommendation

### Test TSM ResNet50 NOW (before Phase 4)

**Why:**
1. 🎯 Designed for **exactly** our use case (edge, real-time)
2. ⚡ Expected 50-80ms (3-5x faster than MViT)
3. 📊 Similar accuracy to other models (~90-95%)
4. 💾 Small model size (~20MB)
5. ⏱️ Only 2-4 hours to test

**If successful:**
- ✅ Beats all other options (speed + accuracy)
- ✅ Meets <200ms target easily
- ✅ Real-time capable (~12-20fps on CPU)
- ✅ Can deploy without GPU

**If it fails:**
- Fallback to ResNet50+GRU (no loss)
- Or try X3D-S as backup

**Expected outcome:** 90% chance TSM works and solves our speed problem!

---

## Summary

**Discovery from comparison table:**
- TSM is **purpose-built** for our exact scenario
- "Hardware-friendly" + "Real-time streaming" = perfect match
- Much faster than transformers (2D CNN vs 3D attention)

**New priority:**
```
1. Test TSM ResNet50 (HIGHEST PRIORITY)
2. If TSM works → Deploy it! (Phase 3 COMPLETE)
3. If TSM fails → Test X3D-S
4. If all fail → ResNet50+GRU (current baseline)
```

**Time investment:** 2-4 hours
**Potential reward:** 3-5x speed improvement
**Risk:** Zero (we keep current model if it fails)

**Let's test TSM!** 🚀
