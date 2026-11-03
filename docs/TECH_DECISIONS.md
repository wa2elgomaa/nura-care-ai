# Technology Decision Log

Record of key technology choices and their rationale.

## Decision Log

### 2026-11-03: Multi-Language Microservices (TypeScript + Python)

**Status**: Accepted

**Context**:
- Computer vision and ML workloads are Python's strength (YOLO, MediaPipe, scikit-learn)
- Business logic and web/mobile development are TypeScript's strength (NestJS, React, React Native)
- Forcing one language for everything would compromise performance or developer experience

**Decision**:
- **TypeScript** for: API services, business logic, web UI, mobile apps, real-time coordination
- **Python** for: Computer vision (nura-perception), face recognition (nura-face), analytics (nura-analytics)
- Services communicate via **NATS JetStream**, not language-specific RPC

**Consequences**:
- ✅ Each service uses the optimal language for its domain
- ✅ Best-in-class libraries available (Ultralytics, MediaPipe, NestJS, React Native)
- ✅ Event-driven architecture decouples language concerns
- ⚠️ Two runtime environments to maintain (Node.js + Python)
- ⚠️ Shared types require manual synchronization (mitigated by JSON Schema)

**Alternatives Considered**:
- **TypeScript only**: Poor ML/CV ecosystem, would reinvent wheels
- **Python only**: Weak typing, slower for business logic, no React Native
- **Go for high-performance services**: Considered for future stream processing

---

### 2026-11-03: NATS JetStream for Event Bus

**Status**: Accepted

**Context**:
- Services need async, decoupled communication
- Offline-first edge box requires persistent message queue
- Must survive internet outages and service restarts

**Decision**:
Use **NATS JetStream** as the primary inter-service event bus.

**Rationale**:
- Lightweight, fast, single binary
- Built-in persistence (JetStream) for offline buffering
- First-class TypeScript and Python clients
- Supports pub/sub, request-reply, streaming
- Battle-tested in edge/IoT scenarios

**Consequences**:
- ✅ Services remain decoupled
- ✅ Offline queue buffering built-in
- ✅ Scales to multi-site deployments
- ⚠️ One more infrastructure component to monitor

**Alternatives Considered**:
- **RabbitMQ**: Heavier, more complex, excellent but overkill for single-edge-box
- **Redis Streams**: Requires Redis anyway, but less mature streaming semantics
- **Kafka**: Enterprise-grade but massive overkill for edge deployment

---

### 2026-11-03: FastAPI for Python Services

**Status**: Accepted

**Context**:
- Python services need async HTTP API framework
- Must generate OpenAPI docs automatically
- Performance matters (real-time video processing)

**Decision**:
Use **FastAPI** with **Uvicorn** for all Python microservices.

**Rationale**:
- Async/await native (critical for video streams)
- Auto-generates OpenAPI/Swagger docs
- Pydantic models for validation and type safety
- Fast (benchmarks comparable to Node.js)
- Growing ecosystem and excellent docs

**Consequences**:
- ✅ Type-safe async Python
- ✅ Auto-generated API docs
- ✅ Fast enough for real-time workloads
- ✅ Consistent across Python services

**Alternatives Considered**:
- **Flask**: Sync-first, slower, older patterns
- **Django REST Framework**: Heavy, ORM-centric, overkill for microservices
- **Sanic**: Fast but smaller ecosystem

---

### 2026-11-03: Nx for TypeScript Monorepo

**Status**: Planned (not yet implemented)

