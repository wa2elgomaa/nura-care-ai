# NURA VLM Service Deployment Guide

**Date:** 2026-11-06  
**Service:** nura-vlm (Hybrid Fast-Path + VLM Router)

---

## Current Status

**nura-vlm is DESIGNED to run as a Docker container**, not as a standalone service.

### Why Containerization is Correct:

1. ✅ **Already configured in `compose.yaml`**
2. ✅ **Dockerfile exists** (`services/nura-vlm/Dockerfile`)
3. ✅ **Part of the NURA stack** (depends on NATS, Postgres, etc.)
4. ✅ **Consistent deployment** across environments
5. ✅ **Environment isolation** (dependencies, models, etc.)

---

## Deployment Options

### Option 1: Full NURA Stack (Recommended for Production)

**Use when:** Deploying the complete NURA system

```bash
# Start entire stack with nura-vlm
docker compose up -d

# Check nura-vlm status
docker compose ps nura-vlm

# View logs
docker compose logs -f nura-vlm
```

**Includes:**
- PostgreSQL
- NATS messaging
- Keycloak auth
- Frigate NVR
- All NURA services
- nura-vlm (with hybrid router)

---

### Option 2: VLM Service Only (Development)

**Use when:** Testing nura-vlm independently

```bash
# Start only dependencies + nura-vlm
docker compose up -d nats ollama nura-vlm

# Or manually for development
cd services/nura-vlm
python3 src/main.py
```

**Dependencies:**
- NATS (for messaging)
- Ollama (for VLM inference)

---

### Option 3: GPU-Accelerated Deployment

**Use when:** GPU available, need best performance

```bash
# Use GPU-specific compose file
docker compose -f compose.gpu.yaml up -d

# Or build GPU-specific image
cd services/nura-vlm
docker build -f Dockerfile.gpu -t nura/vlm:gpu .
```

**GPU Configuration in `.env`:**
```bash
TEMPORAL_MODEL_TYPE=mvit
TEMPORAL_DEVICE=cuda
```

---

## Running Modes Comparison

### Mode 1: Docker Container (Recommended ✅)

**Pros:**
- ✅ Consistent environment
- ✅ Easy deployment
- ✅ Part of orchestrated stack
- ✅ Automatic restarts
- ✅ Resource limits
- ✅ Network isolation

**Cons:**
- ⚠️ Rebuild needed for code changes
- ⚠️ Slightly more complex debugging

**When to use:**
- Production deployment
- Testing full system
- Multi-service coordination

---

### Mode 2: Local Python Process (Development Only)

**Pros:**
- ✅ Fast iteration (no rebuild)
- ✅ Easy debugging
- ✅ Direct file access

**Cons:**
- ❌ Not how it runs in production
- ❌ Environment differences
- ❌ Manual dependency management
- ❌ No orchestration

**When to use:**
- Local development
- Quick testing
- Debugging specific issues

---

## How to Switch Between Modes

### Currently Running Locally? Switch to Container:

```bash
# 1. Stop local process (if running)
pkill -f "python.*nura-vlm"

# 2. Build container image
cd /Users/wgomaa/Work/PixelPlusOne/Nura\ Childcare\ AI/nura-care-source
docker compose build nura-vlm

# 3. Start container
docker compose up -d nura-vlm

# 4. Verify it's running
docker compose ps nura-vlm
docker compose logs -f nura-vlm
```

### Need to Run Locally for Development?

```bash
# 1. Stop container
docker compose stop nura-vlm

# 2. Setup local environment
cd services/nura-vlm
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Install local detector package
cd ../../packages/nura-detectors
pip install -e .

# 4. Run locally
cd ../../services/nura-vlm
python3 src/main.py
```

---

## Environment Configuration

### For Container Deployment:

**.env file** (project root):
```bash
# Model configuration
TEMPORAL_MODEL_TYPE=resnet50_gru  # or mvit for GPU
TEMPORAL_DEVICE=cpu               # or cuda for GPU
ENABLE_TEMPORAL_DETECTION=true

# VLM configuration
VLM_MODEL=qwen3-vl:8b-instruct
OLLAMA_URL=http://ollama:11434    # Container name

# Service ports
VLM_SERVICE_PORT=8001
```

### For Local Development:

**.env file** (same, but adjust URLs):
```bash
# Model configuration (same)
TEMPORAL_MODEL_TYPE=resnet50_gru
TEMPORAL_DEVICE=cpu
ENABLE_TEMPORAL_DETECTION=true

# VLM configuration (use localhost)
VLM_MODEL=qwen3-vl:8b-instruct
OLLAMA_URL=http://localhost:11434  # Localhost for local dev

# Service ports
VLM_SERVICE_PORT=8001
```

---

## Model Files in Container

### Challenge: Large Model Files

**Issue:** Models (especially MViT: 392MB) need to be accessible in container

**Solutions:**

#### Solution 1: Volume Mount (Recommended for Dev)

```yaml
# compose.yaml
services:
  nura-vlm:
    volumes:
      - ./models:/app/models:ro  # Read-only mount
```

**Pros:**
- ✅ No need to rebuild for model updates
- ✅ Easy to switch models
- ✅ Shared across containers

#### Solution 2: Copy into Image (Production)

