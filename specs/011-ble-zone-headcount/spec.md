# Feature Specification: BLE Zone Headcount

**Feature Branch**: `011-ble-zone-headcount`

**Created**: 2026-07-22

**Status**: Draft

**Input**: User description: "As a director, I want to assign tamper-resistant BLE badges to each child and place gateways in every room/zone, so that I can see live headcount per room, get alerted if a child wanders into a restricted area, and automatically verify staff-to-child ratios without manual counting."

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

### User Story 1 - Live Room Headcount from BLE Presence (Priority: P1)

As a director, I can see live child headcount per room based on badge presence so staff know current
occupancy without manual roll counts.

**Why this priority**: Reliable live headcount is the foundation for room safety awareness and ratio
operations.

**Independent Test**: Can be tested independently by assigning badges, moving children between zones,
and confirming room headcount updates accurately in near real time.

**Acceptance Scenarios**:

1. **Given** each child has an active assigned badge,
   **When** children are present in different rooms,
   **Then** the system displays current headcount by room and total on-site count.
2. **Given** a child moves from one room to another,
   **When** the receiving gateway detects badge transition,
   **Then** room counts update to decrement origin and increment destination.

---

### User Story 2 - Restricted Area Safety Alerts (Priority: P2)

As a director and staff team, we receive immediate alerts when a child enters a restricted zone so we
can intervene quickly.

**Why this priority**: Restricted-area alerts prevent unsafe access and reduce critical supervision
risk.

**Independent Test**: Can be tested independently by defining restricted zones and simulating child
entry to verify alert generation and response tracking.

**Acceptance Scenarios**:

1. **Given** restricted zones are configured,
   **When** a child badge is detected in a restricted area,
   **Then** an immediate safety alert is sent to designated staff and logged.
2. **Given** an alert is acknowledged,
   **When** staff resolve the situation,
   **Then** resolution status and timestamp are recorded for audit.

---

### User Story 3 - Automatic Staff-to-Child Ratio Verification (Priority: P3)

As a director, I can view automatic ratio compliance status per room so staffing risks are identified
without manual recounting.

**Why this priority**: Automated ratio checks reduce errors and improve regulatory compliance posture.

**Independent Test**: Can be tested independently by adjusting room occupancy and staff assignments and
verifying ratio state changes and alerts.

**Acceptance Scenarios**:

1. **Given** room-specific ratio rules are configured,
   **When** occupancy or staff presence changes,
   **Then** the system recalculates ratio status and marks rooms compliant or non-compliant.
2. **Given** a room becomes non-compliant,
   **When** ratio breach persists beyond configured tolerance,
   **Then** an alert is issued and tracked until compliance is restored.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- Badge battery is low or depleted during active day.
- Child removes or damages badge despite tamper-resistant design.
- Two gateways report conflicting zone presence for the same badge.
- Temporary gateway outage leaves a room without signal coverage.
- Child crosses boundary between adjacent zones rapidly causing signal flapping.
- Staff member is present but not checked into staffing roster for ratio calculation.
- Emergency evacuation mode requires high-frequency occupancy updates.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST support assignment of one tamper-resistant BLE badge per active child with
  lifecycle status tracking.
- **FR-002**: System MUST support registration and health monitoring of room/zone gateways at each
  site.
- **FR-003**: System MUST determine current child zone presence from gateway observations and maintain
  a single active zone state per child.
- **FR-004**: System MUST provide live headcount by room/zone and consolidated site totals.
- **FR-005**: System MUST support configuration of restricted zones and trigger alerts when a child
  enters one.
- **FR-006**: System MUST support acknowledgement and resolution workflows for restricted-zone alerts.
- **FR-007**: System MUST support configurable staff-to-child ratio rules by room or program context.
- **FR-008**: System MUST recalculate ratio compliance automatically when child occupancy or staff
  assignment changes.
- **FR-009**: System MUST generate ratio-breach alerts when compliance thresholds are violated.
- **FR-010**: System MUST log badge events, zone transitions, alert actions, and ratio states in an
  immutable audit trail.
- **FR-011**: System MUST provide fallback handling for signal conflict, gateway outage, or stale
  badge telemetry while preserving safety visibility.
- **FR-012**: System MUST provide director-level dashboards for live occupancy, restricted-zone events,
  and ratio compliance trends.

### Key Entities *(include if feature involves data)*

- **Child Badge Assignment**: Relationship between child identity and badge identity with assignment,
  active status, and tamper/health indicators.
- **Zone Gateway**: Registered room/zone receiver with site mapping, operational status, and telemetry
  freshness.
- **Zone Presence State**: Current inferred room/zone location for each child with confidence and
  last-seen timestamp.
- **Restricted Zone Policy**: Rules defining areas where child entry triggers immediate safety alerts.
- **Ratio Rule Set**: Configured staffing-to-child ratio requirements by room, age band, or program.
- **Ratio Compliance State**: Real-time compliance result per room with breach start, severity, and
  resolution state.
- **BLE Safety Audit Event**: Immutable record for badge assignment changes, zone transitions,
  restricted alerts, and ratio alerts.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: At least 98% of child zone transitions are reflected in room headcount within 30 seconds
  of movement.
- **SC-002**: 100% of restricted-zone entries generate alerts within 1 minute of detection.
- **SC-003**: At least 95% of ratio-breach conditions are identified automatically without manual
  recount.
- **SC-004**: 100% of restricted-zone and ratio alerts have auditable lifecycle records from trigger to
  resolution.
- **SC-005**: Manual counting workload for headcount and ratio checks is reduced by at least 70%
  during staffed operating periods.

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- Each room/zone has sufficient gateway coverage to support reliable badge detection.
- Badge issuance and replacement processes are managed by site operations teams.
- Staff assignment data is available in near real time for ratio verification.
- Restricted-zone definitions and ratio policies are pre-approved by site governance.
- This feature supports operational safety and compliance counting, not medical diagnosis outputs.

## Constitution Alignment *(mandatory)*

### Phase Classification

- **Target Phase**: Phase 2
- **Prerequisite Validation**: Depends on Phase 1 operational foundation and aligns directly with Phase
  2 BLE zone/headcount pilot obligations.

### Privacy, Consent, and Residency Impact

- **Child Sensitive Data Used**: Child identity linkage, badge identifiers, room presence telemetry,
  restricted-zone events, and staffing-ratio metadata.
- **Edge Processing Boundary**: Zone detection and occupancy inference are processed locally at site
  gateways/edge services; cloud receives operational metadata only.
- **Consent Requirement**: Badge-based location tracking for child safety follows guardian consent and
  policy controls with auditable consent status where required.
- **Retention and Auto-Delete**: Presence and alert metadata follow regional retention policies with
  secure auto-delete defaults and legal-hold exceptions.
- **Regional Residency Scope**: US, EU, and GCC residency controls apply to occupancy and alert
  metadata stored in cloud services.

### Safety and Non-Diagnostic Compliance

- **Behavioral or Safety Outputs**: Outputs include room headcount, restricted-area alerts, and ratio
  compliance status for operational safety management.
- **Prohibited Output Check**: No diagnosis labels, disorder names, or diagnostic confidence outputs
  are generated.
- **Audience Boundary**: Occupancy and ratio controls are staff-facing and director-facing; parent
  messaging for related incidents follows separate approved communication workflows.
