# NURA Deployment Guide - Platform-Specific Configurations

**Date**: November 4, 2026  
**Status**: Production Ready  
**Platforms**: Mac M4 Max (Development) | Windows/Linux GPU (Deployment)

---

## Overview

NURA supports two deployment environments with platform-specific optimizations:

1. **Mac M4 Max** - Development environment with Metal GPU acceleration
2. **Windows/Linux GPU** - Production deployment with NVIDIA CUDA acceleration

Each platform has its own Docker Compose override file for optimal performance.

---

## 🍎 Mac M4 Max Development Setup

### Hardware Requirements
- **Mac M4 Max** (or M3 Max/Pro)
- **128GB RAM** (64GB minimum)
- **macOS Sonoma** or later
- **500GB+ free storage** for models and data

### Software Requirements
- **Docker Desktop** for Mac (latest)
- **Homebrew** package manager
- **Ollama** (native macOS installation)

### Installation Steps

#### 1. Install Native Ollama (Required)

```bash
# Install Ollama via Homebrew
brew install ollama

# Start Ollama service
ollama serve

# Pull VLM model (in a new terminal)
ollama pull llava:7b

# Verify installation
ollama list
```

**Why native Ollama?**
- Direct Metal GPU access (no virtualization overhead)
- Full 128GB RAM available to models
- 2-6x faster than containerized Ollama
- Automatic M4 Max optimization

#### 2. Clone and Configure

```bash
# Clone repository
cd /path/to/nura-care-source

# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Key environment variables:**
```bash
# Database
POSTGRES_PASSWORD=your_secure_password
KEYCLOAK_ADMIN_PASSWORD=your_admin_password

# VLM Configuration
VLM_MODEL=llava:7b
VLM_TEMPERATURE=0.3
VLM_MAX_TOKENS=500
VLM_TIMEOUT=180

# Site Configuration
SITE_ID=dev-site-001
LOG_LEVEL=info
```

#### 3. Start Services (Single Instance)

```bash
# Start core infrastructure + NURA services
docker compose \
  -f compose.yaml \
  -f compose.mac.yaml \
  --env-file .env \
  --profile app \
  up -d

# View logs
docker compose logs -f
```

**Services started:**
- Postgres (with pgvector)
- NATS JetStream
- MQTT (Mosquitto)
- Keycloak
- Frigate
- NURA services (API, UI, Rules, RAG, VLM, etc.)

#### 4. Start Services (Multi-Instance VLM for 10+ Cameras)

```bash
# Start with 4 parallel VLM instances + load balancer
docker compose \
  -f compose.yaml \
  -f compose.mac.yaml \
  --env-file .env \
  --profile app \
  --profile vlm-parallel \
  up -d
```

**Additional services:**
- `nura-vlm-2` on port 8002
- `nura-vlm-3` on port 8003
- `nura-vlm-4` on port 8004
- `nura-vlm-lb` (Nginx load balancer on port 8000)

**Expected performance:**
- Single instance: 30-60s per image (2-3 cameras @ 1 FPS)
- 4 parallel instances: 2-8 FPS aggregate (10-20 cameras @ 1 FPS)

#### 5. Verify Installation

```bash
# Check service health
docker compose ps

# Test VLM service
curl http://localhost:8001/health

# Test VLM with image (if parallel mode)
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "/path/to/test_image.jpg",
    "prompt": "Analyze this classroom for safety violations"
  }'

# Check Ollama (native)
ollama list
ollama ps  # Show loaded models
```

### Mac-Specific Optimizations

#### Postgres (128GB RAM Available)
```yaml
shared_buffers: 2GB
effective_cache_size: 32GB
work_mem: 128MB
maintenance_work_mem: 512MB
```

#### RAG Service
```yaml
USE_NATIVE_EMBEDDINGS: "true"
EMBEDDING_BATCH_SIZE: "32"
```

#### Perception Service
```yaml
USE_COREML: "true"  # Use Neural Engine
DETECTION_BATCH_SIZE: "8"
```

### Performance Monitoring

```bash
# Monitor Ollama performance
ollama ps

