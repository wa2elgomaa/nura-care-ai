# NURA Architecture Overview

**Version**: 1.0.0  
**Last Updated**: 2026-11-03  
**Status**: Active Development

## Executive Summary

NURA is a privacy-first, edge-computing childcare safety and compliance platform combining TypeScript and Python microservices. The architecture enforces **privacy by default** through edge-first inference, where all raw video and biometric data remains on-premise while only anonymized metadata reaches the cloud.

## Architecture Principles

### 1. Privacy by Default & Edge-First
- Raw video and facial embeddings **NEVER** leave the edge box
- All person detection, facial matching, fall detection runs locally
- Cloud receives only anonymized operational metadata

### 2. Language Selection by Best Fit
- **TypeScript/Node.js**: API services, business logic, web/mobile apps, real-time coordination
- **Python**: Computer vision, ML inference, sensor processing, data science workloads
- **Go** (future): High-performance stream processing if needed

### 3. Offline-First Safety
- Edge box operates independently during internet outages
- Attendance, pickup verification, alerts continue without cloud
- Sync queues buffer and replay when connectivity restored

### 4. Event-Driven Microservices
- NATS JetStream for internal event bus
- MQTT for sensor ingestion
- Services communicate via events, not direct calls

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLOUD (Railway)                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Cloud API   │  │ Alert Relay  │  │  Cloud DB    │         │
│  │ (TypeScript) │  │ (TypeScript) │  │ (Postgres)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         │                  │                  │                 │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
    INTERNET BOUNDARY (uplink_net)
          │                  │                  │
┌─────────┼──────────────────┼──────────────────┼─────────────────┐
│         ▼                  ▼                  ▼                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Sync Agent (TypeScript)                     │  │
│  │  - Device authentication & enrollment                    │  │
│  │  - Event queue buffering & replay                        │  │
│  │  - Signed update verification & installation             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                   EDGE BOX (core_net)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         Infrastructure Services                         │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ • Postgres (TimescaleDB + PostGIS)                      │   │
│  │ • NATS JetStream (event bus)                            │   │
│  │ • Mosquitto MQTT (sensors)                              │   │
│  │ • Keycloak (local auth)                                 │   │
│  │ • Qdrant (vector store)                                 │   │
│  │ • ntfy (push notifications)                             │   │
│  │ • Caddy (TLS reverse proxy)                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         TypeScript Services (NestJS)                    │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ • nura-api: REST/GraphQL gateway, business logic        │   │
│  │ • nura-ui: Admin web console                            │   │
│  │ • nura-sensor-adapter: MQTT → NATS bridge              │   │
│  │ • nura-rules: Rule engine, alert orchestration          │   │
│  │ • nura-rag: Document/policy Q&A with embeddings         │   │
│  │ • nura-notifier: Multi-channel notification dispatch    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         Python Services (FastAPI/Uvicorn)               │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ • nura-perception:                                      │   │
│  │   - YOLO person/object detection                        │   │
│  │   - MediaPipe pose estimation (fall detection)          │   │
│  │   - ByteTrack multi-object tracking (camera-follow)     │   │
│  │   - Reads from Frigate restream                         │   │
│  │                                                           │   │
│  │ • nura-face:                                            │   │
│  │   - CompreFace integration (pickup verification)        │   │
│  │   - Local face embedding storage                        │   │
│  │   - Parent consent enforcement                          │   │
│  │                                                           │   │
│  │ • nura-analytics:                                       │   │
│  │   - Time-series aggregation (TimescaleDB)              │   │
│  │   - Anomaly detection (noise, occupancy)               │   │
│  │   - Report generation                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         Edge Infrastructure (camera_net/sensor_net)     │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ • Frigate NVR: Local NVR + object detection             │   │
│  │ • Ollama: Local LLM runtime (optional)                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│              ┌─────────────────────────┐                        │
│              │  Cameras + BLE Sensors  │                        │
│              └─────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Service Catalog

### TypeScript Services (NestJS)

#### nura-api
- **Purpose**: Main business logic API gateway
- **Tech**: NestJS, Prisma ORM, GraphQL (optional)
- **Responsibilities**:
  - Attendance tracking
  - Enrollment management
  - Staff credential tracking
  - Billing operations
  - Parent/teacher/director role-based endpoints
- **Dependencies**: Postgres, NATS, Keycloak

#### nura-ui
- **Purpose**: Web admin console
- **Tech**: Next.js 14+, shadcn/ui, Tailwind, NativeWind
- **Responsibilities**:
  - Director dashboard
  - Staff management
  - Compliance reporting
  - Real-time alerts display
