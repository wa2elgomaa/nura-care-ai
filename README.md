# NURA - AI-Powered Child Safety Monitoring

**Real-time camera violation detection for childcare centers — all data stays on-premise.**

## Core Mission

> **Monitor children 24/7 through cameras, detect violations using AI, alert administrators immediately — while keeping all video data completely offline on school servers.**

## What NURA Does

NURA is an **AI-powered safety monitoring system** that:
- 📹 **Watches cameras continuously** in classrooms, playgrounds, hallways
- 🤖 **Understands context** using Vision-Language Models (like GPT-4V)
- 📋 **Matches violations** against school policies and government regulations
- ⚡ **Alerts within 10 seconds** when rules are broken
- 🔒 **Keeps video local** — nothing leaves the school server
- 📡 **WiFi sensing** for uncovered areas (bathrooms, changing rooms)

## Architecture

```
Edge Box (On-Premise)          Cloud (Railway)
├─ Infrastructure              ├─ cloud-api (TypeScript)
│  ├─ Postgres + TimescaleDB   ├─ alert-relay (TypeScript)
│  ├─ NATS JetStream           └─ cloud-db (Postgres)
│  ├─ Mosquitto MQTT
│  ├─ Keycloak (local auth)
│  ├─ Frigate NVR
│  └─ Caddy (TLS proxy)
├─ TypeScript Services
│  ├─ nura-api (NestJS)
│  ├─ nura-ui (Next.js)
│  ├─ nura-rules (NestJS)
│  ├─ nura-notifier (NestJS)
│  └─ sync-agent (Node.js)
└─ Python Services
   ├─ nura-perception (FastAPI)
   │  ├─ YOLO person detection
   │  ├─ MediaPipe fall detection
   │  └─ ByteTrack tracking
   ├─ nura-face (FastAPI + CompreFace)
   └─ nura-analytics (FastAPI + scikit-learn)
```

**Privacy Boundary**: Only anonymized metadata crosses from edge to cloud. Raw video, face embeddings, and PII stay local.

## Quick Start

See **[QUICKSTART.md](QUICKSTART.md)** for 10-minute setup.

**TL;DR**:
```bash
# 1. Configure
cp .env.example .env
nano .env  # Change all *_PASSWORD values

# 2. Generate signing keys
mkdir -p secrets && chmod 700 secrets
openssl genpkey -algorithm ed25519 -out secrets/update_signing_key.pem
openssl pkey -in secrets/update_signing_key.pem -pubout -out secrets/update_signing_key.pub
chmod 600 secrets/update_signing_key.pem

# 3. Start everything
docker compose --env-file .env --profile app --profile sim --profile cloud --profile dev up -d

# 4. Verify
docker compose ps
curl -k https://nura.localhost:8443
```

## Documentation

| Document | Purpose |
|----------|---------|
| **[QUICKSTART.md](QUICKSTART.md)** | Get running in 10 minutes |
| **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** | System architecture overview |
| **[docs/PROJECT_SETUP.md](docs/PROJECT_SETUP.md)** | Complete setup guide |
| **[docs/SERVICE_TEMPLATE.md](docs/SERVICE_TEMPLATE.md)** | Create new microservices |
| **[docs/TECH_DECISIONS.md](docs/TECH_DECISIONS.md)** | Technology choice rationale |
| **[.speckit/constitution.md](.speckit/constitution.md)** | Core principles and governance |
| **[.speckit/PHASES.md](.speckit/PHASES.md)** | Phase rollout plan |

## Phase Roadmap

### Phase 1: Operational Core (Current)
✅ Infrastructure deployed  
⏳ Attendance tracking  
⏳ Billing automation  
⏳ Staff credential tracker  
⏳ Medication cross-check  

**No AI/ML features in Phase 1.**

### Phase 2: Edge + Safety Pilots
- Edge box hardware deployment
- Fall detection (pose estimation)
- Camera-follow tracking
- BLE zone tracking
- Offline continuity

### Phase 3: Behavioral Intelligence
- Pattern anomaly detection
- Interaction flagging (non-diagnostic)
- Activity interest profiling
- Requires clinical advisory sign-off

