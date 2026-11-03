# NURA Project Setup & Initialization

Complete guide for setting up the NURA development environment and initializing new phases.

## Prerequisites

### System Requirements
- **OS**: Ubuntu 22.04+, Debian 12+, or macOS 13+
- **Docker**: 24.0+ with Compose V2
- **Node.js**: 22+ (for TypeScript services)
- **Python**: 3.11+ (for Python services)
- **OpenSSL**: 3.x (for signing key generation)
- **Git**: 2.40+

### Optional (for development)
- **pnpm**: 8+ (monorepo package manager)
- **Nx**: 17+ (monorepo orchestration)
- **PostgreSQL**: 16+ (local DB client tools)

---

## Initial Setup (First Time)

### 1. Clone & Configure
```bash
git clone <repository-url> nura-care-source
cd nura-care-source

# Copy environment template
cp .env.example .env

# Edit .env and change ALL *_PASSWORD values
# CRITICAL: Change these before first run:
# - POSTGRES_PASSWORD
# - KEYCLOAK_ADMIN_PASSWORD
# - CLOUD_DB_PASSWORD
# - CLOUD_ADMIN_TOKEN
nano .env
```

### 2. Generate Signing Keys (Once)
```bash
mkdir -p secrets && chmod 700 secrets

# Generate Ed25519 keypair for update signing
openssl genpkey -algorithm ed25519 -out secrets/update_signing_key.pem
openssl pkey -in secrets/update_signing_key.pem -pubout -out secrets/update_signing_key.pub

chmod 600 secrets/update_signing_key.pem
chmod 644 secrets/update_signing_key.pub

# Ensure secrets/ is gitignored
grep -qxF 'secrets/' .gitignore 2>/dev/null || echo 'secrets/' >> .gitignore
```

**IMPORTANT**: The `.pem` file is the private signing key and MUST NEVER be committed or shared. Back it up securely offline.

### 3. Start Infrastructure
```bash
# Validate compose file
docker compose --env-file .env config -q

# Start edge infrastructure only (no NURA services yet)
docker compose --env-file .env up -d

# Check health
docker compose ps
docker compose logs -f postgres keycloak nats mosquitto
```

### 4. Verify Infrastructure
```bash
# Database exists
docker compose exec postgres psql -U nura -c '\l'

# NATS is responding
docker run --rm --network nura_core_net natsio/nats-box nats -s nats://nats:4222 pub test hello

# MQTT is accepting connections
docker compose exec mosquitto mosquitto_sub -t 'nura/sensors/#' -C 1

# Keycloak admin console (http://keycloak:8080/admin)
# Default credentials from .env: KEYCLOAK_ADMIN / KEYCLOAK_ADMIN_PASSWORD
```

### 5. Trust Local TLS (Optional)
```bash
# Export Caddy's local CA certificate
docker compose cp caddy:/data/caddy/pki/authorities/local/root.crt ./caddy-root.crt

# macOS
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain caddy-root.crt

# Linux (Debian/Ubuntu)
sudo cp caddy-root.crt /usr/local/share/ca-certificates/caddy.crt
sudo update-ca-certificates

# Now https://nura.localhost:8443 won't show certificate warnings
```

---

## Service Development Setup

### TypeScript Services (NestJS)

#### One-time setup (if using monorepo)
```bash
# Install pnpm globally
npm install -g pnpm

# Install Nx globally
npm install -g nx

# Initialize Nx workspace (future step)
# npx create-nx-workspace@latest nura-workspace --preset=nest
```

#### Per-service setup
```bash
cd services/nura-api  # or any TypeScript service

# Install dependencies
npm install  # or: pnpm install

# Build
npm run build

# Development mode
npm run start:dev

# Tests
npm test
```

### Python Services (FastAPI)

#### Per-service setup
```bash
cd services/nura-perception  # or any Python service

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Development mode
uvicorn src.main:app --reload --port 8000

# Tests
pytest
```

---

## Starting Services

### Profile Overview
- **(none)**: Core infrastructure only
- **app**: NURA-owned services (API, UI, perception, etc.)
- **sim**: Simulated school (camera + sensors)
- **ai**: Local LLM (Ollama)
- **cloud**: Local cloud services
- **dev**: Developer tools (Mailpit)

### Start Everything (Recommended for Development)
```bash
docker compose --env-file .env \
  --profile app \
  --profile sim \
  --profile cloud \
  --profile dev \
  up -d

# Check status
docker compose ps

# Follow logs
docker compose logs -f nura-api nura-perception sync-agent
```

