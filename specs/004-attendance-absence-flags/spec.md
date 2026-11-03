# Feature Specification: Attendance and Absence Flags

**Feature Branch**: `004-attendance-absence-flags`

**Created**: 2026-07-22

**Status**: Draft

**Input**: User description: "As a teacher, I want to check children in/out via badge, QR code, or kiosk, and have the system auto-flag unexplained absences after a configurable threshold, so that I can quickly follow up with parents and maintain accurate daily rolls for ratio compliance."

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

### User Story 1 - Flexible Daily Check-In/Out (Priority: P1)

As a teacher, I can check children in and out using badge, QR code, or kiosk entry so daily attendance
is captured quickly and consistently.

**Why this priority**: Accurate attendance capture is foundational for child safety, daily operations,
and ratio management.

**Independent Test**: Can be tested independently by processing check-in and check-out events across
all three entry methods and confirming a correct daily roll is created.

**Acceptance Scenarios**:

1. **Given** a child is expected for the day,
   **When** the teacher checks the child in using badge, QR code, or kiosk,
   **Then** the child is marked present with timestamp and method used.
2. **Given** a child is currently marked present,
   **When** the teacher checks the child out,
   **Then** the child is marked not currently on-site and the departure timestamp is recorded.
3. **Given** multiple children arrive within a short period,
   **When** the teacher uses mixed check-in methods,
   **Then** each child's attendance state is recorded accurately without overwriting others.

---

### User Story 2 - Auto-Flag Unexplained Absences (Priority: P2)

As a teacher, I receive automatic alerts for children who have not checked in by a configurable
time threshold and do not have a documented absence reason.

**Why this priority**: Early absence detection reduces follow-up delays and supports child welfare and
family communication.

**Independent Test**: Can be tested independently by configuring thresholds, simulating missing
check-ins, and verifying the system flags only unexplained absences.

**Acceptance Scenarios**:

1. **Given** a configured morning threshold and expected attendance list,
   **When** the threshold passes for a child without check-in and without recorded reason,
   **Then** the system flags an unexplained absence for follow-up.
2. **Given** a child has a pre-recorded valid absence reason,
   **When** the threshold passes without check-in,
   **Then** no unexplained absence flag is generated for that child.

---

### User Story 3 - Follow-Up and Ratio-Ready Roll (Priority: P3)

As a teacher and director, we can review unresolved absence flags and maintain an accurate, current
roll that supports classroom ratio decisions.

**Why this priority**: Follow-up accountability and roll integrity help prevent supervision gaps and
compliance risk during active care hours.

**Independent Test**: Can be tested independently by resolving flagged absences, recording outcomes,
and verifying roll and follow-up states update correctly.

**Acceptance Scenarios**:

1. **Given** unresolved unexplained absence flags,
   **When** staff log follow-up outcomes,
   **Then** each flag moves to an updated status with timestamp and actor information.
2. **Given** daily attendance events and resolved follow-ups,
   **When** the current roll is viewed,
   **Then** on-site counts and absent counts reflect latest attendance and absence status.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- Child is checked in twice using different methods within a short interval.
- Child is checked out without a prior same-day check-in record.
- QR or badge scan is unreadable and kiosk fallback is used.
- Family notifies absence after an unexplained flag is already generated.
- Threshold configuration changes mid-day and pending flags need recalculation rules.
- Child transfers classrooms during the day and attendance state must remain continuous.
- Network interruption occurs during check-in/out and events sync later.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST support child check-in and check-out through badge, QR code, and kiosk
  methods.
- **FR-002**: System MUST maintain one current attendance state per child indicating on-site,
  checked-out, absent with reason, or unexplained absence.
- **FR-003**: System MUST record attendance events with child identity, event type, method, timestamp,
  and acting staff member.
- **FR-004**: System MUST prevent duplicate same-moment attendance events from creating conflicting
  current state and MUST preserve event history.
- **FR-005**: System MUST allow authorized staff to configure unexplained absence thresholds by
  operational context.
