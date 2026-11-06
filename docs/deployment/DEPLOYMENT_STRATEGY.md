# Deployment Strategy: Dev vs Production Environments

**Date:** 2026-11-06  
**Critical Issue:** Development ≠ Deployment Hardware

---

## The Problem

**Development Environment (Current):**
- MacBook Pro / Mac hardware
- Apple Silicon (M1/M2/M3) OR Intel x86
- Powerful CPU, good memory
- macOS operating system
- Can test and benchmark locally

**Deployment Environment (Unknown):**
- Could be: Raspberry Pi, edge device, server, cloud VM, embedded system
- Likely: Lower-spec CPU, limited RAM
- OS: Linux (most likely), Windows Server, or embedded OS
- **Performance will be different!**

---

## Critical Questions We Need to Answer

### 1. What is the actual deployment hardware?

**Common scenarios:**

#### Scenario A: Cloud Server (AWS/GCP/Azure)
```
Hardware: 4-8 CPU cores, 8-16GB RAM
OS: Linux (Ubuntu/Amazon Linux)
Cost: $50-200/month
Performance: Similar to dev (maybe slower)
```
**Implications:**
- ✅ Models will run at similar speeds
- ✅ Can upgrade to GPU instances if needed
- ⚠️ Need to consider cost per camera
- ⚠️ Network latency for video streams

#### Scenario B: Edge Device (Raspberry Pi, NVIDIA Jetson)
```
Hardware: ARM CPU, 2-8GB RAM, optional GPU
OS: Linux (Raspbian, JetPack)
Cost: $100-500 per device
Performance: Much slower than dev
```
**Implications:**
- ❌ CPU models will be 2-5x slower
- ⚠️ Memory constraints (models must be small)
- ✅ Local processing (low latency)
- ⚠️ Need ARM-compatible models

#### Scenario C: On-Premise Server
```
Hardware: Multi-core server CPU, 32-64GB RAM
OS: Linux/Windows Server
Cost: One-time hardware cost
Performance: Better than dev
```
**Implications:**
- ✅ Can run heavier models
- ✅ Multiple cameras simultaneously
- ✅ No cloud costs
- ⚠️ Need physical space and maintenance

#### Scenario D: Hybrid (Edge + Cloud)
```
Edge: Fast detectors locally (violence, distress)
Cloud: VLM validation remotely
```
**Implications:**
- ✅ Best of both worlds
- ⚠️ Need network connectivity
- ⚠️ More complex architecture

---

## Model Performance Across Environments

### Current Benchmarks (Development - Mac)

| Model | Dev Speed | Memory | Size |
|-------|-----------|--------|------|
| ResNet50+GRU | 150ms | ~500MB | 1.2MB |
| MViT V2 | 298ms | ~2GB | 392MB |
| YOLOv8-pose | 100ms | ~400MB | 50MB |

### Estimated Performance on Different Hardware

#### Raspberry Pi 4 (8GB RAM)
```
Hardware: ARM Cortex-A72 (4 cores @ 1.5GHz)

Expected speeds:
├─ ResNet50+GRU: ~400-600ms (3-4x slower)
├─ MViT V2: ~800-1200ms (3-4x slower)
├─ YOLOv8-pose: ~250-350ms (2-3x slower)
└─ TSM ResNet50: ~150-250ms (2-3x slower)

Verdict: ⚠️ Too slow for real-time
```

#### NVIDIA Jetson Nano (4GB RAM + GPU)
```
Hardware: ARM CPU + 128-core Maxwell GPU

Expected speeds (GPU):
├─ ResNet50+GRU: ~20-30ms ✅
├─ MViT V2: ~40-60ms ✅
├─ YOLOv8-pose: ~15-25ms ✅
└─ TSM ResNet50: ~15-20ms ✅

Verdict: ✅ Real-time capable with GPU!
```

#### Cloud VM (4 vCPUs, 8GB RAM)
```
Hardware: Intel Xeon or AMD EPYC

Expected speeds:
├─ ResNet50+GRU: ~200-300ms (1.5-2x slower)
├─ MViT V2: ~400-600ms (1.5-2x slower)
├─ YOLOv8-pose: ~150-200ms (1.5x slower)
└─ TSM ResNet50: ~100-150ms (1.5-2x slower)

Verdict: ✅ Acceptable for monitoring
```

