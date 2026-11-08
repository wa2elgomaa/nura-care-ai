# Model Training Guide

## 🚀 Quick Start: Train Distress Detector (10 minutes)

### Step 1: Prepare Dataset (2 minutes)
```bash
cd /Users/wgomaa/Work/PixelPlusOne/Nura\ Childcare\ AI/nura-care-source

# Activate VLM environment
cd services/nura-vlm
source .venv/bin/activate
cd ../..

# Prepare distress detection dataset
python training/prepare_distress_dataset.py
```

**Expected Output:**
```
Processing train split...
Processing valid split...

Dataset Statistics:
TRAIN:
  Distress:      XXXX images
  Non-Distress:  XXXX images
  Total:         XXXX images

✅ Dataset prepared at: datasets/distress_binary
```

### Step 2: Train Model (5-10 minutes on Metal GPU)
```bash
# Option A: Fine-tune existing model (RECOMMENDED)
python training/train_distress_detector.py \
  --epochs 30 \
  --batch-size 32 \
  --learning-rate 1e-4

# Option B: Train from scratch (takes longer)
python training/train_distress_detector.py \
  --from-scratch \
  --epochs 50 \
  --batch-size 32
```

**Expected Output:**
```
Epoch 1/30
███████████████████ 45s 123ms/step - loss: 0.4234 - accuracy: 0.8123
Epoch 2/30
███████████████████ 42s 115ms/step - loss: 0.3012 - accuracy: 0.8756
...
Epoch 30/30
███████████████████ 41s 112ms/step - loss: 0.1234 - accuracy: 0.9512

Final Validation Metrics:
  loss: 0.1456
  accuracy: 0.9345
  precision: 0.9234
  recall: 0.9123

✅ Model saved: models/distress_detector_v2.keras
```

### Step 3: Test Model (1 minute)
```bash
# Test on validation set
python tools/test_distress_detector.py \
  --model models/distress_detector_v2.keras \
  --test-dir datasets/distress_binary/valid/

# Test on specific images
python tools/test_distress_detector.py \
  --model models/distress_detector_v2.keras \
  --image tests/data/ToddlerActions/valid/Toddler\ crying/image001.jpg
```

### Step 4: Deploy Model
```bash
# Update environment to use new model
echo "DISTRESS_MODEL_PATH=models/distress_detector_v2.keras" >> .env

# Restart VLM service
./runner/stop_services.sh vlm
./runner/run_vlm_service.sh

# Test end-to-end
./scripts/test-end-to-end.sh
```

## 📊 Training Details

### Dataset Preparation

**prepare_distress_dataset.py** creates a binary classification dataset:

**Distress Class (crying/upset):**
- Toddler crying
- Toddler yawning (indicates tiredness)

**Non-Distress Class (happy/content):**
- Toddler smiling
- Toddler eating
- Toddler drinking
- Toddler playing (stacking ring, swing)
- Toddler sleeping

**Excluded (handled separately):**
- Toddler with knife (safety hazard)
- Toddler on staircase (safety hazard)
- Toddler in W-sitting (posture, not emotion)

### Model Architecture

**Fine-tuning mode** (default):
- Loads existing `distress_classifier.keras`
- Freezes 80% of layers
- Trains last 20% on ToddlerActions
- Fast: ~5-10 minutes
- Good: Preserves learned features

**From-scratch mode** (`--from-scratch`):
- MobileNetV3Small backbone (pretrained on ImageNet)
- Custom classification head
- Slower: ~10-20 minutes
- Better: Optimized for toddlers

### Training Features

✅ **Data Augmentation:**
- Random horizontal flip
- Random rotation (±10°)
- Random zoom (±10%)
- Random brightness/contrast
- Prevents overfitting

✅ **Class Balancing:**
- Automatic class weight calculation
- Handles imbalanced datasets
- Ensures fair learning

✅ **Early Stopping:**
- Monitors validation loss
- Stops if no improvement for 8 epochs
- Restores best weights