- **Dependencies**: nura-api

#### nura-sensor-adapter
- **Purpose**: Sensor data ingestion bridge
- **Tech**: NestJS, MQTT.js
- **Responsibilities**:
  - MQTT → NATS event translation
  - RuView/ESP32 sensor integration
  - BLE zone tracking (ESPresense)
  - Occupancy counting
- **Dependencies**: Mosquitto, NATS

#### nura-rules
- **Purpose**: Rule engine and alert orchestration
- **Tech**: NestJS, json-rules-engine (or custom)
- **Responsibilities**:
  - Rule pack management (loaded from bundles)
  - VLM verification client (optional Ollama integration)
  - Alert threshold evaluation
  - Escalation workflow
- **Dependencies**: NATS, Ollama (optional)

#### nura-rag
- **Purpose**: Document/policy retrieval-augmented generation
- **Tech**: NestJS, LangChain.js
- **Responsibilities**:
  - Clause-aware policy ingestion
  - Embedding generation (via Ollama or API)
  - Vector search (Qdrant)
  - Compliance Q&A
- **Dependencies**: Qdrant, Ollama (optional)

#### nura-notifier
- **Purpose**: Multi-channel notification dispatch
- **Tech**: NestJS
- **Responsibilities**:
  - Severity-based routing
  - Push notifications (ntfy)
  - Email/SMS (Apprise)
  - Escalation tracking
  - Acknowledgment workflow
- **Dependencies**: ntfy, Apprise, NATS

#### sync-agent
- **Purpose**: Cloud synchronization gateway
- **Tech**: Node.js (vanilla TypeScript)
- **Responsibilities**:
  - Device enrollment & authentication
  - Event queue buffering during offline
  - Signed update verification (Ed25519)
  - Rule pack installation
- **Dependencies**: Cloud API, NATS

---

### Python Services (FastAPI)

#### nura-perception
- **Purpose**: Computer vision perception pipeline
- **Tech**: FastAPI, OpenCV, Ultralytics YOLO, MediaPipe, ByteTrack
- **Responsibilities**:
  - Real-time person/object detection (YOLO)
  - Pose estimation for fall detection (MediaPipe)
  - Multi-object tracking for camera-follow (ByteTrack)
  - Privacy-preserving metadata extraction
  - Publishes anonymized events to NATS
- **Hardware**: Coral TPU or NVIDIA GPU (via compose.gpu.yaml)
- **Input**: RTSP streams from Frigate restream
- **Output**: JSON events to NATS (no raw video/images)
- **Dependencies**: Frigate, NATS

#### nura-face
- **Purpose**: Face recognition and verification (biometric opt-in only)
- **Tech**: FastAPI, CompreFace (REST client)
- **Responsibilities**:
  - Pickup guardian verification
  - Face embedding storage (local only, 7-day retention)
  - Parent consent enforcement
  - Biometric data lifecycle management
- **Privacy**: All embeddings stored locally, never sent to cloud
- **Dependencies**: CompreFace (separate container), Postgres, NATS

#### nura-analytics
- **Purpose**: Time-series analytics and anomaly detection
- **Tech**: FastAPI, Pandas, NumPy, Scikit-learn
- **Responsibilities**:
  - Occupancy trend analysis (TimescaleDB continuous aggregates)
  - Noise spike detection
  - Attendance pattern anomalies
  - Automated report generation (PDF via ReportLab)
- **Dependencies**: Postgres (TimescaleDB), NATS

---

## Technology Stack

### Core Languages
- **TypeScript**: Business logic, APIs, web/mobile frontends
- **Python**: Computer vision, ML inference, data analytics
- **SQL**: Postgres (TimescaleDB + PostGIS extensions)

### Frameworks
- **NestJS**: TypeScript microservices framework (event-driven, DI, decorators)
- **FastAPI**: Python async web framework (auto OpenAPI docs)
- **Next.js 14+**: React framework for web admin (App Router, Server Components)
- **React Native 0.76+**: Mobile apps for parents/teachers/directors

### Infrastructure
- **Docker Compose**: Edge box orchestration (dev + production)
- **PostgreSQL 16**: Primary database with TimescaleDB + PostGIS extensions
- **NATS JetStream**: Event bus for inter-service messaging
- **Mosquitto**: MQTT broker for sensor ingestion
- **Keycloak**: SSO and RBAC (Cloud + Edge instances)
- **Qdrant**: Vector database for RAG embeddings
- **Caddy 2**: TLS reverse proxy with auto HTTPS

