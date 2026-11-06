# Temporal Model Configuration Guide

**Date:** 2026-11-06  
**Purpose:** Guide for switching temporal detection models based on deployment environment

---

## Quick Start

### 1. Choose Your Model

Edit `.env` file and set `TEMPORAL_MODEL_TYPE`:

```bash
# For CPU-only deployment (default, recommended)
TEMPORAL_MODEL_TYPE=resnet50_gru

# For GPU deployment (high accuracy)
TEMPORAL_MODEL_TYPE=mvit
TEMPORAL_DEVICE=cuda

# For edge devices (real-time optimized)
TEMPORAL_MODEL_TYPE=tsm

# For low-latency cloud (efficient)
TEMPORAL_MODEL_TYPE=x3d
```

### 2. Restart Service

```bash
docker-compose restart nura-vlm
# or
python services/nura-vlm/src/main.py
```

That's it! The system will automatically load the correct model.

---

## Available Models

### ResNet50+GRU (Default - Recommended for most deployments)

```bash
TEMPORAL_MODEL_TYPE=resnet50_gru
TEMPORAL_MODEL_PATH="/path/to/models/temporal_violence.keras"
TEMPORAL_DEVICE=cpu
```

**Specs:**
- Framework: TensorFlow/Keras
- Accuracy: **95.83%** (tested)
- Speed: **~150ms CPU**
- Model Size: **1.2MB**
- Sequence: 20 frames

**Best for:**
- ✅ CPU-only deployments
- ✅ Cloud VMs without GPU
- ✅ On-premise servers
- ✅ Cost-conscious deployments
- ✅ Proven, production-ready

**Deployment targets:**
- Cloud CPU instances
- Docker containers
- Standard servers
- Any CPU-based environment

---

### MViT V2 (High Accuracy - Requires GPU or powerful CPU)

```bash
TEMPORAL_MODEL_TYPE=mvit
TEMPORAL_MODEL_PATH="/path/to/models/mvit_violence.pth"
TEMPORAL_DEVICE=cuda  # or cpu (slow)
```

**Specs:**
- Framework: PyTorch
- Accuracy: **97.50%** (tested)
- Speed: **~298ms CPU, ~15ms GPU**
- Model Size: **392MB**
- Sequence: 16 frames

**Best for:**
- ✅ GPU-enabled deployments
- ✅ Maximum accuracy required
- ✅ Cloud GPU instances
- ✅ Batch processing
- ✅ Offline analysis

**Deployment targets:**
- NVIDIA GPU cloud instances (AWS P3, GCP GPU)
- On-premise servers with GPU
- NVIDIA Jetson Xavier (edge + GPU)

**⚠️ Not recommended for:**
- ❌ CPU-only (too slow: 298ms)
- ❌ Edge devices without GPU
- ❌ Real-time requirements on CPU

---

### TSM ResNet50 (Edge-Optimized - For real-time edge devices)

```bash
TEMPORAL_MODEL_TYPE=tsm
TEMPORAL_MODEL_PATH="/path/to/models/tsm_violence.pth"
TEMPORAL_DEVICE=cpu  # or cuda
```

**Specs:**
- Framework: PyTorch
- Accuracy: **~90-95%** (estimated)
- Speed: **~50-80ms CPU** (estimated)
- Model Size: **~20MB**
- Sequence: 8 frames

**Best for:**
- ✅ Edge devices (Raspberry Pi, Jetson)
- ✅ Real-time requirements
- ✅ Hardware-constrained environments
- ✅ Mobile/embedded deployments
- ✅ Low-latency needs

**Deployment targets:**
- NVIDIA Jetson Nano/Xavier
- Raspberry Pi 4 (8GB)
- Edge TPU devices
- Mobile devices

**⚠️ Note:** Model not yet trained. Estimated performance based on paper.

---

### X3D-S (Efficient - For low-latency cloud)

```bash
TEMPORAL_MODEL_TYPE=x3d
TEMPORAL_MODEL_PATH="/path/to/models/x3d_violence.pth"
TEMPORAL_DEVICE=cpu  # or cuda
```

**Specs:**
- Framework: PyTorch
- Accuracy: **~93-95%** (estimated)
- Speed: **~100-120ms CPU** (estimated)
- Model Size: **~15MB**
- Sequence: 13 frames

**Best for:**
- ✅ Low-latency cloud deployments
- ✅ Constrained CPU environments
- ✅ Balance between speed and accuracy
- ✅ Moderate camera counts

**Deployment targets:**
- Cloud CPU instances (AWS t3, GCP e2)
- Docker containers
- Kubernetes pods

**⚠️ Note:** Model not yet trained. Estimated performance based on GFLOPs.

---

## Deployment Scenarios

### Scenario 1: Cloud CPU (No GPU)

