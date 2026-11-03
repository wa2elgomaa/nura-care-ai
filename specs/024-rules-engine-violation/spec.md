# Feature Specification: Rules Engine - Violation Detection

**Feature Branch**: `024-rules-engine-violation`
**Created**: 2026-11-03
**Status**: Draft

**Input**: "As a safety monitoring system, I need a rules engine that receives detection events, queries RAG for matching rules, evaluates thresholds, and generates violation alerts within 10 seconds."

## User Scenarios & Testing

### User Story 1 - Supervision Violation Detection (Priority: P0)

As a safety system, I need to detect when children are unattended and alert administrators immediately.

**Acceptance**:
1. Given YOLO detects "2 children, 0 adults" for 30 seconds, VLM confirms "no adult visible", RAG matches RULE-001, when rules engine evaluates, then violation alert generated within 10 seconds total
2. Given adult returns after 25 seconds, when threshold not met, then no alert generated

### User Story 2 - Threshold Evaluation (Priority: P0)

As a rules engine, I need to track event duration and only alert when thresholds are met (e.g., >30s, >5min).

**Acceptance**:
1. Rule requires "no adult for >30s", event lasts 45s, alert triggered
2. Rule requires "no adult for >30s", event lasts 20s, no alert

### User Story 3 - Evidence Clip Management (Priority: P1)

As an administrator, I need 15-second video clips attached to alerts for verification.

**Acceptance**:
1. Violation detected at 14:23:45, clip saved from 14:23:30-14:23:45 (15s before), alert includes clip path

## Requirements

- **FR-001**: Subscribe to NATS events from nura-perception and nura-vlm
- **FR-002**: Query nura-rag POST /match for rule matching
- **FR-003**: Evaluate threshold conditions (duration, count, frequency)
- **FR-004**: Generate violation events with evidence clip references
- **FR-005**: Publish violation alerts to NATS (consumed by nura-notifier)
- **FR-006**: Store violation events in Postgres (violation_events table)
- **FR-007**: Total latency <10 seconds from detection to alert

## Success Criteria

- **SC-001**: 90%+ of supervision violations detected when threshold met
- **SC-002**: <5% false positive rate (alerts when threshold not met)
- **SC-003**: <10 second total latency (detection → alert)
- **SC-004**: 100% of alerts include evidence clip path

## Constitution Alignment

- **Phase**: Phase 1 - Camera Violation Detection MVP
- **Privacy**: No video data in alerts, only clip path for authorized viewing
- **Edge Processing**: All rule evaluation happens locally

