# Feature Specification: Teacher Pattern Insights

**Feature Branch**: `017-teacher-pattern-insights`

**Created**: 2026-07-22

**Status**: Draft

**Input**: User description: "As a teacher, I want to see a dashboard that surfaces observable patterns (e.g., attention dips after 10am, increased social withdrawal this week, repeated escalation sequence with specific peer) and provides a consider professional evaluation prompt, so that I can act early while staying firmly in the educator role."

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

### User Story 1 - Teacher Pattern Visibility (Priority: P1)

As a teacher, I can view clear, observable classroom patterns for each child so I can intervene early
with supportive classroom strategies.

**Why this priority**: Early pattern visibility is the core value and enables timely educator action
before challenges escalate.

**Independent Test**: Can be tested independently by loading the dashboard for a child with recent
classroom data and confirming pattern cards appear with time-window context and supporting evidence.

**Acceptance Scenarios**:

1. **Given** a child has recent classroom observations,
   **When** a teacher opens the pattern dashboard,
   **Then** observable trends are shown (for example timing dips, social withdrawal increase,
   or repeated escalation sequences).
2. **Given** a pattern is displayed,
   **When** a teacher reviews details,
   **Then** they can see supporting observations and timeframe comparisons.

---

### User Story 2 - Educator Action Guidance (Priority: P2)

As a teacher, I receive practical educator-role next steps and a structured consider professional
evaluation prompt when patterns persist or intensify.

**Why this priority**: Converts pattern awareness into responsible action while preserving role
boundaries.

**Independent Test**: Can be tested independently by validating that persistent pattern conditions
trigger educator guidance and non-diagnostic referral prompts.

**Acceptance Scenarios**:

1. **Given** repeated pattern thresholds are met,
   **When** teacher views recommended actions,
   **Then** the dashboard presents classroom support steps and documentation prompts.
2. **Given** predefined persistence criteria are met,
   **When** the teacher reviews the insight,
   **Then** the system shows a consider professional evaluation nudge with approved wording and
   escalation workflow guidance.

---

### User Story 3 - Director and Compliance Oversight (Priority: P3)

As a director/compliance reviewer, I can audit which patterns were surfaced, which actions were taken,
and whether role boundaries were respected.

**Why this priority**: Ensures governance, consistency, and safe use of sensitive behavioral insights.

**Independent Test**: Can be tested independently by reviewing audit records for surfaced patterns,
teacher actions, referral nudges, and approval events.

**Acceptance Scenarios**:

1. **Given** teachers used the dashboard during a week,
   **When** director reviews oversight reports,
   **Then** pattern usage, intervention logging, and referral-prompt events are visible.
2. **Given** a pattern card contains high-sensitivity context,
   **When** compliance review is conducted,
   **Then** access history and approved phrasing checks are auditable.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- Child has too little data this week to infer reliable patterns.
- Two teachers log contradictory observations for the same time period.
- Peer-related escalation pattern appears to identify another child inappropriately.
- Consent for behavioral inference is revoked after pattern cards were generated.
- Teacher attempts to interpret pattern output as diagnosis in parent communication draft.
- Pattern spikes are driven by schedule anomalies (field trip, substitute day) rather than child trend.
- Dashboard access happens during temporary offline operation and later sync reconciliation.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST present child-level observable pattern cards for teacher-authorized views,
  including time-based, social-interaction, and escalation-sequence trend types.
- **FR-002**: System MUST provide supporting evidence context for each pattern, including observation
  count, timeframe, and trend direction.
- **FR-003**: System MUST provide educator-role intervention suggestions that focus on classroom
  strategy and documentation, not diagnosis.
- **FR-004**: System MUST trigger a consider professional evaluation prompt when predefined persistence
  or intensification criteria are met.
- **FR-005**: System MUST enforce approved referral prompt wording that explicitly avoids clinical
  labeling and preserves educator-role boundaries.
- **FR-006**: System MUST require and validate consent status before generating, displaying, or
  retaining behavioral pattern insights.
- **FR-007**: System MUST suppress or redact peer-identifying details in child-specific insights unless
  explicitly authorized under policy.
- **FR-008**: System MUST provide teacher action logging for interventions attempted, follow-up
  outcomes, and referral-discussion preparation steps.
- **FR-009**: System MUST provide director/compliance oversight views with audit trails for pattern
  generation, access, action usage, and referral prompts.
- **FR-010**: System MUST indicate data-confidence sufficiency and withhold strong pattern framing when
  observations are below minimum reliability thresholds.
- **FR-011**: System MUST enforce role-based access boundaries so parent-facing channels exclude
  staff-only behavioral interpretation outputs unless explicitly approved summaries are generated.
- **FR-012**: System MUST apply retention, residency, and deletion controls to insight metadata and
  related audit records according to regulatory policy.

### Key Entities *(include if feature involves data)*

- **Pattern Insight Card**: Staff-facing summary of an observable child trend with timeframe and
  direction.
- **Evidence Observation Set**: Underlying teacher notes and activity events supporting a pattern.
- **Educator Action Suggestion**: Recommended classroom interventions and documentation steps tied to a
  pattern type.
- **Referral Nudge Event**: Recorded instance where consider professional evaluation prompt criteria are
  met and shown.
- **Consent Eligibility Record**: Auditable status object controlling whether insights are allowed for
  a child.
- **Oversight Audit Entry**: Director/compliance log of access, prompts, actions, and policy checks.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: At least 90% of active teachers access pattern dashboards weekly for children with
  sufficient observations.
- **SC-002**: At least 85% of surfaced high-priority pattern insights receive a logged educator action
  within 2 school days.
- **SC-003**: 100% of referral nudge prompts use approved non-diagnostic language and include
  role-boundary guidance.
- **SC-004**: Unauthorized peer-identifying disclosures in child-specific pattern views remain at 0
  confirmed incidents.
- **SC-005**: Director compliance audits show at least 98% completeness for insight access and action
  history records.

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- Teachers already capture structured observations and incident notes in daily workflows.
- Site policies define approved educator language for referral conversations.
- Director/compliance reviewers are available to monitor high-sensitivity usage patterns.
- This feature is staff-facing and does not automatically publish behavioral interpretations to parents.
- Behavioral insight usage is enabled only for children with valid consent coverage.

## Constitution Alignment *(mandatory)*

### Phase Classification

- **Target Phase**: Phase 3
- **Prerequisite Validation**: Requires completed Phase 1 core operations and Phase 2 edge rollout,
  plus Phase 3 governance readiness for behavioral insight controls.

### Privacy, Consent, and Residency Impact

- **Child Sensitive Data Used**: Behavioral observation patterns, social-interaction trend metadata,
  and teacher notes are treated as sensitive child data.
- **Edge Processing Boundary**: Raw identifiable media remains on edge infrastructure; dashboard
  insights are derived from approved operational metadata and observation logs.
- **Consent Requirement**: Explicit parental opt-in for behavioral inference is mandatory, with
  auditable collection, revocation, and enforcement gates.
- **Retention and Auto-Delete**: Insight metadata and audit logs follow region-configurable retention
  windows and secure deletion defaults.
- **Regional Residency Scope**: US, EU, and GCC residency constraints apply to insight and audit data
  stores.

### Safety and Non-Diagnostic Compliance

- **Behavioral or Safety Outputs**: Outputs are staff-facing observable pattern summaries,
  intervention suggestions, and referral nudges.
- **Prohibited Output Check**: No diagnosis labels, disorder names, or clinical confidence scores are
  shown.
- **Audience Boundary**: Detailed behavioral pattern outputs remain teacher/director-facing; parent
  channels receive only approved non-diagnostic communication.
