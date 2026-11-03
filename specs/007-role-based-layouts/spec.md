# Feature Specification: Role-Based Layouts

**Feature Branch**: `007-role-based-layouts`

**Created**: 2026-07-22

**Status**: Draft

**Input**: User description: "As a product owner, I want a single React Native codebase that renders different UI layouts (Parent, Teacher, Director, Tablet) based on the authenticated user's role, so that we maintain one codebase across all surfaces and drastically reduce engineering overhead."

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

### User Story 1 - Role-Driven Experience Selection (Priority: P1)

As an authenticated user, I am automatically presented with the correct interface layout for my role
(Parent, Teacher, Director, or Tablet context) without installing a separate app.

**Why this priority**: Correct role-based entry experience is the foundation for unified operations and
prevents fragmentation into multiple app variants.

**Independent Test**: Can be tested independently by signing in as each role type and confirming that
the initial navigation structure and primary screens match that role's responsibilities.

**Acceptance Scenarios**:

1. **Given** a user authenticates with Parent role,
   **When** the session starts,
   **Then** the parent-focused layout and navigation are shown by default.
2. **Given** a user authenticates with Teacher or Director role,
   **When** the session starts,
   **Then** the corresponding operational layout is shown with role-relevant entry points.
3. **Given** a tablet-designated session is initiated,
   **When** the user opens the app,
   **Then** the tablet-optimized layout is shown with shared core behavior and tablet-specific workflow
   presentation.

---

### User Story 2 - Unified Feature Behavior Across Roles (Priority: P2)

As a product owner, I want common workflows to behave consistently across role layouts while still
showing role-appropriate controls and content depth.

**Why this priority**: Consistent behavior reduces support burden, onboarding friction, and product
defects caused by divergent implementations.

**Independent Test**: Can be tested independently by validating shared workflows in each role layout
and verifying consistent outcomes with role-appropriate visibility rules.

**Acceptance Scenarios**:

1. **Given** the same operational event is visible to multiple roles,
   **When** each role opens the relevant view,
   **Then** core event facts remain consistent while role-specific actions vary by permissions.
2. **Given** a shared workflow is updated,
   **When** regression checks run across role layouts,
   **Then** expected behavior remains aligned and no role is left with outdated flow logic.

---

### User Story 3 - Reduce Delivery Overhead with One App Surface (Priority: P3)

As an engineering and product leadership team, we can deliver role-specific UI variations from one
application codebase, reducing duplicate implementation and release overhead.

**Why this priority**: This enables faster roadmap delivery and lower long-term maintenance cost.

**Independent Test**: Can be tested independently by measuring release artifacts, duplicate workflow
implementation count, and change lead-time before and after consolidation.

**Acceptance Scenarios**:

1. **Given** a new cross-role feature requirement,
   **When** it is implemented once in the shared product surface with role variants,
   **Then** it appears correctly for all applicable roles without separate app fork delivery.
2. **Given** a production issue affecting a shared workflow,
   **When** a fix is deployed,
   **Then** all affected role layouts receive the correction in the same release cycle.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- User has multiple assigned roles and role priority needs deterministic selection.
- Role assignment changes while a user session is active.
- Tablet is shared by multiple staff members with rapid account switching.
- Unauthorized role data appears in navigation cache after logout/login transitions.
- A role has no configured layout variant for a newly introduced workflow.
- Offline session starts with stale role permissions and must reconcile when online.
- Feature flags differ by role and create partial layout availability.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST determine active user role context at authentication and route users to the
  corresponding role-specific layout.
- **FR-002**: System MUST support distinct layout experiences for Parent, Teacher, Director, and
  Tablet contexts within one unified application surface.
- **FR-003**: System MUST enforce role-based navigation visibility so users only see screens permitted
  for their active role context.
- **FR-004**: System MUST preserve shared workflow logic across role layouts while allowing
  role-appropriate presentation and controls.
- **FR-005**: System MUST support deterministic role-priority rules when a user has multiple roles.
- **FR-006**: System MUST update visible layout behavior when role assignments change and prevent
  access beyond current permissions.
- **FR-007**: System MUST support secure user switching on shared tablet sessions with clear separation
  of role context and data visibility.
