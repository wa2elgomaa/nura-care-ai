# Phase 4: Person Tracking

**Status:** 🟡 In Progress  
**Priority:** High  
**Dependencies:** Phase 3 (Temporal Detection)

---

## Overview

Add multi-person tracking to associate detections with specific individuals across frames and time. This enables per-person action history, relationship analysis, and more accurate incident detection.

---

## Goals

1. **Track individuals** across video frames
2. **Maintain person IDs** consistently
3. **Associate detections** with specific people
4. **Build action history** per person
5. **Enable relationship analysis** (who interacts with whom)

---

## Key Features

### 1. Person Detection & Tracking
- Detect all persons in frame
- Assign unique IDs to each person
- Track across frames (handle occlusions, re-entry)
- Maintain ID consistency

### 2. Per-Person Action History
- Track each person's detected actions over time
- Build timeline of behaviors per individual
- Identify patterns (repeated aggression, sustained distress)

### 3. Relationship Analysis
- Track who is near whom
- Identify interaction patterns
- Detect group behaviors

### 4. Enhanced Detection
- Associate violence/distress with specific individuals
- Track aggressor vs victim
- Monitor vulnerable children

---

## Technical Approach

### Architecture Options

#### Option A: DeepSORT (Deep Learning + SORT)
- Detection: YOLOv8 (already have)
- Tracking: DeepSORT (appearance features + Kalman filter)
- Pros: Good re-identification, handles occlusions
- Cons: Slower (appearance network overhead)

#### Option B: ByteTrack (Simple but Effective)
- Detection: YOLOv8
- Tracking: ByteTrack (motion + low-confidence recovery)
- Pros: Fast, simple, SOTA results
- Cons: Less robust to long occlusions

#### Option C: Hybrid
- Fast path: ByteTrack for real-time
- Validation: DeepSORT for complex scenarios
- Best of both worlds

---

## Implementation Plan

See [spec.md](./spec.md) for full details.

**Quick Summary:**
1. Person detection (YOLOv8)
2. Tracking algorithm (ByteTrack recommended)
3. Integration with existing detectors
4. Per-person history storage
5. Enhanced VLM prompts with person context

---

## Success Criteria

- [ ] Track 5+ people simultaneously
- [ ] Maintain ID through short occlusions (<2s)
- [ ] <50ms overhead per frame
- [ ] Integrate with temporal detector
- [ ] Per-person action history working
- [ ] VLM receives person context

---

## Files

- `README.md` - This file
- `spec.md` - Detailed specification
- Implementation in `packages/nura-detectors/src/nura_detectors/person_tracker.py`