```dockerfile
# Dockerfile
COPY models/ /app/models/
```

**Pros:**
- ✅ Self-contained image
- ✅ No external dependencies
- ✅ Portable

**Cons:**
- ❌ Large image size
- ❌ Rebuild for model updates

#### Solution 3: Download at Runtime (Cloud)

```dockerfile
# Dockerfile
RUN curl -o /app/models/model.pth https://storage/model.pth
```

**Pros:**
- ✅ Smaller image
- ✅ Easy updates

**Cons:**
- ❌ Slower startup
- ❌ Network dependency

---

## Current Docker Setup

### Existing Dockerfiles:

1. **`Dockerfile`** - Standard CPU deployment
2. **`Dockerfile.gpu`** - GPU-accelerated deployment
3. **`Dockerfile.mac`** - Mac-specific (M1/M2/M3)

### Recommended Configuration:

**For your deployment (on-premise, GPU available):**

```bash
# Use compose.gpu.yaml
docker compose -f compose.gpu.yaml up -d

# This configures:
# - NVIDIA GPU support
# - CUDA libraries
# - GPU-optimized models
```

**Edit compose.gpu.yaml to add:**
```yaml
services:
  nura-vlm:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      TEMPORAL_MODEL_TYPE: mvit
      TEMPORAL_DEVICE: cuda
    volumes:
      - ./models:/app/models:ro
```

---

## Best Practices

### For Development:

✅ **Run locally** for fast iteration
```bash
cd services/nura-vlm
source .venv/bin/activate
python3 src/main.py
```

✅ **Test in container** before committing
```bash
docker compose up nura-vlm
```

### For Production:

✅ **Always use containers**
```bash
docker compose -f compose.gpu.yaml up -d
```

✅ **Volume mount models** (don't copy into image)
```yaml
volumes:
  - ./models:/app/models:ro
```

✅ **Set resource limits**
```yaml
deploy:
  resources:
    limits:
      memory: 8G
      cpus: '4'
```

### For GPU Deployment:

✅ **Use compose.gpu.yaml**
✅ **Install NVIDIA Docker runtime**
```bash
# Install nvidia-docker2
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

✅ **Verify GPU in container**
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

---

## Migration Path

### Current State → Containerized

**If currently running locally, migrate in steps:**

#### Step 1: Ensure Models Available
```bash
# Make sure models are in project
ls -lh models/
# Should see:
# - temporal_violence.keras (1.2MB)
# - mvit_violence.pth (392MB)
```

#### Step 2: Test Container Locally
```bash
# Build image
docker compose build nura-vlm

# Run without detaching (see logs)
docker compose up nura-vlm

# Test API
curl http://localhost:8001/health
```

#### Step 3: Deploy Full Stack
```bash
# Stop local process
pkill -f "python.*nura-vlm"

# Start containerized stack
docker compose up -d

# Verify all services
docker compose ps
```

#### Step 4: Configure for Production
```bash
# Use GPU compose file
docker compose -f compose.gpu.yaml up -d

# Set production .env
TEMPORAL_MODEL_TYPE=mvit
TEMPORAL_DEVICE=cuda
```

---

## Troubleshooting

### Container Can't Find Models

**Error:** `Temporal model not found at models/temporal_violence.keras`

**Fix:**
```yaml
# Add volume mount in compose.yaml
services:
  nura-vlm:
    volumes:
      - ./models:/app/models:ro
```

### Container Can't Access GPU

**Error:** `CUDA not available`

**Fix:**
```bash
# Check nvidia-docker runtime
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Ensure compose.gpu.yaml has GPU config
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          capabilities: [gpu]
```

### Imports Fail in Container

**Error:** `ModuleNotFoundError: No module named 'nura_detectors'`

**Fix:**
```dockerfile
# Ensure Dockerfile installs detector package
COPY packages/nura-detectors /app/packages/nura-detectors
RUN pip install -e /app/packages/nura-detectors
```

---

## Recommendation

### ✅ YES, Run as Container

**For your deployment:**

1. **Use Docker containers** (it's designed for this)
2. **Use `compose.gpu.yaml`** (you have GPU)
3. **Volume mount models** (easy updates)
4. **Set `TEMPORAL_MODEL_TYPE=mvit`** (best performance with GPU)

**Quick Start:**
```bash
# 1. Ensure models in place
ls -lh models/

# 2. Configure .env for GPU
echo "TEMPORAL_MODEL_TYPE=mvit" >> .env
echo "TEMPORAL_DEVICE=cuda" >> .env

# 3. Build and start
docker compose -f compose.gpu.yaml up -d nura-vlm

# 4. Verify
docker compose logs -f nura-vlm
curl http://localhost:8001/health
```

---

## Summary

| Aspect | Container | Local Process |
|--------|-----------|---------------|
| **Production** | ✅ Recommended | ❌ Not suitable |
| **Development** | ✅ For testing | ✅ For fast iteration |
| **GPU Support** | ✅ Full support | ⚠️ Requires manual setup |
| **Orchestration** | ✅ Built-in | ❌ Manual |
| **Deployment** | ✅ Easy | ❌ Complex |

**Verdict:** **Use containers for all deployments**, run locally only for active development.