- **FR-008**: System MUST provide fallback handling when a role-specific layout segment is unavailable,
  including safe navigation recovery and user guidance.
- **FR-009**: System MUST maintain audit visibility for role-based routing decisions and role-context
  switches.
- **FR-010**: System MUST support role-targeted feature exposure controls so new capabilities can be
  released to selected roles without duplicating product surfaces.
- **FR-011**: System MUST ensure logout and session reset clear prior role layout state and prevent
  cross-role data leakage.
- **FR-012**: System MUST support consolidated release readiness checks that verify critical workflows
  across all supported role layouts.
- **FR-013**: System MUST use Keycloak OIDC authentication instead of local JWT authentication.
- **FR-014**: System MUST support OIDC authorization code redirect flow for web and PKCE flow for
  mobile clients.
- **FR-015**: System MUST source role mapping (parent, teacher, director, regional manager) from
  Keycloak groups and roles.
- **FR-016**: System MUST handle automatic token refresh and use Edge Keycloak as token issuer for
  teacher and director sessions.

### Key Entities *(include if feature involves data)*

- **User Role Assignment**: Mapping between authenticated user identity and one or more role contexts,
  including effective status and priority.
- **Role Layout Profile**: Definition of navigation structure, home experience, and allowed workflow
  entry points for a given role context.
- **Role Context Session**: Active runtime role context for a user session, including selected role,
  switching history, and permission state.
- **Shared Workflow Definition**: Canonical workflow behavior used across roles with role-specific
  presentation constraints.
- **Role Access Policy**: Permission and visibility rules controlling which actions and views are
  available per role.
- **Role Routing Audit Event**: Immutable event record of role-based entry selection, switches,
  and access denials.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 100% of authenticated sessions are routed to a valid role layout within 2 seconds of
  successful sign-in.
- **SC-002**: At least 95% of critical cross-role workflows pass consolidated role-layout validation
  in each release cycle.
- **SC-003**: Duplicate implementation effort for role-specific UI variants is reduced by at least 50%
  compared with prior multi-surface baseline.
- **SC-004**: Role-based access misrouting incidents remain below 1% of authenticated sessions.
- **SC-005**: Lead time to release shared workflow updates across Parent, Teacher, Director, and
  Tablet experiences is reduced by at least 40%.

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- Keycloak OIDC is available for web/mobile login and returns identity and role claims at sign-in time.
- Product governance defines a clear role hierarchy for users with multiple active roles.
- Shared tablet usage policies require fast account switching and strict session isolation.
- Current core workflows are already defined and can be expressed through role-specific layout variants.
- This feature is about role-driven experience composition and access control, not new diagnostic or
  clinical outputs.

## Constitution Alignment *(mandatory)*

### Phase Classification

- **Target Phase**: Phase 1
- **Prerequisite Validation**: Unified role-based application surface directly supports Phase 1
  operational workflows (attendance, billing, compliance, safety checks) within one maintainable
  product footprint.

### Privacy, Consent, and Residency Impact

- **Child Sensitive Data Used**: Role-based views may expose child operational metadata according to
  role permissions, including attendance, billing, compliance, and alert context.
- **Edge Processing Boundary**: This feature governs presentation and access routing and does not
  require raw video, raw audio, or facial embedding transfer for layout selection.
- **Consent Requirement**: Role-access and visibility controls must honor existing parental consent
  boundaries; sensitive child information remains restricted to authorized roles.
- **Retention and Auto-Delete**: Role-routing and access audit records follow regional retention policy
  windows with secure deletion controls.
- **Regional Residency Scope**: US, EU, and GCC residency obligations apply to role-routing metadata
  and access audit logs tied to child operations.

### Safety and Non-Diagnostic Compliance

- **Behavioral or Safety Outputs**: Outputs are role-appropriate operational interfaces and alerts for
  routine childcare workflows.
- **Prohibited Output Check**: No diagnostic labels, disorder predictions, or diagnostic confidence
  outputs are generated by role-layout routing.
- **Audience Boundary**: Parent, teacher, director, and tablet experiences expose only role-appropriate
  operational information and actions.
