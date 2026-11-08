#!/usr/bin/env python3
"""
Train Enhanced Distress Detector for Toddlers

Fine-tunes the existing distress classifier on ToddlerActions dataset
for improved crying detection in childcare settings.

Usage:
    python training/train_distress_detector.py [--epochs 30] [--batch-size 32]
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import matplotlib.pyplot as plt

# Configuration
DATASET_DIR = Path("datasets/distress_binary")
MODELS_DIR = Path("models")
LOGS_DIR = Path("logs/training")
CHECKPOINT_DIR = Path("models/checkpoints")

# Create directories
LOGS_DIR.mkdir(parents=True, exist_ok=True)
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

# Image settings
IMG_SIZE = (224, 224)
IMG_SHAPE = IMG_SIZE + (3,)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Train Distress Detector")
    parser.add_argument("--epochs", type=int, default=30, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--learning-rate", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--base-model", type=str, default="models/distress_classifier.keras",
                       help="Path to base model for fine-tuning")
    parser.add_argument("--from-scratch", action="store_true",
                       help="Train from scratch instead of fine-tuning")
    parser.add_argument("--output", type=str, default="models/distress_detector_v2.keras",
                       help="Output model path")
    return parser.parse_args()


def create_dataset(data_dir, batch_size, shuffle=True, augment=False):
    """Create TensorFlow dataset from directory."""

    # Data augmentation for training
    if augment:
        data_augmentation = keras.Sequential([
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.1),
            layers.RandomZoom(0.1),
            layers.RandomContrast(0.1),
            layers.RandomBrightness(0.1),
        ])
    else:
        data_augmentation = None

    # Load dataset
    ds = keras.utils.image_dataset_from_directory(
        data_dir,
        labels='inferred',
        label_mode='binary',  # Binary classification
        class_names=['non_distress', 'distress'],  # Order: 0=non-distress, 1=distress
        image_size=IMG_SIZE,
        batch_size=batch_size,
        shuffle=shuffle
    )

    # Normalize images
    normalization = layers.Rescaling(1./255)

    if augment and data_augmentation:
        ds = ds.map(lambda x, y: (data_augmentation(x, training=True), y))

    ds = ds.map(lambda x, y: (normalization(x), y))

    # Performance optimization
    ds = ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    return ds


def create_model_from_scratch():
    """Create a new distress detection model using transfer learning."""

    print("Creating new model with MobileNetV3 backbone...")

    # Use MobileNetV3 pretrained on ImageNet
    base_model = keras.applications.MobileNetV3Small(
        input_shape=IMG_SHAPE,
        include_top=False,
        weights='imagenet'
    )

    # Freeze base model initially
    base_model.trainable = False

    # Create classifier head
    inputs = keras.Input(shape=IMG_SHAPE)
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(1, activation='sigmoid', name='distress_output')(x)

    model = keras.Model(inputs, outputs, name='distress_detector')

    return model, base_model


def load_and_modify_base_model(model_path):
    """Load existing model and prepare for fine-tuning."""

    print(f"Loading base model from {model_path}...")

    try:
        base_model = keras.models.load_model(model_path)
        print(f"✅ Loaded model: {base_model.name}")
        print(f"   Input shape: {base_model.input_shape}")
        print(f"   Output shape: {base_model.output_shape}")

        # Freeze early layers, unfreeze last few layers for fine-tuning
        total_layers = len(base_model.layers)
        freeze_until = int(total_layers * 0.8)  # Freeze 80% of layers

        for i, layer in enumerate(base_model.layers):
            if i < freeze_until:
                layer.trainable = False
            else:
                layer.trainable = True

        trainable = sum([1 for layer in base_model.layers if layer.trainable])
        print(f"   Trainable layers: {trainable}/{total_layers}")

        return base_model, None

    except Exception as e:
        print(f"⚠ Warning: Could not load base model: {e}")
        print(f"   Creating new model from scratch...")
        return create_model_from_scratch()


def calculate_class_weights(train_ds):
    """Calculate class weights for imbalanced dataset."""

    print("Calculating class weights...")

    # Count samples in each class
    class_counts = [0, 0]  # [non-distress, distress]

    for _, labels in train_ds:
        for label in labels.numpy():
            class_counts[int(label)] += 1

    total = sum(class_counts)

    # Calculate weights
    class_weight = {
        0: total / (2 * class_counts[0]),  # non-distress
        1: total / (2 * class_counts[1]),  # distress
    }

    print(f"   Non-distress samples: {class_counts[0]}")
    print(f"   Distress samples: {class_counts[1]}")
    print(f"   Class weights: {class_weight}")

    return class_weight


def plot_training_history(history, output_path):
    """Plot training history."""

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Accuracy
    axes[0, 0].plot(history.history['accuracy'], label='Train')
    axes[0, 0].plot(history.history['val_accuracy'], label='Validation')
    axes[0, 0].set_title('Model Accuracy')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Accuracy')
    axes[0, 0].legend()
    axes[0, 0].grid(True)

    # Loss
    axes[0, 1].plot(history.history['loss'], label='Train')
    axes[0, 1].plot(history.history['val_loss'], label='Validation')
    axes[0, 1].set_title('Model Loss')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Loss')
    axes[0, 1].legend()
    axes[0, 1].grid(True)

    # Precision
    if 'precision' in history.history:
        axes[1, 0].plot(history.history['precision'], label='Train')
        axes[1, 0].plot(history.history['val_precision'], label='Validation')
        axes[1, 0].set_title('Precision')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Precision')
        axes[1, 0].legend()
        axes[1, 0].grid(True)

    # Recall
    if 'recall' in history.history:
        axes[1, 1].plot(history.history['recall'], label='Train')
        axes[1, 1].plot(history.history['val_recall'], label='Validation')
        axes[1, 1].set_title('Recall')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Recall')
        axes[1, 1].legend()
        axes[1, 1].grid(True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"✅ Training history plot saved: {output_path}")


def train_model(args):
    """Main training function."""

    print("=" * 80)
    print("DISTRESS DETECTOR TRAINING")
    print("=" * 80)
    print(f"Dataset: {DATASET_DIR}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch size: {args.batch_size}")
    print(f"Learning rate: {args.learning_rate}")
    print("=" * 80)

    # Check dataset exists
    if not DATASET_DIR.exists():
        print(f"❌ Error: Dataset not found at {DATASET_DIR}")
        print(f"   Run: python training/prepare_distress_dataset.py")
        sys.exit(1)

    # Load datasets
    print("\n📂 Loading datasets...")
    train_ds = create_dataset(
        DATASET_DIR / "train",
        batch_size=args.batch_size,
        shuffle=True,
        augment=True  # Data augmentation for training
    )

    val_ds = create_dataset(
        DATASET_DIR / "valid",
        batch_size=args.batch_size,
        shuffle=False,
        augment=False
    )

    # Calculate class weights
    class_weight = calculate_class_weights(train_ds)

    # Create or load model
    print("\n🧠 Preparing model...")
    if args.from_scratch or not Path(args.base_model).exists():
        model, base_model = create_model_from_scratch()
    else:
        model, base_model = load_and_modify_base_model(args.base_model)

    model.summary()

    # Compile model
    print("\n⚙️  Compiling model...")
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=args.learning_rate),
        loss='binary_crossentropy',
        metrics=[
            'accuracy',
            keras.metrics.Precision(name='precision'),
            keras.metrics.Recall(name='recall'),
            keras.metrics.AUC(name='auc'),
        ]
    )

    # Callbacks
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    callbacks = [
        keras.callbacks.ModelCheckpoint(
            filepath=str(CHECKPOINT_DIR / f"distress_detector_{timestamp}_epoch{{epoch:02d}}_val{{val_accuracy:.4f}}.keras"),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=8,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=4,
            min_lr=1e-7,
            verbose=1
        ),
        keras.callbacks.TensorBoard(
            log_dir=str(LOGS_DIR / f"distress_detector_{timestamp}"),
            histogram_freq=1
        ),
    ]

    # Train
    print("\n🚀 Starting training...")
    print("-" * 80)

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        callbacks=callbacks,
        class_weight=class_weight,
        verbose=1
    )

    # Evaluate
    print("\n📊 Evaluating model...")
    results = model.evaluate(val_ds, verbose=1)

    print("\n" + "=" * 80)
    print("TRAINING COMPLETE")
    print("=" * 80)
    print(f"Final Validation Metrics:")
    for metric_name, value in zip(model.metrics_names, results):
        print(f"  {metric_name}: {value:.4f}")

    # Save final model
    print(f"\n💾 Saving model to {args.output}...")
    model.save(args.output)
    print(f"✅ Model saved successfully!")

    # Plot training history
    plot_path = LOGS_DIR / f"training_history_{timestamp}.png"
    plot_training_history(history, plot_path)

    # Save training summary
    summary_path = LOGS_DIR / f"training_summary_{timestamp}.txt"
    with open(summary_path, "w") as f:
        f.write("Distress Detector Training Summary\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Dataset: {DATASET_DIR}\n")
        f.write(f"Epochs: {args.epochs}\n")
        f.write(f"Batch size: {args.batch_size}\n")
        f.write(f"Learning rate: {args.learning_rate}\n\n")
        f.write("Final Validation Metrics:\n")
        for metric_name, value in zip(model.metrics_names, results):
            f.write(f"  {metric_name}: {value:.4f}\n")
        f.write(f"\nModel saved to: {args.output}\n")

    print(f"✅ Training summary saved: {summary_path}")

    print("\n" + "=" * 80)
    print("Next steps:")
    print(f"  1. Review training plots: {plot_path}")
    print(f"  2. Test model: python tools/test_distress_detector.py --model {args.output}")
    print(f"  3. Update .env: DISTRESS_MODEL_PATH={args.output}")
    print(f"  4. Restart VLM service: ./runner/stop_services.sh vlm && ./runner/run_vlm_service.sh")
    print("=" * 80)


if __name__ == "__main__":
    args = parse_args()
    train_model(args)
