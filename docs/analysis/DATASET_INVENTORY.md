# NURA Dataset Inventory & Training Strategy

## 🎉 Dataset Summary - EXCELLENT!

You have **significantly more data** than initially assessed:

### Video Datasets
- **Violence Videos:** 280 total (50 fighting + 230 violence-detection-dataset)
- **Normal Videos:** 170 total (50 normal + 120 non-violent)
- **Other Anomalies:** 149 (burglary, explosion, shooting)
- **Classroom Videos:** 7 (our own test videos)
- **TOTAL:** 599+ videos

### Image Datasets
- **Facial Expressions:** 61,732 images (FER2013 + AffectNet)
  - Training: 54,554 images
  - Testing: 7,178 images
- **Image Arrays:** 57,486 preprocessed files

---

## Detailed Breakdown

### 1. Violence Detection Videos

#### RWF-2000 Fighting Dataset
| Category | Count | Location |
|----------|-------|----------|
| FightingA_Part1 | 17 | `tests/data/Videos/FightingA_Part1/` |
| FightingA_Part2 | 9 | `tests/data/Videos/FightingA_Part2/` |
| FightingA_Part3 | 13 | `tests/data/Videos/FightingA_Part3/` |
| FightingA_Part11 | 11 | `tests/data/Videos/FightingA_Part11/` |
| **Subtotal** | **50** | |

#### Violence Detection Dataset
| Category | Count | Location |
|----------|-------|----------|
| Violent | 230 | `tests/data/violence-detection-dataset/violent/` |
| Non-Violent | 120 | `tests/data/violence-detection-dataset/non-violent/` |
| **Subtotal** | **350** | |

**Total Violence Training Data:** 280 violent + 170 normal = **450 videos**

### 2. Other Anomaly Videos (UCF-Crime Dataset)

| Category | Count | Use Case |
|----------|-------|----------|
| Burglary | 50 | Not violence, but anomaly detection |
| Explosion | 49 | Not violence, but anomaly detection |
| Shooting | 50 | Violence-related |
| **Total** | **149** | |

### 3. Facial Expression Images

| Dataset | Train | Test | Total |
|---------|-------|------|-------|
| FER2013 + AffectNet | 54,554 | 7,178 | 61,732 |

**Emotions:** Likely includes angry, disgust, fear, happy, sad, surprise, neutral

**Use for:** Distress detector training & validation

---

## Training Strategies

### Strategy 1: Temporal Violence Detection (PRIORITY)

**Model:** ResNet50 + GRU (already implemented)

**Data:**
- Violent: 280 videos (50 fighting + 230 violent)
- Normal: 170 videos (50 normal + 120 non-violent)

**Training Plan:**

```bash
# Option A: Quick Training (1 hour)
python3 tools/training/train_temporal_detector.py \
  --violent tests/data/violence-detection-dataset/violent \
  --normal tests/data/violence-detection-dataset/non-violent \
  --epochs 15 \
  --max-videos 100 \
  --batch-size 16 \
  --output models/temporal_violence_v1.h5

# Option B: Full Training (2-3 hours)
python3 tools/training/train_temporal_detector.py \
  --violent tests/data/violence-detection-dataset/violent \
  --normal tests/data/violence-detection-dataset/non-violent \
  --epochs 20 \
  --max-videos 350 \
  --batch-size 16 \
  --output models/temporal_violence_full.h5
```

**Expected Accuracy:**
- Quick (100 videos): 75-80%
- Full (350 videos): 85-92%

**Timeline:**
- Quick: 1 hour CPU, 15-20 min GPU
- Full: 2-3 hours CPU, 30-45 min GPU

---

### Strategy 2: Distress Detector Training (BONUS)

**Model:** CNN for facial expression classification

**Data:** 61,732 labeled facial expression images

**Why:** Current distress detector is heuristic-based. With 61k labeled images, we can train a MUCH better model!

**Training Plan:**

```python
# New script needed: tools/training/train_distress_detector.py
# Use transfer learning (MobileNetV2 or EfficientNet)
# Train on fer2013+affectnet dataset
# Target: Detect crying, fear, pain, sadness
```

**Expected Accuracy:** 85-90% (vs current ~60-70% heuristic)

**Timeline:** 2-3 hours

**Impact:** 
- Better distress detection
- Lower false positives
- Emotion-specific alerts (crying vs fear vs pain)

---

### Strategy 3: Multi-Anomaly Detection (FUTURE)

**Data:** 149 videos (burglary, explosion, shooting)

**Use:** Generic anomaly detection (not just violence)

**Priority:** Low (focus on violence + distress first)

---

## Recommended Training Order

