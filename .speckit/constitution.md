<!--
Sync Impact Report
- Version change: template -> 1.0.0
- Modified principles:
	- Template Principle 1 -> I. Privacy by Default and Edge-First Inference
	- Template Principle 2 -> II. Explicit Consent and Child Data Dignity
	- Template Principle 3 -> III. Safety-First, Non-Diagnostic Product Boundaries
	- Template Principle 4 -> IV. Mandatory Delivery Sequencing and Commercial Readiness
	- Template Principle 5 -> V. Architecture Integrity and Offline Safety Continuity
- Added sections:
	- Regulatory and Ethical Guardrails
	- Technical and Delivery Enforcement
- Removed sections:
	- None
- Templates requiring updates:
	- ✅ updated .specify/templates/plan-template.md
	- ✅ updated .specify/templates/spec-template.md
	- ✅ updated .specify/templates/tasks-template.md
- Follow-up TODOs:
	- None
-->

# NURA Constitution

## Core Principles

### I. Privacy by Default and Edge-First Inference
Raw video footage and facial biometric embeddings MUST NOT leave the on-premise Edge Box.
Person detection, facial matching, fall detection, and face blurring inference MUST execute locally
on Edge Box workloads. Cloud services MAY process only non-identifiable operational metadata needed
for product operations, billing, and reporting.
Rationale: child privacy risk is minimized only when identifiable perception data remains local.

### II. Explicit Consent and Child Data Dignity
Any feature processing biometric data or behavioral inference MUST be strictly opt-in and blocked by
default. Processing MUST NOT begin until a verifiable parental consent record exists. Consent
collection, revocation, and retention actions MUST be auditable with immutable event history.
Rationale: lawful processing and institutional trust require provable consent lifecycle controls.

### III. Safety-First, Non-Diagnostic Product Boundaries
NURA MUST operate as an educator support and safety platform, not a medical device. Features MUST
NOT produce diagnosis labels, disorder names, or diagnostic confidence scores. Alerts MAY present
observable patterns only, and automated behavioral labels MUST remain staff-facing and excluded from
parent-facing automated messaging.
Rationale: diagnostic claims increase legal and ethical risk and exceed intended platform scope.

### IV. Mandatory Delivery Sequencing and Commercial Readiness
Phase sequencing is mandatory and cannot be bypassed:
1. Phase 1 MUST deliver and operationalize Attendance, Billing, Staff Credential Tracker, and
Medication Cross-Check before AI behavioral capabilities ship.
2. Phase 2 MUST deliver Edge Box rollout, camera-follow, fall detection, and BLE zone/headcount
pilots before any Phase 3 behavioral release.
3. Phase 3 behavioral flagging requires clinical advisory sign-off and production usage evidence.
4. Custom ML models are prohibited before Phase 4 approval.
Rationale: reliable revenue operations and safety baselines must precede higher-risk intelligence work.

### V. Architecture Integrity and Offline Safety Continuity
The platform MUST use a TypeScript monorepo with Nx-enforced module boundaries. Backend services
MUST use NestJS and event-driven messaging over RabbitMQ or NATS. Mobile and web experiences for
parents, teachers, and directors MUST remain in one unified application codebase with role-based
views, not separate binaries. The Edge Box MUST remain offline-first so attendance, pickup
verification, and ratio monitoring continue during internet outages.
Rationale: strict architecture boundaries reduce coupling and preserve safety-critical operations.

## Regulatory and Ethical Guardrails

All child-related data MUST be handled as special-category sensitive data under COPPA, BIPA, and
GDPR-K aligned controls. Data retention MUST be region-configurable with secure auto-delete defaults.
Facial biometric embeddings MUST default to a short retention window of seven days unless longer
retention is covered by explicit legal consent and policy documentation.

Continuous audio recording is prohibited. Audio anomaly detection MAY run on rolling local buffers,
but raw audio MUST be discarded and only event-level alerts may persist.

Regional data residency MUST support isolated data stores and operations in US, EU, and GCC regions.
Livestream parent views MUST only expose the parent’s own child; other children MUST be blurred or
anonymized by edge inference before rendering.

Edge hardware MUST include tamper-resistance controls, including a physical tamper switch that
initiates cryptographic wiping of local biometric data on unauthorized access.

AI explainability MUST be rules-based first. Thresholds, proximity logic, and alert rationale MUST be
documented for directors and compliance reviewers until Phase 4 authorizes advanced ML.

## Technical and Delivery Enforcement

