# SlowFast Demo Feasibility Analysis

**Date:** 2026-11-06  
**Context:** Evaluating if we can achieve Facebook's SlowFast demo performance

---

## Demo Capabilities

The Facebook SlowFast demo shows:

1. ✅ **Multi-person detection** - Bounding boxes around 3+ people
2. ✅ **Action recognition** - Per-person action labels (stand, sit, carry object, talk, watch, listen, read)
3. ✅ **High confidence** - Scores 0.57-1.00 for detected actions
4. ✅ **Real-time** - Appears to run at ~30fps
5. ✅ **Temporal context** - Uses multiple frames for accuracy

---

## Technical Requirements

### 1. Person Detection + Tracking
**What they use:**
- Faster R-CNN or similar object detector
- Per-frame person detection
- Tracking across frames

**What we have:**
- YOLOv8-pose (100ms inference)
- No person tracking yet (Phase 4 planned)

**Gap:** Need person tracking (DeepSORT/ByteTrack)

### 2. Action Recognition Network
**What they use:**
- SlowFast network (dual-pathway: slow for spatial, fast for temporal)
- Pre-trained on Kinetics-400 or AVA dataset
- 32 frames input (slow: 8 frames, fast: 32 frames)

**What we have:**
- ResNet50+GRU (20 frames, 150ms, 95.83% accuracy for violence only)
- MViT V2 (16 frames, 298ms, 97.50% accuracy for violence only)

**Gap:** Need multi-action classifier, not just violence detection

### 3. Inference Performance
**What they show:**
- Real-time ~30fps = ~33ms per frame budget
- Likely GPU-accelerated (NVIDIA Tesla/RTX)

**What we have:**
- CPU-only inference
- MViT: 298ms (10x too slow)
- ResNet50+GRU: 150ms (5x too slow)

**Gap:** Need GPU acceleration OR significantly lighter model

---

## Performance Analysis

### Timing Breakdown (SlowFast Demo - Estimated):

```
Per-frame budget: 33ms (30fps)

With GPU:
├─ Person detection: ~5-10ms
├─ Action recognition: ~15-20ms
└─ Visualization: ~5ms
TOTAL: ~25-35ms ✅ Real-time achieved
```

### Our Current System (CPU-only):

```
Per-frame budget: 33ms (30fps target)

Actual timing:
├─ Person detection (YOLOv8): ~100ms
├─ Temporal violence (ResNet50+GRU): ~150ms
├─ VLM validation: ~8,000ms (when needed)
└─ Visualization: ~5ms
TOTAL: ~255ms ❌ 8fps, not real-time
```

---

## Can We Achieve SlowFast Demo Performance?

### SHORT ANSWER: **Not with current hardware (CPU-only)**

### Detailed Analysis:

| Component | SlowFast Demo | Our System | Achievable? |
|-----------|---------------|------------|-------------|
| **Multi-person detection** | ✅ Real-time | ⚠️ 100ms (YOLOv8) | ✅ YES (with GPU) |
| **Action recognition** | ✅ ~20ms GPU | ❌ 298ms CPU | ⚠️ MAYBE (with GPU) |
| **Tracking** | ✅ Implemented | ❌ Not yet | ✅ YES (Phase 4) |
| **Real-time (30fps)** | ✅ 33ms/frame | ❌ 255ms/frame | ❌ NO (CPU) / ✅ YES (GPU) |
| **Multi-action classes** | ✅ 8+ actions | ❌ Violence only | ✅ YES (retrain) |

---

## Path to SlowFast-Level Performance

### Option 1: GPU Acceleration (Recommended)
**Hardware needed:**
- NVIDIA GPU (RTX 3060 or better)
- CUDA + cuDNN
- 8GB+ VRAM

**Expected performance:**
```
With NVIDIA RTX 3060:
├─ Person detection: ~5-10ms (YOLOv8 GPU)
├─ SlowFast/MViT: ~15-25ms (GPU-accelerated)
└─ Tracking: ~2-5ms
TOTAL: ~22-40ms ✅ 25-45fps achievable
```

**Pros:**
- ✅ Matches demo performance
- ✅ Real-time 30fps
- ✅ Can run full SlowFast network

**Cons:**
- ❌ Requires GPU hardware (~$300-500)
- ❌ Deployment complexity (GPU drivers, CUDA)
- ❌ Higher power consumption

### Option 2: Lighter Models (CPU-Optimized)
**Approach:**
- Use MobileNet-based action recognition
- Reduce frame count (8-12 instead of 32)
- Lighter person detector (YOLO-nano)

