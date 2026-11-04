# Spec 026: Hybrid Fast-Path Architecture for VLM

**Status**: Draft  
**Created**: 2026-11-04  
**Priority**: Critical  
**Reason**: Current VLM missing 100% of safety violations - unacceptable for production

---

## Problem Statement

Current VLM-only approach has critical issues:

### Accuracy Problems (CRITICAL)
- **0% detection rate** on test violence scenarios
- Misses physical aggression (child hitting with pencil)
- Misses physical confrontation (pushing/hitting)
- Misses child distress (crying, covering face)
- Hallucinates observations ("adult present" when none visible)

### Performance Issues
- **11-19 seconds per image** (good, but could be better)
- Cannot process multiple cameras in real-time
- VLM overkill for obvious violations

### Root Causes
1. Generic VLM not trained for childcare scenarios
2. Interprets aggression as "playful behavior"
3. Poor at detecting subtle distress signals
4. No specialized models for specific violation types

---

## Solution: Hybrid Fast-Path Architecture

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Camera Frame Input                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              FAST PATH (CoreML/YOLO)                         │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Violence    │  │  Distress    │  │ Supervision  │     │
│  │  Detector    │  │  Detector    │  │  Detector    │     │
│  │  (I3D/YOLO)  │  │  (Facial)    │  │  (Counting)  │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                  ┌─────────▼─────────┐                      │
│                  │   Confidence      │                      │
│                  │   Scoring         │                      │
│                  └─────────┬─────────┘                      │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                  ┌──────────▼──────────┐
                  │   Routing Logic     │
                  │                     │
                  │  High Conf? → Alert │
                  │  Low Conf?  → VLM   │
                  │  Ambiguous? → VLM   │
                  └──────────┬──────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
    ┌─────────────────┐         ┌─────────────────┐
    │  Direct Alert   │         │  VLM Analysis   │
    │  (Fast, <100ms) │         │  (Slow, 11-19s) │
    └─────────────────┘         └─────────────────┘
```

### Two-Tier Detection System

#### Tier 1: Fast Path (70% of cases, <100ms)
Specialized models for obvious violations:

1. **Violence/Aggression Detector**
   - Model: I3D (Inflated 3D CNN) or YOLO-based action detection
   - Detects: Hitting, pushing, kicking, throwing objects
   - Accuracy target: >95% precision on obvious cases
   - Latency: <50ms per frame
   - Technology: CoreML (Mac), TensorRT (GPU)

2. **Child Distress Detector**
   - Model: Facial expression recognition (FER)
   - Detects: Crying, fear, pain expressions
   - Features: Face detection + emotion classification
   - Accuracy target: >90% on clear distress
   - Latency: <30ms per face
   - Technology: CoreML Vision framework

3. **Supervision Detector**
   - Model: Person detection + age classification
   - Detects: Adult count, child count, ratios
   - Features: YOLO + age classifier
   - Accuracy target: >95% on person counting
   - Latency: <50ms per frame
   - Technology: CoreML or Ultralytics

#### Tier 2: VLM Path (30% of cases, 11-19s)
Reserved for complex scenarios:

- Ambiguous physical contact (playing vs fighting)
- Context-dependent situations
- Novel violation types
- Low confidence from fast-path models
- Validation of high-severity alerts

---

## Implementation Plan

### Phase 1: Fast-Path Models (Week 1)

#### Violence Detector
```python
# services/nura-perception/src/detectors/violence_detector.py

class ViolenceDetector:
    """
    Detects physical aggression and violence using action recognition
    """
    def __init__(self):
        # Load I3D or similar action recognition model
        self.model = self.load_model()
        
    def detect(self, frame):
        """
        Returns:
        {
            "violence_detected": bool,
            "confidence": float,
            "action_type": str,  # "hitting", "pushing", etc.
            "bbox": [x, y, w, h],
            "severity": str  # "low", "medium", "high"
        }
        """