Technology mandates:
1. Language selection by best fit: TypeScript for business logic, APIs, web/mobile apps, and real-time
coordination; Python for computer vision, ML inference, sensor processing, and data science workloads.
Services communicate via NATS JetStream event bus, not direct calls.
2. Monorepo and boundaries: TypeScript services MUST use Nx workspace with enforced module boundaries;
cross-domain imports violating boundaries MUST fail CI. Python services MAY remain independent but MUST
follow standardized FastAPI project structure.
3. Applications: React Native plus NativeWind for mobile role views; Next.js plus shadcn/ui for admin
console. Cross-platform components MUST use gluestack-ui v3 for shared design language.
4. Authentication and RBAC: Keycloak (open-source SSO) MUST be used for all user authentication and
role-based access control.
5. Keycloak deployment model: a central Cloud Keycloak MUST serve parents, regional managers, and
external user management. A lightweight Edge Keycloak container MUST run on each Edge Box for teachers
and directors.
6. Keycloak replication and provisioning: nursery directors manage staff and parent accounts via the Web
Admin Console, which syncs through Cloud Keycloak Admin API. Edge Keycloak MUST sync users and roles
from Cloud Keycloak on a scheduled job (target every 5 minutes when online).
7. Data layer: PostgreSQL with PostGIS and TimescaleDB extensions in one instance; Prisma as primary ORM.
Raw SQL is allowed for PostGIS geometry operations or TimescaleDB continuous aggregates where Prisma
escape hatches are insufficient.
8. Edge inference stack: Frigate NVR for video management, Ultralytics YOLO for object detection,
MediaPipe for pose estimation, ByteTrack for multi-object tracking, and CompreFace for face recognition
on the local appliance. Python services (nura-perception, nura-face, nura-analytics) orchestrate these
components.
9. Event bus: NATS JetStream MUST be used for all inter-service messaging. MQTT via Mosquitto is
allowed only for sensor ingestion, with nura-sensor-adapter bridging MQTT to NATS.
10. Business model readiness: Edge Box and BLE gateways MUST be deployable under recurring HaaS
subscription operations, not one-time hardware purchase assumptions.

Go-to-market and sequencing mandates:
1. Emergency evacuation and headcount reconciliation MUST be treated as a flagship capability in
roadmaps and architecture decisions.
2. Integration seams for future insurer or underwriter APIs MUST be preserved in safety-event,
compliance, and reporting services.
3. Spec 007 role-based layouts MUST use Keycloak OIDC flows: authorization code flow with PKCE for
mobile and web clients.
4. Spec 015 offline resilience MUST include Edge Keycloak local authentication fallback. If Edge
Keycloak cannot reach Cloud Keycloak, it MUST validate teacher and director logins against a locally
cached user and role replica.

## Ethical Development

Role escalation events (for example director override of teacher permissions) MUST be logged and
auditable in Keycloak audit trails.

Keycloak authentication and administration events MUST be forwarded to the NURA audit log service for
cross-system compliance visibility.

Definition-of-done gates:
1. Adoption gate: operational core workflows show daily staff usage in pilot cohorts.
2. Safety gate: incident false-alert rate MUST be below five percent before related marketing claims.
3. Trust gate: biometric opt-in rate MUST be measured; if below fifty percent in pilots, consent UX
must be redesigned before scale rollout.

Constraint hierarchy for all decisions and reviews:
1. Regulatory and privacy obligations.
2. Phase sequencing obligations.
3. Technology stack and architecture obligations.
4. Performance and scalability optimization.

## Governance

This constitution is the highest-priority project policy and supersedes conflicting local practices,
feature preferences, and delivery shortcuts.

Amendment policy:
1. Amendments MUST be proposed via pull request that includes rationale, risk assessment, and template
impact review for plan, spec, and tasks artifacts.
2. Amendments MUST be approved by product, engineering, and compliance stakeholders before merge.
3. Any amendment affecting child data handling, consent, retention, or diagnostic boundaries MUST
include legal review evidence.

Versioning policy:
1. MAJOR for incompatible governance changes or principle removal/redefinition.
2. MINOR for new principle or materially expanded mandatory guidance.
3. PATCH for clarifications that do not alter normative requirements.

Compliance review expectations:
1. Every plan MUST pass a constitution check before Phase 0 research and after Phase 1 design.
2. Every spec MUST declare consent, retention, and non-diagnostic impact where applicable.
3. Every task plan MUST include explicit tasks for regulatory controls, edge constraints, and
phase-gate evidence when relevant.
4. Releases violating any higher-order constraint in the hierarchy are blocked.

**Version**: 1.1.0 | **Ratified**: 2026-07-22 | **Last Amended**: 2026-07-22
