# macOS Deployment Guide (Apple Silicon)

**Date:** 2026-11-06  
**Hardware:** Apple M4 Max (ARM64)  
**OS:** macOS 27.0.1

---

## 🚨 IMPORTANT: No CUDA on macOS!

### Key Differences from Linux/Windows:

1. ❌ **No NVIDIA GPU** - Apple Silicon uses Metal, not CUDA
2. ❌ **No `TEMPORAL_DEVICE=cuda`** - This won't work on Mac
3. ✅ **Apple Silicon is FAST** - Neural Engine + unified memory
4. ✅ **Can use MPS (Metal Performance Shaders)** - PyTorch supports it
5. ⚠️ **Docker has limitations** - No GPU passthrough on Mac

---

## Current Development Environment

**You are developing on:**
- Hardware: Apple M4 Max (ARM64)
- OS: macOS 27.0.1
- Docker: Docker Desktop for Mac

**Deployment target will be:**
- On-premise server with NVIDIA GPU (Linux)
- OR Edge device (Jetson/similar)

**This is a cross-platform scenario!**

---

## macOS Limitations for GPU Acceleration

### Docker on Mac

❌ **Docker on macOS cannot access GPU** (neither Metal nor CUDA)
- Docker Desktop runs in a VM
- No GPU passthrough to containers
- All models run on CPU only in containers

### Native Python on Mac

✅ **Can use Apple's Metal Performance Shaders (MPS)**
- PyTorch supports MPS on Apple Silicon
- Much faster than CPU
- Not as fast as NVIDIA GPU, but decent

---

## Recommended Development Setup (macOS)

### Option 1: Native Python (Recommended for Mac Development)

**Best for:** Active development on Mac

```bash
# Run natively on Mac (not in Docker)
cd services/nura-vlm
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install detector package
cd ../../packages/nura-detectors
pip install -e .

# Run with CPU (or MPS if PyTorch supports it)
cd ../../services/nura-vlm
python3 src/main.py
```

**.env configuration for macOS:**
```bash
# Use CPU for now (most compatible)
TEMPORAL_MODEL_TYPE=resnet50_gru
TEMPORAL_DEVICE=cpu

# MPS (Metal) - experimental, only if PyTorch supports
# TEMPORAL_DEVICE=mps  # Uncomment to try Metal acceleration
```

---

### Option 2: Docker (Mac-specific compose)

**Best for:** Testing containerized deployment on Mac

```bash
# Use Mac-specific compose file
docker compose -f compose.mac.yaml up -d nura-vlm

# Note: Will run on CPU only (no GPU in Docker on Mac)
```

**.env configuration for Docker on Mac:**
```bash
# Docker on Mac = CPU only
TEMPORAL_MODEL_TYPE=resnet50_gru
TEMPORAL_DEVICE=cpu  # No cuda/mps in Docker on Mac
```

---

## Performance Expectations on Mac

### Apple M4 Max Performance (Estimated)

**Running natively (Python):**

| Model | CPU (M4 Max) | MPS (Metal) | Notes |
|-------|--------------|-------------|-------|
| **ResNet50+GRU** | ~80-120ms | ~50-80ms (est) | ✅ Recommended |
| **MViT V2** | ~200-250ms | ~100-150ms (est) | ⚠️ Slower than dev |
| **TSM** | ~40-60ms (est) | ~30-40ms (est) | ⚡ If available |

**Running in Docker:**

| Model | Docker (CPU) | Notes |
|-------|--------------|-------|
| **ResNet50+GRU** | ~150-200ms | ✅ Acceptable |
| **MViT V2** | ~300-400ms | ❌ Too slow |

**Key insight:** M4 Max CPU is **fast**, comparable to good server CPUs!

---

## Cross-Platform Development Strategy

### Your Scenario:

```
Development: macOS (M4 Max) → No CUDA
    ↓
Deployment: Linux Server with NVIDIA GPU → CUDA available
```

### Recommended Workflow:

#### 1. Development on Mac (Native Python)