### Start Incrementally
```bash
# 1. Infrastructure only
docker compose --env-file .env up -d

# 2. Add NURA services + simulator
docker compose --env-file .env --profile app --profile sim up -d

# 3. Add local cloud
docker compose --env-file .env --profile cloud up -d

# 4. Add dev tools
docker compose --env-file .env --profile dev up -d
```

---

## Verification Checklist

Run these after starting services:

### Infrastructure Health
```bash
# Postgres is healthy
docker compose exec postgres pg_isready -U nura

# NATS JetStream is enabled
docker run --rm --network nura_core_net natsio/nats-box \
  nats -s nats://nats:4222 stream list

# Mosquitto is receiving sensor data (with sim profile)
docker compose exec mosquitto mosquitto_sub -t 'nura/sensors/#' -C 3

# Keycloak realm is configured
curl -k https://auth.nura.localhost:8443/realms/nura/.well-known/openid-configuration
```

### Service Health
```bash
# Check all service health endpoints
for service in nura-api nura-perception nura-rules nura-notifier; do
  echo "=== $service ==="
  docker compose exec $service curl -s http://localhost:8000/health || echo "Not responding"
done

# Caddy reverse proxy
curl -k https://nura.localhost:8443

# Frigate NVR
curl -s http://localhost:5000/api/version
```

### Cloud Sync (Local)
```bash
# Cloud API is accessible
curl http://localhost:8081/health

# Sync agent can authenticate
docker compose logs sync-agent | grep -i "authenticated"
```

### Push Notifications (Local)
```bash
# Create ntfy admin user
docker compose exec -it ntfy ntfy user add --role=admin admin

# Send test notification
curl -k -u admin:'YOUR_NTFY_PASSWORD' \
  -d "Test alert from NURA" \
  https://ntfy.nura.localhost:8443/nura-alerts

# Receive notification
curl -k -u admin:'YOUR_NTFY_PASSWORD' \
  "https://ntfy.nura.localhost:8443/nura-alerts/json?poll=1"
```

### Email (Mailpit - Dev Profile)
```bash
# Send test email
printf 'Subject: Test\n\nHello from NURA' | \
docker run -i --rm --network nura_uplink_net curlimages/curl:latest \
  smtp://mailpit:1025 \
  --mail-from noreply@nura.local \
  --mail-rcpt test@nura.local \
  -T -

# Check Mailpit UI: http://localhost:8025
```

---

## Testing Offline Mode

```bash
# Verify only sync-agent can reach "internet"
./scripts/offline-test.sh check

# Simulate internet outage
./scripts/offline-test.sh down

# Test operations (should still work):
# - Login to web UI
# - View dashboard
# - Create attendance record
# - Receive local alerts

# Restore internet
./scripts/offline-test.sh up

# Verify queued events drain
docker compose logs sync-agent | grep -i "queue"
```

---

## Testing Update Signing

```bash
# Create test bundle
mkdir -p test-bundle
echo '{"rule_pack":"demo","version":2}' > test-bundle/manifest.json
tar -cf bundle.tar -C test-bundle .

# Sign bundle
openssl pkeyutl -sign -rawin \
  -inkey secrets/update_signing_key.pem \
  -in bundle.tar \
  -out bundle.sig

# Verify signature (should say "Signature Verified Successfully")
openssl pkeyutl -verify -rawin -pubin \
  -inkey secrets/update_signing_key.pub \
  -in bundle.tar \
  -sigfile bundle.sig

# Tamper with bundle (should fail verification)
echo "tampered" >> bundle.tar
openssl pkeyutl -verify -rawin -pubin \
  -inkey secrets/update_signing_key.pub \
  -in bundle.tar \
  -sigfile bundle.sig
# Expected: "Signature Verification Failure"

# Cleanup
rm -rf test-bundle bundle.tar bundle.sig
```

---

## Phase Rollout Checklist

### Phase 1: Operational Core (Must Ship First)
- [ ] Attendance tracking service implemented
- [ ] Billing automation service implemented
- [ ] Staff credential tracker implemented
- [ ] Medication cross-check implemented
- [ ] **NO AI/ML behavioral features enabled**
- [ ] Web admin console operational
- [ ] Mobile apps (parent/teacher/director) deployed
- [ ] Pilot site onboarded
- [ ] Daily usage metrics tracked

**Gate**: Operational core shows daily staff usage in pilot cohort.

### Phase 2: Edge + Safety Pilots
- [ ] Phase 1 fully operational and adopted
- [ ] Edge box hardware deployed to pilot sites
- [ ] Frigate NVR configured and recording
- [ ] nura-perception service: YOLO detection working
- [ ] nura-perception service: Fall detection (MediaPipe) working
- [ ] Camera-follow tracking operational
- [ ] BLE zone tracking (ESPresense) deployed
- [ ] Offline continuity tested (24+ hour internet outage)
- [ ] Alert false-positive rate measured

