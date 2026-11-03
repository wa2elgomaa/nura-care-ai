# Feature Specification: Regional Safety Ops Dashboard

**Feature Branch**: `020-regional-safety-ops-dashboard`

**Created**: 2026-07-22

**Status**: Draft

**Input**: User description: "As a regional manager, I want a consolidated dashboard that shows real-time safety status, ratio compliance, and incident summaries across all my centres, so that I can quickly identify underperforming sites and allocate support."

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

### User Story 1 - Cross-Centre Real-Time Oversight (Priority: P1)

As a regional manager, I can see real-time safety and ratio status for all centres in one view so I
can detect risk quickly.

**Why this priority**: Unified visibility is the core requirement for timely regional intervention.

**Independent Test**: Can be tested independently by opening the dashboard and confirming each managed
centre shows current safety status, ratio state, and incident posture.

**Acceptance Scenarios**:

1. **Given** centres are operating,
   **When** regional manager opens the consolidated dashboard,
   **Then** real-time safety indicators and ratio compliance states are visible for each centre.
2. **Given** one centre enters elevated risk state,
   **When** status updates occur,
   **Then** the dashboard highlights that centre prominently for rapid attention.

---

### User Story 2 - Incident and Compliance Triage (Priority: P2)

As a regional manager, I can review incident summaries and compliance trends to prioritize which
centres need immediate support.

**Why this priority**: Converts raw status signals into actionable triage and resource decisions.

**Independent Test**: Can be tested independently by reviewing centre rankings, incident summaries,
and compliance trends for a selected time window.

**Acceptance Scenarios**:

1. **Given** multiple centres have recent incidents,
   **When** manager filters by severity and recency,
   **Then** the dashboard surfaces highest-priority centres first.
2. **Given** ratio compliance patterns degrade at a site,
   **When** manager reviews trend summaries,
   **Then** the site is flagged for support allocation planning.

---

### User Story 3 - Support Allocation and Follow-Through (Priority: P3)

As a regional manager, I can assign follow-up actions to centre leaders and monitor resolution
progress from the same dashboard.

**Why this priority**: Ensures identified problems convert into tracked interventions and outcomes.

**Independent Test**: Can be tested independently by creating support actions for flagged centres and
confirming progress status updates are visible.

**Acceptance Scenarios**:

1. **Given** a centre is flagged as underperforming,
   **When** manager assigns support actions,
   **Then** action ownership, due timelines, and status tracking are recorded.
2. **Given** support actions are in progress,
   **When** manager checks follow-through view,
   **Then** they can see progress state and outstanding blockers by centre.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- One centre is temporarily offline and sends delayed updates while others are live.
- Incident severity definitions differ across centres and require normalization.
- Rapid incident burst creates alert fatigue for the regional manager.
- Ratio compliance is briefly non-compliant during legitimate emergency procedures.
- Centres cross midnight in different local time zones for daily summaries.
- A centre has missing staffing roster data needed for ratio evaluation.
- Manager oversees too many centres for one screen and needs prioritized condensation.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST provide a consolidated regional view of all managed centres with current
  safety status indicators.
- **FR-002**: System MUST display centre-level ratio compliance state, including current status and
  recent trend direction.
- **FR-003**: System MUST display centre-level incident summaries with severity, recency, and
  resolution posture.
- **FR-004**: System MUST refresh operational status data frequently enough to support near real-time
  triage decisions.
- **FR-005**: System MUST prioritize and rank centres by configurable risk scoring that combines
  safety, compliance, and incident signals.
- **FR-006**: System MUST support filters by region, centre, timeframe, severity, and compliance
  category.
- **FR-007**: System MUST provide drill-down from regional summary into centre details, including
  contributing factors for risk posture.
- **FR-008**: System MUST support creation and tracking of support actions assigned to centre leaders
  with ownership and due-date fields.
- **FR-009**: System MUST track and display action progress and unresolved blockers for follow-through
  oversight.
- **FR-010**: System MUST handle delayed or missing centre feeds by flagging data freshness and
  confidence indicators.
- **FR-011**: System MUST enforce role-based access boundaries so regional managers only view
  authorized centres.
- **FR-012**: System MUST maintain auditable logs of status changes, triage views, support allocations,
  and action lifecycle events.
- **FR-013**: Regional Manager role MUST be defined in Cloud Keycloak only and MUST NOT be replicated
  to Edge Keycloak.

### Key Entities *(include if feature involves data)*

- **Centre Safety Snapshot**: Time-bound status object summarizing current safety posture for one
  centre.
- **Ratio Compliance Record**: Centre-level compliance measurement entry with status and trend context.
- **Incident Summary Item**: Aggregated representation of recent incidents by severity and resolution
  state.
- **Regional Risk Score**: Composite scoring artifact used to prioritize underperforming centres.
- **Support Allocation Action**: Manager-assigned intervention task with owner, due timeline, and
  progress state.
- **Data Freshness Marker**: Indicator describing recency and reliability of centre feed data.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: At least 95% of managed centres display updated safety/ratio/incident status within
  60 seconds of source updates.
- **SC-002**: Regional managers identify and open the top three highest-risk centres in under
  2 minutes during simulation drills.
- **SC-003**: At least 90% of centres flagged as high-risk receive a documented support action within
  1 business day.
- **SC-004**: Repeat high-severity incident recurrence at previously flagged centres decreases by at
  least 25% over two reporting cycles after support intervention.
- **SC-005**: 100% of regional triage and support-allocation actions are captured in audit logs.

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- Centre-level safety, ratio, and incident modules already produce structured status signals.
- Regional manager-to-centre assignment mapping is already maintained.
- Ratio compliance policy definitions are standardized enough for regional aggregation.
- Regional managers require oversight and action-tracking capabilities, not direct site-level
  operational editing in this feature.
- This dashboard is operational oversight and does not generate clinical or diagnostic outputs.

## Constitution Alignment *(mandatory)*

### Phase Classification

- **Target Phase**: Phase 2
- **Prerequisite Validation**: Depends on Phase 1 operational core and Phase 2 multi-site edge/ratio
  monitoring maturity required for reliable consolidated oversight.

### Privacy, Consent, and Residency Impact

- **Child Sensitive Data Used**: Dashboard uses aggregated safety and incident operational metadata,
  with minimal child-identifiable detail in regional summary views.
- **Edge Processing Boundary**: Raw media remains edge-local; consolidated dashboard consumes approved
  event-level and compliance metadata.
- **Consent Requirement**: Any underlying biometric/behavioral sources must already satisfy existing
  consent controls before contributing signals to regional summaries.
- **Retention and Auto-Delete**: Aggregated dashboard and audit metadata follow regional retention
  windows and secure deletion policies.
- **Regional Residency Scope**: US, EU, and GCC residency controls apply to cross-centre aggregated
  operational data and audit logs.

### Safety and Non-Diagnostic Compliance

- **Behavioral or Safety Outputs**: Outputs are operational safety/compliance risk indicators and
  incident trend summaries for management.
- **Prohibited Output Check**: No diagnostic labels, disorder names, or clinical certainty outputs are
  produced.
- **Audience Boundary**: Consolidated risk dashboards are management-facing and operationally scoped,
  not parent-facing.
