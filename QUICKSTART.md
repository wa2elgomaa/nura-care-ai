# NURA Quick Start Guide

Get NURA running in 5-10 minutes. Choose your platform:

---

## Choose Your Platform

### 🍎 **Mac M4 Max Development** → Skip to [Mac Setup](#-mac-m4-max-setup)
- **Best for**: Development, testing, demos
- **Performance**: 30-60s per image (2-20 cameras with parallel mode)
- **Cost**: $0 (uses existing hardware)
- **Setup time**: 5 minutes

### 🖥️ **Linux/Windows GPU** → Skip to [GPU Setup](#-gpu-deployment)
- **Best for**: Production deployments
- **Performance**: 3-30s per image (depends on GPU)
- **Cost**: $500-2,000 (GPU)
- **Setup time**: 30 minutes

---

## 🍎 Mac M4 Max Setup

### Prerequisites
- Mac with M3/M4 Max chip
- 64GB+ RAM (128GB recommended)
- Docker Desktop for Mac
- Homebrew

### Step 1: Install Native Ollama (Required)

```bash
# Install Ollama
brew install ollama

# Start Ollama service (keep this running)
ollama serve

# In a NEW terminal, pull the VLM model
ollama pull llava:7b

# Verify
ollama list
```

**Why native?** 2-6x faster than containerized Ollama, direct Metal GPU access.

### Step 2: Configure Environment

```bash
# Clone repository (if not already)
git clone <repository-url> nura-care-source
cd nura-care-source

# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Required changes in .env**:
```bash
POSTGRES_PASSWORD=your_secure_password
KEYCLOAK_ADMIN_PASSWORD=your_admin_password
CLOUD_DB_PASSWORD=your_cloud_db_password
VLM_MODEL=llava:7b
```

### Step 3: Generate Signing Keys

```bash
mkdir -p secrets && chmod 700 secrets
openssl genpkey -algorithm ed25519 -out secrets/update_signing_key.pem
openssl pkey -in secrets/update_signing_key.pem -pubout -out secrets/update_signing_key.pub
chmod 600 secrets/update_signing_key.pem
```

⚠️ **NEVER commit `secrets/update_signing_key.pem`**

### Step 4: Start Services

**For 2-5 cameras (single VLM instance):**
```bash
docker compose \
  -f compose.yaml \
  -f compose.mac.yaml \
  --env-file .env \
  --profile app \
  up -d
```

**For 10-20 cameras (4 parallel VLM instances):**
```bash
docker compose \
  -f compose.yaml \
  -f compose.mac.yaml \
  --env-file .env \
  --profile app \
  --profile vlm-parallel \
  up -d
```

### Step 5: Verify Installation

```bash
# Check all services are running
docker compose ps

# Test VLM service
curl http://localhost:8001/health

# Test load balancer (if using parallel mode)
curl http://localhost:8000/health

# Check Ollama
ollama ps  # Should show llava:7b loaded
```

**Expected output:**
- All containers: `Up` status
- Health endpoints: `{"status":"ok"}`
- Ollama: Model loaded in VRAM

### Mac Performance Targets
- **Single instance**: 30-60s per image
- **4 parallel instances**: 2-8 FPS aggregate (10-20 cameras @ 1 FPS)

### Mac Troubleshooting

**"Connection refused" to Ollama:**
```bash
# Ensure Ollama is running
ps aux | grep ollama

# If not running
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

**VLM timeouts:**
```bash
# Increase timeout in .env
VLM_TIMEOUT=300

# Restart services
docker compose -f compose.yaml -f compose.mac.yaml restart nura-vlm
```

---

## 🖥️ GPU Deployment

### Prerequisites
- Linux (Ubuntu 22.04 LTS recommended) or Windows 11 with WSL2
- NVIDIA GPU (RTX 3060 12GB or better)
- 32GB+ RAM
- Docker with GPU support

### Step 1: Install NVIDIA Support

**Ubuntu/Debian:**
```bash
# Install NVIDIA driver
sudo apt update
sudo apt install nvidia-driver-535

# Reboot
sudo reboot

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update
sudo apt install -y nvidia-container-toolkit

# Configure Docker
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Verify GPU access
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

**Windows WSL2:**
1. Install NVIDIA GPU driver on Windows (not WSL)
2. Install WSL2 and Docker Desktop
3. Follow Ubuntu steps above inside WSL2

### Step 2: Clone and Configure

```bash
# Clone repository
git clone <repository-url> nura-care-source
cd nura-care-source

# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Required changes in .env**:
```bash
POSTGRES_PASSWORD=your_secure_password
KEYCLOAK_ADMIN_PASSWORD=your_admin_password
CLOUD_DB_PASSWORD=your_cloud_db_password
VLM_MODEL=llava:7b

# GPU-specific settings
OLLAMA_NUM_PARALLEL=4
OLLAMA_MAX_LOADED_MODELS=2
```