**Recommended:** ResNet50+GRU

```bash
# .env configuration
TEMPORAL_MODEL_TYPE=resnet50_gru
TEMPORAL_DEVICE=cpu
ENABLE_TEMPORAL_DETECTION=true
```

**Why:**
- ✅ Fast enough (~150ms = 6-7 fps)
- ✅ Proven accuracy (95.83%)
- ✅ Small model (1.2MB)
- ✅ Cost-effective (no GPU needed)

**Scaling:**
- 1 CPU core can handle 3-5 cameras
- Sample every 2-3 seconds per camera
- VLM validation only on suspicious frames

---

### Scenario 2: Cloud GPU

**Recommended:** MViT V2

```bash
# .env configuration
TEMPORAL_MODEL_TYPE=mvit
TEMPORAL_DEVICE=cuda
ENABLE_TEMPORAL_DETECTION=true
```

**Why:**
- ✅ Best accuracy (97.50%)
- ✅ Fast on GPU (~15ms = 66 fps)
- ✅ Can handle many cameras simultaneously
- ✅ Real-time capable

**Scaling:**
- 1 GPU can handle 20-30 cameras at 30fps
- Or 50+ cameras at 10fps sampling

**Cost consideration:**
- GPU instance: ~$0.35/hour (AWS g4dn.xlarge)
- vs CPU: ~$0.05/hour (t3.large)
- Worth it for >10 cameras or high-accuracy needs

---

### Scenario 3: Edge Device with GPU (NVIDIA Jetson)

**Recommended:** TSM ResNet50 or MViT

```bash
# .env configuration - Option A: TSM (fastest)
TEMPORAL_MODEL_TYPE=tsm
TEMPORAL_DEVICE=cuda
ENABLE_TEMPORAL_DETECTION=true

# Option B: MViT (most accurate)
TEMPORAL_MODEL_TYPE=mvit
TEMPORAL_DEVICE=cuda
ENABLE_TEMPORAL_DETECTION=true
```

**Why:**
- ✅ Real-time capable with GPU
- ✅ Local processing (no cloud costs)
- ✅ Low latency
- ✅ Privacy (data stays on device)

**Scaling:**
- Jetson Nano: 5-10 cameras at 30fps
- Jetson Xavier: 15-20 cameras at 30fps

**Hardware cost:**
- Jetson Nano: ~$150
- Jetson Xavier NX: ~$400

---

### Scenario 4: Edge Device CPU-Only (Raspberry Pi)

**Recommended:** ResNet50+GRU (only option)

```bash
# .env configuration
TEMPORAL_MODEL_TYPE=resnet50_gru
TEMPORAL_DEVICE=cpu
ENABLE_TEMPORAL_DETECTION=true
```

**Why:**
- ✅ Only model fast enough for Pi
- ✅ Small memory footprint
- ⚠️ Limited to 1-2 cameras
- ⚠️ Slower inference (~400-600ms on Pi)

**Scaling:**
- Raspberry Pi 4 (8GB): 1-2 cameras max
- Sample every 5-10 seconds
- Consider hybrid: edge screening + cloud VLM

**⚠️ Not recommended for:**
- ❌ Real-time needs (too slow)
- ❌ Many cameras (not enough power)
- ❌ Consider Jetson Nano instead for $50 more

---

### Scenario 5: Hybrid (Edge Fast-Path + Cloud VLM)

**Recommended:** ResNet50+GRU (edge) + Qwen3-VL (cloud)

```bash
# Edge device .env
TEMPORAL_MODEL_TYPE=resnet50_gru
TEMPORAL_DEVICE=cpu
ENABLE_TEMPORAL_DETECTION=true
VLM_URL=https://your-cloud-vlm-api.com

# Cloud VLM service .env
VLM_MODEL=qwen3-vl:8b-instruct
```

**Architecture:**
```
Childcare Center (Edge):
├─ Camera feeds → Edge device
├─ Fast screening (ResNet50+GRU ~150ms)
├─ Local alerts (high confidence)
└─ Send suspicious clips → Cloud VLM

Cloud (Central):
├─ Receives clips from all centers
├─ VLM validation (~8s)
├─ Central dashboard
└─ Historical storage
```

**Why:**
- ✅ Low bandwidth (only suspicious clips sent)
- ✅ Fast local response
- ✅ Accurate cloud validation
- ✅ Scales to many locations
- ✅ Cost-effective

---

## Performance Comparison

### CPU Performance (Development Mac → Production estimates)

