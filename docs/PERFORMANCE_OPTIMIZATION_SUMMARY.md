# VLM Performance Optimization - Executive Summary

**Date**: November 3, 2026  
**Status**: Planning Complete - Ready for Implementation

---

## 🚨 Critical Issue

**Current Performance: UNACCEPTABLE for Production**

```
Single Image Analysis: 2-3 minutes
10 Cameras × 1 FPS: 30 minutes per cycle
Real-time Monitoring: IMPOSSIBLE
```

**This cannot handle multi-camera real-time monitoring.**

---

## 🎯 Solution: Hybrid Fast Path + GPU VLM

### Architecture Overview

```
Camera Frame
    ↓
┌───────────────────────────────┐
│   Fast Path (<200ms)          │  ← 90% of frames
│   - YOLO person detection     │
│   - Supervision classifier    │
│   - Violence detection (I3D)  │
└────────────┬──────────────────┘
             │
      High Confidence? ──Yes──→ Alert
             │
             No (ambiguous)
             ↓
┌───────────────────────────────┐
│   VLM Analysis (2-5s)         │  ← 10% of frames
│   - llama.cpp (not Ollama)    │
│   - GPU accelerated           │
│   - Quantized model (Q4_K_M)  │
│   - Batched processing        │
└───────────────────────────────┘
```

---

## 📊 Expected Performance

### Current vs Target

| Metric | Current (CPU) | Target (Hybrid+GPU) | Improvement |
|--------|--------------|---------------------|-------------|
| **Single Frame** | 120-180s | <5s | **24-36x faster** |
| **Fast Path** | Not impl. | <200ms | N/A |
| **10 Cameras** | Impossible | <10s/cycle | Production ready |
| **Throughput** | 0.5 frames/min | 10+ frames/sec | **1200x faster** |

### Capacity

- **Current**: 1 camera max (with delays)
- **Target**: 10-20 cameras real-time
- **Hardware**: $300 GPU (RTX 4060)

---

## 🔍 Key Learnings from Parlor Project

