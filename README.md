# NURA - AI-Powered Child Safety Monitoring

**Real-time camera violation detection for childcare centers — all data stays on-premise.**

[![Platform](https://img.shields.io/badge/Platform-Mac%20M4%20|%20Linux%20GPU-blue)]()
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)]()
[![TypeScript](https://img.shields.io/badge/TypeScript-NestJS-3178C6?logo=typescript)]()
[![Python](https://img.shields.io/badge/Python-FastAPI-3776AB?logo=python)]()

---

## 🎯 Core Mission

> **Monitor children 24/7 through cameras, detect violations using AI, alert administrators immediately — while keeping all video data completely offline on school servers.**

## What NURA Does

NURA is an **AI-powered safety monitoring system** that:
- 📹 **Watches cameras continuously** in classrooms, playgrounds, hallways
- 🤖 **Understands context** using Vision-Language Models (VLM)
- 📋 **Matches violations** against school policies and government regulations  
- ⚡ **Alerts within 10 seconds** when rules are broken
- 🔒 **Keeps video local** — nothing leaves the school server
- 📡 **WiFi sensing** for uncovered areas (bathrooms, changing rooms)

### Key Features
- **Real-time violation detection**: Supervision ratios, physical aggression, safety hazards
- **Context-aware AI**: Understands difference between "playing" and "fighting"
- **Multi-camera support**: Process 10-20+ cameras simultaneously
- **Offline-first**: Works during internet outages
- **Privacy by design**: Video never leaves premises

---

## 🚀 Quick Start

### Choose Your Platform

**🍎 Mac M4 Max Development** (2-20 cameras):
```bash
# 1. Install native Ollama
brew install ollama && ollama serve
ollama pull llava:7b

# 2. Configure environment
cp .env.example .env
nano .env  # Set passwords

# 3. Start services
docker compose -f compose.yaml -f compose.mac.yaml --env-file .env --profile app up -d
```

**🖥️ Linux/Windows GPU Deployment** (Production):
```bash
# 1. Install NVIDIA support (Ubuntu/Debian)
sudo apt install nvidia-driver-535 nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# 2. Configure environment
cp .env.example .env
nano .env  # Set passwords

# 3. Start services
docker compose -f compose.yaml -f compose.gpu.yaml --env-file .env --profile ai --profile app up -d

# 4. Pull VLM model
docker network connect nura_lan_net nura-ollama
docker exec nura-ollama ollama pull llava:7b
docker network disconnect nura_lan_net nura-ollama
```

**📖 Full Setup Guide**: See [QUICK_START.md](QUICK_START.md) or [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)

---

## 📁 Project Structure

```
nura-care-source/
├── services/              # Microservices
│   ├── nura-vlm/         # Vision-Language Model (Python/FastAPI)
│   ├── nura-rules/       # Rules engine (TypeScript/NestJS)
│   ├── nura-rag/         # RAG for policy matching (TypeScript/NestJS)
│   ├── nura-perception/  # Object detection (Python/FastAPI)
│   ├── nura-api/         # REST API (TypeScript/NestJS)
│   └── nura-ui/          # Admin dashboard (Next.js)
├── edge/                  # Edge infrastructure configs
│   ├── frigate/          # NVR camera management
│   ├── postgres/         # Database init scripts
│   └── caddy/            # TLS proxy
├── docs/                  # Documentation
│   ├── DEPLOYMENT_GUIDE.md       # Platform-specific deployment
│   ├── MAC_M4_OPTIMIZATION.md    # Mac performance tuning
│   ├── PERFORMANCE_OPTIMIZATION_SUMMARY.md
│   └── VISION_REALIGNMENT.md     # Product vision
├── specs/                 # Technical specifications
│   └── 025-vlm-performance-optimization/
├── tools/                 # Development tools
│   ├── vlm/              # VLM model management
│   └── testing/          # Test scripts
├── compose.yaml           # Base Docker Compose
├── compose.mac.yaml       # Mac M4 Max override
├── compose.gpu.yaml       # GPU deployment override
├── QUICK_START.md         # Platform selection guide
└── README.md              # This file
```

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Edge Box (On-Premise)                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  📹 Cameras → Frigate NVR → nura-perception (YOLO)          │
│                       ↓                                       │
│              nura-vlm (LLaVA 7B)                             │
│                       ↓                                       │
│           nura-rules (Policy Engine)                         │
│                       ↓                                       │
│         nura-rag (Semantic Rule Search)                      │
│                       ↓                                       │
│     nura-notifier → Staff Alerts (10s latency)               │
│                                                               │
│  💾 Data: Postgres + pgvector                                │
│  📨 Events: NATS JetStream                                   │
│  🔐 Auth: Keycloak (Local)                                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                         ↕ (Metadata only)
┌─────────────────────────────────────────────────────────────┐
│                      Cloud (Railway)                         │
├─────────────────────────────────────────────────────────────┤
│  cloud-api        │ Device enrollment                        │
│  alert-relay      │ SMS/Email notifications                  │
│  cloud-db         │ Aggregate reporting                      │
└─────────────────────────────────────────────────────────────┘
```

**Privacy Boundary**: Only anonymized metadata crosses from edge to cloud. Raw video, face embeddings, and PII stay local.

### Technology Stack

| Layer | Mac M4 Max | GPU Deployment | Purpose |
|-------|------------|----------------|---------|
| **VLM** | Native Ollama (Metal GPU) | Dockerized Ollama (CUDA) | Scene understanding |
| **Object Detection** | Frigate + YOLO | Frigate + TensorRT | Person detection |
| **Database** | Postgres + pgvector | Postgres + pgvector | Storage + embeddings |
| **Events** | NATS JetStream | NATS JetStream | Microservice messaging |
| **API** | NestJS (TypeScript) | NestJS (TypeScript) | REST endpoints |
| **Frontend** | Next.js + shadcn/ui | Next.js + shadcn/ui | Admin dashboard |

---

## 🎭 Platform Configurations

### Mac M4 Max Development
- **Purpose**: Development, testing, demos
- **Performance**: 30-60s per image (single) | 2-8 FPS (4 parallel)
- **Cameras**: 2-20 @ 1 FPS
- **Cost**: $0 (uses existing hardware)
- **Setup time**: 5 minutes

### NVIDIA GPU Deployment
- **Purpose**: Production environments
- **Performance**: 3-30s per image (depends on GPU)
- **Cameras**: 2-26 depending on GPU
- **Cost**: $500-2,000 (GPU hardware)
- **Setup time**: 30 minutes

**See**: [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for complete comparison

---

## 📚 Documentation

### Getting Started
| Document | Description |
|----------|-------------|
| **[QUICK_START.md](QUICK_START.md)** | Platform selection and 3-step setup |
| **[QUICKSTART.md](QUICKSTART.md)** | Original quick start (general) |
| **[docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)** | Complete deployment guide (800+ lines) |
| **[docs/MAC_M4_OPTIMIZATION.md](docs/MAC_M4_OPTIMIZATION.md)** | Mac performance tuning |

### Architecture & Design
| Document | Description |
|----------|-------------|
| **[docs/VISION_REALIGNMENT.md](docs/VISION_REALIGNMENT.md)** | Product vision and core mission |
| **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** | System architecture overview |
| **[.speckit/constitution.md](.speckit/constitution.md)** | Core principles and governance |
| **[.speckit/PHASES.md](.speckit/PHASES.md)** | Development phases |

### Performance & Optimization
| Document | Description |
|----------|-------------|
| **[specs/025-vlm-performance-optimization/spec.md](specs/025-vlm-performance-optimization/spec.md)** | VLM optimization (2,000 lines) |
| **[docs/PERFORMANCE_OPTIMIZATION_SUMMARY.md](docs/PERFORMANCE_OPTIMIZATION_SUMMARY.md)** | Performance summary |
| **[docs/NEXT_STEPS.md](docs/NEXT_STEPS.md)** | Optimization roadmap |

### Development
| Document | Description |
|----------|-------------|
| **[docs/PROJECT_SETUP.md](docs/PROJECT_SETUP.md)** | Development environment setup |
| **[docs/SERVICE_TEMPLATE.md](docs/SERVICE_TEMPLATE.md)** | Create new microservices |
| **[docs/TESTING.md](docs/TESTING.md)** | Testing guide |
| **[docs/TECH_DECISIONS.md](docs/TECH_DECISIONS.md)** | Technology choices |

---

## 🔧 Development Workflow

### Running Tests
```bash
# Integration tests
./tests/scripts/test-pipeline.sh

# VLM testing
python tools/testing/test_vlm_image.py tests/images/test_classroom1.jpg

# Performance benchmarks
python tools/testing/test_m4_performance.py
```

### Building Services
```bash
# Build all services
docker compose build

# Build specific service
docker compose build nura-vlm

# Build with platform override
docker compose -f compose.yaml -f compose.mac.yaml build
```

### Monitoring
```bash
# View logs
docker compose logs -f nura-vlm

# Check service health
docker compose ps

# Monitor GPU (Linux)
nvidia-smi -l 1

# Monitor native Ollama (Mac)
ollama ps
```

---

## ⚡ Performance Benchmarks

### Mac M4 Max (128GB RAM, Metal GPU)
```
Configuration         | Latency/Image | Throughput | Cameras @ 1 FPS
---------------------|---------------|------------|----------------
Single instance      | 30-60s        | 0.017 FPS  | 2-3
4 parallel instances | 7-15s avg     | 0.27 FPS   | 5-11
With MLX (future)    | 0.5-1.0s      | 1-2 FPS    | 20-40
```

### NVIDIA RTX GPUs
```
GPU                  | Latency/Image | Parallel   | Cameras @ 1 FPS
---------------------|---------------|------------|----------------
RTX 3060 (12GB)      | 15-30s        | 1-2        | 1-4
RTX 3080 (10GB)      | 10-20s        | 2-3        | 2-6
RTX 4090 (24GB)      | 3-8s          | 4+         | 10-26
```

**Full benchmarks**: See [docs/PERFORMANCE_OPTIMIZATION_SUMMARY.md](docs/PERFORMANCE_OPTIMIZATION_SUMMARY.md)

---

## 🛠️ Tools & Utilities

### VLM Model Management
```bash
# Download models (Mac)
tools/vlm/download_llava_model.sh

# Download compatible models
tools/vlm/download_compatible_llava.sh
```

### Testing Tools
```bash
# Test with single image
python tools/testing/test_vlm_image.py <image_path>

# Performance testing
python tools/testing/test_m4_performance.py

# MLX testing (when library fixed)
python tools/testing/test_mlx_final.py
```

---

## 📋 Phase Roadmap

### Phase 1: Safety Monitoring Core ✅
- ✅ Multi-camera VLM processing
- ✅ RAG-based policy matching
- ✅ Real-time violation detection
- ✅ Platform-specific deployment (Mac/GPU)
- ⏳ Violence severity classification
- ⏳ Supervision ratio monitoring

### Phase 2: WiFi Sensing
- 📡 WiFi-based occupancy detection
- 🚪 Bathroom/changing room coverage
- 📊 Headcount verification
- 🔔 Zone-based alerting

### Phase 3: Fleet Management
- 🏢 Multi-site dashboard
- 📈 Compliance reporting
- 📊 Analytics and insights
- 🔐 Advanced RBAC

### Phase 4: Monetization (Optional)
- 📅 Attendance tracking
- 💰 Billing automation
- 👥 Staff credential management
- 💊 Medication cross-checks

**Note**: Safety monitoring IS the product. Other features are secondary.

---

## 🤝 Contributing

### Development Setup
1. Clone repository
2. Choose platform configuration (Mac or GPU)
3. Follow [QUICK_START.md](QUICK_START.md)
4. Read [docs/PROJECT_SETUP.md](docs/PROJECT_SETUP.md)

### Code Standards
- **TypeScript**: NestJS for services, Next.js for UI
- **Python**: FastAPI for ML services
- **Testing**: Integration tests required
- **Documentation**: Update docs/ for significant changes

### Commit Guidelines
- Use conventional commits
- Reference issue numbers
- Update relevant documentation

---

## 📄 License

[License information to be added]

---

## 🆘 Support

### Quick Links
- **Issues**: [GitHub Issues](https://github.com/yourorg/nura-care-source/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourorg/nura-care-source/discussions)
- **Documentation**: [docs/](docs/)

### Common Issues

**Mac: "Connection refused to Ollama"**
```bash
ollama serve  # Ensure Ollama is running
curl http://localhost:11434/api/tags  # Test connection
```

**GPU: "could not select device driver"**
```bash
sudo apt install nvidia-container-toolkit
sudo systemctl restart docker
```

**Both: "VLM timeout"**
```bash
# Increase timeout in .env
VLM_TIMEOUT=300
docker compose restart nura-vlm
```

---

## 🌟 Key Differentiators

1. **Privacy-First**: Video never leaves premises
2. **Context-Aware**: VLM understands nuance (playing vs fighting)
3. **Offline-First**: Works during internet outages
4. **Platform-Flexible**: Develop on Mac, deploy on GPU
5. **Cost-Effective**: From $0 (Mac M4) to production scale
6. **Real-Time**: <10 second alert latency
7. **Multi-Camera**: Process 10-20+ cameras simultaneously
8. **Production-Ready**: Dual platform deployment options

---

**Built with ❤️ for child safety**

*Last Updated: November 4, 2026*
