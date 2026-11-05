# Phase 3C: X3D Architecture for Enhanced Temporal Detection

**Status:** 📋 Specification  
**Priority:** Medium (Optional improvement to Phase 3)  
**Timeline:** 1-2 weeks  
**Dependencies:** Phase 3A complete (temporal detector trained)

---

## 🎯 Objective

Evaluate and potentially integrate X3D (Expanding Architectures for Efficient Video Recognition) to improve temporal violence detection accuracy while maintaining real-time performance.

**Current:** ResNet50+GRU (95.83% accuracy, ~150ms inference)  
**Target:** X3D-S or X3D-M (96-97% accuracy, <200ms inference)  
**Improvement:** +1-2% accuracy with acceptable speed trade-off

---

## 📊 Background

### Why X3D?

From OUC-CGE research and Facebook Research:

**Advantages:**
1. ✅ **Better accuracy:** 96.8% in OUC-CGE tests (vs our 95.83%)
2. ✅ **Efficient design:** 4.8x fewer multiply-adds than comparable models
3. ✅ **Small parameter count:** 3.8M parameters (X3D-S/M) vs ~25M (our ResNet50+GRU)
4. ✅ **Proven track record:** State-of-the-art on Kinetics, UCF-101, HMDB-51
5. ✅ **Scalable:** Multiple variants (XS, S, M, L) for different speed/accuracy trade-offs

**Key Innovation:**
- Progressive expansion along space, time, width, and depth axes
- High spatiotemporal resolution with low width/parameters
- Optimized for video (not image model + temporal layer)

---

## 🏗️ X3D Architecture Overview

### Model Variants

| Variant | Frames | Top-1 (Kinetics) | Params | FLOPs | Use Case |
|---------|--------|------------------|--------|-------|----------|
| **X3D-XS** | 4 | 68.7% | 3.8M | 0.60G | Mobile/Edge |
| **X3D-S** | 13 | 73.1% | 3.8M | 1.96G | **Recommended for NURA** |
| **X3D-M** | 16 | 75.1% | 3.8M | 4.73G | High accuracy |
| **X3D-L** | 16 | 76.9% | 6.2M | 18.37G | Maximum accuracy |

**Recommendation: X3D-S**
- Sweet spot for accuracy/speed
- 3.8M parameters (6x smaller than our current model)
- 1.96 GFLOPs (reasonable for real-time)
- 13 frames at 6 fps sample rate = ~2 seconds of video

### Architecture Components

```
Input Video Clip
    ↓
Stem (2D Conv + Pool)
    ↓
Stage 1 (Spatial Bottleneck)
    ↓
Stage 2 (Spatiotemporal Expansion)
    ↓
Stage 3 (Temporal Deepening)
    ↓
Stage 4 (Width Expansion)
    ↓
Global Average Pool
    ↓
FC Layer (Classification)
```

**Key Design Principles:**
1. Start small (tiny 2D network)
2. Progressively expand along one axis at a time
3. Prioritize spatiotemporal resolution over width
4. Use depthwise separable convolutions for efficiency

---

## 📋 Implementation Plan

### Phase 3C-1: Research & Setup (2-3 days)

**Goals:**
- Download and test X3D pre-trained models
- Benchmark inference speed on our hardware
- Understand training pipeline

**Tasks:**
1. Install PyTorch and SlowFast framework
   ```bash
   pip install torch torchvision
   git clone https://github.com/facebookresearch/SlowFast.git
   cd SlowFast
   pip install -r requirements.txt
   python setup.py build develop
   ```

2. Download X3D pre-trained models
   ```bash
   # X3D-S (recommended)
   wget https://dl.fbaipublicfiles.com/pyslowfast/x3d_models/x3d_s.pyth
   
   # X3D-M (if S not accurate enough)
   wget https://dl.fbaipublicfiles.com/pyslowfast/x3d_models/x3d_m.pyth
   ```

