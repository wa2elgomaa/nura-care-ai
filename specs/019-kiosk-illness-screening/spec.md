# Feature Specification: Kiosk Illness Screening

**Feature Branch**: `019-kiosk-illness-screening`

**Created**: 2026-07-22

**Status**: Draft

**Input**: User description: "As a director, I want a kiosk that takes a child’s thermal temperature and optionally collects a parent-declared symptom checklist at drop-off, and feeds this into the attendance/absence module, so that we screen for illness without creating an administrative bottleneck."

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

### User Story 1 - Fast Drop-Off Screening Capture (Priority: P1)

As a director, I want each child drop-off to capture thermal temperature and optional parent symptom
declaration quickly so entry screening is consistent and efficient.

**Why this priority**: This is the core workflow needed to reduce bottlenecks while maintaining
screening coverage.

**Independent Test**: Can be tested independently by running drop-off sessions and confirming
temperature capture plus optional symptom checklist completion in a short interaction.

**Acceptance Scenarios**:

1. **Given** a child arrives at drop-off,
   **When** screening begins at the kiosk,
   **Then** thermal temperature is captured and associated with the child attendance attempt.
2. **Given** parent chooses to provide symptom details,
   **When** they complete the optional checklist,
   **Then** responses are recorded and linked to the same screening event.

---

### User Story 2 - Attendance and Absence Workflow Integration (Priority: P2)

As a teacher/admin, I want screening outcomes to feed directly into attendance and absence workflows
so staff do not need duplicate manual entry.

**Why this priority**: Removes administrative friction and preserves operational throughput at peak
arrival times.

**Independent Test**: Can be tested independently by verifying screening records automatically appear
in attendance/absence views and influence status guidance.

**Acceptance Scenarios**:

1. **Given** screening data is captured,
   **When** the attendance module updates,
   **Then** attendance status includes screening context without extra manual steps.
2. **Given** screening criteria indicate follow-up is needed,
   **When** staff review attendance/absence queue,
   **Then** the child entry is flagged for policy-driven review before final check-in decision.

---

### User Story 3 - Director Oversight and Auditability (Priority: P3)

As a director, I can monitor screening throughput, follow-up rates, and exceptions to ensure policy
compliance without slowing front-desk operations.

**Why this priority**: Provides accountability and continuous process improvement for health screening
operations.

**Independent Test**: Can be tested independently by reviewing screening reports for completion,
follow-up outcomes, and processing time trends.

**Acceptance Scenarios**:

1. **Given** daily screening events are completed,
   **When** director opens oversight reports,
   **Then** they can view completion rates, flagged cases, and average screening time.
2. **Given** a screening record is disputed,
   **When** director inspects audit history,
   **Then** kiosk capture details and status changes are traceable.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- Parent skips optional symptom checklist but temperature is captured.
- Kiosk thermal reading is unavailable or unreadable on first attempt.
- Same child is screened twice during a busy drop-off period.
- Child arrives with different guardian than normal and consent context must be verified.
- Connectivity interruption occurs after screening capture but before attendance sync.
- Kiosk queue surges create wait-time spikes near program start cutoff.
- Screening indicates follow-up threshold while parent disputes measurement accuracy.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST capture a thermal temperature reading for each child screening attempt at
  drop-off.
- **FR-002**: System MUST provide an optional parent-declared symptom checklist and record submitted
  responses when completed.
- **FR-003**: System MUST associate screening data with the correct child and same-day attendance
  attempt.
- **FR-004**: System MUST update attendance/absence workflows automatically with screening context and
  follow-up indicators.
- **FR-005**: System MUST allow screening completion to continue when optional symptom checklist is
  skipped.
- **FR-006**: System MUST handle unreadable or failed thermal captures with immediate retry or
  staff-assisted fallback guidance.
- **FR-007**: System MUST prevent duplicate finalized screening records for the same child and drop-off
  event window.
- **FR-008**: System MUST support offline-tolerant capture and synchronize queued screening metadata
  when connectivity returns.
- **FR-009**: System MUST provide policy-driven follow-up flagging based on temperature/symptom
  criteria without issuing diagnostic conclusions.
- **FR-010**: System MUST provide director/staff reporting on throughput, flagged cases, and unresolved
  exceptions.
- **FR-011**: System MUST enforce role-based visibility so sensitive screening details are limited to
  authorized staff and directors.
- **FR-012**: System MUST maintain auditable logs of screening capture, checklist declarations,
  attendance linkage, and status changes.

### Key Entities *(include if feature involves data)*

- **Screening Event**: Single drop-off screening record containing temperature capture outcome,
  timestamp, and child linkage.
- **Symptom Declaration**: Optional parent-submitted checklist responses tied to a screening event.
- **Attendance Screening Link**: Relationship object connecting screening event outcomes to attendance
  or absence status workflow.
- **Follow-Up Flag**: Policy-triggered indicator for staff review before final entry decision.
- **Screening Queue State**: Operational state for pending, synchronized, or exception screening items.
- **Screening Audit Entry**: Immutable trail of capture actions, edits, and workflow decisions.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: At least 95% of child drop-offs complete temperature screening in under 45 seconds.
- **SC-002**: At least 90% of optional symptom checklists submitted by parents are linked to
  attendance records without manual correction.
- **SC-003**: Duplicate finalized screening records remain below 0.2% of daily screened entries.
- **SC-004**: Screening-related administrative manual data entry time is reduced by at least 60%
  compared to pre-kiosk process.
- **SC-005**: 100% of flagged follow-up cases appear in staff review queues with auditable status
  tracking.

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- Attendance and absence modules are already operational and can accept screening-linked metadata.
- Nursery policy defines screening follow-up thresholds and staff escalation procedures.
- Parents/guardians can complete quick kiosk interactions at drop-off.
- Optional symptom declaration is informational and not mandatory for routine check-in processing.
- This feature supports operational illness screening and does not provide medical diagnosis.

## Constitution Alignment *(mandatory)*

### Phase Classification

- **Target Phase**: Phase 1
- **Prerequisite Validation**: Aligns with Phase 1 operational core readiness for attendance and
  medication cross-check workflows before higher-risk behavioral releases.

### Privacy, Consent, and Residency Impact

- **Child Sensitive Data Used**: Thermal temperature readings and optional symptom declarations are
  treated as sensitive health-adjacent child data.
- **Edge Processing Boundary**: Kiosk capture occurs locally; only required operational metadata for
  attendance and follow-up workflows is synchronized.
- **Consent Requirement**: Parent/guardian symptom declaration is optional and explicitly submitted;
  capture and use are auditable under policy-defined consent and notice rules.
- **Retention and Auto-Delete**: Screening metadata follows regional retention windows with secure
  deletion defaults and policy exceptions where legally required.
- **Regional Residency Scope**: US, EU, and GCC residency controls apply to screening and audit data.

### Safety and Non-Diagnostic Compliance

- **Behavioral or Safety Outputs**: Outputs are operational screening status and follow-up flags for
  staff workflows.
- **Prohibited Output Check**: No diagnostic conclusions, disorder labels, or medical certainty claims
  are generated.
- **Audience Boundary**: Detailed screening data is staff/director-facing; parent-facing messages use
  policy-approved non-diagnostic wording.