```

**Model Options:**
1. **I3D (Inflated 3D ConvNet)** - Pre-trained on Kinetics dataset
2. **SlowFast Networks** - Dual-pathway for action recognition
3. **X3D** - Efficient 3D CNN
4. **YOLO-based** - Custom trained for childcare actions

#### Distress Detector
```python
# services/nura-perception/src/detectors/distress_detector.py

class DistressDetector:
    """
    Detects child distress through facial expression recognition
    """
    def __init__(self):
        self.face_detector = FaceDetector()  # YOLO or MTCNN
        self.emotion_classifier = EmotionClassifier()  # FER model
        
    def detect(self, frame):
        """
        Returns:
        {
            "distress_detected": bool,
            "confidence": float,
            "emotion": str,  # "crying", "fear", "pain"
            "face_bbox": [x, y, w, h],
            "severity": str
        }
        """
```

**Model Options:**
1. **FER2013 trained model** - Emotion recognition
2. **AffectNet** - More comprehensive emotions
3. **Custom model** - Fine-tuned on childcare scenarios

#### Supervision Detector
```python
# services/nura-perception/src/detectors/supervision_detector.py

class SupervisionDetector:
    """
    Detects supervision ratio violations
    """
    def __init__(self):
        self.person_detector = PersonDetector()  # YOLO
        self.age_classifier = AgeClassifier()
        
    def detect(self, frame):
        """
        Returns:
        {
            "violation_detected": bool,
            "adult_count": int,
            "child_count": int,
            "ratio": float,
            "required_ratio": float,
            "confidence": float
        }
        """
```

### Phase 2: Routing Logic (Week 1)

```python
# services/nura-vlm/src/hybrid_router.py

class HybridRouter:
    """
    Routes frames to fast-path or VLM based on confidence
    """
    def __init__(self):
        self.violence_detector = ViolenceDetector()
        self.distress_detector = DistressDetector()
        self.supervision_detector = SupervisionDetector()
        self.vlm_client = OllamaVLMClient()
        
    async def analyze_frame(self, frame):
        # Step 1: Run all fast-path detectors in parallel
        violence_result = self.violence_detector.detect(frame)
        distress_result = self.distress_detector.detect(frame)
        supervision_result = self.supervision_detector.detect(frame)
        
        # Step 2: Aggregate results
        fast_path_results = {
            "violence": violence_result,
            "distress": distress_result,
            "supervision": supervision_result
        }
        
        # Step 3: Decision logic
        if self._high_confidence_violation(fast_path_results):
            # Direct alert (fast path)
            return self._create_alert(fast_path_results, source="fast_path")
            
        elif self._requires_vlm_analysis(fast_path_results):
            # Send to VLM for complex analysis
            vlm_result = await self.vlm_client.analyze(
                frame, 
                context=fast_path_results  # Give VLM the fast-path context
            )
            return self._create_alert(vlm_result, source="vlm")
            
        else:
            # No violation detected
            return {"violation": False, "source": "fast_path"}
    
    def _high_confidence_violation(self, results):
        """
        High confidence = direct alert (no VLM needed)
        """
        # Violence with high confidence
        if (results["violence"]["violence_detected"] and 
            results["violence"]["confidence"] > 0.9):
            return True
            
        # Distress with high confidence
        if (results["distress"]["distress_detected"] and 
            results["distress"]["confidence"] > 0.85):
            return True
            
        # Supervision violation (usually clear-cut)
        if results["supervision"]["violation_detected"]:
            return True
            
        return False
        
    def _requires_vlm_analysis(self, results):
        """
        Ambiguous cases need VLM analysis
        """
        # Medium confidence detections
        if (results["violence"]["violence_detected"] and 
            0.5 < results["violence"]["confidence"] < 0.9):
            return True
            
        if (results["distress"]["distress_detected"] and 
            0.5 < results["distress"]["confidence"] < 0.85):
            return True
            
        return False
