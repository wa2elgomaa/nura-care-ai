# Feature Specification: RAG Rule Knowledge Base

**Feature Branch**: `023-rag-rule-knowledge`
**Created**: 2026-11-03
**Status**: Draft

**Input**: "As a rules engine, I need a RAG service that matches detected events to school policies and regulations using semantic similarity search."

## User Scenarios & Testing

### User Story 1 - Rule Matching from Event Context (Priority: P0)

As a rules engine, I need to find which rules are violated when given an event description.

**Acceptance**:
1. Given "children alone in room for 45 seconds", returns RULE-001 (supervision) with >0.8 similarity
2. Given "8 children in room posted for 6", returns RULE-002 (capacity)

### User Story 2 - Policy Document Ingestion (Priority: P1)

As an administrator, I need to upload policy PDFs and have them automatically indexed.

**Acceptance**:
1. Upload PDF with 5 policies, all 5 extracted and searchable within 60 seconds

## Requirements

- **FR-001**: POST /match endpoint for semantic rule matching
- **FR-002**: Embedding generation (sentence-transformers all-MiniLM-L6-v2)
- **FR-003**: pgvector storage and search
- **FR-004**: PDF ingestion with text extraction
- **FR-005**: Rule CRUD endpoints
- **FR-006**: <100ms query latency for 500 rules

## Success Criteria

- **SC-001**: 95%+ accuracy matching violations to correct rules
- **SC-002**: <100ms rule matching latency
- **SC-003**: 90%+ PDF extraction success rate

## Constitution Alignment

- **Phase**: Phase 1
- **Privacy**: Rule text only, no child data
- **Edge Processing**: All policy data stays local

