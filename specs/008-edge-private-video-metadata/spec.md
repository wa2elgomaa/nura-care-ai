# Feature Specification: Edge Private Video Metadata

**Feature Branch**: `008-edge-private-video-metadata`

**Created**: 2026-07-22

**Status**: Draft

**Input**: User description: "As a system administrator, I want to install a small edge server (Docker Compose or k3s) at each site that ingests camera feeds locally, runs Frigate NVR + YOLO object detection on a Coral TPU, and publishes only anonymised metadata to the cloud, so that raw video and face embeddings never leave the building."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Site-Local Ingest and Detection (Priority: P1)

As a system administrator, I can deploy a small on-site edge server that ingests camera feeds and runs
local detection workloads without relying on cloud video transport.

**Why this priority**: Local ingestion and inference are required for privacy-by-design and low-latency
site operations.

**Independent Test**: Can be tested independently by connecting site cameras to the edge server and
verifying local processing runs continuously during operating hours.

**Acceptance Scenarios**:

1. **Given** a site with configured cameras,
   **When** the edge server is provisioned and started,
   **Then** camera streams are ingested and processed locally for detection events.
2. **Given** local processing is active,
   **When** cloud connectivity is unavailable,
   **Then** local ingestion and detection continue without uploading raw footage.

---

### User Story 2 - Anonymized Metadata Publication (Priority: P2)

As a system administrator, I can configure cloud publication so only anonymized event metadata is sent
off-site while privacy-sensitive media remains local.

**Why this priority**: Anonymized telemetry enables central reporting while preserving strict child
privacy constraints.

**Independent Test**: Can be tested independently by inspecting cloud-bound payloads and confirming
they contain only approved anonymized event fields.

**Acceptance Scenarios**:

1. **Given** local events are produced,
   **When** cloud publication occurs,
   **Then** only approved anonymized metadata fields are transmitted.
2. **Given** a payload includes disallowed media identifiers,
   **When** publication validation runs,
   **Then** the payload is blocked and an alert is logged for administrator action.

---

### User Story 3 - Enforce Privacy Guardrails Across Sites (Priority: P3)

As a platform and compliance team, we can verify that each site enforces no-raw-video/no-embedding
egress policies with auditable evidence.

**Why this priority**: Policy enforcement at every site is necessary for regulatory trust and scale
operations.

**Independent Test**: Can be tested independently by running policy checks and audit reviews across
multiple sites to confirm prohibited data never leaves local boundary.

**Acceptance Scenarios**:

1. **Given** site privacy policies are active,
   **When** outbound transfer monitoring runs,
   **Then** any attempt to export raw video or face embeddings is denied and recorded.
2. **Given** periodic compliance review is initiated,
   **When** audit reports are generated,
   **Then** reports show policy status, denied egress attempts, and anonymized metadata publication
   history by site.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- Site network outage persists for an extended period while local event volume increases.
- Camera feed quality degrades and detection confidence drops.
- Edge hardware accelerator is unavailable or temporarily disconnected.
- Site configuration drift causes mismatched anonymization rules between locations.
- Duplicate camera identifiers are accidentally configured on the same site.
- Time synchronization drift causes event ordering inconsistencies in cloud metadata.
- Unauthorized administrator attempts to alter outbound privacy policy controls.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST support site-level edge deployment profiles appropriate for small local
  server operation.
- **FR-002**: System MUST ingest site camera streams locally and run detection pipelines on the local
  edge host.
- **FR-003**: System MUST maintain local processing continuity during cloud connectivity interruptions.
- **FR-004**: System MUST define and enforce an allowlist schema for cloud-bound metadata fields.
- **FR-005**: System MUST block outbound transmission of raw video, raw image frames, and facial
  biometric embeddings.
- **FR-006**: System MUST publish anonymized event metadata to cloud services for centralized analytics
  and operations.
- **FR-007**: System MUST provide site-level policy controls that prevent disabling privacy guardrails
  without authorized change procedures.
- **FR-008**: System MUST log all outbound publication attempts, blocked transfers, and privacy-policy
  changes with immutable audit records.
- **FR-009**: System MUST provide administrators with health visibility for camera ingestion, edge
  compute state, local queue depth, and publication status.
- **FR-010**: System MUST support secure buffering and delayed publication of approved anonymized
  metadata when connectivity is restored.
- **FR-011**: System MUST support cross-site compliance reporting demonstrating no prohibited media
  egress.
- **FR-012**: System MUST provide policy-verification checks that can be executed on demand and on a
  recurring schedule.

### Key Entities *(include if feature involves data)*

- **Edge Site Node**: On-premise processing unit for a single nursery site with deployment profile,
  hardware status, and policy state.
- **Camera Ingest Source**: Registered camera feed endpoint with site mapping, health status,
  and stream configuration metadata.
- **Local Detection Event**: Event produced by on-site detection workloads containing event type,
  timestamp, and non-identifying context.
- **Anonymized Metadata Payload**: Cloud-bound structured record derived from local events and filtered
  to approved fields only.
- **Egress Policy Rule**: Rule describing which data categories are prohibited or allowed for outbound
  transmission.
- **Egress Audit Event**: Immutable record of publish attempt, allow/deny outcome, reason code, and
  actor or service origin.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 100% of active sites process camera ingestion locally without requiring continuous cloud
  media transport.
- **SC-002**: 100% of outbound cloud payloads conform to approved anonymized metadata schema.
- **SC-003**: 0 confirmed incidents of raw video or face-embedding egress from site boundaries.
- **SC-004**: At least 99% of local detection events are published as approved metadata within
  5 minutes under normal connectivity conditions.
- **SC-005**: Site-level privacy policy verification checks pass at least 98% of scheduled runs across
  deployed locations.

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- Each site has minimum required local compute and acceleration capacity for approved detection
  workloads.
- Camera inventory and network segmentation per site are available before edge installation.
- Central cloud services accept only approved anonymized metadata payload contracts.
- Security and compliance teams define prohibited data classes and audit expectations centrally.
- This feature governs infrastructure-level privacy-preserving perception pipeline behavior and not
  parent-facing diagnosis outputs.

## Constitution Alignment *(mandatory)*

### Phase Classification

- **Target Phase**: Phase 2
- **Prerequisite Validation**: Phase 1 operational core workflows are expected live before broad edge
  rollout; this feature implements the Phase 2 edge rollout and local inference foundation.

### Privacy, Consent, and Residency Impact

- **Child Sensitive Data Used**: On-site camera feeds and potentially identifying perception artifacts
  are processed locally; cloud receives only anonymized event metadata.
- **Edge Processing Boundary**: Raw video and facial biometric embeddings remain on the local edge
  boundary; outbound transfer is restricted to approved anonymized metadata fields.
- **Consent Requirement**: Any biometric-related inference path remains consent-gated per policy;
  absence or revocation of consent must prevent prohibited biometric processing or publication.
- **Retention and Auto-Delete**: Local and cloud metadata retention follows region-configurable
  policies with secure auto-delete defaults and legal-hold exceptions.
- **Regional Residency Scope**: US, EU, and GCC residency controls apply to cloud-stored metadata and
  related audit logs, with site-local data confinement for raw media artifacts.

### Safety and Non-Diagnostic Compliance

- **Behavioral or Safety Outputs**: Outputs are operational detection events and anonymized metadata
  summaries for staff and system workflows.
- **Prohibited Output Check**: No diagnosis labels, disorder names, or diagnostic confidence outputs
  are generated for parent-facing communication.
- **Audience Boundary**: Infrastructure and compliance telemetry are staff-facing and admin-facing;
  parent-facing communications are governed by separate approved operational channels.