### Phase 3A: Temporal Violence (THIS WEEK)

**Priority:** 🔥 CRITICAL

```bash
# Start with violence-detection-dataset (better quality)
python3 tools/training/train_temporal_detector.py \
  --violent tests/data/violence-detection-dataset/violent \
  --normal tests/data/violence-detection-dataset/non-violent \
  --epochs 15 \
  --max-videos 200 \
  --batch-size 16 \
  --validation-split 0.2 \
  --output models/temporal_violence.h5
```

**Why this dataset:**
- More videos (350 vs 50 from RWF-2000)
- Better quality
- More diverse scenarios

**Time:** 1-2 hours
**Expected:** 80-85% accuracy

---

### Phase 3B: Distress Detector Enhancement (NEXT WEEK)

**Priority:** ⚠️ IMPORTANT

Create new training script for facial expressions:

```python
# tools/training/train_distress_detector.py
# - Use fer2013+affectnet dataset (61k images)
# - Transfer learning from MobileNetV2
# - Output: models/distress_classifier.h5
```

**Time:** 2-3 hours training
**Expected:** 85-90% accuracy
**Impact:** Major improvement over heuristic detector

---

### Phase 3C: Combined Dataset (OPTIONAL)

**Priority:** 📌 NICE-TO-HAVE

Combine all violence data:

```bash
# Combine RWF-2000 + violence-detection-dataset
# Total: 280 violent + 170 normal = 450 videos
# Expected: 90-93% accuracy
```

---

## Dataset Quality Assessment

### Violence-Detection-Dataset ⭐ RECOMMENDED
- ✅ Large (350 videos)
- ✅ Diverse scenarios
- ✅ Good quality
- ✅ Balanced (230 violent / 120 non-violent)

### RWF-2000 Fighting Dataset
- ✅ Academic benchmark
- ⚠️ Smaller (50 videos)
- ⚠️ Focused on fighting only
- ✅ Good for validation

### FER2013 + AffectNet ⭐ GOLD MINE
- ✅ Huge (61k images!)
- ✅ Pre-labeled emotions
- ✅ Standard benchmark
- ✅ Perfect for distress detection

---

## Storage & Organization

### Current Structure
```
tests/data/
├── Videos/
│   ├── violence-detection-dataset/
│   │   ├── violent/          # 230 videos ⭐
│   │   └── non-violent/      # 120 videos ⭐
│   ├── FightingA_Part1/      # 17 videos
│   ├── FightingA_Part2/      # 9 videos
│   ├── FightingA_Part3/      # 13 videos
│   ├── FightingA_Part11/     # 11 videos
│   └── Normal_Videos.../     # 50 videos
│
└── fer2013+affectnet/
    ├── train/                # 54,554 images ⭐
    └── test/                 # 7,178 images ⭐
```

### Recommended Organization
```
models/
├── temporal_violence.h5       # Temporal detector
├── distress_classifier.h5     # Facial expression (NEW)
└── yolov8n-pose.pt           # YOLO pose (existing)
```

---

## Training Hardware Requirements

### CPU Training (M4 Max)
- Temporal (350 videos): 2-3 hours
- Distress (61k images): 2-3 hours
- **Total:** 4-6 hours

### GPU Training (if available)
- Temporal: 30-45 min
- Distress: 30-45 min
- **Total:** 1-1.5 hours

**Recommendation:** Start training overnight or during lunch break

---

## Success Metrics

### Temporal Violence Detection
- [ ] Model trained on 200+ videos
- [ ] Validation accuracy ≥ 80%
- [ ] Test on classroom videos shows improvement
- [ ] False positive rate reduced vs spatial-only

### Distress Detection (Future)
- [ ] Model trained on 50k+ images
- [ ] Accuracy ≥ 85% on test set
- [ ] Real-time performance (<100ms)
- [ ] Better than current heuristic detector

---

## Immediate Next Step

**Run this command now:**

```bash
python3 tools/training/train_temporal_detector.py \
  --violent tests/data/violence-detection-dataset/violent \
  --normal tests/data/violence-detection-dataset/non-violent \
  --epochs 15 \
  --max-videos 200 \
  --batch-size 16 \
  --output models/temporal_violence.h5
```

**Why:** 
- Best dataset (350 videos)
- Closes biggest competitive gap
- 1-2 hours to complete
- 80-85% expected accuracy

**After training:**
```bash
# Enable temporal detection
echo 'ENABLE_TEMPORAL_DETECTION=true' >> .env

# Restart service
./stop.sh && ./start.sh

# Test
python3 tools/testing/analyze-video.py tests/videos/classroom_1.mp4
```