#### Cloud VM with GPU (NVIDIA T4)
```
Hardware: Cloud GPU instance

Expected speeds:
├─ ResNet50+GRU: ~5-10ms ✅
├─ MViT V2: ~15-25ms ✅
├─ YOLOv8-pose: ~5-10ms ✅
└─ TSM ResNet50: ~8-12ms ✅

Verdict: ✅ Real-time, high cost (~$0.35/hour)
```

---

## Strategy Based on Deployment Environment

### Strategy 1: **CPU-Only Deployment** (Most Conservative)

**Best for:** Cloud VMs, on-premise servers without GPU

**Model Selection:**
```
Primary: ResNet50+GRU (150ms dev → 200-300ms prod)
Backup: TSM ResNet50 (if 50-80ms dev → 100-150ms prod)
Avoid: MViT (too slow)
```

**Architecture:**
```
Per-camera pipeline:
├─ Frame sampling: Every 2-3 seconds
├─ Fast detector: ResNet50+GRU (~200ms)
├─ VLM validation: Qwen3-VL (~8s, on suspicious only)
└─ Alert generation: <10s total
```

**Scaling:**
```
One CPU can handle:
- 3-5 cameras simultaneously
- 200ms per frame = 5 fps
- With 3s sampling = 1.5 frames/camera/sec
- Total: 15-25 frames/sec across all cameras
```

### Strategy 2: **Edge Device with GPU** (Best Performance/Cost)

**Best for:** NVIDIA Jetson Nano/Xavier, Coral TPU

**Model Selection:**
```
Primary: TSM ResNet50 or MViT (both fast on GPU)
GPU speeds: 15-25ms
```

**Architecture:**
```
Per-camera pipeline:
├─ Real-time processing: 30fps
├─ Fast detector: TSM (~15ms) = 66fps capable
├─ VLM validation: On-device or cloud
└─ Alert generation: <1s
```

**Scaling:**
```
One Jetson Nano can handle:
- 5-10 cameras at 30fps
- Or 15-20 cameras at 10fps
- Hardware cost: ~$100-200 per location
```

### Strategy 3: **Hybrid Edge + Cloud** (Recommended)

**Best for:** Distributed childcare facilities

**Model Selection:**
```
Edge (local device):
├─ Fast screening: Lightweight TSM or MobileNet (~50ms)
├─ Quick alerts: Immediate local response
└─ Low bandwidth: Only send suspicious clips to cloud

Cloud (central server):
├─ VLM validation: High-accuracy verification
├─ Central monitoring: All facilities visible
└─ Storage: Long-term video archive
```

**Architecture:**
```
Childcare Center A:
├─ Edge device (Jetson/Pi)
├─ Fast local detection
└─ Send alerts → Cloud

Cloud:
├─ Receives alerts from all centers
├─ VLM validation
├─ Dashboard for staff
└─ Historical analysis
```

**Scaling:**
```
Per location:
- Edge device: $100-200 one-time
- Handles 5-10 cameras locally
- Low cloud cost (only alerts sent)

Cloud:
- Shared across all locations
- $50-100/month total
```

---

## Model Selection Matrix

### Based on Deployment Hardware

| Hardware | Best Model | Expected Speed | Cost | Cameras/Device |
|----------|------------|----------------|------|----------------|
| **Raspberry Pi 4** | ResNet50+GRU | 400-600ms | $75 | 1-2 cameras |
| **Jetson Nano** | TSM/MViT GPU | 15-25ms | $150 | 5-10 cameras ✅ |
| **Cloud CPU VM** | ResNet50+GRU | 200-300ms | $50/mo | 3-5 cameras |
| **Cloud GPU VM** | MViT/TSM | 10-20ms | $250/mo | 20+ cameras |
| **Server (no GPU)** | ResNet50+GRU | 150-250ms | $1000+ | 5-10 cameras |

---

## Recommendations

### Before Proceeding with Model Selection:

**1. Define Deployment Hardware** (Critical!)

Ask:
- Where will the system run? (Cloud, edge, on-premise)
- How many cameras per location?
- What's the hardware budget?
- Is GPU available?
- Network connectivity quality?

**2. Define Performance Requirements**

