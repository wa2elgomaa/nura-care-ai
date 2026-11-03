# Feature Specification: Parent Channel Alerts

**Feature Branch**: `006-parent-channel-alerts`

**Created**: 2026-07-22

**Status**: Draft

**Input**: User description: "As a parent, I want to receive daily reports, billing reminders, and urgent alerts (e.g., pickup mismatch, incident) via my preferred channel (email, SMS, WhatsApp), with quiet-hours respect, so that I stay informed without being overwhelmed."

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

### User Story 1 - Receive Notifications on Preferred Channel (Priority: P1)

As a parent, I can select my preferred communication channel and receive routine nursery updates
through that channel.

**Why this priority**: Channel preference is essential to timely parent awareness and trust in everyday
communications.

**Independent Test**: Can be tested independently by setting each available preference and verifying
daily reports and billing reminders are delivered to the selected channel.

**Acceptance Scenarios**:

1. **Given** a parent has selected email as preferred channel,
   **When** a daily report is generated,
   **Then** the report is delivered by email and logged as sent.
2. **Given** a parent has selected SMS or WhatsApp as preferred channel,
   **When** a billing reminder is issued,
   **Then** the reminder is delivered through the selected channel with matching delivery status.

---

### User Story 2 - Respect Quiet Hours for Routine Messages (Priority: P2)

As a parent, I can define quiet hours so non-urgent messages are deferred and delivered at appropriate
times.

**Why this priority**: Quiet-hours control reduces notification fatigue and improves parent experience
without losing important information.

**Independent Test**: Can be tested independently by scheduling routine messages during quiet hours and
verifying deferment and later delivery behavior.

**Acceptance Scenarios**:

1. **Given** quiet hours are configured,
   **When** a routine daily report is generated during quiet hours,
   **Then** delivery is deferred until the quiet-hours window ends.
2. **Given** a deferred queue contains multiple routine notifications,
   **When** quiet hours end,
   **Then** notifications are delivered according to configured sequencing without duplicates.

---

### User Story 3 - Deliver Urgent Alerts Immediately (Priority: P3)

As a parent and director, urgent safety alerts are sent immediately and can bypass quiet hours so
critical events are not missed.

**Why this priority**: Immediate delivery for high-risk events is a direct child-safety requirement and
must take precedence over convenience settings.

**Independent Test**: Can be tested independently by triggering urgent alert types and confirming
immediate dispatch, escalation fallback, and delivery audit records.

**Acceptance Scenarios**:

1. **Given** quiet hours are active,
   **When** a pickup mismatch alert is triggered,
   **Then** the alert is sent immediately via urgent-routing rules and logged as urgent delivery.
2. **Given** urgent delivery fails on the preferred channel,
   **When** fallback rules are enabled,
   **Then** the system retries or escalates to alternate allowed channels and records outcome.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- Parent changes preferred channel shortly before scheduled dispatch.
- Parent enables quiet hours spanning midnight across local time boundaries.
- Multiple guardians for one child define different channels and quiet-hours windows.
- Urgent alert is triggered while routine notifications are queued for deferment.
- Selected channel endpoint is unreachable or invalid during send attempt.
- Duplicate event triggers attempt to send repeated urgent alerts for the same incident.
- Parent opts out of one channel but remains subscribed on another channel.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST support parent notification preferences for email, SMS, and WhatsApp
  channels.
- **FR-002**: System MUST route routine message categories, including daily reports and billing
  reminders, to each guardian's currently active preferred channel.
- **FR-003**: System MUST support guardian-level quiet-hours configuration for routine message
  categories.
- **FR-004**: System MUST defer routine notifications generated during quiet hours and deliver them
  after quiet hours end.
- **FR-005**: System MUST classify urgent alert categories (including pickup mismatch and incident
  alerts) as quiet-hours bypass eligible.
- **FR-006**: System MUST dispatch urgent alerts immediately, regardless of quiet-hours state.
- **FR-007**: System MUST support delivery fallback for urgent alerts when the preferred channel fails,
  using preconfigured allowed alternatives.
