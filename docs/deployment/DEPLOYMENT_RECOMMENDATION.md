# Deployment Recommendation for NURA System

**Date:** 2026-11-06  
**Target Environment:** On-premise server or Edge device with GPU  
**Camera Count:** 10+ cameras

---

## Your Deployment Scenario

Based on your requirements:
1. ✅ On-premise server or edge device
2. ✅ GPU potentially available
3. ✅ 10+ cameras

**This is an ideal scenario for GPU-accelerated deployment!**

---

## Recommended Configuration

### Primary Recommendation: MViT V2 with GPU

```bash
# .env Configuration
TEMPORAL_MODEL_TYPE=mvit
TEMPORAL_DEVICE=cuda
TEMPORAL_MODEL_PATH="/path/to/models/mvit_violence.pth"
ENABLE_TEMPORAL_DETECTION=true
VLM_MODEL=qwen3-vl:8b-instruct
```

**Why this is perfect for your case:**

1. **GPU Available** → MViT runs at **~15ms** (vs 298ms on CPU)
2. **10+ cameras** → GPU can handle 20-30 cameras easily
3. **Best accuracy** → 97.50% (vs 95.83% for ResNet50+GRU)
4. **Real-time capable** → 15ms = 66 fps per camera
5. **On-premise** → No cloud costs, data stays local

---

## Performance Projections

### With NVIDIA GPU (Recommended Setup)

**Hardware Options:**

#### Option A: Entry-Level GPU (~$300-500)
```
GPU: NVIDIA RTX 3060 (12GB VRAM)
CPU: 6-8 cores
RAM: 16-32GB

Performance:
├─ MViT inference: ~15ms per frame
├─ Cameras supported: 15-20 at 30fps
├─ Or: 30-40 cameras at 15fps
└─ Total cost: ~$1,500 (including server)
```

#### Option B: Mid-Range GPU (~$800-1200)
```
GPU: NVIDIA RTX 4070 or A4000 (16GB VRAM)
CPU: 8-12 cores
RAM: 32-64GB

Performance:
├─ MViT inference: ~10-12ms per frame
├─ Cameras supported: 20-30 at 30fps
├─ Or: 50+ cameras at 15fps
└─ Total cost: ~$2,500-3,500
```

#### Option C: Edge Device (~$400-600)
```
Device: NVIDIA Jetson AGX Xavier
GPU: 512-core Volta + Tensor Cores
RAM: 32GB

Performance:
├─ MViT inference: ~20-30ms per frame
├─ Cameras supported: 10-15 at 30fps
├─ Compact, low power (~30W)
└─ Total cost: ~$600 (device only)
```

---

## Scaling for 10+ Cameras

### Scenario: 15 Cameras

**With MViT on GPU:**
```
Per-camera processing:
├─ Frame sampling: Every 2 seconds
├─ MViT detection: ~15ms
├─ VLM validation: ~8s (only for suspicious frames)

GPU utilization:
├─ 15 cameras × 0.5 fps = 7.5 frames/sec
├─ 7.5 frames × 15ms = 112.5ms per second
├─ GPU idle 88.7% of the time
└─ Can handle 40+ cameras at this sampling rate!

Real-time mode (30fps):
├─ 15 cameras × 30 fps = 450 frames/sec
├─ 450 frames × 15ms = 6.75 seconds
├─ Impossible... unless parallel processing
└─ Solution: Process cameras in batches
```

**Optimized for 15 cameras:**
```python
# Smart sampling strategy
cameras = 15
fps_per_camera = 2  # Sample every 0.5s
total_fps = 30  # 15 cameras × 2 fps

# GPU can process: 1000ms / 15ms = 66 fps
# You need: 30 fps
# Utilization: 45%
# ✅ Plenty of headroom!
```

---

## Recommended Architecture

### System Design for 10+ Cameras

```
On-Premise Server with GPU:
├─ NVIDIA GPU (RTX 3060 or better)
├─ Docker containers for services
├─ Local NATS message broker
└─ Local storage for recordings

Camera Setup:
├─ 10-15 RTSP cameras
├─ Frigate NVR for stream management
├─ Frame sampling: 1-2 fps per camera
└─ GPU inference: MViT detector

Processing Pipeline:
├─ Frigate → Frame extraction
├─ MViT GPU → Fast violence detection (~15ms)
├─ High confidence → Immediate alert
├─ Medium confidence → VLM validation (~8s)
└─ Alerts → Staff dashboard

Optional Cloud Backup:
├─ Central monitoring across multiple sites
├─ Historical analysis
└─ Model updates
```

---

## Configuration Steps

### Step 1: Install NVIDIA Drivers & CUDA

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install nvidia-driver-535
sudo apt-get install nvidia-cuda-toolkit

# Verify installation
nvidia-smi
nvcc --version
```

### Step 2: Install PyTorch with CUDA

```bash
# For CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Verify GPU available
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

### Step 3: Configure .env for GPU

```bash
# Edit .env file
cat >> .env << 'EOF'

# ============================================================================
# GPU Configuration for 10+ Camera Deployment
# ============================================================================

# Use MViT with GPU for best performance
TEMPORAL_MODEL_TYPE=mvit
TEMPORAL_DEVICE=cuda
TEMPORAL_MODEL_PATH="/app/models/mvit_violence.pth"
ENABLE_TEMPORAL_DETECTION=true

# VLM for validation (runs on GPU too)
VLM_MODEL=qwen3-vl:8b-instruct
OLLAMA_GPU_LAYERS=99  # Use all GPU layers

# Camera configuration
MAX_CAMERAS=15
FRAME_SAMPLING_RATE=2  # fps per camera

EOF
```

