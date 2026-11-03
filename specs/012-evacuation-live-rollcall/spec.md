# Feature Specification: Evacuation Live Rollcall

**Feature Branch**: `012-evacuation-live-rollcall`

**Created**: 2026-07-22

**Status**: Draft

**Input**: User description: "As a director, I want to trigger a one-tap evacuation mode that turns every teacher's tablet into a live roll-call view, automatically cross-checked against BLE exit gate reads, so that I know exactly who is unaccounted for in real time during a drill or emergency."

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

### User Story 1 - One-Tap Evacuation Activation (Priority: P1)

As a director, I can activate evacuation mode instantly and switch all teacher tablets to emergency
roll-call state.

**Why this priority**: Fast mode activation is critical for reducing response time during drills and
real emergencies.

**Independent Test**: Can be tested independently by triggering evacuation mode and confirming all
teacher tablets enter the emergency roll-call interface immediately.

**Acceptance Scenarios**:

1. **Given** normal operations are active,
   **When** the director taps evacuation mode,
   **Then** all connected teacher tablets switch to live roll-call view.
2. **Given** evacuation mode is active,
   **When** new tablet sessions connect,
   **Then** they open directly into evacuation roll-call state.

---

### User Story 2 - Live Cross-Checked Accountability (Priority: P2)

As a director, I can see real-time accounted and unaccounted lists that combine teacher roll-call
inputs with BLE exit gate reads.

**Why this priority**: Automated cross-checking reduces counting errors and surfaces missing children
faster under pressure.

**Independent Test**: Can be tested independently by simulating evacuation movement and verifying
roll-call states reconcile against BLE exit events.

**Acceptance Scenarios**:

1. **Given** children are evacuating through monitored exits,
   **When** BLE gate reads and teacher confirmations are captured,
   **Then** accountability status updates in real time for each child.
2. **Given** a discrepancy exists between manual roll-call and BLE read data,
   **When** reconciliation logic runs,
   **Then** the child is flagged for immediate verification with discrepancy reason.

---

### User Story 3 - Emergency Audit and Post-Event Review (Priority: P3)

As a director and safety reviewer, I can access a complete timeline of evacuation actions,
accountability updates, and unresolved cases for compliance and debrief.

**Why this priority**: Verified post-event records are required for drills, incident review, and
process improvement.

**Independent Test**: Can be tested independently by closing an evacuation event and reviewing
generated timelines, alerts, and final accounted status.

**Acceptance Scenarios**:

1. **Given** evacuation mode has been used,
   **When** the event is closed,
   **Then** the system stores an immutable event summary with all accountability transitions.
2. **Given** unaccounted cases occurred during event,
   **When** incident review is opened,
   **Then** the system presents escalation actions and resolution outcomes for each case.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- Tablet loses connectivity during active evacuation while local roll-call actions continue.
- BLE exit gate misses a read for a child badge during high traffic.
- Same child is marked accounted by teacher before BLE gate read arrives.
- Duplicate BLE reads occur for a child exiting and re-entering checkpoint area.
- Evacuation is triggered accidentally and must be canceled or reset safely.
- Staff role changes during event and new supervisor needs immediate control access.
- Power disruption affects a subset of gateways during emergency.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST provide a one-action evacuation trigger for authorized director roles.
- **FR-002**: System MUST force all teacher tablets into a dedicated live roll-call interface while
  evacuation mode is active.
- **FR-003**: System MUST maintain real-time child accountability state categories at minimum: accounted,
  unaccounted, and needs verification.
- **FR-004**: System MUST ingest BLE exit gate events and correlate them with child identity and
  evacuation event context.
- **FR-005**: System MUST reconcile teacher roll-call updates and BLE exit reads to compute
  cross-checked accountability status.
- **FR-006**: System MUST surface discrepancies between manual and BLE evidence with explicit reason
  codes for rapid follow-up.
