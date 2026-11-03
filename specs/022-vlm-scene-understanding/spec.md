# Feature Specification: VLM Scene Understanding Service

**Feature Branch**: `022-vlm-scene-understanding`

**Created**: 2026-11-03

**Status**: Draft

**Input**: User description: "As a safety monitoring system, I need a Vision-Language Model service that can analyze camera frames and understand context (supervision, activities, safety concerns) so that the rules engine can accurately detect violations beyond simple object detection."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Supervision Detection (Priority: P0 - CRITICAL)

As a rules engine, I need to determine if an adult is supervising children in a classroom, so that I can alert when children are left unattended.

**Why this priority**: This is the #1 safety violation. Children must be supervised at all times per regulations. This single capability alone provides immediate value.

**Independent Test**: Send a classroom frame to VLM with prompt "Is there an adult supervising?" Verify response correctly identifies presence/absence of adults.

**Acceptance Scenarios**:

1. **Given** a camera frame with 2 children and 1 adult teacher,
   **When** VLM analyzes with supervision prompt,
   **Then** response indicates "adults_detected: true" with explanation.

2. **Given** a camera frame with 2 children and no adults,
   **When** VLM analyzes with supervision prompt,
   **Then** response indicates "adults_detected: false" with explanation.

3. **Given** a frame with only children visible,
   **When** VLM analyzes scene,
   **Then** response is returned within 2 seconds and parsed correctly.

---

### User Story 2 - Child Counting (Priority: P1)

As a rules engine, I need to count how many children are in a room, so that I can detect capacity violations and ratio issues.

**Why this priority**: Capacity limits and staff-to-child ratios are regulated. Accurate counting enables multiple safety rules.

**Independent Test**: Send frames with known child counts (1, 2, 5, 10) and verify VLM returns correct counts ±1.

**Acceptance Scenarios**:

1. **Given** a frame with 3 clearly visible children,
   **When** VLM counts children,
   **Then** response indicates count of 3 (or 2-4 range acceptable).

2. **Given** a frame with children partially obscured,
   **When** VLM counts,
   **Then** response provides best estimate with confidence note.

---

### User Story 3 - Behavior Analysis (Priority: P2)

As a rules engine, I need to detect concerning behaviors (aggression, distress, inappropriate contact), so that I can alert staff immediately.

**Why this priority**: Behavioral incidents require quick intervention but are less common than supervision issues.

**Independent Test**: Use test frames with staged concerning behaviors and verify VLM flags them.

**Acceptance Scenarios**:

1. **Given** a frame showing children engaged in calm activities,
   **When** VLM analyzes behavior,
   **Then** response indicates "safety_concern: false".

2. **Given** a frame showing physical aggression (hitting, pushing),
   **When** VLM analyzes behavior,
   **Then** response flags "safety_concern: true" with description.

---

### User Story 4 - Restricted Area Detection (Priority: P2)

As a rules engine, I need to identify if children are in restricted areas (kitchen, storage, staff rooms), so that I can prevent unauthorized access.

**Why this priority**: Certain areas have safety hazards (kitchen appliances, cleaning supplies) and must be off-limits.

**Independent Test**: Send frames from different room types and verify VLM correctly identifies area type.

**Acceptance Scenarios**:

1. **Given** a frame showing a kitchen with commercial equipment,
   **When** VLM identifies area type,
   **Then** response indicates "restricted_area: true, type: kitchen".

2. **Given** a frame of a regular classroom,
   **When** VLM identifies area type,
   **Then** response indicates "restricted_area: false, type: classroom".

---

### Edge Cases