| Model | Dev (Mac) | Cloud CPU | Raspberry Pi 4 | Jetson Nano CPU |
|-------|-----------|-----------|----------------|-----------------|
| **ResNet50+GRU** | 150ms | 200-300ms | 400-600ms | 300-400ms |
| **MViT** | 298ms | 400-600ms | 800-1200ms | 600-800ms |
| **TSM** | (est) 50-80ms | (est) 100-150ms | (est) 200-300ms | (est) 150-200ms |
| **X3D-S** | (est) 100-120ms | (est) 150-250ms | (est) 300-500ms | (est) 200-300ms |

### GPU Performance (estimated)

| Model | Jetson Nano GPU | Cloud GPU (T4) | Notes |
|-------|-----------------|----------------|-------|
| **ResNet50+GRU** | ~10ms | ~5ms | Not optimized for GPU |
| **MViT** | ~20-30ms | ~15ms | ✅ Best GPU performance |
| **TSM** | ~15-20ms | ~8-12ms | ✅ Very fast |
| **X3D-S** | ~12-18ms | ~8-12ms | ✅ Efficient |

---

## Migration Guide

### From Default to MViT (Adding GPU)

**Before:**
```bash
TEMPORAL_MODEL_TYPE=resnet50_gru
TEMPORAL_DEVICE=cpu
```

**After:**
```bash
TEMPORAL_MODEL_TYPE=mvit
TEMPORAL_DEVICE=cuda
```

**Steps:**
1. Ensure NVIDIA GPU drivers installed
2. Install PyTorch with CUDA: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118`
3. Verify GPU available: `python -c "import torch; print(torch.cuda.is_available())"`
4. Update `.env` file
5. Restart service
6. Monitor GPU usage: `nvidia-smi`

### From ResNet50+GRU to TSM (Edge optimization)

**When:** Deploying to edge device, need faster inference

**Before:**
```bash
TEMPORAL_MODEL_TYPE=resnet50_gru
```

**After:**
```bash
TEMPORAL_MODEL_TYPE=tsm
```

**Steps:**
1. Train TSM model on violence dataset (or use pre-trained + fine-tune)
2. Save model to `models/tsm_violence.pth`
3. Update `.env` file
4. Test inference speed on target hardware
5. Verify accuracy acceptable
6. Deploy

---

## Troubleshooting

### Model fails to load

**Error:** `ModuleNotFoundError: No module named 'torch'`

**Solution:**
```bash
# For MViT, TSM, X3D (PyTorch models)
pip install torch torchvision

# For ResNet50+GRU (TensorFlow model)
pip install tensorflow
```

### Model loads but inference is slow

**Check:**
1. Device setting: `TEMPORAL_DEVICE=cpu` vs `cuda`
2. Model type appropriate for hardware
3. GPU drivers installed (if using CUDA)

**Quick test:**
```python
from nura_detectors.temporal_detector_factory import create_temporal_detector
import time

detector = create_temporal_detector()
# Test inference time
# (add test code based on model type)
```

### GPU not being used

**Error:** Model loads but still slow, GPU idle

**Check:**
1. `TEMPORAL_DEVICE=cuda` in `.env`
2. PyTorch sees GPU: `python -c "import torch; print(torch.cuda.is_available())"`
3. CUDA version matches PyTorch: `nvcc --version`

**Fix:**
```bash
# Reinstall PyTorch with correct CUDA version
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

---

## Best Practices

### 1. Start Conservative

```bash
# Start with proven, safe option
TEMPORAL_MODEL_TYPE=resnet50_gru
TEMPORAL_DEVICE=cpu
```

- ✅ Works everywhere
- ✅ Known performance
- ✅ Easy to debug

### 2. Benchmark on Target Hardware

```python
# Before deployment, test on actual hardware
python tools/testing/benchmark_speed.py --iterations 50
```

- ⏱️ Measure real inference time
- 📊 Verify accuracy on test set
- 💾 Check memory usage

### 3. Monitor in Production

```bash
# Log inference times
# Alert if degraded performance
# Track accuracy over time
```

### 4. Have Fallback

```python
# Hybrid router has automatic fallback
# If temporal detector fails → spatial detector
# If fast-path fails → VLM validation
```

---

## Summary

**Decision Tree:**

```
Do you have GPU?
├─ Yes → Use MViT (best accuracy, 97.50%)
│   └─ Cloud GPU or Jetson with GPU
│
└─ No (CPU-only) → What's your hardware?
    ├─ Powerful server/cloud → ResNet50+GRU (proven, 95.83%)
    ├─ Edge device → TSM (if trained) or ResNet50+GRU
    └─ Raspberry Pi → ResNet50+GRU only (slow but works)
```

**Current Status:**
- ✅ **ResNet50+GRU** - Trained, tested, production-ready
- ✅ **MViT** - Trained, tested, requires GPU
- ⏳ **TSM** - Not yet trained (pending)
- ⏳ **X3D** - Not yet trained (pending)

**Recommendation:** Use `resnet50_gru` until deployment hardware is known, then optimize if needed.