# Monitor Docker containers
docker stats

# Monitor Metal GPU usage
sudo powermetrics --samplers gpu_power -i 1000

# Check logs for performance issues
docker compose logs -f nura-vlm
```

### Troubleshooting Mac

**Ollama not accessible from Docker:**
```bash
# Ensure Ollama is running
ps aux | grep ollama

# If not running
ollama serve

# Test connectivity
curl http://localhost:11434/api/tags
```

**VLM timeouts:**
```bash
# Check Ollama logs
journalctl -u ollama -f

# Increase timeout in .env
VLM_TIMEOUT=300

# Restart services
docker compose -f compose.yaml -f compose.mac.yaml restart nura-vlm
```

**Slow performance:**
```bash
# Check if model is loaded in Ollama
ollama ps

# Pre-load model
ollama run llava:7b "test"

# Monitor GPU usage
sudo powermetrics --samplers gpu_power -i 1000
```

---

## 🖥️ Windows/Linux GPU Deployment

### Hardware Requirements
- **NVIDIA GPU**: RTX 3060 (12GB VRAM) or better
  - RTX 3060 12GB: 1-2 VLM instances
  - RTX 3080 10GB: 2-3 VLM instances
  - RTX 4090 24GB: 4+ VLM instances
- **RAM**: 32GB minimum, 64GB recommended
- **Storage**: 500GB+ for models and data
- **CPU**: 8+ cores recommended

### Software Requirements
- **Ubuntu 22.04 LTS** or Windows 11 with WSL2
- **NVIDIA Driver**: 525.60.13 or newer
- **NVIDIA Container Toolkit**: 1.14.0 or newer
- **Docker**: 24.0.0 or newer with GPU support
- **CUDA**: 12.0 or newer (included in images)

### Installation Steps (Ubuntu/Debian)

#### 1. Install NVIDIA Drivers

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install NVIDIA driver
sudo apt install -y nvidia-driver-535

# Reboot
sudo reboot

# Verify driver
nvidia-smi
```

#### 2. Install NVIDIA Container Toolkit

```bash
# Add NVIDIA package repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Install toolkit
sudo apt update
sudo apt install -y nvidia-container-toolkit

# Configure Docker runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Verify GPU access in Docker
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

#### 3. Clone and Configure

```bash
# Clone repository
git clone https://github.com/yourorg/nura-care-source.git
cd nura-care-source

# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Key environment variables:**
```bash
# Database
POSTGRES_PASSWORD=your_secure_password
KEYCLOAK_ADMIN_PASSWORD=your_admin_password
CLOUD_DB_PASSWORD=your_cloud_db_password

# VLM Configuration
VLM_MODEL=llava:7b
VLM_TEMPERATURE=0.3
VLM_MAX_TOKENS=500
VLM_TIMEOUT=180

# Ollama GPU settings
OLLAMA_NUM_PARALLEL=4
OLLAMA_MAX_LOADED_MODELS=2
OLLAMA_FLASH_ATTENTION=true

# Site Configuration
SITE_ID=prod-site-001
LOG_LEVEL=info
```

#### 4. Start Services (Single Instance)

```bash
# Start core infrastructure + NURA services with GPU
docker compose \
  -f compose.yaml \
  -f compose.gpu.yaml \
  --env-file .env \
  --profile ai \
  --profile app \
  up -d

# View logs
docker compose logs -f
```

#### 5. Start Services (Multi-Instance VLM)

```bash
# Start with parallel VLM instances (if GPU has enough VRAM)
docker compose \
  -f compose.yaml \
  -f compose.gpu.yaml \
  --env-file .env \
  --profile ai \
  --profile app \
  --profile vlm-parallel \
  up -d
```

**VRAM Requirements:**
- llava:7b: ~4-5GB per instance + 2-3GB overhead
- RTX 3060 12GB: 1 instance
- RTX 3080 10GB: 1-2 instances
- RTX 4090 24GB: 4 instances

#### 6. Pull Models

```bash
# Connect Ollama to internet temporarily
docker network connect nura_lan_net nura-ollama

# Pull model
docker exec nura-ollama ollama pull llava:7b

# Disconnect from internet
docker network disconnect nura_lan_net nura-ollama

# Verify model
docker exec nura-ollama ollama list
```

