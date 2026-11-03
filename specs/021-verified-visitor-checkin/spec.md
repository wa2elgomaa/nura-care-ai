# Feature Specification: Verified Visitor Check-In

**Feature Branch**: `021-verified-visitor-checkin`

**Created**: 2026-07-22

**Status**: Draft

**Input**: User description: "As a director, I want to check in visitors (inspectors, plumbers, substitutes) using the same verified-access logic as guardian pickup, with expiry-based credentials, so that I can track everyone entering the building."

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

### User Story 1 - Verified Visitor Entry (Priority: P1)

As a director/front-desk staff member, I can verify and check in visitors using the same trusted
access logic as guardian pickup before granting entry.

**Why this priority**: Secure identity verification is the core safety requirement for visitor access.

**Independent Test**: Can be tested independently by attempting visitor check-ins with valid and
invalid credentials and confirming only verified entries are approved.

**Acceptance Scenarios**:

1. **Given** a visitor arrives,
   **When** staff initiates check-in,
   **Then** the system verifies visitor identity and authorization using pickup-grade access rules.
2. **Given** verification succeeds,
   **When** entry is approved,
   **Then** a check-in record with timestamp and purpose is created.

---

### User Story 2 - Expiry-Based Visitor Credentials (Priority: P2)

As a director, I can issue and manage time-limited visitor credentials so building access expires
automatically after approved windows.

**Why this priority**: Time-bounded credentials reduce risk from stale or reused access.

**Independent Test**: Can be tested independently by issuing expiring credentials and confirming they
work only during authorized periods.

**Acceptance Scenarios**:

1. **Given** a substitute or contractor is expected,
   **When** staff issues a temporary credential,
   **Then** the credential includes explicit start and expiry boundaries.
2. **Given** a credential has expired,
   **When** the visitor attempts entry,
   **Then** access is denied and staff receives follow-up guidance.

---

### User Story 3 - Building-Wide Visitor Tracking and Audit (Priority: P3)

As a director, I can see who is currently in the building and review full visitor history for safety,
compliance, and incident response.

**Why this priority**: Complete visibility and auditability support safeguarding and regulatory
readiness.

**Independent Test**: Can be tested independently by checking active visitor lists and historical logs
for accurate check-in/check-out trails.

**Acceptance Scenarios**:

1. **Given** multiple visitors are present,
   **When** director opens active occupancy view,
   **Then** all currently checked-in visitors are listed with role and location context.
2. **Given** an audit or incident review is required,
   **When** director filters visitor history,
   **Then** complete entry/exit records and verification outcomes are available.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- Visitor credential is valid but assigned to a different centre.
- Contractor needs repeated access over several days with varying time windows.
- Visitor forgets to check out, leaving active occupancy list inaccurate.
- Connectivity drops during check-in after verification but before log persistence.
- Emergency evacuation occurs while temporary visitors are on site.
- A denied visitor disputes the verification result at front desk.
- Duplicate visitor profiles exist with similar names and roles.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST support visitor check-in workflows for inspectors, contractors, substitutes,
  and other non-guardian adults.
- **FR-002**: System MUST apply the same verified-access rule set used for guardian pickup to visitor
  authorization decisions.
- **FR-003**: System MUST issue visitor credentials with explicit validity start and expiry times.
- **FR-004**: System MUST deny or block access attempts for expired, revoked, or invalid credentials.
- **FR-005**: System MUST record check-in and check-out events with timestamp, visitor type, purpose,
  and centre context.
- **FR-006**: System MUST maintain an active in-building visitor roster based on check-in status.
- **FR-007**: System MUST provide staff workflows for manual override requests subject to documented
  approval and audit capture.
- **FR-008**: System MUST prevent duplicate finalized access sessions for the same visitor within the
  same visit window.
- **FR-009**: System MUST support offline-tolerant capture of visitor access events and synchronize
  metadata when connectivity returns.
- **FR-010**: System MUST provide search/filterable visitor history for audit, compliance, and
  incident-response use.
- **FR-011**: System MUST enforce role-based permissions so only authorized personnel can create,
  approve, or review visitor access records.
- **FR-012**: System MUST retain auditable logs for credential issuance, access decisions, overrides,
  and entry/exit lifecycle actions.

### Key Entities *(include if feature involves data)*

- **Visitor Profile**: Identity and role record for a non-guardian adult requesting site access.
- **Visitor Credential**: Time-bounded authorization artifact with validity window and status.
- **Access Verification Result**: Decision object capturing pass/fail outcome and reason code.
- **Visitor Session**: Active or completed in-building presence record from check-in to check-out.
- **Override Approval Record**: Documented authorization event for exceptions to standard verification.
- **Visitor Audit Log Entry**: Immutable trace of credential, verification, and movement events.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: At least 95% of verified visitor check-ins complete in under 60 seconds at front desk.
- **SC-002**: 100% of expired credential attempts are denied and logged with actionable reason
  feedback.
- **SC-003**: At least 99% of completed visitor sessions include both check-in and check-out timestamps
  after operational stabilization.
- **SC-004**: Manual visitor log reconciliation effort is reduced by at least 70% compared to the
  pre-feature process.
- **SC-005**: 100% of active-occupancy and historical visitor audit views are available to authorized
  directors during compliance review windows.

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- Verified-access logic from guardian pickup is already available and trusted operationally.
- Centre staff can identify visitor purpose and expected duration at arrival.
- Each centre has a front-desk or reception workflow for entry control.
- Visitor check-in policy defines when overrides are allowed and who can approve them.
- This feature manages access verification and tracking, not medical or behavioral assessment.

## Constitution Alignment *(mandatory)*

### Phase Classification

- **Target Phase**: Phase 1
- **Prerequisite Validation**: Builds on Phase 1 operational safety and attendance controls,
  extending verified-access governance to all building entrants.

### Privacy, Consent, and Residency Impact

- **Child Sensitive Data Used**: Feature primarily processes adult visitor identity and access metadata,
  while indirectly protecting child environments.
- **Edge Processing Boundary**: Verification and session capture can execute locally with only required
  access metadata synchronized for centralized oversight.
- **Consent Requirement**: Visitor identity capture and credential issuance follow notice and
  policy-consent procedures appropriate for premises access control.
- **Retention and Auto-Delete**: Visitor access metadata follows region-configurable retention windows
  and secure deletion requirements.
- **Regional Residency Scope**: US, EU, and GCC residency controls apply to visitor access and audit
  records.

### Safety and Non-Diagnostic Compliance

- **Behavioral or Safety Outputs**: Outputs are access approvals/denials, active occupancy status, and
  visitor tracking summaries.
- **Prohibited Output Check**: No diagnostic labels, disorder names, or clinical conclusions are
  produced.
- **Audience Boundary**: Detailed visitor verification and movement logs are staff/director-facing
  only.
