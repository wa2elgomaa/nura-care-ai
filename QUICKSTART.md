# NURA Quick Start Guide

Get the NURA development environment running in 10 minutes.

## Prerequisites

- Docker 24.0+ with Compose V2
- OpenSSL 3.x (check: `openssl version`)
- 8GB+ RAM, 20GB+ disk space

## 1. Clone & Configure (2 min)

```bash
git clone <repository-url> nura-care-source
cd nura-care-source

# Copy environment template
cp .env.example .env

# CRITICAL: Change all *_PASSWORD values in .env
nano .env  # or use your preferred editor
```

**Required changes in .env**:
- `POSTGRES_PASSWORD`
- `KEYCLOAK_ADMIN_PASSWORD`
- `CLOUD_DB_PASSWORD`
- `CLOUD_ADMIN_TOKEN`

## 2. Generate Signing Keys (1 min)

```bash
mkdir -p secrets && chmod 700 secrets
openssl genpkey -algorithm ed25519 -out secrets/update_signing_key.pem
openssl pkey -in secrets/update_signing_key.pem -pubout -out secrets/update_signing_key.pub
chmod 600 secrets/update_signing_key.pem
grep -qxF 'secrets/' .gitignore 2>/dev/null || echo 'secrets/' >> .gitignore
```

⚠️ **NEVER commit `secrets/update_signing_key.pem`** — it's your private key!

## 3. Start Everything (5 min)

```bash
# Start full stack (infrastructure + services + simulator + local cloud)
docker compose --env-file .env \
  --profile app \
  --profile sim \
  --profile cloud \
  --profile dev \
  up -d

# Wait for services to become healthy (check status)
docker compose ps
```

## 4. Verify Setup (2 min)

```bash
# Database is ready
docker compose exec postgres psql -U nura -c '\l'

# NATS is responding
docker run --rm --network nura_core_net natsio/nats-box nats -s nats://nats:4222 pub test hello

# Sensor data is flowing (simulated)
docker compose exec mosquitto mosquitto_sub -t 'nura/sensors/#' -C 3

# Web UI is accessible
curl -k https://nura.localhost:8443

# Keycloak is running
curl -k -I https://auth.nura.localhost:8443

# Cloud API is healthy (local dev)
curl http://localhost:8081/health
```

## 5. Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Main UI** | https://nura.localhost:8443 | TBD (Keycloak) |
| **Keycloak Admin** | https://auth.nura.localhost:8443/admin | From .env: `KEYCLOAK_ADMIN` |
| **Frigate NVR** | http://localhost:5000 | None (local dev) |
| **Mailpit (Email)** | http://localhost:8025 | None |
| **Cloud API** | http://localhost:8081 | None (local dev) |

## What's Running?

### Infrastructure
- PostgreSQL (TimescaleDB + PostGIS)
- NATS JetStream (event bus)
- Mosquitto (MQTT for sensors)
- Keycloak (authentication)
- Qdrant (vector database)
- ntfy (push notifications)
- Caddy (reverse proxy)

### NURA Services
- **nura-api**: Business logic API (TypeScript/NestJS)
- **nura-ui**: Admin web console (Next.js)
- **nura-perception**: Computer vision (Python/FastAPI) - *stub for now*
- **nura-sensor-adapter**: MQTT → NATS bridge (TypeScript)
- **nura-rules**: Rule engine (TypeScript)
- **nura-rag**: Document Q&A (TypeScript)
- **nura-notifier**: Multi-channel alerts (TypeScript)
- **sync-agent**: Cloud synchronization (TypeScript)

### Simulation
- **sim-cam**: Looped RTSP camera feed
- **sensor-sim**: Fake room occupancy sensor

### Local Cloud
- **cloud-api**: Device enrollment & updates (TypeScript)
- **alert-relay**: Alert fan-out (TypeScript)
- **cloud-db**: Cloud database (PostgreSQL)

## Next Steps

### For Backend Development
```bash
# Work on TypeScript service
cd services/nura-api
npm install
npm run start:dev  # Hot reload

# Work on Python service
cd services/nura-perception
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

### For Testing Offline Mode
```bash
# Verify isolation
./scripts/offline-test.sh check

# Simulate internet outage
./scripts/offline-test.sh down
# (Test UI, alerts, attendance still work)

# Restore internet
./scripts/offline-test.sh up
```

### For Exploring
- Read [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system overview
- Read [PROJECT_SETUP.md](docs/PROJECT_SETUP.md) for detailed setup
- Read [.speckit/constitution.md](.speckit/constitution.md) for core principles
- Read [.speckit/PHASES.md](.speckit/PHASES.md) for roadmap

## Stopping

```bash
# Stop all services
docker compose --profile app --profile sim --profile cloud --profile dev down

# Stop and delete ALL data (including database)
docker compose --profile app --profile sim --profile cloud --profile dev down -v
```

## Troubleshooting

### "Cannot connect to Docker daemon"
```bash
# Start Docker Desktop (macOS/Windows) or Docker service (Linux)
sudo systemctl start docker  # Linux
```

### "Port already in use"
```bash
# Check what's using the port
lsof -i :8443  # or other port number
# Stop the conflicting service or change HTTPS_PORT in .env
```

### "Service unhealthy"
```bash
# Check service logs
docker compose logs <service-name>

# Restart specific service
docker compose restart <service-name>
```

### "Permission denied" on secrets/
```bash
# Fix permissions
chmod 700 secrets/
chmod 600 secrets/update_signing_key.pem
chmod 644 secrets/update_signing_key.pub
```

## Getting Help

- **Documentation**: See [docs/](docs/) folder
- **Issues**: Check existing issues or create new one
- **Architecture Questions**: Read [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Constitution**: Read [.speckit/constitution.md](.speckit/constitution.md)

---

**Ready to build!** 🚀

For Phase 1 implementation, start with:
1. Attendance tracking service ([specs/004-attendance-absence-flags/](specs/004-attendance-absence-flags/))
2. Billing automation ([specs/005-billing-finance-automation/](specs/005-billing-finance-automation/))
3. Staff credentials ([specs/001-staff-compliance-tracker/](specs/001-staff-compliance-tracker/))

See [.speckit/PHASES.md](.speckit/PHASES.md) for mandatory delivery sequencing.
