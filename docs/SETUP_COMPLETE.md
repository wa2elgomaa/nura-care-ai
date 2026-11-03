# NURA Project Setup - Complete ✅

**Date**: 2026-11-03  
**Status**: Ready for Phase 1 Development

## What Was Done

### 1. Architecture Documentation ✅
Created comprehensive architecture documentation combining Python + TypeScript microservices:

- **[docs/ARCHITECTURE.md](ARCHITECTURE.md)**: Complete system architecture
  - Multi-language service strategy (TypeScript + Python)
  - Network topology and data flow
  - Service catalog with technology choices
  - Phase rollout plan
  - Privacy enforcement patterns

### 2. Python Service Templates ✅
Created standardized Python service scaffolding:

- **services/nura-perception/**: Computer vision service (FastAPI)
  - Dockerfile with OpenCV dependencies
  - requirements.txt with YOLO, MediaPipe, NATS
  - Structured FastAPI application
  - Health check endpoint
  - README with setup instructions

- **Template for future Python services**:
  - nura-face (face recognition)
  - nura-analytics (time-series analytics)

### 3. Configuration Updates ✅

- **Updated compose.yaml**: 
  - nura-perception now builds from local Dockerfile
  - Proper dependencies (Frigate, NATS)
  - Environment variable configuration
  - Network assignments (core_net + camera_net)

- **Updated .speckit/constitution.md**:
  - Added multi-language mandate
  - Clarified language selection criteria
  - Updated edge inference stack description
  - Added NATS JetStream requirement

### 4. Phase Planning ✅

- **[.speckit/PHASES.md](.speckit/PHASES.md)**: Mandatory delivery sequencing
  - Phase 1: Operational Core (attendance, billing, credentials, medication)
  - Phase 2: Edge + Safety Pilots (fall detection, camera-follow, BLE)
  - Phase 3: Behavioral Intelligence (clinical sign-off required)
  - Phase 4: Custom ML Models (stakeholder approval required)

### 5. Developer Documentation ✅

- **[QUICKSTART.md](../QUICKSTART.md)**: 10-minute setup guide
- **[docs/PROJECT_SETUP.md](PROJECT_SETUP.md)**: Comprehensive setup and troubleshooting
- **[docs/SERVICE_TEMPLATE.md](SERVICE_TEMPLATE.md)**: Templates for creating new services
- **[docs/TECH_DECISIONS.md](TECH_DECISIONS.md)**: Technology choice rationale
- **Updated README.md**: Clear project overview and links

## Architecture Highlights

### Language Selection Strategy
- **TypeScript**: APIs, business logic, web/mobile apps, coordination
- **Python**: Computer vision, ML inference, analytics, data science
- **Communication**: NATS JetStream event bus (language-agnostic)

### Privacy-First Design
- Raw video stays on edge (Frigate NVR)
- Face embeddings local only (CompreFace)
- Only anonymized metadata reaches cloud
- Offline-first operation (sync-agent buffers during outages)

### Event-Driven Architecture
```
Camera → Frigate → nura-perception (Python)
                      ↓ (NATS event)
                   nura-rules (TypeScript)
                      ↓ (NATS event)
                   nura-notifier (TypeScript)
                      ↓
                   sync-agent → Cloud
```

### Technology Stack
| Component | Technology | Language |
|-----------|-----------|----------|
| Business API | NestJS | TypeScript |
| Computer Vision | YOLO + MediaPipe | Python |
| Web Admin | Next.js 14 + shadcn/ui | TypeScript |
| Mobile Apps | React Native + NativeWind | TypeScript |
| Analytics | FastAPI + scikit-learn | Python |
| Event Bus | NATS JetStream | - |
| Database | Postgres + TimescaleDB + PostGIS | - |
| NVR | Frigate | - |
| Auth | Keycloak | - |

## Project Structure

```
nura-care-source/
├── .speckit/
│   ├── constitution.md      # Core principles and governance
│   └── PHASES.md            # Phase rollout plan
├── docs/
│   ├── ARCHITECTURE.md      # System architecture
│   ├── PROJECT_SETUP.md     # Setup guide
│   ├── SERVICE_TEMPLATE.md  # Service templates
│   ├── TECH_DECISIONS.md    # Technology rationale
│   └── SETUP_COMPLETE.md    # This file
├── services/
│   ├── cloud-api/           # Cloud API (TypeScript)
│   ├── sync-agent/          # Edge-cloud sync (TypeScript)
│   ├── nura-perception/     # Computer vision (Python) ✨ NEW
│   ├── nura-face/           # Face recognition (Python) 📋 TODO
│   └── nura-analytics/      # Analytics (Python) 📋 TODO
├── specs/                   # Feature specifications (001-021)
├── edge/                    # Edge box configs (Caddy, Frigate, etc.)
├── scripts/                 # Helper scripts
├── QUICKSTART.md            # Quick start guide
├── README.md                # Project overview
├── compose.yaml             # Docker Compose orchestration
└── .env                     # Environment configuration
```

## Next Steps for Development

### Immediate (Phase 1 - Week 1-2)
1. **Initialize Nx Monorepo** (TypeScript services)
   ```bash
   npx create-nx-workspace@latest nura-workspace --preset=nest
   # Or migrate existing services into Nx
   ```

2. **Implement nura-api Core Features**:
   - [ ] Attendance tracking endpoints
   - [ ] Billing calculation logic
   - [ ] Staff credential CRUD
   - [ ] Medication log endpoints

3. **Implement nura-ui Admin Console**:
   - [ ] Director dashboard
   - [ ] Attendance view
   - [ ] Staff management
   - [ ] Billing reports

### Near-Term (Phase 1 - Week 3-4)
4. **Database Schema** (Prisma):
   - [ ] Define schema.prisma
   - [ ] Create initial migration
   - [ ] Seed dev data

5. **NATS Event Contracts**:
   - [ ] Define event schemas (TypeScript interfaces)
   - [ ] Create shared types package
   - [ ] Document event flow

6. **Testing**:
   - [ ] Unit tests for business logic
   - [ ] Integration tests for APIs
   - [ ] E2E tests for critical flows

### Mid-Term (Phase 2 - Month 2-3)
7. **Implement nura-perception MVP**:
   - [ ] YOLO person detection loop
   - [ ] MediaPipe pose estimation
   - [ ] ByteTrack integration
   - [ ] NATS event publishing
   - [ ] Frigate restream ingestion

8. **Edge Deployment**:
   - [ ] Test on target hardware (Mini PC + Coral TPU)
   - [ ] Network segmentation setup
   - [ ] Offline continuity testing

### Long-Term (Phase 3+ - Month 4+)
9. **Implement nura-face**:
   - [ ] CompreFace integration
   - [ ] Consent enforcement
   - [ ] Pickup verification workflow

10. **Implement nura-analytics**:
    - [ ] TimescaleDB continuous aggregates
    - [ ] Anomaly detection algorithms
    - [ ] Report generation

## Development Workflow

### Start Development Environment
```bash
# Full stack
docker compose --env-file .env \
  --profile app --profile sim --profile cloud --profile dev up -d

# Watch logs
docker compose logs -f nura-api nura-perception sync-agent
```

### Work on TypeScript Service
```bash
cd services/nura-api
npm install
npm run start:dev  # Hot reload
```

### Work on Python Service
```bash
cd services/nura-perception
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

### Rebuild Service After Changes
```bash
docker compose build nura-perception
docker compose up -d nura-perception
```

## Constitution Compliance Checklist

- ✅ **Privacy by Default**: Edge-first architecture documented
- ✅ **Language Selection**: Best-fit criteria defined
- ✅ **Phase Sequencing**: Mandatory phases documented
- ✅ **Technology Stack**: NestJS, FastAPI, React Native, Keycloak specified
- ✅ **Data Layer**: Postgres + TimescaleDB + PostGIS + Prisma
- ✅ **Edge Inference**: Frigate + YOLO + MediaPipe + CompreFace
- ✅ **Event Bus**: NATS JetStream mandated
- ✅ **Offline Continuity**: sync-agent design documented

## Resources

### Internal Documentation
- [Constitution](.speckit/constitution.md) - Core principles
- [Architecture](ARCHITECTURE.md) - System design
- [Phases](.speckit/PHASES.md) - Roadmap
- [Tech Decisions](TECH_DECISIONS.md) - Technology rationale

### External References
- [NestJS Docs](https://nestjs.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Ultralytics YOLO](https://docs.ultralytics.com/)
- [MediaPipe](https://developers.google.com/mediapipe)
- [Frigate NVR](https://docs.frigate.video/)
- [NATS JetStream](https://docs.nats.io/nats-concepts/jetstream)
- [Keycloak](https://www.keycloak.org/documentation)

## Support

For questions or issues:
1. Check [docs/PROJECT_SETUP.md](PROJECT_SETUP.md) troubleshooting section
2. Review relevant spec in [specs/](../specs/) directory
3. Consult [Constitution](.speckit/constitution.md) for governance
4. Create issue with detailed context

---

**Project Status**: ✅ Ready for Phase 1 Development  
**Next Milestone**: Phase 1 Operational Core MVP  
**Target**: 4 weeks  
**Focus**: Attendance, Billing, Staff Credentials, Medication Tracking

---

**Setup completed by**: Claude Sonnet 4.5  
**Review required by**: Engineering Lead, Product Lead, Compliance Lead
