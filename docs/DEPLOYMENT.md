# Deployment Guide

## Environment-Specific Deployment

### Local Development (Mac with Metal GPU)

**What runs where:**
- **Native on Mac**: VLM service (Python + Ollama + Metal GPU)
- **Docker**: All other services
- **Special**: VLM Proxy bridges Docker ↔ Native VLM

```bash
# Start VLM service natively
cd services/nura-vlm
source .venv/bin/activate
python -m src.main

# Start all Docker services (uses compose.override.yml automatically)
docker compose up -d
```

**Services that DON'T run locally:**
- ❌ Keycloak (dev auth only)
- ❌ PgAdmin (use psql or DB client)  
- ❌ MediaMTX (testing only)
- ❌ Sync-agent (mock cloud sync)

### Production Server (Edge Box with NVIDIA GPU)

**What runs where:**
- **All in Docker**: Including VLM service with GPU passthrough
- **No proxy needed**: Services communicate via Docker network

```bash
# Production deployment
docker compose -f compose.yaml -f compose.prod.yml up -d
```

**Services that run in production:**
- ✅ VLM Service (Docker with NVIDIA GPU)
- ✅ Ollama (Docker with NVIDIA GPU)
- ✅ Frigate (Docker with NVIDIA GPU for hardware acceleration)
- ✅ Stream Processor
- ✅ Alert Service
- ✅ PostgreSQL
- ✅ NATS
- ✅ MQTT (Mosquitto)

**Services that DON'T run in production:**
- ❌ VLM Proxy (not needed - direct Docker network access)
- ❌ MediaMTX (real cameras publish directly to Frigate)
- ❌ Keycloak (use external auth)
- ❌ Sync-agent (use cloud-sync-agent instead)

## Architecture Differences

### Local (Mac Development)
```
┌─────────────────────────────────────────┐
│  Mac Host (Metal GPU)                   │
│  ┌─────────────────┐                    │
│  │ VLM Service     │ ← Native Python    │
│  │ (Ollama+Metal)  │                    │
│  └────────┬────────┘                    │
│           │ localhost:8001               │
│  ┌────────▼────────┐                    │
│  │ VLM Proxy       │ ← host network     │
│  │ (nginx)         │                    │
│  └────────┬────────┘                    │
└───────────┼─────────────────────────────┘
            │ 192.168.176.1:8001
┌───────────▼─────────────────────────────┐
│  Docker Bridge Network (core_net)       │
│  ┌──────────────────┐                   │
│  │ Stream Processor │                   │
│  └─────────┬────────┘                   │
│  ┌─────────▼────────┐                   │
│  │ Other Services   │                   │
│  └──────────────────┘                   │
└──────────────────────────────────────────┘
```

### Production (Edge Box with NVIDIA GPU)
```
┌──────────────────────────────────────────┐
│  Docker Network (core_net)               │
│  ┌─────────────────┐                     │
│  │ VLM Service     │ ← Docker + NVIDIA   │
│  │ (Ollama+CUDA)   │                     │
│  └────────┬────────┘                     │
│           │ nura-vlm:8001                │
│  ┌────────▼────────┐                     │
│  │ Stream Processor│                     │
│  └─────────┬───────┘                     │
│  ┌─────────▼────────┐                    │
│  │ Other Services   │                    │
│  └──────────────────┘                    │
└──────────────────────────────────────────┘
```

## Quick Reference

| Component | Local | Production |
|-----------|-------|------------|
| VLM Service | Native (Metal GPU) | Docker (NVIDIA GPU) |
| VLM Proxy | ✅ Required | ❌ Not needed |
| Ollama | Native on Mac | Docker with GPU |
| Stream Processor | Docker | Docker |
| Alert Service | Docker | Docker |
| Frigate | Docker (CPU) | Docker (NVIDIA GPU) |
| NATS/MQTT/PostgreSQL | Docker | Docker |

## File Structure

- `compose.yaml` - Base configuration for all environments
- `compose.override.yml` - Local development overrides (auto-merged)
- `compose.prod.yml` - Production overrides (explicit: `-f compose.prod.yml`)

## Environment Variables

Critical differences:

**Local (.env):**
```bash
VLM_SERVICE_URL=http://192.168.176.1:8001  # Via proxy
OLLAMA_URL=http://localhost:11434  # Native Mac
```

**Production (.env.production):**
```bash
VLM_SERVICE_URL=http://nura-vlm:8001  # Direct Docker service
OLLAMA_URL=http://ollama:11434  # Docker service
```
