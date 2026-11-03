# Feature Specification: Staff Compliance Tracker

**Feature Branch**: `001-staff-compliance-tracker`

**Created**: 2026-07-22

**Status**: Draft

**Input**: User description: "As a director, I want to track staff CPR/first-aid certifications, background-check renewal dates, and ratio-qualified staff counts per room, so that I never miss a licensing audit deadline and can instantly prove compliance to inspectors."

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

### User Story 1 - Track Credential Expiry and Deadlines (Priority: P1)

As a director, I can view each staff member's CPR/first-aid certification and background-check status,
including issue dates, renewal dates, and current compliance state.

**Why this priority**: Missing renewal dates can immediately create licensing risk and staffing
disruptions.

**Independent Test**: Can be fully tested by creating staff records with mixed expiration dates,
then verifying the system correctly marks compliant, expiring soon, and expired statuses.

**Acceptance Scenarios**:

1. **Given** a staff member with valid CPR/first-aid and background-check records,
   **When** the director opens the compliance view,
   **Then** the staff member is shown as compliant with the correct next renewal deadlines.
2. **Given** a staff member with a credential expiring within the configured warning window,
   **When** the director views upcoming expirations,
   **Then** that staff member appears in an expiring-soon list with the due date and required action.
3. **Given** a staff member with an expired credential,
   **When** the compliance view is opened,
   **Then** the staff member is clearly marked as non-compliant and appears in overdue alerts.

---

### User Story 2 - Monitor Ratio-Qualified Coverage by Room (Priority: P2)

As a director, I can see room-by-room counts of scheduled ratio-qualified staff so I can detect coverage
gaps before inspections or daily operations are impacted.

**Why this priority**: Even if credentials are tracked, room-level non-compliance still creates audit
and safety risk.

**Independent Test**: Can be fully tested by assigning staff to rooms and shifts, then verifying each
room reflects qualified counts and highlights any shortfall against required minimums.

**Acceptance Scenarios**:

1. **Given** staff assignments for multiple rooms,
   **When** the director opens room compliance coverage,
   **Then** each room shows required qualified count, current qualified count, and compliance status.
2. **Given** a room where qualified count falls below the required threshold,
   **When** coverage is recalculated,
   **Then** the room is flagged as out of compliance with the exact shortfall.

---

### User Story 3 - Produce Inspector-Ready Compliance Evidence (Priority: P3)

As a director, I can generate an audit-ready compliance summary showing current credential status,
renewal timelines, and room coverage so inspectors can verify compliance immediately.

**Why this priority**: Fast evidence delivery reduces audit disruption and improves regulator trust.

**Independent Test**: Can be fully tested by generating a report from known sample data and verifying it
contains staff credential statuses, deadline details, and room coverage outcomes.

**Acceptance Scenarios**:

1. **Given** current compliance and room coverage data,
   **When** the director requests an audit summary,
   **Then** the system produces a timestamped report with compliant, expiring, and overdue records.
2. **Given** an active compliance shortfall,
   **When** the director generates the report,
   **Then** the report explicitly shows deficiencies and affected rooms.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- A staff member has multiple certifications with different expiry dates and only one is expired.
- A renewal date is unknown or not yet provided for a newly hired staff member.
- A staff member is assigned to more than one room in the same day and only counts where scheduled.
- Credential records are updated after report generation; reports preserve generated-at timestamps.
- Required qualified count for a room changes due to age-band or policy updates mid-period.
- No staff are assigned to a room during an expected operating window.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST store per-staff compliance records for CPR/first-aid certifications and
  background checks, including issue date, renewal date, and verification status.
- **FR-002**: System MUST classify each tracked credential as compliant, expiring soon, or expired
  based on configurable warning windows.
- **FR-003**: System MUST provide directors with a consolidated list of all staff who are expiring soon
  or overdue, sorted by nearest deadline.
- **FR-004**: System MUST maintain room-level required ratio-qualified staffing thresholds.
- **FR-005**: System MUST calculate current ratio-qualified staff counts per room from active staff
  assignments.
- **FR-006**: System MUST flag rooms whose current qualified count is below required thresholds and show
  the numeric shortfall.