```

### Phase 3: Improved VLM Prompts (Week 1)

```python
# services/nura-vlm/src/prompts/childcare_prompts.py

VIOLENCE_DETECTION_PROMPT = """You are a childcare safety expert analyzing this image.

CONTEXT FROM FAST DETECTORS:
- Violence detector confidence: {violence_confidence}
- Detected action: {detected_action}
- Location: {bbox}

CRITICAL: Look specifically at the children's interactions in the highlighted area.

EXAMPLES OF VIOLENCE/AGGRESSION:
1. One child hitting another with hand, fist, or object
2. One child pushing, shoving, or kicking another
3. One child pulling hair, pinching, or biting another
4. Children fighting or in physical conflict
5. A child throwing objects AT another child

EXAMPLES OF NORMAL PLAY:
1. Children sitting together working
2. Gentle touch on shoulder/arm
3. Passing objects to each other
4. Running/playing without contact

ANALYZE THIS IMAGE:
1. What EXACTLY are the children doing? Describe their body positions and movements.
2. Is there any physical contact? If yes, describe the TYPE and FORCE of contact.
3. Are any children using objects? If yes, HOW are they using them?
4. Body language: Do any children appear defensive, hurt, or scared?
5. Is this aggressive behavior or normal play?

CLASSIFY:
- VIOLENCE: Yes/No
- If yes, TYPE: hitting/pushing/throwing/other
- SEVERITY: LOW/MEDIUM/HIGH
- CONFIDENCE: 0.0-1.0

Be specific and objective. Do not assume play if you see physical contact.
"""