- **FR-008**: System MUST prevent duplicate sends for the same notification event within defined
  deduplication rules.
- **FR-009**: System MUST allow parents to update channel preferences and quiet-hours settings and
  apply updates to subsequent notifications.
- **FR-010**: System MUST provide delivery status tracking (sent, delivered, failed, deferred,
  retried) per notification and per guardian.
- **FR-011**: System MUST provide staff with an audit trail of message generation, routing decisions,
  quiet-hours deferment, urgent bypass, and delivery outcomes.
- **FR-012**: System MUST provide parent-facing controls to reduce routine-notification volume through
  configurable digest behavior while preserving urgent alert immediacy.

### Key Entities *(include if feature involves data)*

- **Guardian Notification Profile**: Parent or guardian communication profile containing preferred
  channel, contact endpoints, consent state, and quiet-hours configuration.
- **Notification Event**: Generated communication unit linked to a child, event category, urgency
  classification, and message content.
- **Delivery Attempt**: Per-channel send attempt record including timestamp, result status, and
  failure reason.
- **Quiet-Hours Policy**: Guardian-specific or account-specific schedule defining deferment windows for
  non-urgent notifications.
- **Urgent Alert Rule**: Rule set defining alert types that bypass quiet hours and allowed fallback
  channels.
- **Notification Audit Record**: Immutable history of routing, deferment, bypass, deduplication, and
  delivery actions.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: At least 95% of routine notifications are delivered on the guardian's selected preferred
  channel on first dispatch attempt.
- **SC-002**: 100% of urgent alerts are dispatched within 1 minute of alert creation, including during
  quiet hours.
- **SC-003**: At least 98% of routine notifications generated during quiet hours are deferred and sent
  only after quiet hours end.
- **SC-004**: Duplicate-notification incidents for the same event are below 1% of total sends.
- **SC-005**: Parent-reported notification-overload complaints decrease by at least 40% within
  60 days of rollout while urgent-alert acknowledgment rates remain above 95%.

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- Parents or guardians have at least one verified communication endpoint on file.
- Notification categories and urgency definitions are centrally governed and consistent across
  classrooms.
- Staff can trigger urgent alerts through existing incident and pickup workflows.
- Regulatory requirements for consent and communication opt-in/opt-out are already captured in account
  setup processes.
- This feature governs parent communication delivery behavior and does not provide diagnostic clinical
  outputs.

## Constitution Alignment *(mandatory)*

### Phase Classification

- **Target Phase**: Phase 1
- **Prerequisite Validation**: Parent communication for attendance, billing, and urgent operations is
  required to support Phase 1 core workflows and safety response continuity.

### Privacy, Consent, and Residency Impact

- **Child Sensitive Data Used**: Child identity linkage metadata, incident and pickup alert details,
  guardian contact endpoints, and notification delivery logs.
- **Edge Processing Boundary**: This feature handles communication metadata and notifications and does
  not require transfer of raw video, raw audio, or facial embeddings for routine parent messaging.
- **Consent Requirement**: Parent communication channel usage and urgent-alert routing require explicit
  communication consent controls, auditable preference changes, and opt-out handling for non-urgent
  categories.
- **Retention and Auto-Delete**: Notification logs and delivery evidence follow region-specific
  retention controls with secure deletion after policy windows expire.
- **Regional Residency Scope**: US, EU, and GCC residency requirements apply for parent communication
  metadata and audit records.

### Safety and Non-Diagnostic Compliance

- **Behavioral or Safety Outputs**: Outputs include routine daily summaries, billing reminders,
  operational urgent alerts, and delivery confirmations.
- **Prohibited Output Check**: No diagnostic labels, disorder predictions, or diagnostic confidence
  outputs are generated.
- **Audience Boundary**: Parent-facing messages are limited to operational updates and urgent
  notifications; staff-facing views expose routing and delivery controls.