### Phase 4: Custom ML Models
- Fine-tuned YOLO models
- Custom audio anomaly detection
- Behavioral clustering

See [.speckit/PHASES.md](.speckit/PHASES.md) for detailed sequencing.

## Technology Stack

- **Languages**: TypeScript (Node.js 22+), Python 3.11+
- **Frameworks**: NestJS, FastAPI, Next.js 14+, React Native 0.76+
- **Data**: PostgreSQL 16 (TimescaleDB + PostGIS), Prisma ORM
- **Events**: NATS JetStream, Mosquitto MQTT
- **Auth**: Keycloak (OIDC/OAuth2)
- **CV/ML**: YOLO, MediaPipe, ByteTrack, CompreFace, Ollama (optional)
- **Deployment**: Docker Compose (edge), Railway/K8s (cloud)

## Development

### TypeScript Services
```bash
cd services/nura-api
npm install
npm run start:dev  # Hot reload
```

### Python Services
```bash
cd services/nura-perception
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

## Testing

### Verification Suite
### 3.1 Verify setup 

```bash
# Databases exist
docker compose exec postgres psql -U nura -c '\l'
# Sensor data is flowing
docker compose exec mosquitto mosquitto_sub -t 'nura/sensors/#' -C 3
# Message bus works 
docker run --rm --network nura_core_net natsio/nats-box nats -s nats://nats:4222 pub test hello
# The web entry point and Keycloak 
curl -k https://nura.localhost:8443
curl -k -I https://auth.nura.localhost:8443

# Simulated camera stream
docker run --rm --network nura_camera_net --entrypoint ffprobe \
  bluenviron/mediamtx:latest-ffmpeg rtsp://sim-cam:8554/testpattern

# Your Eufy camera
docker network connect nura_lan_net $(docker compose ps -q frigate)

#Push notifications
docker compose exec -it ntfy ntfy user add --role=admin admin
curl -k -u admin:'YOURPASS' -d "test alert" https://ntfy.nura.localhost:8443/nura-alerts
curl -k -u admin:'YOURPASS' "https://ntfy.nura.localhost:8443/nura-alerts/json?poll=1"

# Email goes to Mailpit

printf 'Subject: test\n\nhello' | docker run -i --rm --network nura_uplink_net curlimages/curl:latest \
  smtp://mailpit:1025 --mail-from a@nura.local --mail-rcpt b@nura.local -T -

# Local cloud
curl http://localhost:8082

# Offline isolation
chmod +x scripts/offline-test.sh
./scripts/offline-test.sh check
chmod +x scripts/agent.sh
scripts/agent.sh status



```

### 4. Test update signing
```bash
mkdir -p test-bundle
echo '{"rule_pack":"demo","version":1}' > test-bundle/manifest.json
tar -cf bundle.tar -C test-bundle .

# sign
openssl pkeyutl -sign -rawin -inkey secrets/update_signing_key.pem \
  -in bundle.tar -out bundle.sig

# verify the untouched bundle (expect: Signature Verified Successfully)
openssl pkeyutl -verify -rawin -pubin -inkey secrets/update_signing_key.pub \
  -in bundle.tar -sigfile bundle.sig

# tamper, then verify again (expect: Signature Verification Failure)
echo "x" >> bundle.tar
openssl pkeyutl -verify -rawin -pubin -inkey secrets/update_signing_key.pub \
  -in bundle.tar -sigfile bundle.sig

# clean up
rm -rf bundle.tar bundle.sig test-bundle
```
If a signature fails unexpectedly, the file changed after signing (including a rebuilt tar). Sign the exact bytes you ship.

### 5. Test offline mode
```bash
./scripts/offline-test.sh check   # confirm only sync-agent can reach the "internet"
./scripts/offline-test.sh down    # simulate internet loss
# run for hours: alerts, dashboard and login must keep working
./scripts/offline-test.sh up      # reconnect; queued messages should drain
```

### 6. Stop
```bash
docker compose --env-file .env --profile app --profile sim --profile cloud --profile dev down
# add -v to also delete volumes (all local data)
```