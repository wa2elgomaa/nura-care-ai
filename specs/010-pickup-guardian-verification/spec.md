# Feature Specification: Pickup Guardian Verification

**Feature Branch**: `010-pickup-guardian-verification`

**Created**: 2026-07-22

**Status**: Draft

**Input**: User description: "As a director, I want to verify a guardian's identity at pickup via QR code, PIN, or optional on-device facial match, and receive an alert if a non-authorised person attempts pickup, so that I can prevent unauthorised access and document every handover."

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

### User Story 1 - Verify Pickup Identity at Handover (Priority: P1)

As a director or authorized staff member, I can verify guardian identity at pickup using approved
methods before releasing a child.

**Why this priority**: Identity verification at handover is a direct child-safety control and must be
reliable under daily operations.

**Independent Test**: Can be tested independently by completing pickup with each approved method and
verifying handover is allowed only after successful identity check.

**Acceptance Scenarios**:

1. **Given** an authorized guardian arrives for pickup,
   **When** staff validates identity using QR code or PIN,
   **Then** pickup is approved and child handover can proceed.
2. **Given** optional facial verification is enabled and consented,
   **When** staff initiates on-device facial match,
   **Then** pickup is approved only if the match result is successful.

---

### User Story 2 - Detect and Alert Unauthorized Attempts (Priority: P2)

As a director, I receive immediate alerts when a non-authorized person attempts pickup so staff can
intervene safely.

**Why this priority**: Rapid unauthorized-attempt detection reduces risk of improper child release.

**Independent Test**: Can be tested independently by simulating unauthorized pickup attempts and
verifying immediate alert creation and escalation flow.

**Acceptance Scenarios**:

1. **Given** a pickup attempt fails authorization,
   **When** verification checks complete,
   **Then** pickup is blocked and an immediate alert is sent to designated staff.
2. **Given** repeated failed attempts occur for the same child,
   **When** attempt thresholds are reached,
   **Then** alert severity is escalated according to safety policy.

---

### User Story 3 - Maintain Full Pickup Audit Trail (Priority: P3)

As a director and compliance reviewer, I can view complete records of each handover, including
verification method, result, and responsible staff action.

**Why this priority**: Auditability supports investigations, policy enforcement, and regulatory
evidence.

**Independent Test**: Can be tested independently by reviewing recorded pickup events and confirming
all required verification and decision details are present.

**Acceptance Scenarios**:

1. **Given** a completed pickup event,
   **When** a director reviews handover history,
   **Then** the record includes child, guardian, verification method, outcome, timestamp, and staff
   identity.
2. **Given** a blocked pickup attempt,
   **When** compliance audit is requested,
   **Then** the system provides the blocked-attempt timeline, alerts generated, and resolution notes.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- Guardian forgets QR and PIN but is otherwise authorized.
- Child has multiple authorized guardians arriving simultaneously.
- QR token is expired, reused, or presented from an unrecognized device.
- PIN is entered incorrectly multiple times within a short window.
- Optional facial match is requested but consent is absent or revoked.
- Temporary camera or device issue prevents facial verification at pickup station.
- Network outage occurs during pickup and verification must continue safely.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST support guardian pickup verification using QR code, PIN, and optionally
  on-device facial match when consented.
- **FR-002**: System MUST validate that a pickup requester is explicitly authorized for the specific
  child before handover approval.
- **FR-003**: System MUST block child handover when identity verification fails or authorization is not
  present.
- **FR-004**: System MUST generate immediate staff alerts for unauthorized pickup attempts.
- **FR-005**: System MUST support alert escalation rules for repeated or high-risk unauthorized
  attempts.
- **FR-006**: System MUST require explicit consent before optional facial verification can be used.
- **FR-007**: System MUST execute optional facial verification on local edge processing boundaries and
  prevent raw biometric embedding export.
- **FR-008**: System MUST support secure fallback verification paths when one method is unavailable,
  while maintaining authorization requirements.
- **FR-009**: System MUST record every pickup attempt and handover decision with method used,
  outcome, timestamp, and acting staff identity.
- **FR-010**: System MUST provide directors with searchable pickup audit history and incident logs.
- **FR-011**: System MUST support immediate session reset and lockout safeguards after suspicious
  repeated verification failures.
- **FR-012**: System MUST maintain pickup verification continuity during temporary connectivity
  interruptions and reconcile audit records afterward.

### Key Entities *(include if feature involves data)*

- **Guardian Authorization Record**: Allowed guardian-child relationship with validity window,
  permissions, and status.
- **Pickup Verification Attempt**: Single identity-check attempt containing method, result,
  timestamp, and staff operator context.
- **Pickup Handover Event**: Final handover decision record (approved or blocked) for a child pickup
  transaction.
- **Consent Record**: Consent state for optional biometric verification including opt-in status and
  revocation history.
- **Unauthorized Pickup Alert**: Alert event generated from failed or suspicious verification attempts,
  including severity and response status.
- **Pickup Audit Record**: Immutable compliance history of all pickup verification and handover actions.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: At least 99% of authorized pickup handovers complete with successful identity
  verification and full audit capture.
- **SC-002**: 100% of unauthorized pickup attempts are blocked before child release.
- **SC-003**: 100% of blocked unauthorized attempts generate alert notifications within 1 minute.
- **SC-004**: 100% of pickup events (approved or blocked) have retrievable audit records with required
  fields.
- **SC-005**: Unauthorized or unverified handover incidents are reduced by at least 80% compared with
  pre-feature baseline.

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- Authorized guardian rosters for each child are maintained and up to date before pickup windows.
- Staff devices at pickup points can perform QR/PIN checks and optional local biometric verification.
- Emergency override procedures exist and require documented supervisory approval.
- Consent lifecycle controls already exist for biometric opt-in and revocation.
- This feature addresses operational identity verification and safety handover controls, not medical
  diagnostics.

## Constitution Alignment *(mandatory)*

### Phase Classification

- **Target Phase**: Phase 1
- **Prerequisite Validation**: Pickup verification is part of the mandatory operational safety baseline
  and aligns with Phase 1 readiness before higher-risk AI capabilities.

### Privacy, Consent, and Residency Impact

- **Child Sensitive Data Used**: Child identity linkage, guardian identity references, pickup logs,
  alert records, and optional biometric verification artifacts when consented.
- **Edge Processing Boundary**: Optional facial verification remains on-device/on-edge; raw biometric
  embeddings and raw video are not exported to cloud systems.
- **Consent Requirement**: Facial verification is optional and strictly opt-in with revocation support;
  non-biometric methods remain available as primary alternatives.
- **Retention and Auto-Delete**: Pickup audit and incident records follow regional retention policies;
  biometric artifacts follow shortest legal retention with secure auto-delete defaults.
- **Regional Residency Scope**: US, EU, and GCC residency controls apply to pickup metadata and audit
  evidence.

### Safety and Non-Diagnostic Compliance

- **Behavioral or Safety Outputs**: Outputs include pickup verification status, unauthorized-attempt
  alerts, and handover decision records.
- **Prohibited Output Check**: No diagnostic labels, disorder names, or diagnostic confidence outputs
  are generated.
- **Audience Boundary**: Verification controls and incident alerts are staff-facing; parent-facing
  communication is limited to approved operational notifications.