Ask:
- Real-time (30fps) or near-real-time (1-5fps)?
- Alert latency tolerance? (1s, 5s, 10s?)
- Multiple cameras simultaneously?
- Cost constraints?

**3. Choose Development Strategy**

#### Option A: **Target-Specific Development**
```
Know deployment target → Benchmark on actual hardware
- Rent/buy target device
- Test models on real environment
- Optimize for that specific hardware
```
**Pros:**
- ✅ Accurate performance predictions
- ✅ Optimized for production
- ✅ No surprises at deployment

**Cons:**
- ⏱️ Need hardware access
- 💰 Additional cost

#### Option B: **Flexible Architecture** (Recommended)
```
Design for multiple deployment options:
- Model serving API (can swap models)
- Configuration-driven (adjust for hardware)
- Fallback options (heavy → light models)
```
**Pros:**
- ✅ Works on any hardware
- ✅ Can optimize later
- ✅ Future-proof

**Cons:**
- 🔧 More complex architecture
- ⚙️ Configuration overhead

#### Option C: **Conservative Approach**
```
Optimize for worst-case (low-spec hardware):
- Use lightest model (ResNet50+GRU)
- Test on Raspberry Pi equivalent
- Over-engineer for constraints
```
**Pros:**
- ✅ Works anywhere
- ✅ No hardware surprises
- ✅ Simple deployment

**Cons:**
- ❌ Miss performance opportunities
- ❌ May over-constrain

---

## Practical Next Steps

### Immediate Actions:

**1. Clarify Deployment Target** 
```
Questions to answer:
- Cloud or edge?
- GPU available?
- How many cameras?
- Budget per location?
- Real-time requirement?
```

**2. Worst-Case Benchmark**
```
Test on low-spec hardware:
- Rent AWS t3.medium (2 CPU, 4GB RAM) for $0.05/hour
- Or test on older laptop
- Benchmark ResNet50+GRU
- Measure actual production-like performance
```

**3. Design for Flexibility**
```
Architecture that adapts:

config.yaml:
  model: "resnet50_gru"  # Can change to "tsm" or "mvit"
  device: "cpu"          # Can change to "cuda"
  batch_size: 1          # Adjust for hardware
  frame_skip: 2          # Adjust for performance
```

---

## Current Recommendation

### Given Uncertainty About Deployment:

**Use ResNet50+GRU as baseline** because:
1. ✅ **Known performance:** 150ms dev, ~200-300ms prod
2. ✅ **Small size:** 1.2MB (easy to deploy anywhere)
3. ✅ **Proven accuracy:** 95.83%
4. ✅ **Works on any hardware:** CPU-only
5. ✅ **Low risk:** Conservative choice

**Build flexibility to upgrade** later:
```python
class TemporalDetector:
    def __init__(self, model_type="resnet50_gru"):
        if model_type == "resnet50_gru":
            self.model = load_resnet_gru()
        elif model_type == "tsm":
            self.model = load_tsm()
        elif model_type == "mvit":
            self.model = load_mvit()
```

**When deployment hardware is known:**
- Raspberry Pi → ResNet50+GRU (only option)
- Jetson/GPU → TSM or MViT (much faster)
- Cloud CPU → ResNet50+GRU (cost-effective)
- Cloud GPU → MViT (best accuracy + speed)

---

## Summary

**The deployment environment matters A LOT:**

| Environment | Best Choice | Why |
|-------------|-------------|-----|
| **Unknown** | ResNet50+GRU | Safe, works anywhere |
| **Low-spec CPU** | ResNet50+GRU | Only fast enough option |
| **Edge + GPU** | TSM or MViT | Real-time capable |
| **Cloud CPU** | ResNet50+GRU | Cost-effective |
| **Cloud GPU** | MViT | Best performance |

**Critical question to answer NOW:**
- **Where will this actually deploy?**
- **Is GPU available in production?**
- **What's the performance requirement?**

**Without knowing deployment target:**
→ Stick with **ResNet50+GRU** (95.83%, 150ms, proven)
→ Build **flexible architecture** (can swap models later)
→ **Don't optimize prematurely** until target is clear

Should we:
1. **Clarify deployment environment** first?
2. **Build flexible architecture** (model-agnostic)?
3. **Stick with ResNet50+GRU** and move to Phase 4?