DISTRESS_DETECTION_PROMPT = """You are a childcare safety expert analyzing this image for child distress.

CONTEXT FROM FAST DETECTORS:
- Distress detector confidence: {distress_confidence}
- Detected emotion: {detected_emotion}
- Face location: {face_bbox}

CRITICAL: Look at the child's face and body language.

SIGNS OF DISTRESS:
1. Crying (tears, red face, mouth open)
2. Fear (wide eyes, pulled back, defensive posture)
3. Pain (grimacing, holding body part, tears)
4. Sadness (downturned mouth, tears, withdrawn)
5. Covering face with hands (hiding, crying)

NORMAL EXPRESSIONS:
1. Concentration (focused, neutral face)
2. Thinking (hand on chin, looking up)
3. Boredom (neutral, looking away)
4. Mild frustration (frown but engaged)

ANALYZE THIS IMAGE:
1. Describe the child's facial expression in detail
2. What is their body posture? (open/closed, tense/relaxed)
3. Are they crying or showing tears?
4. Are they isolated or with others?
5. Context: What might be causing this emotion?

CLASSIFY:
- DISTRESS: Yes/No
- If yes, TYPE: crying/fear/pain/sadness
- SEVERITY: LOW/MEDIUM/HIGH
- IMMEDIATE_ATTENTION_NEEDED: Yes/No
- CONFIDENCE: 0.0-1.0

Be compassionate but objective. Distinguish between temporary upset and real distress.
"""
```

---

## Performance Targets

### Latency

| Component | Target | Current | Improvement |
|-----------|--------|---------|-------------|
| **Fast Path Total** | <100ms | N/A | New |
| - Violence Detector | <50ms | N/A | New |
| - Distress Detector | <30ms | N/A | New |
| - Supervision Detector | <50ms | N/A | New |
| **VLM Path** | 11-19s | 11-19s | Same |
| **Hybrid Average** | <3s | N/A | 3-6x faster |

**Calculation**: 
- 70% fast path: 0.7 × 0.1s = 0.07s
- 30% VLM path: 0.3 × 15s = 4.5s
- Average: 4.57s (vs 15s VLM-only)

### Accuracy

| Metric | Target | Current VLM | Improvement |
|--------|--------|-------------|-------------|
| **Precision** | >95% | Unknown (misses all) | Critical |
| **Recall** | >90% | 0% (missed all test cases) | Critical |
| **F1 Score** | >0.92 | 0.0 | Critical |
| **False Positives** | <5% | Unknown | TBD |

---

## Technology Stack

### Mac M4 Max (Development)
- **Fast Path**: CoreML models
- **Framework**: Vision framework (built-in)
- **Person Detection**: Vision.framework or YOLO-CoreML
- **Face Detection**: Vision.VNDetectFaceRectanglesRequest
- **Action Recognition**: Custom CoreML model (I3D converted)

### GPU Deployment (Production)
- **Fast Path**: TensorRT models
- **Framework**: PyTorch + TensorRT
- **Person Detection**: Ultralytics YOLOv8
- **Face Detection**: MTCNN or RetinaFace
- **Action Recognition**: I3D or SlowFast (TensorRT)

---

## Testing Strategy

### Validation Dataset
Create ground truth dataset:
1. **Violence cases** (50 images)
   - Clear aggression: 20 images
   - Ambiguous: 15 images
   - Normal play: 15 images

2. **Distress cases** (50 images)
   - Clear distress: 20 images
   - Mild upset: 15 images
   - Normal emotions: 15 images

3. **Supervision cases** (30 images)
   - Clear violations: 15 images
   - Adequate supervision: 15 images

### Metrics to Track
```python
{
    "total_images": 130,
    "violence_metrics": {
        "precision": 0.95,
        "recall": 0.92,
        "f1": 0.93,
        "false_positives": 3,
        "false_negatives": 5
    },
    "distress_metrics": {...},
    "supervision_metrics": {...},
    "hybrid_performance": {
        "fast_path_usage": 0.72,  # 72% handled by fast path
        "vlm_usage": 0.28,
        "average_latency": "2.8s",
        "accuracy": 0.94
    }
}
```

---

## Deployment Strategy

### Phase 1: Development (Week 1)
- Implement fast-path detectors
- Create routing logic
- Test with existing 3 images
- Validate improvements

### Phase 2: Integration (Week 2)
- Integrate with nura-perception service
- Deploy on Mac M4 Max
- Create comprehensive test suite
- Measure accuracy metrics

### Phase 3: Production (Week 3-4)
- Convert models to GPU-optimized versions
- Deploy on GPU servers
- A/B test vs VLM-only
- Monitor in production

---

## Success Criteria

### Must Have (Week 1)
- ✅ >90% precision on clear violations
- ✅ >85% recall on test dataset
- ✅ <3s average latency (hybrid)
- ✅ Zero false negatives on test images

### Should Have (Week 2)
- ✅ Fast-path handles 70%+ of frames
- ✅ VLM only for ambiguous cases
- ✅ Confidence scoring working
- ✅ Monitoring dashboard

### Nice to Have (Week 3+)
- ✅ Fine-tuned models on childcare data
- ✅ Real-time multi-camera processing
- ✅ Automatic model updates
- ✅ A/B testing framework

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Fast-path models have high false positive rate | High | Tune confidence thresholds, use VLM for validation |
| Model conversion to CoreML/TensorRT fails | Medium | Use PyTorch inference as fallback |
| Fast-path still not fast enough | Low | Models are well-optimized, <100ms is achievable |
| VLM still misses violations | High | Improved prompts + ensemble validation |

---

## Next Steps

1. ✅ **This Week**: Implement Phase 1 (fast-path detectors)
2. ✅ **Week 2**: Routing logic + improved VLM prompts
3. ✅ **Week 3**: Validation suite + accuracy measurement
4. ✅ **Week 4**: Production deployment + monitoring

---

**Status**: Ready to implement  
**Owner**: Development team  
**Timeline**: 4 weeks to production-ready  
**Priority**: CRITICAL - Current 0% detection rate unacceptable