```bash
# .env for development on Mac
TEMPORAL_MODEL_TYPE=resnet50_gru
TEMPORAL_DEVICE=cpu  # Works on Mac and Linux

# Run locally for fast iteration
cd services/nura-vlm
source .venv/bin/activate
python3 src/main.py
```

**Why:**
- ✅ Fast iteration (no Docker rebuild)
- ✅ Works on Mac M4 Max
- ✅ Same code will work on Linux
- ✅ Easy debugging

#### 2. Test in Docker (Mac) Before Deployment

```bash
# Build Mac-compatible image
docker compose -f compose.mac.yaml build nura-vlm

# Test containerized
docker compose -f compose.mac.yaml up nura-vlm

# Verify it works (will be CPU-only)
curl http://localhost:8001/health
```

**Why:**
- ✅ Tests containerization
- ✅ Catches Docker-specific issues
- ⚠️ Won't test GPU (Mac limitation)

#### 3. Deploy to Linux with GPU

```bash
# On Linux server with NVIDIA GPU
git pull

# Use GPU-specific compose
docker compose -f compose.gpu.yaml up -d

# .env on Linux server
TEMPORAL_MODEL_TYPE=mvit
TEMPORAL_DEVICE=cuda
```

**Why:**
- ✅ Production environment has GPU
- ✅ MViT runs at ~15ms (fast!)
- ✅ Can handle 10+ cameras

---

## .env Configuration Strategy

### Single .env for Both Environments

**Use CPU-compatible defaults that work everywhere:**

```bash
# .env (works on Mac AND Linux)
TEMPORAL_MODEL_TYPE=resnet50_gru
TEMPORAL_DEVICE=cpu
ENABLE_TEMPORAL_DETECTION=true
```

**Then override on deployment server:**

```bash
# .env.production (Linux server with GPU)
TEMPORAL_MODEL_TYPE=mvit
TEMPORAL_DEVICE=cuda
ENABLE_TEMPORAL_DETECTION=true
```

### OR: Environment-Specific .env Files

```bash
# .env.mac (for development)
TEMPORAL_MODEL_TYPE=resnet50_gru
TEMPORAL_DEVICE=cpu

# .env.linux (for deployment)
TEMPORAL_MODEL_TYPE=mvit
TEMPORAL_DEVICE=cuda
```

---

## Testing GPU Code on Mac

### Problem: Can't test CUDA on Mac

**You can't test:**
- ❌ `TEMPORAL_DEVICE=cuda`
- ❌ MViT on GPU
- ❌ GPU performance
- ❌ CUDA errors

**You CAN test:**
- ✅ Model switching logic
- ✅ Factory pattern
- ✅ Configuration loading
- ✅ Fallback to CPU
- ✅ ResNet50+GRU performance

### Testing Strategy:

```bash
# On Mac: Test CPU models
TEMPORAL_MODEL_TYPE=resnet50_gru python3 src/main.py

# On Mac: Test model switching
TEMPORAL_MODEL_TYPE=mvit TEMPORAL_DEVICE=cpu python3 src/main.py

# On Linux: Test GPU after deployment
TEMPORAL_MODEL_TYPE=mvit TEMPORAL_DEVICE=cuda python3 src/main.py
```

---

## MPS (Metal) Support - Experimental

### Can we use Apple's Metal GPU?

**PyTorch supports MPS on Apple Silicon:**

```python
import torch
if torch.backends.mps.is_available():
    device = torch.device("mps")
    print("Metal GPU available!")
else:
    device = torch.device("cpu")
```

**To enable in .env:**

```bash
# Try Metal (if PyTorch supports it)
TEMPORAL_DEVICE=mps  # Instead of cpu
```

**Expected performance:**
- MViT on MPS: ~100-150ms (2x faster than CPU)
- ResNet50+GRU on MPS: ~50-80ms (2x faster than CPU)

**Caveats:**
- ⚠️ Not all PyTorch ops support MPS
- ⚠️ May have compatibility issues
- ⚠️ Not available in Docker (VM limitation)
- ✅ Only for native Python on Mac

### How to Test MPS:

```bash
# Install PyTorch with MPS support
pip install torch torchvision

# Test MPS availability
python3 -c "import torch; print('MPS available:', torch.backends.mps.is_available())"

# Try running with MPS
TEMPORAL_DEVICE=mps python3 tools/testing/benchmark_speed.py
```

---

## Recommended Setup for Your Case

### Current: Development on Mac M4 Max

```bash
# Run natively (not in Docker) for development
cd services/nura-vlm
source .venv/bin/activate

# .env configuration
TEMPORAL_MODEL_TYPE=resnet50_gru
TEMPORAL_DEVICE=cpu  # or mps if available

# Run
python3 src/main.py
```

**Performance:**
- ResNet50+GRU: ~80-120ms on M4 Max CPU ✅
- Fast enough for development and testing

### Future: Deployment on Linux + NVIDIA GPU

```bash
# On production server
docker compose -f compose.gpu.yaml up -d

# .env.production
TEMPORAL_MODEL_TYPE=mvit
TEMPORAL_DEVICE=cuda

# Performance: ~15ms ✅ Real-time capable
```

---

## Docker Compose Files

### compose.mac.yaml (For Mac Development)

Already exists! Designed for:
- ✅ ARM64 architecture (M1/M2/M3/M4)
- ✅ CPU-only inference
- ✅ Docker Desktop for Mac

### compose.gpu.yaml (For Linux Deployment)

For production server with NVIDIA GPU:
- ✅ CUDA support
- ✅ GPU acceleration
- ✅ NVIDIA Docker runtime

**Don't use compose.gpu.yaml on Mac!** It won't work (no NVIDIA GPU).

---

## Summary & Recommendations

### ✅ For Development on Mac (Now):

```bash
# 1. Run natively (not Docker) for best performance
cd services/nura-vlm
python3 src/main.py

# 2. Use CPU-compatible model
TEMPORAL_MODEL_TYPE=resnet50_gru
TEMPORAL_DEVICE=cpu  # or try mps

# 3. Test in Docker occasionally
docker compose -f compose.mac.yaml up nura-vlm
```

### ✅ For Deployment on Linux (Later):

```bash
# 1. Use Docker with GPU support
docker compose -f compose.gpu.yaml up -d

# 2. Use GPU-accelerated model
TEMPORAL_MODEL_TYPE=mvit
TEMPORAL_DEVICE=cuda

# 3. Expect ~15ms inference (fast!)
```

### ⚠️ Don't:

- ❌ Use `TEMPORAL_DEVICE=cuda` on Mac (won't work)
- ❌ Use `compose.gpu.yaml` on Mac (won't work)
- ❌ Expect GPU performance in Docker on Mac (VM limitation)
- ❌ Test CUDA code on Mac (no NVIDIA GPU)

### ✅ Do:

- ✅ Develop natively on Mac (fast iteration)
- ✅ Use `resnet50_gru` for development (works everywhere)
- ✅ Test Docker builds on Mac (validates containerization)
- ✅ Deploy with GPU on Linux server (production)
- ✅ Use model switching (supports both environments)

---

## Current Recommendation

**Keep developing natively on Mac:**

```bash
# Your current .env is perfect for Mac development
TEMPORAL_MODEL_TYPE=resnet50_gru
TEMPORAL_DEVICE=cpu
```

**When deploying to Linux server with GPU, change to:**

```bash
# .env.production
TEMPORAL_MODEL_TYPE=mvit
TEMPORAL_DEVICE=cuda
```

The model switching we built supports this perfectly! 🎉

---

## Final Answer to Your Question

**"Should I run it as a container on macOS?"**

### For Development: **No, run natively**
- Faster iteration
- Better performance (no VM overhead)
- Can potentially use Metal (MPS)
- Easier debugging

### For Testing Containerization: **Yes, occasionally**
- Use `compose.mac.yaml`
- Validates Docker setup
- Tests before deployment

### For Production (on Linux): **Yes, always**
- Use `compose.gpu.yaml`
- GPU acceleration available
- Orchestrated with other services

**Your workflow:**
1. Develop natively on Mac ✅ (current)
2. Test in Docker on Mac occasionally ✅
3. Deploy in Docker on Linux with GPU ✅ (later)