- **FR-007**: System MUST provide high-priority alerts for unaccounted children and stale unresolved
  discrepancies.
- **FR-008**: System MUST support offline-tolerant tablet roll-call updates and synchronize them once
  connectivity returns.
- **FR-009**: System MUST allow authorized incident command roles to acknowledge, assign, and resolve
  unaccounted cases during event.
- **FR-010**: System MUST log all evacuation trigger actions, roll-call changes, BLE correlations,
  alerts, acknowledgements, and resolutions in immutable audit history.
- **FR-011**: System MUST provide a controlled evacuation-close workflow that records final accounted
  status and open exceptions.
- **FR-012**: System MUST provide post-event reporting for drills or emergencies including timeline,
  response latency, and unresolved risk indicators.

### Key Entities *(include if feature involves data)*

- **Evacuation Event**: Active emergency or drill record with trigger source, start/end times,
  command owner, and event status.
- **Tablet Roll-Call Session**: Teacher-side emergency roll-call workspace linked to event,
  participant role, and update stream.
- **Child Accountability State**: Per-child current event state with last evidence source and
  verification confidence.
- **BLE Exit Read Event**: Exit-gate telemetry record including badge identifier, gate location,
  timestamp, and event quality.
- **Accountability Discrepancy**: Exception record when manual and BLE evidence disagree or remain
  incomplete.
- **Evacuation Alert**: High-priority notification generated for unaccounted children,
  unresolved discrepancies, or prolonged stale states.
- **Evacuation Audit Record**: Immutable event history covering trigger, updates, reconciliations,
  alerts, and closeout summary.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 100% of connected teacher tablets enter evacuation roll-call mode within 10 seconds of
  authorized trigger.
- **SC-002**: At least 98% of BLE exit reads are correlated to the correct child accountability record
  during drills.
- **SC-003**: Unaccounted-child alerts are generated within 1 minute when reconciliation cannot confirm
  accountability.
- **SC-004**: 100% of evacuation events produce a complete audit timeline with final accounted and
  unaccounted outcomes.
- **SC-005**: Time to identify all unaccounted children during drills is reduced by at least 60%
  compared with manual-only roll-call baseline.

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- BLE badge assignments and exit-gate infrastructure are already deployed and operational per site.
- Teacher tablets are enrolled and available for emergency-mode command override.
- Role permissions for emergency command and incident resolution are preconfigured.
- Drill and real emergency workflows share the same accountability engine with distinct labels.
- This feature supports operational emergency accountability and does not provide diagnostic outputs.

## Constitution Alignment *(mandatory)*

### Phase Classification

- **Target Phase**: Phase 2
- **Prerequisite Validation**: Requires Phase 1 operational readiness and Phase 2 BLE zone/headcount
  infrastructure to be active for cross-checking.

### Privacy, Consent, and Residency Impact

- **Child Sensitive Data Used**: Child identity linkage, live location/accountability telemetry,
  staff verification actions, and evacuation alert metadata.
- **Edge Processing Boundary**: BLE read processing and immediate reconciliation can run locally with
  only required operational metadata forwarded for centralized command and reporting.
- **Consent Requirement**: Emergency safety processing is operationally required; biometric-related
  consent controls remain unchanged and are not expanded by this feature.
- **Retention and Auto-Delete**: Evacuation event telemetry and audit records follow region-specific
  retention and secure deletion policies, with legal-hold support where required.
- **Regional Residency Scope**: US, EU, and GCC residency obligations apply to stored accountability
  and alert metadata.

### Safety and Non-Diagnostic Compliance

- **Behavioral or Safety Outputs**: Outputs include live roll-call states, unaccounted alerts,
  discrepancy indicators, and event closeout summaries.
- **Prohibited Output Check**: No diagnostic labels, disorder names, or diagnostic confidence outputs
  are generated.
- **Audience Boundary**: Emergency accountability and discrepancy views are staff-facing and
  director-facing; parent communication follows separate approved notification workflows.