- **Poor lighting**: Camera in dimly lit room (naptime) - VLM may struggle to identify people
- **Occlusion**: Adult behind furniture/door, not visible but present in room
- **Ambiguous age**: Teenage volunteer could be misidentified as child vs adult
- **Camera angle**: High-angle camera shows tops of heads, harder to distinguish adults
- **Multiple adults**: Several staff members in frame, ensure "adults_detected: true" not just "adult_detected"
- **Empty room**: No people visible - VLM should return zero counts, not error
- **Non-human objects**: Mannequins, dolls, or posters with faces could confuse counting
- **Motion blur**: Fast-moving children blur in frame, harder to count accurately
- **Timeout**: VLM takes >10 seconds - system should handle gracefully
- **Ollama down**: VLM service cannot reach Ollama - return error, don't crash

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide REST API endpoint POST /analyze accepting base64-encoded images and text prompts
- **FR-002**: System MUST support multiple VLM models (LLaVA 13B, LLaVA 7B, Moondream 2B) with runtime selection
- **FR-003**: System MUST return structured responses with parsed fields (adults_detected, children_count, safety_concern)
- **FR-004**: System MUST complete analysis within 2 seconds for P0 prompts (supervision check)
- **FR-005**: System MUST include predefined prompt templates for common safety queries
- **FR-006**: System MUST handle Ollama connection failures gracefully without crashing
- **FR-007**: System MUST log all analyses with timestamps, prompts, and response summaries (no full images)
- **FR-008**: System MUST expose health check endpoint indicating Ollama connectivity and model loaded
- **FR-009**: System MUST support batch analysis of multiple frames from a clip
- **FR-010**: System MUST publish analysis events to NATS for downstream consumption by rules engine
- **FR-011**: System MUST process images in-memory only (no disk storage of frames)
- **FR-012**: System MUST validate image format and size before processing

### Key Entities

- **VLM Analysis Request**: Contains base64 image, text prompt, optional camera ID and timestamp
- **VLM Analysis Response**: Contains raw VLM text response, parsed structured fields, confidence metrics
- **Prompt Template**: Predefined question patterns for common safety scenarios (supervision, counting, behavior)
- **Model Configuration**: VLM model selection, temperature, max tokens, timeout settings

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: VLM correctly identifies adult presence/absence in supervision checks with 90%+ accuracy on test dataset
- **SC-002**: Child counting accuracy within ±1 for 85%+ of test frames with 1-10 children
- **SC-003**: 95%+ of P0 supervision analyses complete within 2 seconds
- **SC-004**: System handles 30 frames/minute sustained load without degradation
- **SC-005**: Zero image data written to disk during normal operation (verified by file system audit)
- **SC-006**: Service maintains 99.9% uptime over 2-week pilot period

## Assumptions

- Ollama is deployed and accessible at http://ollama:11434 with required VLM models pre-pulled
- Input images are from 1080p cameras, base64-encoded JPEG format, <2MB per frame
- NATS JetStream is available for event publishing
- GPU with 16-24GB VRAM is available for VLM inference (or CPU fallback accepted with slower performance)
- Frames are pre-screened by nura-perception (YOLO) to trigger VLM analysis only when needed, not every frame
- English language prompts and responses (multi-language support deferred to Phase 2)

## Constitution Alignment *(mandatory)*

### Phase Classification

- **Target Phase**: Phase 1 - Camera Violation Detection MVP
- **Prerequisite Validation**: Frigate NVR and nura-perception (YOLO detection) operational

### Privacy, Consent, and Residency Impact

- **Child Sensitive Data Used**: Camera frames processed in real-time for safety analysis
- **Edge Processing Boundary**: All image processing occurs on edge box. Only text analysis results (no images) published to NATS and stored in database. Raw frames never leave edge box.
- **Consent Requirement**: Not required for safety monitoring. VLM processes frames for supervision/safety only, not biometric identification.
- **Retention and Auto-Delete**: Text analysis results retained for 90 days (configurable), automatically deleted. No image retention.
- **Regional Residency Scope**: All processing local to edge box, no cross-border data transfer

### Safety and Non-Diagnostic Compliance

- **Behavioral or Safety Outputs**: Outputs are descriptive observations ("two children visible, no adult present") not diagnostic labels
- **Prohibited Output Check**: VLM prompts explicitly instruct "describe what you see" not "diagnose conditions"
- **Audience Boundary**: VLM analysis results consumed by rules engine only, not directly shown to parents. Staff-facing alerts include context but not raw VLM text.

