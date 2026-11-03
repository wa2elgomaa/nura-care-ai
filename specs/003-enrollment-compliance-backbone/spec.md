# Feature Specification: Enrollment Compliance Backbone

**Feature Branch**: `003-enrollment-compliance-backbone`

**Created**: 2026-07-22

**Status**: Draft

**Input**: User description: "As a director or admin, I want to capture enrollment forms, medical/allergy records, immunisation proof, emergency contacts, and consent forms (including biometric opt-ins) in a single digital workspace, so that I have a complete, auditable compliance backbone for every child."

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

### User Story 1 - Create Complete Enrollment Record (Priority: P1)

As a director or admin, I can create and maintain one complete child compliance record that combines
enrollment, health, emergency, and consent documentation in a single workspace.

**Why this priority**: A complete baseline record is required before safe care operations and
regulatory reviews can be reliably performed.

**Independent Test**: Can be tested independently by enrolling a child and verifying all required
document categories can be captured, tracked, and retrieved from one record.

**Acceptance Scenarios**:

1. **Given** a newly enrolled child,
   **When** the director or admin opens the compliance workspace,
   **Then** they can add enrollment forms, medical/allergy records, immunisation proof, emergency
   contacts, and consent forms under that child record.
2. **Given** a child record with partial documentation,
   **When** the director or admin reviews compliance status,
   **Then** missing required items are clearly indicated for follow-up.

---

### User Story 2 - Manage Consent Lifecycle (Priority: P2)

As a director or admin, I can collect, update, and revoke family consents, including biometric opt-ins,
with clear status history so that data handling is always permission-aligned.

**Why this priority**: Consent integrity is a legal and trust-critical control for child data
processing, especially for biometric workflows.

**Independent Test**: Can be tested independently by recording consent decisions, changing consent
state, and verifying current status and historical actions are auditable.

**Acceptance Scenarios**:

1. **Given** a family has not yet provided biometric consent,
   **When** the admin records consent status,
   **Then** the child record reflects biometric processing as not permitted until explicit opt-in is
   documented.
2. **Given** a family revokes a previously granted consent,
   **When** revocation is recorded,
   **Then** the child record updates immediately and the change is preserved in consent history.

---

### User Story 3 - Produce Audit-Ready Compliance Evidence (Priority: P3)

As a director, I can review and export an auditable timeline of document submissions, updates,
approvals, and consent changes for each child.

**Why this priority**: Audit readiness reduces inspection risk and improves confidence that compliance
obligations are continuously met.

**Independent Test**: Can be tested independently by generating evidence outputs for selected child
records and confirming timeline completeness and traceability.

**Acceptance Scenarios**:

1. **Given** a child record with document and consent history,
   **When** a director requests a compliance review,
   **Then** the system shows a chronological audit trail with actor, action, and timestamp.
2. **Given** an upcoming inspection,
   **When** the director prepares compliance evidence,
   **Then** the system provides child-level records indicating completeness and outstanding items.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- A child is transferred between rooms/sites while enrollment documents are still incomplete.
- Immunisation proof is uploaded but unreadable or expired.
- Emergency contact entries contain duplicate people with conflicting phone numbers.
- Medical/allergy records are updated after consent forms were signed and require re-acknowledgement.
- Parent grants biometric consent for one child but not siblings in the same household.
- Consent is revoked during active enrollment period and previous records must remain auditable.
- Required documentation deadlines pass without completion.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST provide a single child-centric workspace that stores enrollment forms,
  medical/allergy records, immunisation proof, emergency contacts, and consent forms together.
- **FR-002**: System MUST define required document categories and mark each child record as complete,
  incomplete, or overdue based on required items.
- **FR-003**: System MUST allow authorized directors/admins to add, update, replace, and review
  compliance documents without breaking audit continuity.
- **FR-004**: System MUST support structured emergency contact capture including contact role,
  priority, and reachable details.
- **FR-005**: System MUST support medical and allergy record capture with effective dates and status so
  current safety information is distinguishable from historical entries.
- **FR-006**: System MUST support immunisation proof capture and status tracking, including expired or
  soon-due indicators.