**Expected performance:**
```
With optimized models:
├─ Person detection: ~30-40ms (YOLO-nano)
├─ Action recognition: ~50-80ms (MobileNetV2)
└─ Tracking: ~5-10ms
TOTAL: ~85-130ms ✅ 7-12fps
```

**Pros:**
- ✅ No hardware changes
- ✅ Cheaper deployment
- ✅ Lower power

**Cons:**
- ❌ Not true real-time (7-12fps vs 30fps)
- ❌ Lower accuracy than SlowFast
- ❌ May miss fast actions

### Option 3: Hybrid Approach (Our Current Strategy)
**What we do:**
- Fast-path detectors (150ms) for real-time screening
- VLM validation (8s) for high-confidence decisions
- Focus on critical events (violence, distress) not all actions

**Expected performance:**
```
Hybrid system:
├─ Fast screening: ~300-500ms (every frame)
├─ VLM validation: ~8s (only when suspicious)
└─ Result: Alerts within 8-10s of event
```

**Pros:**
- ✅ Works on CPU
- ✅ High accuracy (95%+)
- ✅ Already implemented
- ✅ Childcare-specific focus

**Cons:**
- ❌ Not real-time action labeling
- ❌ Delayed alerts (8-10s)
- ❌ No multi-action visualization like demo

---

## Recommendations

### For Production (Now):
**Keep current hybrid approach** (ResNet50+GRU + VLM)
- Reason: Works on CPU, high accuracy, proven
- Trade-off: 8-10s alert delay vs real-time
- Good for: Childcare monitoring where 8s is acceptable

### For Future (Phase 5+):
**Add GPU support** for real-time performance
- Implement: GPU-accelerated inference path
- Models: SlowFast or optimized MViT on GPU
- Result: Match demo performance (~30fps)

### For Phase 4 (Next):
**Implement person tracking** (DeepSORT/ByteTrack)
- Closes gap: Multi-person tracking like demo
- Enables: Per-person action history
- Foundation: Needed for real-time system later

---

## SlowFast Network Specifics

### Architecture:
```
SlowFast Network:
├─ Slow pathway (spatial): 8 frames @ 2fps → ResNet-50
├─ Fast pathway (temporal): 32 frames @ 16fps → Lightweight ResNet
└─ Fusion: Lateral connections → Action classifier

Input: 32 frames (2 seconds @ 16fps)
Output: Action probabilities (80 classes for AVA)
```

### Performance (from papers):
- GPU (V100): ~15-20ms per clip
- CPU: ~500-800ms per clip (too slow)
- Accuracy: 79.8% mAP on AVA v2.2

### Our comparison:
| Network | Frames | CPU Speed | GPU Speed | Accuracy |
|---------|--------|-----------|-----------|----------|
| **SlowFast** | 32 | 500-800ms | 15-20ms | 79.8% |
| **MViT V2** | 16 | 298ms | ~10-15ms (est) | 97.5% (violence) |
| **ResNet50+GRU** | 20 | 150ms | ~5-10ms (est) | 95.8% (violence) |

---

## Action Items

### If we want SlowFast demo performance:

**Phase 4 (Immediate):**
1. ✅ Implement person tracking (DeepSORT/ByteTrack)
2. ✅ Add per-person tracking IDs
3. ✅ Track action history per person

**Phase 5 (Short-term):**
1. ⚠️ GPU acceleration (optional but recommended)
2. ⚠️ Retrain for multi-action (not just violence)
3. ⚠️ Real-time visualization

**Phase 6 (Long-term):**
1. ⚠️ Full SlowFast network implementation
2. ⚠️ AVA dataset training
3. ⚠️ Match demo capabilities

---

## Conclusion

**Can we achieve SlowFast demo performance?**

✅ **YES - with GPU hardware**
- Need: NVIDIA GPU (RTX 3060+)
- Result: 25-45fps real-time
- Cost: ~$300-500 hardware

❌ **NO - with CPU-only (current setup)**
- Best: 7-12fps with optimized models
- Current: ~4fps with MViT, ~6fps with ResNet50+GRU
- Limitation: CPU too slow for real-time video transformers

⚠️ **PARTIAL - with hybrid approach (current)**
- Fast screening: 300-500ms
- Accurate detection: 95%+
- Alert delay: 8-10s
- Good enough for: Childcare monitoring

**Recommendation:**
- **Now:** Continue with CPU-optimized hybrid approach (Phase 3 complete)
- **Phase 4:** Add person tracking (closes gap with demo)
- **Phase 5:** Evaluate GPU deployment (enables real-time like demo)
- **Phase 6:** Full SlowFast if GPU available

The demo is impressive, but requires GPU. Our hybrid approach achieves similar **accuracy** without the **speed**.