3. Test inference on sample videos
   ```bash
   python tools/run_net.py \
     --cfg configs/Kinetics/X3D_S.yaml \
     NUM_GPUS 0 \
     TEST.CHECKPOINT_FILE_PATH x3d_s.pyth \
     TEST.BATCH_SIZE 1
   ```

**Deliverables:**
- ✅ SlowFast installed and working
- ✅ X3D models downloaded
- ✅ Inference speed benchmarked on M4 Max
- ✅ Understanding of data format requirements

---

### Phase 3C-2: Data Preparation (2-3 days)

**Goals:**
- Convert our dataset to X3D format
- Create training/validation splits
- Implement data loading pipeline

**Tasks:**
1. Convert videos to X3D format
   ```python
   # X3D expects:
   # - Uniform frame sampling (e.g., 13 frames from 2-second clip)
   # - 224x224 resolution
   # - RGB format
   # - Labels: 0 (normal), 1 (violent)
   ```

2. Create dataset manifest
   ```python
   # Format: video_path start_frame end_frame label
   # datasets/x3d/train.csv
   # datasets/x3d/val.csv
   # datasets/x3d/test.csv
   ```

3. Update dataset class
   ```python
   # tools/training/x3d_dataset.py
   class ViolenceDataset(torch.utils.data.Dataset):
       def __init__(self, csv_file, num_frames=13):
           # Load video clips
           # Sample frames uniformly
           # Resize to 224x224
           # Normalize
   ```

**Deliverables:**
- ✅ Dataset converted to X3D format
- ✅ train/val/test splits created (same as Phase 3A for comparison)
- ✅ Data loader tested and working

---

### Phase 3C-3: Fine-tuning (3-5 days)

**Goals:**
- Fine-tune X3D on our violence detection dataset
- Achieve >96% accuracy
- Optimize for inference speed

**Training Configuration:**

```yaml
# configs/Violence/X3D_S.yaml

TRAIN:
  ENABLE: True
  DATASET: violence
  BATCH_SIZE: 16
  EVAL_PERIOD: 5
  CHECKPOINT_PERIOD: 5
  AUTO_RESUME: True

DATA:
  NUM_FRAMES: 13
  SAMPLING_RATE: 6
  TRAIN_JITTER_SCALES: [256, 320]
  TRAIN_CROP_SIZE: 224
  TEST_CROP_SIZE: 224
  INPUT_CHANNEL_NUM: [3]

MODEL:
  MODEL_NAME: X3D
  NUM_CLASSES: 2  # normal, violent
  ARCH: x3d_s
  LOSS_FUNC: cross_entropy

SOLVER:
  BASE_LR: 0.01
  LR_POLICY: cosine
  MAX_EPOCH: 30
  MOMENTUM: 0.9
  WEIGHT_DECAY: 1e-4
  WARMUP_EPOCHS: 5.0
  WARMUP_START_LR: 0.001
  OPTIMIZING_METHOD: sgd

TEST:
  ENABLE: True
  DATASET: violence
  BATCH_SIZE: 8
  NUM_ENSEMBLE_VIEWS: 10
  NUM_SPATIAL_CROPS: 3
```

**Training Command:**
```bash
python tools/run_net.py \
  --cfg configs/Violence/X3D_S.yaml \
  DATA.PATH_TO_DATA_DIR datasets/x3d \
  NUM_GPUS 0 \
  TRAIN.CHECKPOINT_FILE_PATH x3d_s.pyth
```

**Expected Results:**
- Training accuracy: >97%
- Validation accuracy: >96%
- Test accuracy: >95%
- Training time: 4-6 hours (30 epochs)

**Deliverables:**
- ✅ Trained X3D-S model
- ✅ Training logs and metrics
- ✅ Model saved to `models/x3d_violence.pyth`

---

### Phase 3C-4: Integration (2-3 days)

**Goals:**
- Integrate X3D into existing detection pipeline
- Create unified interface
- Benchmark against ResNet50+GRU

**Tasks:**

