#!/usr/bin/env python3
"""
Train Enhanced Distress Detector (Phase 3B)
Trains facial expression classifier on FER2013 + AffectNet dataset

Dataset: 61,732 images
- Training: 54,554 images
- Testing: 7,178 images
- Classes: anger, disgust, fear, happy, sad, surprise, neutral

Target: 85-90% accuracy (vs current ~60% heuristic)
Model: MobileNetV2 (transfer learning)
"""
import sys
import argparse
from pathlib import Path
import numpy as np
from tqdm import tqdm
import os

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "nura-detectors" / "src"))

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    from tensorflow.keras.optimizers import Adam
    import cv2
    HAS_DEPS = True
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install: pip install tensorflow opencv-python")
    HAS_DEPS = False


# ANSI colors
BLUE = '\033[0;34m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'


def create_model(num_classes=7, input_shape=(224, 224, 3)):
    """
    Create MobileNetV2-based facial expression classifier

    Args:
        num_classes: Number of emotion classes
        input_shape: Input image shape

    Returns:
        Compiled Keras model
    """
    # Load MobileNetV2 without top layers (transfer learning)
    base_model = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=input_shape
    )

    # Freeze base model layers (use pretrained weights)
    base_model.trainable = False

    # Add custom classification head
    model = keras.Sequential([
        base_model,
        GlobalAveragePooling2D(),
        Dense(256, activation='relu'),
        Dropout(0.5),
        Dense(128, activation='relu'),
        Dropout(0.3),
        Dense(num_classes, activation='softmax', name='predictions')
    ])

    # Compile model
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy', 'top_k_categorical_accuracy']
    )

    return model