**Context**:
- Multiple TypeScript services, web app, mobile apps in one repo
- Need enforced module boundaries (billing can't import from video processing)
- Want to run only affected tests/builds on CI

**Decision**:
Use **Nx** for TypeScript monorepo orchestration.

**Rationale**:
- Project graph understands dependencies
- "Affected" commands run only what changed
- Enforced module boundaries (Constitutional requirement)
- Code generators for new services/libraries
- Scales to 10+ apps/services

**Consequences**:
- ✅ Enforced architecture boundaries
- ✅ Fast CI (only builds/tests affected code)
- ✅ Shared types/utils as internal libraries
- ⚠️ Learning curve for team
- ⚠️ More tooling to configure

**Alternatives Considered**:
- **Turborepo**: Simpler, faster to start, but no boundary enforcement
- **Lerna**: Legacy, less actively maintained
- **pnpm workspaces alone**: No boundary enforcement, manual dependency graph

---

### 2026-11-03: Prisma for TypeScript ORM

**Status**: Accepted (with PostGIS exception)

**Context**:
- Need type-safe database access in TypeScript services
- PostgreSQL with TimescaleDB + PostGIS extensions
- Want auto-generated types from schema

**Decision**:
Use **Prisma** as the default ORM, with **raw SQL** escape hatches for PostGIS geometry queries.

**Rationale**:
- Schema-first, auto-generates TypeScript types
- Excellent DX with autocomplete and type safety
- Supports PostgreSQL extensions (TimescaleDB)
- PostGIS support improving (Unsupported types + raw SQL)

**Consequences**:
- ✅ Type-safe queries across most services
- ✅ Migration tooling built-in
- ✅ Single source of truth (schema.prisma)
- ⚠️ PostGIS queries require raw SQL or manual type mapping

**Alternatives Considered**:
- **TypeORM**: Better PostGIS support, but weaker types and more boilerplate
- **Drizzle ORM**: Newer, promising, but less mature ecosystem
- **Kysely**: Type-safe SQL builder, but no schema management

---

### 2026-11-03: Keycloak for Authentication

**Status**: Mandated by Constitution

**Context**:
- Need enterprise-grade SSO and RBAC
- Must support offline authentication on edge box
- Parents, teachers, directors have different access levels

**Decision**:
**Keycloak** for all authentication and role-based access control:
- **Cloud Keycloak**: Parents, regional managers, external users
- **Edge Keycloak**: Teachers, directors (syncs from cloud, survives offline)

**Rationale** (from Constitution):
- Open-source SSO standard
- OIDC/OAuth2 flows for web/mobile
- Fine-grained RBAC with role mapping
- Can run lightweight on edge box
- Audit logging built-in

**Consequences**:
- ✅ Enterprise-grade authentication
- ✅ Offline authentication on edge
- ✅ Auditable role escalation events
- ⚠️ Two Keycloak instances to sync (cloud ↔ edge)

**Alternatives Considered**:
- **Auth0**: SaaS-only, no offline support
- **SuperTokens**: Open-source but less mature RBAC
- **Ory**: Modern, but steeper learning curve

---

### 2026-11-03: Docker Compose for Edge Deployment

**Status**: Accepted

**Context**:
- Edge box is a single physical machine per site
- Need simple, reliable orchestration
- Staff are not Kubernetes experts

**Decision**:
Use **Docker Compose** for edge box orchestration (not Kubernetes).

**Rationale**:
- Single-machine deployment: Compose is perfect fit
- Simple `docker compose up` for staff/installers
- Profile-based startup (infrastructure, services, sim)
- Built-in networking and volume management
- Lightweight (no K8s overhead)

**Consequences**:
- ✅ Simple edge deployment and updates
- ✅ No Kubernetes complexity for single-node
- ✅ Easy for staff to troubleshoot
- ⚠️ No horizontal scaling (not needed on edge)

**Alternatives Considered**:
- **K3s**: Lightweight Kubernetes, but overkill for single-node
- **Nomad**: Good, but smaller ecosystem than Compose
- **Swarm**: Docker's native clustering, but Compose is simpler

---

### 2026-11-03: Frigate NVR for Video Management

**Status**: Accepted

**Context**:
- Need local NVR with object detection
- Must run on edge hardware (Coral TPU or GPU)
- Privacy requirement: video never leaves edge

**Decision**:
**Frigate NVR** as the foundation for camera management and local detection.

**Rationale**:
- Purpose-built for local-first video processing
- Native Coral TPU and GPU support
- YOLO-based object detection built-in
- MQTT integration for events
- Restream capability for nura-perception
- Active development and community

**Consequences**:
- ✅ Battle-tested local NVR
- ✅ Hardware acceleration out-of-box
- ✅ Privacy-preserving by design
- ✅ Saves development time (don't build NVR from scratch)

**Alternatives Considered**:
- **ZoneMinder**: Older, no built-in object detection
- **Blue Iris**: Windows-only, commercial license
- **MotionEye**: Simpler, but no object detection
- **Custom solution**: Would take 6+ months to match Frigate

---

### 2026-11-03: Ultralytics YOLO for Object Detection

**Status**: Accepted

**Context**:
- Need real-time person detection on edge hardware
- Must run on Coral TPU or NVIDIA GPU
- Potentially fine-tune for site-specific objects (Phase 4)

**Decision**:
**Ultralytics YOLO (v8/v11)** for object detection in nura-perception service.

**Rationale**:
- Industry standard for real-time detection
- Excellent accuracy/speed tradeoff
- Runs on Coral TPU (quantized) and GPU
- Easy fine-tuning for custom objects
- Active development and ecosystem

**Consequences**:
- ✅ Real-time detection on modest hardware
- ✅ Can fine-tune for toys, activities (Phase 4)
- ✅ Large community and pre-trained models
- ⚠️ AGPL-3.0 license (acceptable for edge deployment)

**Alternatives Considered**:
- **EfficientDet**: Slower, less active development
- **Faster R-CNN**: Older, slower than YOLO
- **Custom model**: Would take months to match YOLO accuracy

---

### 2026-11-03: MediaPipe for Pose Estimation

**Status**: Accepted

**Context**:
- Need skeletal keypoint extraction for fall detection
- Must run real-time on edge hardware
- Privacy requirement: no raw pose data to cloud

**Decision**:
**Google MediaPipe Pose** for pose estimation in nura-perception service.

**Rationale**:
- Lightweight, on-device inference
- 33 keypoints per person (full body)
- Runs on CPU (no GPU required for pose)
- Python SDK well-documented
- Reference fall-detection patterns exist

**Consequences**:
- ✅ Real-time pose on CPU
- ✅ Proven fall-detection patterns
- ✅ Privacy-preserving (local only)

**Alternatives Considered**:
- **OpenPose**: More accurate but much slower
- **AlphaPose**: Good accuracy, but heavier than MediaPipe
- **Custom model**: Overkill for fall detection

---

### 2026-11-03: CompreFace for Face Recognition

**Status**: Accepted

**Context**:
- Need pickup verification (guardian face matching)
- Privacy requirement: embeddings never leave edge
- Must be self-hosted and open-source

**Decision**:
**CompreFace (Exadel)** for face recognition in nura-face service.

**Rationale**:
- Fully self-hosted (Docker)
- REST API (language-agnostic)
- Built on InsightFace/FaceNet
- Apache 2.0 license
- Zero data sent to external services

**Consequences**:
- ✅ Privacy-preserving by design
- ✅ REST API easy to integrate
- ✅ Proven face verification accuracy
- ⚠️ One more container to run

**Alternatives Considered**:
- **InsightFace directly**: Lower-level, more code required
- **DeepFace**: Good library, but no REST API
- **Amazon Rekognition / Azure Face API**: Cloud-only, violates privacy requirements

---

## Amendment Process

When a new technology decision is made:

1. Document the decision in this log with:
   - Date
   - Status (Proposed / Accepted / Deprecated)
   - Context (why this decision matters)
   - Decision (what was chosen)
   - Rationale (why this choice)
   - Consequences (benefits and tradeoffs)
   - Alternatives Considered

2. Link from [ARCHITECTURE.md](./ARCHITECTURE.md) if it affects system design

3. Update [constitution.md](../.speckit/constitution.md) if it's a Constitutional mandate

4. Get approval from:
   - Engineering lead (technical feasibility)
   - Product lead (aligns with roadmap)
   - Compliance lead (if affects child data, security, or privacy)

---

**Document Owner**: Engineering Team  
**Review Cycle**: When new technology is introduced or existing tech deprecated