1. Create X3D detector wrapper
   ```python
   # packages/nura-detectors/src/nura_detectors/x3d_detector.py
   
   class X3DTemporalDetector:
       def __init__(self, model_path, num_frames=13):
           self.model = load_x3d_model(model_path)
           self.num_frames = num_frames
           self.frame_buffer = deque(maxlen=num_frames)
       
       def add_frame(self, frame):
           # Add frame to buffer
           # Sample uniformly when buffer full
           pass
       
       def detect(self):
           # Run X3D inference
           # Return probability and detection
           pass
   ```

2. Update hybrid router
   ```python
   # services/nura-vlm/src/hybrid_router.py
   
   # Add X3D option
   if os.getenv('USE_X3D_TEMPORAL', 'false') == 'true':
       self.temporal_detector = X3DTemporalDetector(
           model_path=os.getenv('X3D_MODEL_PATH'),
           num_frames=13
       )
   else:
       self.temporal_detector = TemporalViolenceDetector(...)
   ```

3. Environment configuration
   ```bash
   # .env
   USE_X3D_TEMPORAL=false  # Set to true to use X3D
   X3D_MODEL_PATH=models/x3d_violence.pyth
   X3D_NUM_FRAMES=13
   X3D_CONFIDENCE_THRESHOLD=0.7
   ```

**Deliverables:**
- ✅ X3D detector integrated
- ✅ Switchable between ResNet50+GRU and X3D
- ✅ Configuration via .env

---

### Phase 3C-5: Evaluation & Comparison (2-3 days)

**Goals:**
- Comprehensive comparison: X3D vs ResNet50+GRU
- Decision: Keep, switch, or run both

**Metrics to Compare:**

| Metric | ResNet50+GRU | X3D-S | X3D-M | Winner |
|--------|--------------|-------|-------|--------|
| Test Accuracy | 95.83% | ? | ? | TBD |
| False Positive Rate | 8.3% | ? | ? | TBD |
| False Negative Rate | 8.3% | ? | ? | TBD |
| F1-Score | 0.96 | ? | ? | TBD |
| Model Size | ~25MB | ~15MB | ~15MB | X3D |
| Parameters | ~25M | 3.8M | 3.8M | X3D |
| Inference Time (CPU) | 150ms | ? | ? | TBD |
| Inference Time (GPU) | N/A | ? | ? | TBD |
| Training Time | 45min | ? | ? | TBD |
| Memory Usage | ~2GB | ? | ? | TBD |

**Test Script:**
```bash
# tools/testing/compare_temporal_models.py

python3 tools/testing/compare_temporal_models.py \
  --model1 models/temporal_violence.keras \
  --model1-type rnn \
  --model2 models/x3d_violence.pyth \
  --model2-type x3d \
  --test-dir datasets/videos \
  --output comparison_report.md
```

**Decision Matrix:**

```
IF X3D accuracy > ResNet50+GRU + 2% AND X3D speed < 300ms:
    → Switch to X3D (clear winner)
    
ELIF X3D accuracy > ResNet50+GRU + 1% AND X3D speed < 200ms:
    → Switch to X3D (better accuracy, acceptable speed)
    
ELIF X3D accuracy ≈ ResNet50+GRU (±0.5%) AND X3D speed < ResNet50+GRU:
    → Switch to X3D (same accuracy, faster/smaller)
    
ELIF X3D accuracy < ResNet50+GRU:
    → Keep ResNet50+GRU (our model is better)
    
ELSE:
    → Keep both as options, let user choose via .env
```

**Deliverables:**
- ✅ Comprehensive comparison report
- ✅ Decision documented
- ✅ Recommendation with justification

---

## 🎯 Success Criteria

### Must Have
- ✅ X3D model trained on our dataset
- ✅ Inference speed benchmarked
- ✅ Accuracy compared with baseline
- ✅ Integration working (switchable via config)

### Should Have
- ✅ X3D accuracy ≥ 96% (better than our 95.83%)
- ✅ Inference time < 200ms (acceptable for real-time)
- ✅ Model size < 20MB (for deployment)
- ✅ Clear documentation on which model to use when

### Nice to Have
- Multi-scale ensemble (ResNet50+GRU short-term + X3D long-term)
- GPU-optimized inference
- Quantized models for edge deployment