### Step 4: Test GPU Performance

```bash
# Benchmark MViT on GPU
cd /path/to/nura-care-source
python3 tools/testing/benchmark_speed.py --iterations 50

# Expected output:
# MViT V2 with CUDA:
#   Avg Time: ~15-20ms
#   Min Time: ~12-15ms
#   ✓ Meets <200ms target
```

---

## Fallback Configuration (No GPU)

If GPU is not available or fails:

```bash
# .env Configuration (CPU fallback)
TEMPORAL_MODEL_TYPE=resnet50_gru
TEMPORAL_DEVICE=cpu
TEMPORAL_MODEL_PATH="/app/models/temporal_violence.keras"
ENABLE_TEMPORAL_DETECTION=true
```

**Performance with CPU only:**
```
ResNet50+GRU CPU:
├─ Inference: ~200-300ms per frame
├─ Cameras supported: 3-5 at 1 fps sampling
├─ Not ideal for 10+ cameras
└─ Consider: Lighter sampling or multiple servers
```

**For 10+ cameras without GPU:**
- Option 1: Multiple servers (2-3 servers, 4-5 cameras each)
- Option 2: Very light sampling (every 10-15 seconds)
- Option 3: Hybrid (edge pre-screening + cloud GPU)

---

## Cost Analysis

### GPU Server (One-time cost)

| Component | Cost | Notes |
|-----------|------|-------|
| Server/Workstation | $800-1200 | Decent CPU, motherboard, PSU |
| NVIDIA RTX 3060 | $300-400 | 12GB VRAM, sufficient |
| RAM (32GB) | $100-150 | For 10+ cameras |
| Storage (2TB SSD) | $150-200 | Video recordings |
| **Total** | **~$1,500** | For 15-20 cameras |

**Alternative: Cloud GPU**
- AWS g4dn.xlarge: $0.35/hour = $252/month
- Not recommended for on-premise requirement

**Alternative: NVIDIA Jetson**
- Jetson AGX Xavier: $600 (compact, low power)
- Can handle 10-15 cameras

---

## Deployment Checklist

### Pre-Deployment

- [ ] Purchase/setup server with NVIDIA GPU
- [ ] Install Ubuntu Server 22.04 LTS
- [ ] Install NVIDIA drivers (nvidia-smi working)
- [ ] Install Docker & Docker Compose
- [ ] Install CUDA toolkit
- [ ] Verify GPU accessible in Docker

### Model Setup

- [ ] Copy MViT model to server: `models/mvit_violence.pth`
- [ ] Test model loading
- [ ] Benchmark inference speed (~15ms target)
- [ ] Verify accuracy on test videos

### System Configuration

- [ ] Configure `.env` with GPU settings
- [ ] Setup camera RTSP streams
- [ ] Configure Frigate NVR
- [ ] Test end-to-end pipeline
- [ ] Monitor GPU usage (nvidia-smi)

### Production Launch

- [ ] Start all services
- [ ] Verify all 10+ cameras connected
- [ ] Check detection working
- [ ] Setup alerting/notifications
- [ ] Monitor for 24 hours
- [ ] Document any issues

---

## Monitoring & Optimization

### GPU Monitoring

```bash
# Watch GPU usage in real-time
watch -n 1 nvidia-smi

# Expected usage for 10 cameras:
# GPU Utilization: 30-50%
# Memory Used: 2-4GB (out of 12GB)
# Temperature: 50-65°C
```

### Performance Tuning

If GPU underutilized:
```bash
# Increase sampling rate
FRAME_SAMPLING_RATE=5  # More frames per camera

# Or add more cameras
MAX_CAMERAS=20  # GPU can handle it
```

If GPU overloaded:
```bash
# Reduce sampling rate
FRAME_SAMPLING_RATE=1  # Less frequent sampling

# Or process in batches
BATCH_SIZE=4  # Process 4 cameras at once
```

---

## Summary & Final Recommendation

**For your deployment (on-premise, GPU available, 10+ cameras):**

### ✅ Use This Configuration:

```bash
TEMPORAL_MODEL_TYPE=mvit          # Best accuracy (97.50%)
TEMPORAL_DEVICE=cuda             # Use GPU
ENABLE_TEMPORAL_DETECTION=true    # Enable temporal analysis
VLM_MODEL=qwen3-vl:8b-instruct   # Fast VLM validation
```

### ✅ Hardware Recommendation:

**Best Value:** Server with NVIDIA RTX 3060 (12GB)
- Cost: ~$1,500 total
- Can handle: 15-20 cameras comfortably
- Scalable: Upgrade GPU later if needed

**Compact Alternative:** NVIDIA Jetson AGX Xavier
- Cost: ~$600
- Can handle: 10-15 cameras
- Low power, fanless option

### ✅ Expected Performance:

```
System Capacity:
├─ Cameras: 15-20 simultaneous
├─ Detection speed: ~15ms per frame
├─ Sampling: 2 fps per camera
├─ Alert latency: <1s (fast-path) or <10s (with VLM)
└─ Accuracy: 97.50% (violence detection)
```

### ✅ Next Steps:

1. **Finalize hardware procurement** (GPU server or Jetson)
2. **Complete Phase 3** with MViT model ready
3. **Move to Phase 4**: Person tracking (works great with GPU!)
4. **Deploy pilot** with 3-5 cameras first
5. **Scale to 10+** cameras after validation

**This setup will give you the best performance and accuracy for your requirements!**

---

**Questions?**
- GPU selection advice?
- Server vs Jetson decision?
- Scaling beyond 15 cameras?
- Cost optimization?

Let me know and I can provide more specific guidance!