### Computer Vision Stack (Python)
- **Frigate NVR**: Local video management + object detection
- **Ultralytics YOLO (v8/v11)**: Real-time person/object detection
- **MediaPipe Pose**: Skeletal keypoint extraction (fall detection)
- **ByteTrack**: Multi-object tracking
- **CompreFace**: Self-hosted face recognition (Apache 2.0)
- **InsightFace**: Underlying face embedding models

### AI/ML (Optional)
- **Ollama**: Local LLM runtime (VLM verification, RAG)
- **Models**: LLaMA 3.2, Mistral, or similar open-source models

### Frontend
- **shadcn/ui**: Copy-paste React components (web admin)
- **gluestack-ui v3**: Cross-platform components (web + React Native)
- **NativeWind**: Tailwind for React Native
- **Lucide Icons**: Icon library
- **Recharts**: Data visualization

### ORM & Data Access
- **Prisma**: Default ORM (schema-first, type-safe)
- **Raw SQL**: PostGIS/TimescaleDB queries where needed

### Monorepo (Future)
- **Nx**: Monorepo orchestration (project graph, enforced boundaries, affected commands)
- **pnpm**: Package manager with workspace support

---

## Network Topology

### Edge Networks (Docker Compose)

| Network | Purpose | Internet Access | Services |
|---------|---------|----------------|----------|
| `lan_net` | Staff devices → Caddy | Yes (dev) | Caddy |
| `core_net` | Service-to-service | No (internal) | All NURA services, Postgres, NATS, Keycloak |
| `camera_net` | Cameras → Frigate | No (internal) | Frigate, sim-cam |
| `sensor_net` | Sensors → Mosquitto | No (internal) | Mosquitto, sensor-sim, RuView |
| `uplink_net` | Sync Agent → Cloud | Yes | sync-agent, cloud-api (local dev only) |
| `cloud_net` | Cloud services | No (internal) | cloud-api, cloud-db, alert-relay |

**Key Isolation Rule**: Only `sync-agent` has access to both `core_net` and `uplink_net`, enforcing the privacy boundary.

---

## Data Flow Examples

### 1. Fall Detection Alert
```
Camera (RTSP) 
  → Frigate (restream) 
  → nura-perception (YOLO + MediaPipe) 
  → NATS event: {type: "fall_detected", zone: "room3", confidence: 0.92}
  → nura-rules (evaluates severity) 
  → nura-notifier (dispatches to ntfy + Apprise)
  → sync-agent (buffers anonymized alert metadata)
  → Cloud API (stores for compliance reporting)
```

**Privacy Check**: No video frames or face embeddings leave the edge box. Only `{zone, timestamp, alert_type, confidence}` sent to cloud.

### 2. Pickup Verification (Biometric)
```
Guardian arrives (camera frame)
  → Frigate (motion trigger)
  → nura-perception (person detected)
  → nura-face (CompreFace REST API)
  → Match result → nura-api (checks consent + authorized guardian list)
  → nura-ui (displays verification status to staff)
  → NATS event: {type: "pickup_verified", child_id: "...", timestamp: "..."}
  → sync-agent (logs event, no embedding data)
```

**Privacy Check**: Face embeddings stored in CompreFace local DB only. Consent enforced before processing.

### 3. BLE Zone Occupancy
```
BLE beacon (ESP32 + ESPresense)
  → Mosquitto (MQTT topic: nura/sensors/room3/occupancy)
  → nura-sensor-adapter (MQTT subscriber)
  → NATS event: {zone: "room3", count: 5, timestamp: 1699000000}
  → nura-analytics (stores in TimescaleDB)
  → nura-rules (checks ratio compliance)
  → nura-ui (real-time dashboard update)
```

---

## Deployment Models

### Edge Box (Docker Compose)
- **Hardware**: Mini PC (Intel NUC or similar) with Coral TPU or NVIDIA GPU
- **OS**: Ubuntu Server 22.04+ or Debian 12+
- **Orchestration**: Docker Compose with profiles
- **Storage**: 512GB+ SSD (Frigate recordings, Postgres, model weights)
- **Network**: 3+ VLANs (staff, cameras, sensors) + internet uplink

### Cloud (Railway or Kubernetes)
- **Services**: cloud-api, alert-relay, cloud-db
- **Database**: Managed Postgres (Neon, Supabase, or Railway Postgres)
- **Scaling**: Horizontal (stateless services) + read replicas (DB)
- **Regions**: US, EU, GCC (data residency compliance)