---

## 📊 Expected Outcomes

### Scenario 1: X3D is Better (70% probability)
**Result:** X3D accuracy 96-97%, speed 150-200ms  
**Action:** Switch to X3D as default temporal detector  
**Impact:** +1-2% accuracy improvement, smaller model size

### Scenario 2: Similar Performance (20% probability)
**Result:** X3D accuracy ~96%, speed ~150ms  
**Action:** Offer both models as options  
**Impact:** Flexibility for different deployment scenarios

### Scenario 3: ResNet50+GRU is Better (10% probability)
**Result:** X3D accuracy < 95% or speed > 300ms  
**Action:** Keep ResNet50+GRU, archive X3D research  
**Impact:** Validation that our approach was already optimal

---

## 🛠️ Technical Challenges

### Challenge 1: Framework Integration
**Issue:** SlowFast uses PyTorch, we use TensorFlow/Keras  
**Solutions:**
- Option A: Convert X3D to TensorFlow/Keras (using ONNX)
- Option B: Run PyTorch model via ONNX Runtime
- Option C: Keep separate PyTorch environment for X3D
**Recommendation:** Option B (ONNX Runtime) for best compatibility

### Challenge 2: Frame Sampling
**Issue:** X3D expects uniform sampling, our current system is sequential  
**Solutions:**
- Buffer frames and sample uniformly every N frames
- Pre-process videos offline with uniform sampling
**Recommendation:** Runtime uniform sampling (more flexible)

### Challenge 3: Inference Speed on CPU
**Issue:** SlowFast models may be slower on CPU than GPU  
**Solutions:**
- Optimize with ONNX Runtime
- Quantize model (INT8)
- Use smaller variant (X3D-XS) if needed
**Recommendation:** Start with X3D-S + ONNX optimization

### Challenge 4: Different Temporal Windows
**Issue:** X3D uses 13 frames (~2s), we use 20 frames (0.67s)  
**Solutions:**
- Accept the difference (different time scales)
- Run both: ResNet50+GRU (fast) + X3D (accurate)
**Recommendation:** Two-tier system (covered in Challenge solutions)

---

## 📁 File Structure

```
specs/030-phase3c-x3d/
├── spec.md                           # This file
├── x3d_architecture.md               # Detailed architecture docs
└── comparison_metrics.md             # Evaluation criteria

packages/nura-detectors/src/nura_detectors/
├── x3d_detector.py                   # X3D detector wrapper
└── temporal_detector.py              # Current RNN detector (keep)

tools/training/
├── train_x3d_detector.py             # X3D training script
├── train_temporal_detector.py        # Current training (keep)
└── compare_temporal_models.py        # Comparison script

configs/Violence/
├── X3D_S.yaml                        # X3D-S config
└── X3D_M.yaml                        # X3D-M config

models/
├── temporal_violence.keras           # Current model
├── x3d_violence.pyth                 # Trained X3D model
└── x3d_s.pyth                        # Pre-trained X3D-S (Kinetics)

datasets/x3d/
├── train.csv                         # Training manifest
├── val.csv                           # Validation manifest
└── test.csv                          # Test manifest
```

---

## 🔄 Integration with Existing System

### Current Architecture
```
Frame → ResNet50 Feature Extraction → GRU Sequence → Classification
        (2048 features)                (20 frames)    (violent/normal)
```

### X3D Architecture
```
Frame Sequence → X3D Network → Classification
(13 frames)      (end-to-end)  (violent/normal)
```

### Hybrid Option (Both Models)
```
Frame Buffer
    ├── Short-term (20 frames, 0.67s) → ResNet50+GRU → Immediate alerts
    └── Long-term (13 frames, 2s)     → X3D          → Episode detection
         ↓
    Fusion Layer (optional)
         ↓
    Final Decision
```

---

## 💰 Cost-Benefit Analysis

### Costs
- **Development time:** 1-2 weeks
- **Training time:** 4-6 hours
- **Learning curve:** PyTorch/SlowFast framework
- **Framework dependency:** Additional library (PyTorch)
- **Deployment complexity:** Two models vs one