def train_model(train_dir, test_dir, epochs=20, batch_size=32, output_path='models/distress_classifier.keras'):
    """
    Train facial expression classifier

    Args:
        train_dir: Training data directory
        test_dir: Test data directory
        epochs: Training epochs
        batch_size: Batch size
        output_path: Output model path
    """
    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}ENHANCED DISTRESS DETECTOR TRAINING (Phase 3B){NC}")
    print(f"{BLUE}{'='*70}{NC}\n")

    print(f"Training data: {train_dir}")
    print(f"Test data: {test_dir}")
    print(f"Epochs: {epochs}")
    print(f"Batch size: {batch_size}")
    print(f"Output: {output_path}\n")

    # Check directories
    train_path = Path(train_dir)
    test_path = Path(test_dir)

    if not train_path.exists():
        print(f"{RED}❌ Training directory not found: {train_dir}{NC}")
        return

    if not test_path.exists():
        print(f"{RED}❌ Test directory not found: {test_dir}{NC}")
        return

    # Get emotion classes
    classes = sorted([d.name for d in train_path.iterdir() if d.is_dir()])
    num_classes = len(classes)

    print(f"{BLUE}📊 Dataset Info:{NC}")
    print(f"  Classes: {num_classes} emotions")
    print(f"  {', '.join(classes)}\n")

    # Count images per class
    print(f"{BLUE}📁 Training Set:{NC}")
    total_train = 0
    for emotion in classes:
        count = len(list((train_path / emotion).glob('*.jpg'))) + \
                len(list((train_path / emotion).glob('*.png')))
        total_train += count
        print(f"  {emotion}: {count:,} images")
    print(f"  Total: {total_train:,} images\n")

    print(f"{BLUE}📁 Test Set:{NC}")
    total_test = 0
    for emotion in classes:
        count = len(list((test_path / emotion).glob('*.jpg'))) + \
                len(list((test_path / emotion).glob('*.png')))
        total_test += count
        print(f"  {emotion}: {count:,} images")
    print(f"  Total: {total_test:,} images\n")

    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    # No augmentation for test (only rescale)
    test_datagen = ImageDataGenerator(rescale=1./255)

    # Load datasets
    print(f"{YELLOW}⏳ Loading datasets...{NC}\n")

    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=True
    )

    test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=False
    )

    # Create model
    print(f"{BLUE}🏗️  Building model...{NC}\n")
    model = create_model(num_classes=num_classes)

    print(f"{BLUE}📋 Model Architecture:{NC}")
    model.summary()
    print()

    # Callbacks
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=1
        ),
        keras.callbacks.ModelCheckpoint(
            str(output_file),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
    ]

    # Train model
    print(f"{BLUE}🎓 Training model...{NC}\n")

    steps_per_epoch = train_generator.samples // batch_size
    validation_steps = test_generator.samples // batch_size

    history = model.fit(
        train_generator,
        steps_per_epoch=steps_per_epoch,
        epochs=epochs,
        validation_data=test_generator,
        validation_steps=validation_steps,
        callbacks=callbacks,
        verbose=1
    )

    # Evaluate final model
    print(f"\n{BLUE}📊 Evaluating model...{NC}\n")

    test_loss, test_accuracy, test_top3 = model.evaluate(test_generator, verbose=0)

    print(f"{GREEN}✅ Training Complete!{NC}\n")
    print(f"📈 Final Results:")
    print(f"  Test Accuracy: {test_accuracy*100:.2f}%")
    print(f"  Test Top-3 Accuracy: {test_top3*100:.2f}%")
    print(f"  Test Loss: {test_loss:.4f}\n")

    # Per-class accuracy
    print(f"{BLUE}📊 Per-Class Performance:{NC}")

    # Get predictions
    test_generator.reset()
    predictions = model.predict(test_generator, verbose=0)
    predicted_classes = np.argmax(predictions, axis=1)
    true_classes = test_generator.classes
    class_labels = list(test_generator.class_indices.keys())

    from sklearn.metrics import classification_report, confusion_matrix

    print(classification_report(
        true_classes,
        predicted_classes,
        target_names=class_labels,
        digits=3
    ))

    print(f"\n{BLUE}📊 Confusion Matrix:{NC}")
    cm = confusion_matrix(true_classes, predicted_classes)
    print(cm)
    print()

    # Distress-specific metrics (anger, fear, sad)
    distress_emotions = ['anger', 'fear', 'sad']
    distress_indices = [class_labels.index(e) for e in distress_emotions if e in class_labels]

    if distress_indices:
        distress_mask = np.isin(true_classes, distress_indices)
        distress_true = true_classes[distress_mask]
        distress_pred = predicted_classes[distress_mask]

        distress_accuracy = np.mean(np.isin(distress_pred, distress_indices))

        print(f"{GREEN}🎯 Distress Detection Performance:{NC}")
        print(f"  Distress classes: {', '.join(distress_emotions)}")
        print(f"  Distress recall: {distress_accuracy*100:.2f}%")
        print(f"  (Ability to detect distressed emotions)\n")

    print(f"{GREEN}💾 Model saved to: {output_path}{NC}\n")

    # Comparison
    print(f"{BLUE}📚 Performance Comparison:{NC}")
    print(f"  Current (heuristic):  ~60% accuracy")
    print(f"  New (deep learning):  {test_accuracy*100:.2f}% accuracy")

    improvement = test_accuracy * 100 - 60
    if improvement > 0:
        print(f"  {GREEN}✅ Improvement: +{improvement:.1f}%{NC}")
    print()


def main():
    parser = argparse.ArgumentParser(description='Train enhanced distress detector')

    parser.add_argument(
        '--train-dir',
        required=True,
        help='Training data directory (with subdirs per emotion)'
    )

    parser.add_argument(
        '--test-dir',
        required=True,
        help='Test data directory (with subdirs per emotion)'
    )

    parser.add_argument(
        '--epochs',
        type=int,
        default=20,
        help='Training epochs (default: 20)'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='Batch size (default: 32)'
    )

    parser.add_argument(
        '--output',
        default='models/distress_classifier.keras',
        help='Output model path (default: models/distress_classifier.keras)'
    )

    args = parser.parse_args()

    if not HAS_DEPS:
        sys.exit(1)

    train_model(
        args.train_dir,
        args.test_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        output_path=args.output
    )


if __name__ == '__main__':
    main()
