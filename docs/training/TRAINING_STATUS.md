# Model Training Status

**Last Updated:** 2026-11-05

## Phase 3A: Temporal Violence Detection

### Current Training Session

**Status:** ✅ COMPLETE

**Completed:** 2026-11-05  
**Model:** ResNet50 + GRU (Temporal Sequence Detector)  
**Dataset:** violence-detection-dataset  
**Final Command:**
```bash
python3 tools/training/train_temporal_detector.py \
  --violent tests/data/violence-detection-dataset/violent \
  --normal tests/data/violence-detection-dataset/non-violent \
  --epochs 30 \
  --max-videos 120 \
  --batch-size 8 \
  --output models/temporal_violence.h5
```

**Training Configuration:**
- Sequence Length: 20 frames (~0.67s at 30fps)
- Epochs: 30 (early stopped at 25)
- Batch Size: 8
- Videos: 240 total (120 violent + 120 normal - balanced)
- Training Time: ~45 minutes

**Results:**
- ✅ **Accuracy: 95.83%** (exceeded 80-85% target!)
- Test Loss: 0.3412
- Precision (Normal): 92%, Precision (Violent): 100%
- Recall (Normal): 100%, Recall (Violent): 92%
- F1-Score: 0.96 (both classes)
- Confusion Matrix: TN=24, FP=0, FN=2, TP=22

**Output Model:** `models/temporal_violence.h5` (1.2MB)

### Next Steps After Training

1. **Enable Temporal Detection**
   ```bash
   # Update .env
   ENABLE_TEMPORAL_DETECTION=true
   
   # Restart services
   ./stop.sh && ./start.sh
   ```

2. **Test on Classroom Videos**
   ```bash
   python3 tools/testing/analyze-video.py \
     --video tests/data/classroom/classroom1.mp4 \
     --camera-id classroom-1
   ```

3. **Monitor Performance**
   - Check routing decisions in VLM logs
   - Verify temporal detector triggers on sustained violence
   - Confirm VLM validation on medium-confidence cases

---

## Phase 3B: Distress Detection Enhancement (PLANNED)

**Status:** 📌 READY TO START (after Phase 3A)

**Dataset:** FER2013 + AffectNet (61,732 images)
- Training: 54,554 images
- Testing: 7,178 images

**Model:** MobileNetV2 Transfer Learning

**Expected Improvement:**
- Current: ~60% accuracy (heuristic-based)
- Target: 85-90% accuracy (deep learning)

**Command (when ready):**
```bash
python3 tools/training/train_distress_detector.py \
  --train-dir tests/data/fer2013+affectnet/train \
  --test-dir tests/data/fer2013+affectnet/test \
  --epochs 20 \
  --output models/distress_classifier.h5
```

---

## Dataset Summary

### Available Datasets

| Dataset | Type | Count | Status | Purpose |
|---------|------|-------|--------|---------|
| violence-detection-dataset | Video | 350 videos | ✅ In Use | Temporal violence (Phase 3A) |
| RWF-2000 | Video | 50 videos | ✅ Available | Alternative violence dataset |
| FER2013 + AffectNet | Images | 61,732 | ✅ Ready | Distress detection (Phase 3B) |
| Anomalies (burglary, explosion, shooting) | Video | 149 videos | 📌 Future | Multi-class detection (Phase 6+) |

### Dataset Organization

All datasets are organized in `datasets/` with clear structure:
```
datasets/
├── videos/
│   ├── violence/violent-230          # Primary violence dataset
│   ├── normal/non-violent-120        # Primary normal dataset
│   ├── fighting/                     # RWF-2000 (4 parts, 50 total)
│   └── anomalies/                    # Future use (burglary, explosion, shooting)
└── images/
    └── facial-expressions/
        ├── train-54554               # FER2013 + AffectNet training
        └── test-7178                 # FER2013 + AffectNet testing
```

---

## Training History

### Completed Training Sessions

#### Session 1: Temporal Violence Detector (2026-11-05)
- **Dataset:** violence-detection-dataset (balanced: 120 violent + 120 normal)
- **Model:** ResNet50 + GRU
- **Accuracy:** 95.83%
- **Notes:** Balanced dataset crucial - first attempt with 200:120 ratio achieved only 62.5%

---

## Performance Metrics (After Training)

### Temporal Violence Detector

**Target Metrics:**
- Accuracy: 80-85%
- False Positive Rate: <10%
- False Negative Rate: <15%
- Inference Time: ~300-500ms per sequence

**Actual Metrics:** *Pending training completion*

### Distress Detector (Current Baseline)

**Current Performance (Heuristic):**
- Accuracy: ~60% (estimated)
- Method: Crying sound + facial distress heuristics
- Confidence: Low (0.5-0.7)

**Target Performance (After Phase 3B):**
- Accuracy: 85-90%
- Method: MobileNetV2 transfer learning
- Confidence: High (0.7-0.9)

---

## Integration Status

### Phase 3 Components

| Component | Status | Location |
|-----------|--------|----------|
| Temporal Detector Model | ✅ Implemented | `packages/nura-detectors/src/nura_detectors/temporal_detector.py` |
| Hybrid Router Integration | ✅ Complete | `services/nura-vlm/src/hybrid_router.py` |
| Environment Configuration | ✅ Complete | `.env` (TEMPORAL_* variables) |
| Model File | 🟡 Training | `models/temporal_violence.h5` |
| Testing Script | ✅ Available | `tools/testing/analyze-video.py` |

---

## Troubleshooting

### If Training Fails

1. **Check GPU/Memory:**
   ```bash
   # Monitor system resources
   top
   ```

2. **Reduce Batch Size:**
   ```bash
   python3 tools/training/train_temporal_detector.py \
     --batch-size 8 \  # Reduce from 16
     ...
   ```

3. **Reduce Max Videos:**
   ```bash
   python3 tools/training/train_temporal_detector.py \
     --max-videos 100 \  # Reduce from 200
     ...
   ```

4. **Check Logs:**
   ```bash
   tail -f /tmp/temporal_training.log
   ```

### If Model Accuracy is Low (<75%)

1. **Increase Epochs:**
   - Try 20-30 epochs instead of 15

2. **Use More Data:**
   - Combine violence-detection-dataset + RWF-2000
   - Use all 450 videos

3. **Adjust Sequence Length:**
   - Try 30 frames for longer context
   - Try 15 frames for faster inference

4. **Data Augmentation:**
   - Add horizontal flip
   - Add brightness/contrast adjustments
   - Add random cropping

---

## Notes

- **Dataset Quality:** violence-detection-dataset has better quality than RWF-2000 (more diverse scenarios)
- **Training Time:** M4 Max CPU training takes ~1-2 hours for 200 videos
- **Memory Usage:** Expect ~8-12GB RAM usage during training
- **Model Size:** Final model will be ~25-30MB

---

**Training Progress:** Check `/tmp/claude-*/tasks/bysyvttm2.output` for live updates