- **FR-007**: System MUST capture explicit consent decisions by consent type, including biometric
  opt-in, and store current status per child.
- **FR-008**: System MUST record consent lifecycle events (granted, denied, revoked, updated) with
  actor identity and timestamp.
- **FR-009**: System MUST restrict biometric-permission status to opt-in only and treat missing consent
  as not permitted by default.
- **FR-010**: System MUST provide a child-level compliance timeline that includes document actions,
  consent changes, and status transitions.
- **FR-011**: System MUST provide filters and reporting views that let directors identify incomplete,
  overdue, or high-risk records across all active children.
- **FR-012**: System MUST retain auditable history of all compliance record changes in alignment with
  regional retention policies.
- **FR-013**: When a child is enrolled, the system MUST automatically create or update parent user
  accounts in Cloud Keycloak through the Keycloak Admin API and trigger sync to Edge Keycloak for the
  relevant site.

### Key Entities *(include if feature involves data)*

- **Child Compliance Profile**: Consolidated record for one child containing compliance status,
  required-item checklist, and links to all supporting records.
- **Enrollment Form Record**: Enrollment intake data and form submission history associated with a
  child compliance profile.
- **Medical and Allergy Record**: Child health safety details, including allergies, care notes,
  effective dates, and historical revisions.
- **Immunisation Proof Record**: Submitted evidence of immunisation status with validity and review
  metadata.
- **Emergency Contact Record**: Authorized contact entries with relationship, priority order, and
  communication details.
- **Consent Record**: Consent decisions by type (including biometric), current state, and legal
  acknowledgment references.
- **Compliance Audit Event**: Immutable event entry describing who changed what, when, and why in the
  compliance workspace.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 95% of newly enrolled children have all required compliance records completed within
  5 business days of enrollment start.
- **SC-002**: Directors/admins can retrieve a child's full compliance record in under 30 seconds for
  at least 95% of lookup attempts.
- **SC-003**: 100% of biometric-related child records show explicit consent state (opted in, not
  opted in, or revoked) with auditable history.
- **SC-004**: 100% of document and consent state changes are represented in audit history with actor
  and timestamp.
- **SC-005**: Overdue compliance items across active children are reduced by at least 60% within the
  first 90 days after rollout compared with pre-rollout baseline.

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- Directors and designated admins are the primary users authorized to manage child compliance records.
- Families provide source documents through existing enrollment or admin-assisted intake processes.
- Existing child identity records are already available and reused as the anchor for compliance
  profiles.
- Regulatory document requirements may vary by region and are configurable through policy settings.
- This feature focuses on compliance record management and auditability, not automated clinical or
  diagnostic interpretation.

## Constitution Alignment *(mandatory)*

### Phase Classification

- **Target Phase**: Phase 1
- **Prerequisite Validation**: This capability is part of mandatory operational foundations and
  compliance readiness needed before higher-phase AI features.

### Privacy, Consent, and Residency Impact

- **Child Sensitive Data Used**: Child identity data, medical/allergy records, immunisation proof,
  emergency contact details, and consent records including biometric permission state.
- **Edge Processing Boundary**: This feature stores and manages compliance records and consent metadata;
  no raw biometric media processing is required within this workflow.
- **Consent Requirement**: Biometric-related permission must be explicit opt-in, revocable, and
  auditable; absence of explicit consent is treated as not permitted.
- **Retention and Auto-Delete**: Compliance records and audit events follow regional retention policy
  controls with auto-delete defaults where legally allowed and legal-hold exceptions where required.
- **Regional Residency Scope**: US, EU, and GCC regional data residency support is required for
  compliance and consent records.

### Safety and Non-Diagnostic Compliance

- **Behavioral or Safety Outputs**: Outputs are compliance status indicators and record completeness
  alerts for staff operations.
- **Prohibited Output Check**: No diagnostic labels, medical condition predictions, or diagnostic
  confidence outputs are generated.
- **Audience Boundary**: Administrative compliance views are staff-facing; parent-facing communication
  remains constrained to approved record-sharing policies.