- **FR-007**: Directors MUST be able to update credential records and effective dates when renewals are
  completed.
- **FR-008**: System MUST produce a timestamped inspector-ready compliance summary including
  organization-wide credential status, upcoming deadlines, overdue items, and room coverage.
- **FR-009**: System MUST preserve historical snapshots of generated compliance summaries for audit
  evidence.
- **FR-010**: System MUST record an audit trail of compliance data changes, including who changed what
  and when.
- **FR-011**: Staff user accounts MUST be created in Cloud Keycloak and synchronized to Edge Keycloak
  replica when a staff member is added.
- **FR-012**: Staff role assignments (teacher, director, substitute) MUST be managed through Keycloak
  groups and roles.

### Key Entities *(include if feature involves data)*

- **Staff Member**: Represents an employee requiring licensing-related checks; key attributes include
  staff identifier, name, employment status, and role qualification flags.
- **Credential Record**: Represents a single compliance credential (CPR/first-aid or background check)
  for a staff member; includes credential type, issue date, renewal date, verification status, and
  compliance status.
- **Room Requirement**: Represents required ratio-qualified staffing thresholds for a room; includes
  room identifier, required qualified count, effective date, and policy basis.
- **Room Assignment**: Represents staff-to-room scheduling for a date/time window; used to calculate
  qualified coverage.
- **Compliance Alert**: Represents a generated warning or violation for expiring credentials,
  overdue renewals, or room coverage shortfalls.
- **Audit Summary Snapshot**: Represents a generated, timestamped compliance evidence package and its
  included metrics at generation time.
- **Compliance Change Log**: Represents immutable events for record updates and status changes,
  including actor, timestamp, prior value, and new value.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 100% of staff with required credentials have visible next renewal dates and current
  compliance statuses in the director compliance view.
- **SC-002**: Directors can identify all expiring-within-30-days and overdue credential records within
  60 seconds of opening the compliance dashboard.
- **SC-003**: 100% of rooms display required versus current ratio-qualified counts and clear compliant/
  non-compliant status during operating hours.
- **SC-004**: Directors can generate an inspector-ready compliance summary in under 2 minutes.
- **SC-005**: In pilot audits, at least 95% of inspector information requests related to staff
  credentials and room coverage are satisfied from generated compliance summaries without manual lookup.

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- Directors and authorized administrators are the only users who can manage compliance records and
  generate inspector summaries.
- Renewal reminder windows are organization-configurable, with a default of 30 days before expiration.
- Existing staff directory and room roster data are available and reused for this feature.
- This feature covers CPR/first-aid and background-check compliance only; other credential types may be
  added later.
- Licensing audit processes accept timestamped digital compliance summaries as evidence when records are
  complete.

## Constitution Alignment *(mandatory)*

### Phase Classification

- **Target Phase**: Phase 1
- **Prerequisite Validation**: This is part of the Phase 1 operational core (Staff Credential
  Tracker) required before AI/behavioral feature rollout.

### Privacy, Consent, and Residency Impact

- **Child Sensitive Data Used**: None. This feature processes staff compliance and scheduling records,
  not child biometric, video, or audio data.
- **Edge Processing Boundary**: Not applicable for inference boundaries because no CV/audio/biometric
  inference is used; only operational compliance metadata is processed.
- **Consent Requirement**: Parental biometric consent is not required for this feature. Staff data
  handling must still follow employment and privacy policies with role-based access and audit logging.
- **Retention and Auto-Delete**: Compliance snapshots and change logs follow region-configured
  retention policies with secure archival and deletion schedules.
- **Regional Residency Scope**: US, EU, and GCC support required; compliance data stays within the
  configured regional data store.

### Safety and Non-Diagnostic Compliance

- **Behavioral or Safety Outputs**: Outputs are administrative compliance indicators only
  (compliant/expiring/overdue and room coverage status).
- **Prohibited Output Check**: No medical or behavioral condition labels, and no diagnostic confidence
  outputs are produced.
- **Audience Boundary**: Compliance alerts are director/admin and authorized staff operations views
  only; no automated parent-facing labels are generated.
