# NURA Datasets - Organized Structure

This directory contains organized links to all training datasets.

## Directory Structure

```
datasets/
├── videos/
│   ├── violence/          # Violence detection dataset
│   ├── normal/            # Normal/non-violent videos
│   ├── fighting/          # RWF-2000 fighting dataset
│   └── anomalies/         # Other anomalies (burglary, explosion, shooting)
│
├── images/
│   └── facial-expressions/  # FER2013 + AffectNet dataset
│
└── README.md              # This file
```

## Video Datasets

### Violence Detection
- **violent-230**: 230 violent videos from violence-detection-dataset
- **non-violent-120**: 120 non-violent videos from violence-detection-dataset
- **Total**: 350 videos (balanced dataset)

### Fighting (RWF-2000)
- **part1-17**: 17 fighting videos
- **part2-9**: 9 fighting videos
- **part3-13**: 13 fighting videos
- **part11-11**: 11 fighting videos
- **Total**: 50 videos

### Normal Videos
- **normal-50**: 50 normal behavior videos

### Combined Violence Training Data
- **Violent**: 280 videos (230 + 50 fighting)
- **Normal**: 170 videos (120 + 50 normal)
- **Total**: 450 videos

### Anomalies (Future Use)
- **burglary-50**: 50 burglary videos
- **explosion-49**: 49 explosion videos
- **shooting-50**: 50 shooting videos

## Image Datasets

### Facial Expressions (FER2013 + AffectNet)
- **train-54554**: 54,554 training images
- **test-7178**: 7,178 test images
- **Total**: 61,732 images
- **Emotions**: anger, disgust, fear, happy, sad, surprise, neutral

## Usage

### Temporal Violence Detection Training

**Recommended (Best Quality):**
```bash
python3 tools/training/train_temporal_detector.py \
  --violent datasets/videos/violence/violent-230 \
  --normal datasets/videos/normal/non-violent-120 \
  --epochs 15 \
  --max-videos 200 \
  --batch-size 16 \
  --output models/temporal_violence.h5
```

**Alternative (Fighting Dataset):**
```bash
# Combine all fighting videos
mkdir -p datasets/videos/fighting/combined
find datasets/videos/fighting/part* -type f -name "*.mp4" -exec ln -sf {} datasets/videos/fighting/combined/ \;

python3 tools/training/train_temporal_detector.py \
  --violent datasets/videos/fighting/combined \
  --normal datasets/videos/normal/normal-50 \
  --epochs 15 \
  --max-videos 100 \
  --output models/temporal_fighting.h5
```

### Facial Expression Training (Future)

```bash
python3 tools/training/train_distress_detector.py \
  --train-dir datasets/images/facial-expressions/train-54554 \
  --test-dir datasets/images/facial-expressions/test-7178 \
  --epochs 20 \
  --output models/distress_classifier.h5
```

## Dataset Statistics

| Dataset Type | Count | Status |
|--------------|-------|--------|
| Violence Videos | 280 | ✅ Ready |
| Normal Videos | 170 | ✅ Ready |
| Facial Expression Images | 61,732 | ✅ Ready |
| Anomaly Videos | 149 | 📌 Future |

## Notes

- All directories are **symbolic links** to avoid data duplication
- Original data remains in `tests/data/`
- Videos are in MP4 format
- Images are in various formats (JPG, PNG)