---

## Security & Compliance

### Authentication
- **Edge Keycloak**: Local staff/director authentication (survives offline)
- **Cloud Keycloak**: Parent/regional manager authentication
- **Sync**: Edge Keycloak pulls user/role updates from Cloud Keycloak every 5 minutes

### Data Retention
- **Face Embeddings**: 7-day default (edge only), configurable with consent
- **Video Recordings**: 14-day default (edge only), configurable
- **Event Metadata**: 90-day default (cloud), region-specific auto-delete
- **Audit Logs**: Immutable, 7-year retention

### Privacy Enforcement
- **No Raw Video to Cloud**: Enforced at sync-agent egress policy layer
- **Consent Gates**: nura-face blocks biometric processing without verified parental consent
- **Anonymization**: All cloud events stripped of PII/biometric data
- **Audit Trail**: Every data access, consent change, role escalation logged

### Update Security
- **Signed Bundles**: All edge updates (rule packs, model weights) signed with Ed25519
- **Verification**: sync-agent verifies signature before installation
- **Rollback**: Previous bundle retained for emergency rollback

---

## Phase Rollout (per Constitution)

### Phase 1: Operational Core (MUST ship first)
- Attendance tracking
- Billing automation
- Staff credential tracker
- Medication cross-check
- **No AI/ML behavioral features**

### Phase 2: Edge + Safety Pilots (requires Phase 1 live)
- Edge box rollout
- Camera-follow (person tracking)
- Fall detection (pose estimation)
- BLE zone tracking
- Offline continuity

### Phase 3: Behavioral Intelligence (requires clinical sign-off)
- Pattern anomaly detection
- Interaction flagging (non-diagnostic)
- Activity interest profiling

### Phase 4: Custom ML Models (requires Phase 3 evidence)
- Fine-tuned YOLO models
- Custom audio anomaly models
- Behavioral clustering

---

## Development Workflow

### Local Development
```bash
# Start edge infrastructure only
docker compose --env-file .env up -d

# Add NURA services + simulator
docker compose --env-file .env --profile app --profile sim up -d

# Add local cloud + dev tools
docker compose --env-file .env --profile cloud --profile dev up -d

# All profiles at once
docker compose --env-file .env --profile app --profile sim --profile cloud --profile dev up -d
```

### Service Development (TypeScript example)
```bash
cd services/nura-api
pnpm install
pnpm build
pnpm test
docker build -t nura/api:dev .
```

### Service Development (Python example)
```bash
cd services/nura-perception
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
docker build -t nura/perception:dev .
```

---

## Open Source Components

### Video & Vision
- [Frigate NVR](https://frigate.video) (MIT)
- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) (AGPL-3.0)
- [MediaPipe](https://github.com/google/mediapipe) (Apache 2.0)
- [ByteTrack](https://github.com/ifzhang/ByteTrack) (MIT)
- [CompreFace](https://github.com/exadel-inc/CompreFace) (Apache 2.0)

### Infrastructure
- [Keycloak](https://www.keycloak.org) (Apache 2.0)
- [Qdrant](https://qdrant.tech) (Apache 2.0)
- [NATS](https://nats.io) (Apache 2.0)
- [Mosquitto](https://mosquitto.org) (EPL/EDL)
- [Caddy](https://caddyserver.com) (Apache 2.0)

### Sensors
- [ESPresense](https://espresense.com) (MIT)

---

## Next Steps

1. ✅ Document architecture
2. ⏳ Initialize Nx monorepo (TypeScript services)
3. ⏳ Scaffold Python service templates (FastAPI + Docker)
4. ⏳ Update compose.yaml with proper service definitions
5. ⏳ Create shared type definitions (Prisma schema, NATS event types)
6. ⏳ Implement core NATS event contracts
7. ⏳ Build nura-perception MVP (YOLO + MediaPipe)

---

## References

- [NURA Constitution](.speckit/constitution.md) - Core principles and governance
- [Edge Private Video Metadata Spec](../specs/008-edge-private-video-metadata/spec.md) - Privacy-preserving architecture
- [Offline Continuity Spec](../specs/015-edge-offline-continuity/) - Edge resilience design
- [Fall Detection Spec](../specs/013-edge-fall-stillness-alerts/) - Pose-based safety alerts

---

**Document Owner**: Engineering Team  
**Review Cycle**: Every sprint during Phase 1-2, quarterly thereafter  
**Approval**: Product, Engineering, Compliance stakeholders