## Technical Implementation

### Architecture

```
nura-perception (YOLO detects event)
    ↓ (HTTP POST)
nura-vlm (FastAPI service)
    ↓ (Internal call)
Ollama + LLaVA (local inference)
    ↓ (Response parsing)
nura-vlm (structured output)
    ↓ (NATS event)
nura-rules (violation matching)
```

### API Endpoints

#### POST /analyze
```json
Request:
{
  "image_base64": "<base64-encoded-jpeg>",
  "prompt": "Is there an adult supervising?",
  "camera_id": "classroom-2",
  "timestamp": "2024-11-03T14:23:15Z"
}

Response:
{
  "analysis": "Two children approximately ages 4-5 sitting at a table. No adults visible in frame.",
  "adults_detected": false,
  "children_count": 2,
  "safety_concern": true,
  "confidence": 0.89,
  "inference_time_ms": 1850
}
```

#### GET /prompts
List available prompt templates

#### POST /analyze/supervision (Quick check)
Specialized endpoint with predefined supervision prompt

#### GET /health
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "vlm_model": "llava:13b",
  "model_loaded": true,
  "ollama_connected": true
}
```

### Technology Stack

- **FastAPI**: Async Python web framework
- **Ollama Python client**: Communication with Ollama API
- **Pillow**: Image preprocessing
- **NATS.py**: Event publishing
- **Prometheus client**: Metrics

### Performance Targets

| Metric | Target | Hardware |
|--------|--------|----------|
| **Supervision check latency** | <2s | NVIDIA RTX 4090 (24GB) |
| **Throughput** | 30 frames/min | Same |
| **Memory usage** | <4GB (service) | Excludes Ollama VRAM |
| **CPU usage** | <20% (idle) | 8-core system |

### Security Considerations

- No authentication on internal API (within core_net Docker network only)
- Images processed in-memory, never written to disk
- Text logs exclude PII, contain only aggregated metrics
- NATS events encrypted in transit if TLS enabled

## Dependencies

- **Ollama**: Local LLM runtime (http://ollama:11434)
- **VLM Models**: LLaVA 13B, LLaVA 7B, or Moondream 2B (pre-pulled)
- **NATS JetStream**: Event bus (nats://nats:4222)
- **Frigate/nura-perception**: Upstream detection services

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **VLM inference too slow** | Alerts delayed >10s | Use Moondream 2B (faster), or GPU upgrade |
| **Ollama crashes** | Service down | Health check + auto-restart, graceful degradation |
| **VLM hallucinations** | False alerts | Combine with YOLO confidence, human review of first 100 alerts |
| **GPU memory exhaustion** | Service OOM | Monitor VRAM, queue requests, load shedding |
| **Prompt injection** | VLM misused | Sanitize prompts, predefined templates only in production |

## Testing Strategy

### Unit Tests
- Ollama client connection handling
- Response parsing logic
- Prompt template rendering

### Integration Tests
- End-to-end analysis with sample frames
- NATS event publishing
- Health check endpoint

### Performance Tests
- Latency under load (30 frames/min)
- Memory leak detection (24-hour run)
- GPU utilization monitoring

### Accuracy Tests
- 100 labeled frames (adults/children counts known)
- Measure precision/recall for supervision detection
- Edge case handling (poor lighting, occlusion)

## Rollout Plan

### Week 1: Development
- Implement Ollama client integration
- Build FastAPI endpoints
- Add response parsing logic

### Week 2: Testing
- Unit + integration tests
- Accuracy validation on test dataset
- Performance benchmarking

### Week 3: Pilot Deployment
- Deploy to dev edge box
- Test with live Frigate streams
- Tune thresholds and prompts

### Week 4: Production Readiness
- 24-hour stability test
- Documentation complete
- Handoff to operations team

---

**Document Owner**: Engineering Team  
**Review Cycle**: Weekly during Phase 1 development  
**Approval**: Product Lead, Engineering Lead, Compliance Lead
