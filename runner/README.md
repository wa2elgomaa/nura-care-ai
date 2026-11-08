# Nura Service Runners

Individual scripts to run each Nura service independently for local development.

## Quick Start

```bash
# Start Ollama (LLM backend)
./runner/run_ollama.sh

# Start VLM Service (AI analysis)
./runner/run_vlm_service.sh

# Start Enrollment API (optional - face identification)
./runner/run_enrollment_api.sh

# Stop all services
./runner/stop_services.sh

# Stop individual service
./runner/stop_services.sh vlm
./runner/stop_services.sh enrollment
./runner/stop_services.sh ollama
```

## Scripts

### 1. `run_ollama.sh`
Starts Ollama with GPU acceleration (Metal on Mac, CUDA on Linux).
- **Port:** 11434
- **Model:** qwen3-vl:8b-instruct (auto-downloads if missing)
- **Logs:** `/tmp/ollama.log`
- **Stop:** `killall ollama` or `./runner/stop_services.sh ollama`

### 2. `run_vlm_service.sh`
Starts the VLM (Vision-Language Model) service for AI scene analysis.
- **Port:** 8001 (configurable via `.env` → `VLM_SERVICE_PORT`)
- **Prerequisites:** Ollama running on port 11434
- **Dependencies:** Auto-creates Python venv and installs packages
- **Logs:** `logs/vlm-service.log`
- **PID:** Saved to `.vlm.pid`
- **Stop:** `kill $(cat .vlm.pid)` or `./runner/stop_services.sh vlm`

**Environment Variables (from `.env`):**
- `OLLAMA_URL` - Default: `http://localhost:11434`
- `VLM_MODEL` - Default: `qwen3-vl:8b-instruct`
- `VLM_SERVICE_PORT` - Default: `8001`
- `ENABLE_TEMPORAL_DETECTION` - Violence detection
- `ENABLE_PERSON_TRACKING` - Person tracking
- `ENABLE_FACE_IDENTIFICATION` - Face recognition

### 3. `run_enrollment_api.sh`
Starts the enrollment API for face identification (Phase 4B).
- **Port:** 8002 (configurable via `.env` → `ENROLLMENT_API_PORT`)
- **UI:** `http://localhost:8002/static/enrollment.html`
- **Prerequisites:** 
  - VLM service venv created
  - PostgreSQL running (for face embeddings)
  - `.env` → `ENABLE_FACE_IDENTIFICATION=true`
- **Logs:** `logs/enrollment-api.log`
- **PID:** Saved to `.enrollment.pid`
- **Stop:** `kill $(cat .enrollment.pid)` or `./runner/stop_services.sh enrollment`

### 4. `stop_services.sh`
Stops all or specific Nura services.

```bash
# Stop all
./runner/stop_services.sh

# Stop specific service
./runner/stop_services.sh vlm
./runner/stop_services.sh enrollment
./runner/stop_services.sh ollama
```

## Typical Workflow

### For VLM Development/Testing:
```bash
# 1. Start Ollama (LLM backend)
./runner/run_ollama.sh

# 2. Start VLM service
./runner/run_vlm_service.sh

# 3. Test it
curl http://localhost:8001/health

# 4. View logs
tail -f logs/vlm-service.log

# 5. When done
./runner/stop_services.sh
```

### For Full System (with Face ID):
```bash
# 1. Start PostgreSQL (Docker)
docker compose up -d postgres

# 2. Start Ollama
./runner/run_ollama.sh

# 3. Start VLM service
./runner/run_vlm_service.sh

# 4. Start Enrollment API
./runner/run_enrollment_api.sh

# 5. Enroll people
open http://localhost:8002/static/enrollment.html

# 6. When done
./runner/stop_services.sh
docker compose down postgres
```

## Why Use These Instead of Docker?

✅ **Faster iteration** - No rebuild on code changes  
✅ **Better debugging** - Direct access to Python debugger  
✅ **Native performance** - Metal GPU on Mac (100x faster than CPU)  
✅ **Easier development** - Edit code and restart quickly  

Docker is still recommended for:
- Production deployment
- Full end-to-end testing
- Edge device simulation

## Environment Configuration

All services read from `.env` in the project root. Key variables:

```bash
# AI Services
OLLAMA_URL=http://localhost:11434
VLM_SERVICE_URL=http://localhost:8001

# Feature Flags
ENABLE_TEMPORAL_DETECTION=true
ENABLE_PERSON_TRACKING=true
ENABLE_FACE_IDENTIFICATION=true

# Database (for enrollment API)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=nura_db
POSTGRES_USER=nura
POSTGRES_PASSWORD=PaSSw0rd!
```

## Troubleshooting

**VLM service won't start:**
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check Python venv
ls -la services/nura-vlm/.venv

# View detailed logs
tail -f logs/vlm-service.log
```

**Enrollment API fails:**
```bash
# Check PostgreSQL is running
docker compose ps postgres

# Check database connection
psql -h localhost -U nura -d nura_db

# Check ENABLE_FACE_IDENTIFICATION
grep ENABLE_FACE_IDENTIFICATION .env
```

**Port conflicts:**
```bash
# Find what's using a port
lsof -i :8001
lsof -i :8002
lsof -i :11434

# Kill specific process
kill $(lsof -t -i:8001)
```