### Step 3: Generate Signing Keys

```bash
mkdir -p secrets && chmod 700 secrets
openssl genpkey -algorithm ed25519 -out secrets/update_signing_key.pem
openssl pkey -in secrets/update_signing_key.pem -pubout -out secrets/update_signing_key.pub
chmod 600 secrets/update_signing_key.pem
```

### Step 4: Start Services

**Single VLM instance:**
```bash
docker compose \
  -f compose.yaml \
  -f compose.gpu.yaml \
  --env-file .env \
  --profile ai \
  --profile app \
  up -d
```

**Multiple instances (if GPU has enough VRAM):**
```bash
docker compose \
  -f compose.yaml \
  -f compose.gpu.yaml \
  --env-file .env \
  --profile ai \
  --profile app \
  --profile vlm-parallel \
  up -d
```

### Step 5: Pull VLM Models

```bash
# Connect Ollama to internet temporarily
docker network connect nura_lan_net nura-ollama

# Pull model (this will take a few minutes)
docker exec nura-ollama ollama pull llava:7b

# Disconnect from internet
docker network disconnect nura_lan_net nura-ollama

# Verify model loaded
docker exec nura-ollama ollama list
```

### Step 6: Verify Installation

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

### GPU Performance Targets

| GPU | VRAM | Latency | Max Instances | Cameras @ 1 FPS |
|-----|------|---------|---------------|-----------------|
| RTX 3060 | 12GB | 15-30s | 1-2 | 1-4 |
| RTX 3080 | 10GB | 10-20s | 2-3 | 2-6 |
| RTX 4090 | 24GB | 3-8s | 4+ | 10-26 |

### GPU Troubleshooting

**"could not select device driver":**
```bash
# Reinstall NVIDIA Container Toolkit
sudo apt install --reinstall nvidia-container-toolkit
sudo systemctl restart docker
```

**"out of memory":**
```bash
# Check GPU memory usage
nvidia-smi

# Reduce instances or use smaller model
# Edit .env:
VLM_MODEL=llava:7b  # Instead of llava:13b
```

**Slow performance:**
```bash
# Monitor GPU utilization
nvidia-smi -l 1

# Should show ~90%+ during inference
# If low, check CUDA is enabled:
docker logs nura-ollama | grep -i cuda
```

---

## Common Commands

### Mac M4 Max

```bash
# Start services
docker compose -f compose.yaml -f compose.mac.yaml --profile app up -d

# Start with parallel VLM
docker compose -f compose.yaml -f compose.mac.yaml --profile app --profile vlm-parallel up -d

# Stop services
docker compose -f compose.yaml -f compose.mac.yaml down

# View logs
docker compose logs -f nura-vlm

# Restart VLM
docker compose -f compose.yaml -f compose.mac.yaml restart nura-vlm

# Check Ollama status (native)
ollama ps
```

### GPU Deployment

```bash
# Start services
docker compose -f compose.yaml -f compose.gpu.yaml --profile ai --profile app up -d

# Stop services
docker compose -f compose.yaml -f compose.gpu.yaml down

# Monitor GPU usage
nvidia-smi -l 1

# View VLM logs
docker compose logs -f nura-vlm

# Check GPU in container
docker exec nura-ollama nvidia-smi
```

---

## Platform Comparison

| Platform | Setup | Cost | Single Instance | 4 Parallel | Best For |
|----------|-------|------|-----------------|------------|----------|
| **Mac M4 Max** | 5 min | $0 | 30-60s | 2-8 FPS | Dev, demos, 2-20 cameras |
| **RTX 3060** | 30 min | $500 | 15-30s | N/A | Budget prod, 1-4 cameras |
| **RTX 3080** | 30 min | $700 | 10-20s | 0.1-0.2 FPS | Production, 2-6 cameras |
| **RTX 4090** | 30 min | $2,000 | 3-8s | 0.5-1.3 FPS | Large scale, 10+ cameras |

---

## Next Steps

### Immediate
1. ✅ Services running
2. Test with sample images: `python tools/testing/test_vlm_image.py tests/images/test_classroom1.jpg`
3. Monitor performance: `docker compose logs -f nura-vlm`
4. Check resource usage: `docker stats`

### This Week
1. Connect real cameras to Frigate
2. Test with 2-3 live camera feeds
3. Configure violation rules
4. Set up notifications

### For More Information
- **Complete Deployment Guide**: [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- **Mac Optimization**: [docs/MAC_M4_OPTIMIZATION.md](docs/MAC_M4_OPTIMIZATION.md)
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Performance Optimization**: [specs/025-vlm-performance-optimization/spec.md](specs/025-vlm-performance-optimization/spec.md)

---

## Support

**Issues?** Check [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) troubleshooting section

**Questions?** See complete documentation in [README.md](README.md)

---

*Last updated: November 4, 2026*