- **FR-006**: System MUST generate unexplained absence flags only when a child has not checked in by
  threshold time and no valid absence reason is recorded.
- **FR-007**: System MUST allow staff to record absence reasons and follow-up outcomes against flags.
- **FR-008**: System MUST update flag status from open to resolved when follow-up outcome is logged.
- **FR-009**: System MUST provide live classroom and center-level daily roll views that reflect latest
  attendance states.
- **FR-010**: System MUST provide directors with a daily unresolved absence queue sorted by urgency or
  elapsed time since threshold breach.
- **FR-011**: System MUST retain an auditable history of attendance events, threshold-triggered flags,
  and follow-up actions.
- **FR-012**: System MUST continue to support attendance capture during temporary connectivity loss and
  reconcile records once connectivity is restored.

### Key Entities *(include if feature involves data)*

- **Child Daily Attendance Record**: Current-day attendance state for one child, including latest
  check-in/out status and timestamps.
- **Attendance Event**: Immutable check-in or check-out event including method, timestamp, actor, and
  source context.
- **Absence Reason Record**: Documented reason for expected absence, validity window, and submitter.
- **Absence Threshold Policy**: Configurable rule defining when an expected child without check-in is
  considered unexplained.
- **Unexplained Absence Flag**: Alert generated when threshold criteria are met, including status,
  urgency, and follow-up owner.
- **Follow-Up Action Log**: Recorded outreach and resolution outcomes linked to each absence flag.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: At least 98% of attendance events are captured successfully on first attempt across badge,
  QR, and kiosk methods during staffed hours.
- **SC-002**: 100% of expected children without check-in and without valid absence reason are flagged
  as unexplained within 2 minutes after configured threshold breach.
- **SC-003**: 95% of unexplained absence flags receive first follow-up action within 15 minutes of
  flag creation.
- **SC-004**: Daily roll accuracy, measured against validated end-of-day reconciliation, reaches at
  least 99%.
- **SC-005**: Ratio-related attendance discrepancies identified during daily operations are reduced by
  at least 70% compared with pre-rollout baseline.

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- Teachers and directors already have role-based authorization for attendance and follow-up workflows.
- Expected daily child roster is available before threshold evaluation begins.
- Families can submit planned absence reasons through existing communication channels integrated into
  operations.
- Attendance threshold defaults are centrally defined but configurable by authorized administrators.
- This feature addresses attendance operations and parent follow-up initiation, not medical diagnosis
  or behavioral inference.

## Constitution Alignment *(mandatory)*

### Phase Classification

- **Target Phase**: Phase 1
- **Prerequisite Validation**: Attendance is explicitly required in Phase 1 operational core sequencing
  and underpins ratio compliance and daily safety operations.

### Privacy, Consent, and Residency Impact

- **Child Sensitive Data Used**: Child identity, attendance timestamps, room assignment context,
  attendance method metadata, and absence/follow-up records.
- **Edge Processing Boundary**: This workflow processes operational attendance metadata and does not
  require exporting raw video or raw biometric embeddings for routine attendance state tracking.
- **Consent Requirement**: If badge or QR workflows involve biometric-linked identity artifacts,
  biometric usage remains explicit opt-in and revocable per child profile; non-biometric kiosk entry is
  available as an operational alternative.
- **Retention and Auto-Delete**: Attendance and follow-up records follow region-specific retention and
  auto-delete policies with legal-hold exceptions as required.
- **Regional Residency Scope**: US, EU, and GCC regional residency obligations apply to attendance and
  follow-up records.

### Safety and Non-Diagnostic Compliance

- **Behavioral or Safety Outputs**: Outputs include attendance state, unexplained absence flags, and
  follow-up status prompts for staff action.
- **Prohibited Output Check**: No diagnostic labels, disorder predictions, or diagnostic confidence
  outputs are generated.
- **Audience Boundary**: Attendance and unexplained-absence operational alerts are staff-facing;
  parent-facing communications remain controlled through approved follow-up workflows.