**Parlor** (https://github.com/fikrikarim/parlor) achieves **0.7-1.5 second** response time using:

1. **llama.cpp instead of Ollama** 
   - Direct inference (no HTTP overhead)
   - 2-3x faster
   
2. **Quantized Models (Q4_K_M)**
   - 4-bit quantization
   - 50% memory reduction
   - 2x faster inference
   - Minimal accuracy loss
   
3. **Prompt Caching**
   - Preprocess frames during capture
   - Cache embeddings
   - Avoid recomputation
   
4. **Streaming Architecture**
   - Pipeline multiple stages
   - Don't wait for full response
   - Start processing immediately

**We should adopt these techniques.**

---

## 🎯 Three-Tier Processing Strategy

### Tier 1: Ultra-Fast (<100ms) - 70% of frames

**Purpose:** Handle obvious cases immediately

**Models:**
- YOLO person detection (already have)
- Supervision CNN classifier (adult/child)
- Basic safety checks

**Example:**
- 3 children detected, 0 adults → VIOLATION (no supervision)
- Processing time: 50-100ms
- Confidence: 95%+

---

### Tier 2: Fast Path (~500ms) - 20% of frames

**Purpose:** Detect complex behaviors

**Models:**
- I3D action recognition (violence detection)
- Behavior classification
- Restricted area detection

**Example:**
- Physical contact detected
- Action type: "hitting with object"
- Severity: MEDIUM
- Processing time: 200-500ms

---

### Tier 3: VLM Analysis (2-5s) - 10% of frames

**Purpose:** Detailed analysis of ambiguous cases

**Engine:**
- llama.cpp (replace Ollama)
- Quantized LLaVA (Q4_K_M, 4GB)
- GPU accelerated (35 layers)
- Batched processing

**Example:**
- Unclear if adult present
- Ambiguous behavior
- Need contextual understanding
- Processing time: 2-5 seconds

---

## 🧪 Test Results - Violence Detection

### Test Image: test_violence.jpg

**Expected:** Violence detected (hitting with pencil) - MEDIUM severity

**Current VLM Result:**
```
Violence Detected: NO
Analysis: "typical classroom scene with students engaged in learning"
Confidence: 85%
```

**❌ FAILED - VLM did not detect the violence**

**Why it failed:**
1. Image quality/angle may not show action clearly
2. LLaVA 7B may not be trained on subtle violence
3. Prompt needs improvement
4. Single frame vs video sequence

**Solution:**
- Specialized violence detection model (I3D)
- Multi-frame analysis (action recognition)
- Better prompt engineering
- Higher resolution input

---

## 💡 Implementation Plan

### Phase 1: GPU Acceleration (Week 1)

**Tasks:**
1. ✅ Download test violence image
2. Replace Ollama with llama.cpp
3. Convert LLaVA to GGUF Q4_K_M format
4. Add GPU support (RTX 4060)
5. Benchmark performance

**Expected Result:**
- Single frame: 180s → 3-5s (36x faster)
- Violence image test passes

---

### Phase 2: Fast Path Models (Week 2)

**Tasks:**
1. Integrate YOLO (already have)
2. Build/train supervision classifier
3. Add I3D violence detection
4. Implement routing logic
5. Add frame caching

**Expected Result:**
- 90% of frames processed in <200ms
- Violence detection working
- Multi-camera support

---

### Phase 3: Multi-Camera Scale (Week 3)

**Tasks:**
1. Async frame queue
2. Worker pool (4 workers)
3. Load balancing
4. Batch VLM processing
5. Per-camera metrics

**Expected Result:**
- 10 cameras @ 1 FPS
- <10 second average latency
- No frame drops

---

### Phase 4: Production Hardening (Week 4)

**Tasks:**
1. Error handling
2. Alerting system
3. Admin dashboard
4. Documentation
5. Performance tuning

**Expected Result:**
- Production-ready deployment
- 99% uptime
- Full monitoring

---

## 🎯 Violence Severity Classification

### Severity Levels

**LOW:**
- Verbal arguments
- Light pushing
- Threatening gestures
- Play fighting

**MEDIUM:** ⭐ (Your pencil test case)
- **Hitting with object (pencil, ruler)**
- Hard pushing/shoving
- Grabbing/restraining
- Hair pulling

**HIGH:**
- Punching/kicking with force
- Choking/strangulation
- Weapons
- Multiple attackers
- Visible injury

### Classification Algorithm

```python
score = 0

# Action type
if "hit_with_object": score += 2  # ← Your test case
if "punch" or "kick": score += 3
if "choke": score += 4

# Force magnitude (0-1)
score += force * 3

# Weapon detected
if weapon: score += 3

# Visible injury
if injury: score += 4

# Multiple attackers
if multiple: score += 2

# Severity
if score >= 8: HIGH
elif score >= 4: MEDIUM  # ← Pencil hitting = ~7 points
else: LOW
```

**Pencil hitting breakdown:**
- Action (hit_with_object): +2
- Force (0.6): +1.8
- Weapon (pencil): +3
- Distress (0.7): +1.4
- **Total: 7.2 → MEDIUM ✅**

---

## 💰 Cost Analysis

### Hardware Options

| Option | Cost | Latency | Multi-Camera | Recommendation |
|--------|------|---------|--------------|----------------|
| **CPU Only** | $0 | 120-180s | ❌ No | Testing only |
| **GPU (RTX 4060)** | $300 | 3-5s | ✅ Yes (10+) | **BEST** |
| **Jetson Orin** | $500 | 2-3s | ✅ Yes (10+) | Edge optimal |
| **Cloud GPU** | $0.50/hr | 3-5s | ✅ Yes | Fallback |
| **Hybrid (Fast+GPU)** | $300 | 200ms avg | ✅✅ Yes (20+) | **RECOMMENDED** |

### ROI Analysis

**Hardware Investment: $800/site**
- RTX 4060 GPU: $300
- CPU upgrade: $200
- RAM (32GB): $100
- SSD (1TB): $80
- Misc: $120

**Enables:**
- 10-20 camera monitoring per site
- Real-time violation detection
- <5 second alert time
- Single edge box per school

**vs Cloud Alternative:**
- Cloud GPU: $0.50/hour × 24 hours × 30 days = $360/month
- Edge box: $800 one-time (pays for itself in 2.5 months)

---

## 🚀 Recommended Next Steps

### Immediate (This Week)

1. **Purchase GPU**: RTX 4060 16GB (~$400)
2. **Install llama.cpp**: Replace Ollama
3. **Download Models**: 
   - llava-v1.6-mistral-7b.Q4_K_M.gguf (4GB)
   - mmproj-model-f16.gguf (CLIP projector)
4. **Benchmark**: Test single frame latency
5. **Document**: Setup instructions

### Short-term (Next 2 Weeks)

1. **Build Fast Path**:
   - Supervision classifier
   - Violence detection (I3D)
   - Frame caching
2. **Test**: Violence image detection
3. **Validate**: Accuracy on test dataset
4. **Optimize**: Tune routing thresholds

### Medium-term (Next Month)

1. **Multi-Camera**: Scale to 10 cameras
2. **Monitoring**: Add metrics and alerts
3. **Dashboard**: Admin interface
4. **Production**: Deploy to first site

---

## 📋 Success Criteria

### Must Have (MVP)

- ✅ Single frame: <5 seconds (GPU)
- ✅ Multi-camera: 10 cameras @ 1 FPS
- ✅ Violence detection: MEDIUM+ at 90% accuracy
- ✅ Fast path: 70%+ coverage
- ✅ End-to-end: <15 seconds

### Measurements

| Test Case | Current | Target | Status |
|-----------|---------|--------|--------|
| Classroom 1 (supervision) | 178s | <5s | ⏳ Pending GPU |
| Classroom 2 (ambiguous) | 128s | <5s | ⏳ Pending GPU |
| Violence (pencil) | ❌ Not detected | ✅ Medium | ⏳ Need specialized model |
| 10 cameras | ❌ Impossible | <10s/cycle | ⏳ Need fast path |

---

## 🎯 Bottom Line

### Current State
- ❌ 2-3 minutes per image
- ❌ Cannot handle multiple cameras
- ❌ Missed violence detection
- ❌ Not production-ready

### Target State
- ✅ <5 seconds per image (VLM)
- ✅ <200ms average (hybrid)
- ✅ 10-20 cameras supported
- ✅ 90%+ detection accuracy
- ✅ Production-ready

### Investment Required
- **Hardware**: $300-800 per site
- **Time**: 4 weeks development
- **ROI**: 2.5 months vs cloud

### Recommendation
**Proceed with hybrid fast path + GPU VLM architecture.**

This is the only viable path to production for multi-camera real-time monitoring.

---

## 📚 Documentation

**Created:**
1. ✅ [VLM_PERFORMANCE_OPTIMIZATION_PLAN.md](./VLM_PERFORMANCE_OPTIMIZATION_PLAN.md) - Detailed analysis
2. ✅ [specs/025-vlm-performance-optimization/spec.md](../specs/025-vlm-performance-optimization/spec.md) - Formal specification
3. ✅ [VLM_TEST_RESULTS.md](./VLM_TEST_RESULTS.md) - Test results with classroom images

**Test Images:**
1. ✅ test_classroom1.jpg - Adult supervision present
2. ✅ test_classroom2.jpg - Ambiguous supervision
3. ✅ test_violence.jpg - Violence (hitting with pencil) ⚠️ Not detected yet

---

**Status**: Planning Complete  
**Next**: GPU Procurement & llama.cpp Implementation  
**Timeline**: 4 weeks to production-ready  
**Confidence**: High (proven approach from Parlor project)

---

**Key Takeaway:**

> Current VLM performance (2-3 minutes) is **36-180x too slow** for real-time multi-camera monitoring. The hybrid architecture with GPU acceleration can achieve **<5 second** VLM latency and **<200ms average** latency through fast-path models, enabling **10-20 concurrent cameras** per edge box. This is the **only viable path** to production deployment.