**Gate**: Incident false-alert rate below 5%.

### Phase 3: Behavioral Intelligence
- [ ] Phase 2 safety pilots complete
- [ ] Clinical advisory board sign-off obtained
- [ ] Pattern anomaly detection (non-diagnostic) implemented
- [ ] Interaction flagging (staff-facing only) implemented
- [ ] Activity interest profiling implemented
- [ ] Biometric opt-in rate measured in pilots

**Gate**: Biometric opt-in rate above 50%, or consent UX redesigned.

### Phase 4: Custom ML Models
- [ ] Phase 3 production evidence collected
- [ ] Fine-tuned YOLO models trained on site-specific data
- [ ] Custom audio anomaly models (if needed)
- [ ] Behavioral clustering models
- [ ] Model performance validated in controlled pilots

**Gate**: Product, engineering, and compliance stakeholder approval.

---

## Development Workflow

### Daily Development
```bash
# Start services
docker compose --env-file .env --profile app --profile sim up -d

# Work on a service (TypeScript example)
cd services/nura-api
npm run start:dev  # Hot reload

# Work on a service (Python example)
cd services/nura-perception
source .venv/bin/activate
uvicorn src.main:app --reload

# Watch logs
docker compose logs -f nura-api nura-perception

# Stop services
docker compose down
```

### Making Changes
```bash
# Create feature branch
git checkout -b feature/new-alert-rule

# Make changes to service code
# ...

# Rebuild service image
docker compose build nura-rules

# Restart service
docker compose up -d nura-rules

# Test changes
curl http://localhost:3000/health

# Commit
git add .
git commit -m "Add new alert rule for occupancy threshold"
git push origin feature/new-alert-rule
```

### Database Migrations (Future with Prisma)
```bash
# Generate migration
cd services/nura-api
npx prisma migrate dev --name add_alert_rules_table

# Apply migration to running DB
docker compose exec -e DATABASE_URL="postgresql://nura:PASSWORD@postgres:5432/nura" \
  nura-api npx prisma migrate deploy
```

---

## Troubleshooting

### Services won't start
```bash
# Check logs
docker compose logs <service-name>

# Check environment variables
docker compose config

# Verify dependencies are healthy
docker compose ps
```

### Database connection errors
```bash
# Check Postgres is running
docker compose ps postgres

# Check credentials match .env
docker compose exec postgres psql -U nura -d nura
```

### NATS not connecting
```bash
# Check NATS is running
docker compose ps nats

# Test NATS connection
docker run --rm --network nura_core_net natsio/nats-box \
  nats -s nats://nats:4222 pub test hello
```

### Frigate not detecting
```bash
# Check Frigate logs
docker compose logs frigate

# Check camera stream
docker run --rm --network nura_camera_net --entrypoint ffprobe \
  bluenviron/mediamtx:latest-ffmpeg rtsp://frigate:8554/<camera_name>

# Check Frigate config
docker compose exec frigate cat /config/config.yml
```

### Offline mode not working
```bash
# Verify network isolation
./scripts/offline-test.sh check

# Check sync-agent is the only service with internet access
docker inspect nura-sync-agent | jq '.[0].NetworkSettings.Networks | keys'
# Should show: ["nura_core_net", "nura_uplink_net"]
```

---

## Cleanup

### Remove all containers and volumes
```bash
# Stop everything
docker compose --profile app --profile sim --profile cloud --profile dev down

# Remove volumes (DELETES ALL DATA)
docker compose --profile app --profile sim --profile cloud --profile dev down -v

# Remove images
docker compose --profile app --profile sim --profile cloud --profile dev down --rmi all
```

### Reset to clean state
```bash
# Full cleanup
docker compose down -v --rmi all
rm -rf caddy-root.crt bundle.tar bundle.sig test-bundle/

# Keep secrets (DO NOT DELETE IN PRODUCTION)
# rm -rf secrets/

# Restart fresh
docker compose --env-file .env up -d
```

---

## Next Steps

1. ✅ Initial setup complete
2. ⏳ Initialize Nx monorepo for TypeScript services
3. ⏳ Implement Phase 1 operational core services
4. ⏳ Deploy pilot site
5. ⏳ Measure adoption metrics
6. ⏳ Plan Phase 2 edge rollout

---

## References

- [Architecture Overview](./ARCHITECTURE.md)
- [Service Template](./SERVICE_TEMPLATE.md)
- [NURA Constitution](../.speckit/constitution.md)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [NestJS Documentation](https://nestjs.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