#### 7. Verify Installation

```bash
# Check all services
docker compose ps

# Verify GPU access
docker exec nura-ollama nvidia-smi

# Test VLM service
curl http://localhost:8001/health

# Check Ollama
docker exec nura-ollama ollama ps
```

### Installation Steps (Windows with WSL2)

#### 1. Install WSL2 and Ubuntu

```powershell
# Install WSL2 (PowerShell as Administrator)
wsl --install
wsl --set-default-version 2

# Install Ubuntu 22.04
wsl --install -d Ubuntu-22.04

# Restart computer
```

#### 2. Install NVIDIA GPU Driver (Windows)

1. Download latest driver from [NVIDIA website](https://www.nvidia.com/Download/index.aspx)
2. Install driver on **Windows** (not WSL)
3. Restart computer
4. Verify in WSL: `wsl nvidia-smi`

#### 3. Install Docker Desktop

1. Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. Install and enable WSL2 integration
3. Settings → Resources → WSL Integration → Enable for Ubuntu-22.04
4. Restart Docker Desktop

#### 4. Install NVIDIA Container Toolkit (in WSL2)

```bash
# Open Ubuntu in WSL2
wsl -d Ubuntu-22.04

# Follow steps 2-7 from Ubuntu installation above
```

### GPU-Specific Optimizations

#### Ollama Configuration
```yaml
OLLAMA_NUM_PARALLEL: 4        # Parallel inference requests
OLLAMA_MAX_LOADED_MODELS: 2   # Models in VRAM
OLLAMA_FLASH_ATTENTION: true  # Faster attention mechanism
```

#### VLM Configuration
```yaml
CUDA_VISIBLE_DEVICES: "0"     # GPU selection
VLM_TIMEOUT: 180              # Allow GPU warmup time
```

#### Perception Service
```yaml
USE_CUDA: true
DETECTION_BATCH_SIZE: 16      # Larger batches with GPU
TORCH_CUDA_ARCH_LIST: "8.6"   # RTX 30xx series
```

### Performance Monitoring

```bash
# Monitor GPU usage
nvidia-smi -l 1

# Monitor container GPU usage
docker stats

# Monitor Ollama
docker exec nura-ollama ollama ps

# Check VLM logs
docker compose logs -f nura-vlm

# Check inference performance
docker compose logs nura-vlm | grep "Processing time"
```

### Troubleshooting GPU

**"could not select device driver" error:**
```bash
# Verify NVIDIA Container Toolkit
dpkg -l | grep nvidia-container-toolkit

# Reinstall if needed
sudo apt install --reinstall nvidia-container-toolkit
sudo systemctl restart docker
```

**"nvidia-smi not found":**
```bash
# Check NVIDIA driver
nvidia-smi

# If not working, reinstall driver
sudo apt install --reinstall nvidia-driver-535
sudo reboot
```

**"out of memory" error:**
```bash
# Check VRAM usage
nvidia-smi

# Reduce parallel instances or use smaller model
# Edit compose.gpu.yaml:
# - Remove vlm-parallel profile
# - Use llava:7b instead of llava:13b
```

**Slow performance:**
```bash
# Check GPU utilization
nvidia-smi

# Should show ~90%+ GPU usage during inference
# If low:
# - Check CUDA is enabled: docker exec nura-ollama ollama ps
# - Verify GPU layers: docker logs nura-ollama | grep "gpu"
# - Check for CPU fallback: docker logs nura-vlm | grep "CPU"
```

---

## Performance Comparison

### Mac M4 Max (128GB RAM)

| Configuration | Latency | Throughput | Cameras @ 1 FPS |
|---------------|---------|------------|-----------------|
| Single instance | 30-60s | 0.017-0.033 FPS | 1-2 |
| 4 parallel instances | 7-15s avg | 0.27-0.57 FPS | 5-11 |
| With MLX (future) | 0.5-1.0s | 1-2 FPS | 20-40 |

**Cost**: $0 (using existing hardware)

### NVIDIA RTX 3080 (10GB VRAM)

| Configuration | Latency | Throughput | Cameras @ 1 FPS |
|---------------|---------|------------|-----------------|
| Single instance | 10-20s | 0.05-0.1 FPS | 1-2 |
| 2 parallel instances | 10-20s | 0.1-0.2 FPS | 2-4 |

**Cost**: ~$500-700 (GPU only)

### NVIDIA RTX 4090 (24GB VRAM)

| Configuration | Latency | Throughput | Cameras @ 1 FPS |
|---------------|---------|------------|-----------------|
| Single instance | 3-8s | 0.125-0.33 FPS | 2-6 |
| 4 parallel instances | 3-8s | 0.5-1.33 FPS | 10-26 |

**Cost**: ~$1,600-2,000 (GPU only)

---

## Switching Between Platforms

### From Mac to GPU Deployment

1. **Build images on Mac:**
```bash
# Build all services
docker compose -f compose.yaml build
```

2. **Export images:**
```bash
# Tag and save images
docker save nura/vlm:dev | gzip > nura-vlm.tar.gz
docker save nura/rules:dev | gzip > nura-rules.tar.gz
docker save nura/rag:dev | gzip > nura-rag.tar.gz
```

3. **Transfer to GPU server:**
```bash
# Copy to production server
scp *.tar.gz user@gpu-server:/tmp/
```

4. **Load on GPU server:**
```bash
# Load images
docker load < /tmp/nura-vlm.tar.gz
docker load < /tmp/nura-rules.tar.gz
docker load < /tmp/nura-rag.tar.gz
```

5. **Start with GPU config:**
```bash
# Use GPU compose file
docker compose \
  -f compose.yaml \
  -f compose.gpu.yaml \
  --env-file .env \
  --profile ai \
  --profile app \
  up -d
```

### From GPU to Mac Development

1. **Pull from registry** (if using):
```bash
docker pull yourregistry/nura-vlm:latest
```

2. **Start with Mac config:**
```bash
# Ensure native Ollama is running
ollama serve

# Start services
docker compose \
  -f compose.yaml \
  -f compose.mac.yaml \
  --env-file .env \
  --profile app \
  up -d
```

---

## Production Recommendations

### For Mac M4 Max Development
✅ **Use for:**
- Development and testing
- Demo environments
- Small-scale deployments (2-5 cameras)
- Cost-sensitive deployments

❌ **Avoid for:**
- Large-scale production (10+ cameras)
- High-availability requirements
- Environments without 128GB RAM

### For GPU Deployment
✅ **Use for:**
- Production environments
- Large-scale deployments (10+ cameras)
- High-availability setups
- Data center deployments

❌ **Avoid for:**
- Development (higher cost)
- Budget-constrained projects
- Environments without GPU support

---

## Next Steps

### Immediate (Week 1)
1. ✅ Test Mac M4 Max setup with single instance
2. ✅ Measure actual performance with test images
3. ✅ Configure monitoring and logging
4. ✅ Test with 2-3 cameras

### Short-term (Weeks 2-4)
1. ⏳ Deploy multi-instance VLM on Mac
2. ⏳ Build hybrid fast path (CoreML + VLM)
3. ⏳ Test with 10+ cameras
4. ⏳ Prepare GPU deployment environment

### Long-term (Months 2-3)
1. ⏳ Deploy to production GPU server
2. ⏳ Integrate MLX-VLM when library fixed
3. ⏳ Scale to 20+ cameras
4. ⏳ Implement full monitoring stack

---

## Support and Documentation

- **Main Documentation**: [README.md](../README.md)
- **VLM Optimization**: [specs/025-vlm-performance-optimization/spec.md](../specs/025-vlm-performance-optimization/spec.md)
- **Mac M4 Max Guide**: [MAC_M4_OPTIMIZATION.md](./MAC_M4_OPTIMIZATION.md)
- **Next Steps**: [NEXT_STEPS.md](../NEXT_STEPS.md)

---

*Last Updated: November 4, 2026*  
*Version: 1.0*  
*Status: Production Ready*