✅ **Learning Rate Scheduling:**
- Reduces LR when validation loss plateaus
- Helps find optimal minimum
- Factor: 0.5, Patience: 4 epochs

✅ **Checkpointing:**
- Saves best model during training
- Located in `models/checkpoints/`
- Timestamped filenames

## 🎯 Expected Results

### Training Time (Mac M1/M2 with Metal):
- Data preparation: ~2 minutes
- Fine-tuning: ~5-10 minutes (30 epochs)
- From scratch: ~10-20 minutes (50 epochs)

### Accuracy Expectations:
| Model | Expected Accuracy | Notes |
|-------|------------------|-------|
| Baseline (current) | 70-80% | Generic distress, not toddler-specific |
| Fine-tuned | 85-92% | Trained on ToddlerActions |
| From scratch | 90-95% | Fully optimized for toddlers |

### Performance Metrics:
- **Accuracy:** Overall correctness
- **Precision:** Of detected distress, how many are truly distressed
- **Recall:** Of truly distressed, how many we detected
- **AUC:** Area under ROC curve (threshold-independent)

**Target:** >90% accuracy, >88% precision/recall

## 📁 Output Files

```
models/
├── distress_detector_v2.keras          # Final trained model
└── checkpoints/
    └── distress_detector_20261108_*.keras  # Best epoch checkpoints

logs/training/
├── training_history_20261108_*.png     # Training plots
├── training_summary_20261108_*.txt     # Training summary
└── distress_detector_20261108_*/       # TensorBoard logs

datasets/
└── distress_binary/
    ├── train/
    │   ├── distress/
    │   └── non_distress/
    ├── valid/
    │   ├── distress/
    │   └── non_distress/
    └── dataset_info.txt
```

## 🔧 Troubleshooting

### Issue: "Dataset not found"
```bash
# Solution: Run dataset preparation first
python training/prepare_distress_dataset.py
```

### Issue: "Out of memory" during training
```bash
# Solution: Reduce batch size
python training/train_distress_detector.py --batch-size 16
```

### Issue: "Model not improving"
```bash
# Solution: Try from-scratch training
python training/train_distress_detector.py --from-scratch --epochs 50
```

### Issue: Low accuracy (<80%)
**Possible causes:**
1. Dataset imbalance - Check dataset statistics
2. Too few epochs - Increase `--epochs`
3. Learning rate too high - Decrease `--learning-rate`
4. Need more data - Consider downloading additional datasets

## 📈 Monitoring Training

### View TensorBoard:
```bash
tensorboard --logdir logs/training/
# Open: http://localhost:6006
```

### Check Training Plots:
```bash
open logs/training/training_history_*.png
```

### View Training Summary:
```bash
cat logs/training/training_summary_*.txt
```

## 🎓 Advanced Options

### Custom Training:
```bash
# Train with custom hyperparameters
python training/train_distress_detector.py \
  --epochs 100 \
  --batch-size 64 \
  --learning-rate 2e-4 \
  --output models/distress_custom.keras
```

### Resume Training:
```bash
# Continue from checkpoint
python training/train_distress_detector.py \
  --base-model models/checkpoints/distress_detector_*.keras \
  --epochs 20
```

### Experiment Tracking:
```bash
# Use TensorBoard for visualization
tensorboard --logdir logs/training/ --port 6006
```

## 🚀 Next Steps After Training

1. **Evaluate on test set** - Check real-world performance
2. **Compare with baseline** - A/B test old vs new model
3. **Integrate into pipeline** - Update VLM service
4. **Monitor in production** - Track false positives/negatives
5. **Iterate** - Collect edge cases, retrain

## 🔗 Related Scripts

- `prepare_distress_dataset.py` - Dataset preparation
- `train_distress_detector.py` - Model training
- `tools/test_distress_detector.py` - Model testing
- `tools/evaluate_model.py` - Full evaluation

## 📚 Documentation

- Dataset: `datasets/distress_binary/dataset_info.txt`
- Training logs: `logs/training/training_summary_*.txt`
- Model architecture: Run with `model.summary()`