### Benefits
- **Accuracy improvement:** +1-2% expected
- **Smaller model:** 3.8M vs 25M parameters
- **State-of-the-art:** Proven architecture
- **Flexibility:** Multiple variants for different needs
- **Future-proof:** Active research/development

### ROI Calculation
```
IF accuracy improvement > 1%:
    Benefit = (1% fewer false positives/negatives) × (incidents per day) × (time saved)
    Cost = 2 weeks development + maintenance overhead
    
    For 100 incidents/day, 1% = 1 fewer false alarm/day
    1 false alarm = ~5 minutes investigation time
    = 5 minutes × 365 days = 30 hours/year saved
    
    ROI = Positive if accuracy gain > 1%
```

---

## 📝 Decision Points

### Go/No-Go Decision (After Phase 3C-1)
**Criteria:**
- ✅ SlowFast framework works on our system
- ✅ Inference speed < 300ms on CPU
- ✅ Can convert to ONNX for deployment

**If NO:** Abort Phase 3C, keep ResNet50+GRU

### Continue/Pivot Decision (After Phase 3C-3)
**Criteria:**
- ✅ Training accuracy > 96%
- ✅ Validation accuracy > 95%
- ✅ Training converged (not overfitting)

**If NO:** Try X3D-M or adjust hyperparameters

### Deploy/Archive Decision (After Phase 3C-5)
**Criteria:**
- ✅ X3D accuracy ≥ ResNet50+GRU + 1%
- ✅ X3D speed < 200ms
- ✅ Integration stable

**If YES:** Deploy X3D as default  
**If NO:** Keep ResNet50+GRU, document findings

---

## 🎓 Learning Outcomes

**Technical Skills:**
- PyTorch model training and deployment
- SlowFast framework usage
- Video action recognition architectures
- Model comparison and benchmarking
- ONNX conversion and optimization

**Research Skills:**
- Reading academic papers (CVPR 2020)
- Reproducing research results
- Adapting pre-trained models to new domains
- Hyperparameter tuning for video models

**Product Skills:**
- Cost-benefit analysis for ML improvements
- A/B testing of models
- Performance optimization
- Deployment decision-making

---

## 📚 References

**Papers:**
- X3D: Expanding Architectures for Efficient Video Recognition (CVPR 2020)
  - https://arxiv.org/abs/2004.04730
- SlowFast Networks for Video Recognition (ICCV 2019)
  - https://arxiv.org/abs/1812.03982

**Code:**
- PySlowFast: https://github.com/facebookresearch/SlowFast
- Model Zoo: https://github.com/facebookresearch/SlowFast/blob/main/MODEL_ZOO.md

**Related:**
- OUC-CGE (classroom engagement): https://github.com/oucyy361/OUC-CGE
- Our Phase 3A: ResNet50+GRU (95.83% accuracy)

---

## ✅ Checklist

### Before Starting
- [ ] Phase 3A complete (baseline established)
- [ ] Phase 3B complete (distress detector trained)
- [ ] 1-2 weeks allocated for Phase 3C
- [ ] Decision to proceed approved

### Phase 3C-1: Setup
- [ ] SlowFast installed
- [ ] X3D models downloaded
- [ ] Inference tested
- [ ] Speed benchmarked

### Phase 3C-2: Data Prep
- [ ] Dataset converted
- [ ] Manifests created
- [ ] Data loader working

### Phase 3C-3: Training
- [ ] Training completed
- [ ] Accuracy > 95%
- [ ] Model saved

### Phase 3C-4: Integration
- [ ] X3D detector wrapper created
- [ ] Hybrid router updated
- [ ] Configuration working

### Phase 3C-5: Evaluation
- [ ] Comprehensive comparison done
- [ ] Decision made
- [ ] Documentation updated

---

**Status:** Ready for implementation when Phase 3B completes  
**Next Step:** Review and approve specification  
**Owner:** TBD  
**Estimated Effort:** 1-2 weeks full-time
