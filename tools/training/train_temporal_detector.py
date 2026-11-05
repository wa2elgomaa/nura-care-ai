#!/usr/bin/env python3
"""
Train Temporal Violence Detector
Trains RNN model on RWF-2000 video dataset

Usage:
    python tools/training/train_temporal_detector.py \\
        --violent tests/data/Videos/FightingA_Part1 \\
        --normal tests/data/Videos/Normal_Videos \\
        --epochs 10 \\
        --output models/temporal_violence_detector.h5
"""
import sys
import argparse
from pathlib import Path
import numpy as np
import cv2
from tqdm import tqdm

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "nura-detectors" / "src"))

try:
    import tensorflow as tf
    from tensorflow import keras
    from nura_detectors.temporal_detector import TemporalViolenceDetector
    HAS_DEPS = True
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install: pip install tensorflow opencv-python")
    HAS_DEPS = False


def extract_frames_from_video(video_path, num_frames=20, skip=5):
    """
    Extract frames from video

    Args:
        video_path: Path to video file
        num_frames: Number of frames to extract
        skip: Skip every N frames (for sampling)

    Returns:
        List of frames or None if error
    """
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        return None

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames < num_frames:
        cap.release()
        return None

    # Sample frames evenly
    frame_indices = np.linspace(0, total_frames - 1, num_frames * skip, dtype=int)
    frame_indices = frame_indices[::skip][:num_frames]

    frames = []
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()

        if ret:
            frames.append(frame)

    cap.release()

    return frames if len(frames) == num_frames else None


def prepare_dataset(violent_dir, normal_dir, sequence_length=20, max_videos_per_class=100):
    """
    Prepare training dataset from videos

    Args:
        violent_dir: Directory with violent videos
        normal_dir: Directory with normal videos
        sequence_length: Frames per sequence
        max_videos_per_class: Limit videos per class

    Returns:
        X (sequences), y (labels)
    """
    print("📦 Preparing dataset...")

    # Initialize detector for feature extraction
    detector = TemporalViolenceDetector(sequence_length=sequence_length)

    if detector.feature_extractor is None:
        print("❌ Feature extractor not available")
        return None, None

    X_sequences = []
    y_labels = []

    # Process violent videos
    violent_videos = list(Path(violent_dir).glob("*.mp4"))[:max_videos_per_class]
    print(f"\n🔴 Processing {len(violent_videos)} violent videos...")

    for video_path in tqdm(violent_videos, desc="Violent"):
        frames = extract_frames_from_video(video_path, num_frames=sequence_length)

        if frames is None:
            continue

        # Extract features for each frame
        detector.reset()
        for frame in frames:
            detector.add_frame(frame)

        if len(detector.frame_buffer) == sequence_length:
            sequence = np.array(list(detector.frame_buffer))
            X_sequences.append(sequence)
            y_labels.append(1)  # Violent = 1

    # Process normal videos
    normal_videos = list(Path(normal_dir).glob("*.mp4"))[:max_videos_per_class]
    print(f"\n🟢 Processing {len(normal_videos)} normal videos...")

    for video_path in tqdm(normal_videos, desc="Normal"):
        frames = extract_frames_from_video(video_path, num_frames=sequence_length)

        if frames is None:
            continue

        detector.reset()
        for frame in frames:
            detector.add_frame(frame)

        if len(detector.frame_buffer) == sequence_length:
            sequence = np.array(list(detector.frame_buffer))
            X_sequences.append(sequence)
            y_labels.append(0)  # Normal = 0

    if len(X_sequences) == 0:
        print("❌ No sequences extracted")
        return None, None

    X = np.array(X_sequences)
    y = np.array(y_labels)

    # Convert labels to categorical
    y_categorical = keras.utils.to_categorical(y, num_classes=2)

    print(f"\n✅ Dataset prepared:")
    print(f"   Total sequences: {len(X)}")
    print(f"   Violent: {np.sum(y == 1)}")
    print(f"   Normal: {np.sum(y == 0)}")
    print(f"   Sequence shape: {X.shape}")
    print(f"   Labels shape: {y_categorical.shape}")

    return X, y_categorical


def train_model(X_train, y_train, X_val, y_val, epochs=10, batch_size=8):
    """
    Train RNN model

    Args:
        X_train: Training sequences
        y_train: Training labels
        X_val: Validation sequences
        y_val: Validation labels
        epochs: Training epochs
        batch_size: Batch size

    Returns:
        Trained model and history
    """
    print("\n🎓 Training model...")

    # Create model
    detector = TemporalViolenceDetector(sequence_length=X_train.shape[1])

    if detector.rnn_model is None:
        print("❌ Model creation failed")
        return None, None

    print("\n📋 Model Architecture:")
    print(detector.get_model_summary())

    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=3,
            restore_best_weights=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=2,
            min_lr=1e-6
        )
    ]

    # Train
    history = detector.rnn_model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1
    )

    return detector, history


def evaluate_model(detector, X_test, y_test):
    """Evaluate trained model"""
    print("\n📊 Evaluating model...")

    loss, accuracy = detector.rnn_model.evaluate(X_test, y_test, verbose=0)

    print(f"\n✅ Test Results:")
    print(f"   Loss: {loss:.4f}")
    print(f"   Accuracy: {accuracy:.2%}")

    # Predictions
    predictions = detector.rnn_model.predict(X_test, verbose=0)
    y_pred = np.argmax(predictions, axis=1)
    y_true = np.argmax(y_test, axis=1)

    # Confusion matrix
    from sklearn.metrics import confusion_matrix, classification_report

    cm = confusion_matrix(y_true, y_pred)
    print(f"\n📈 Confusion Matrix:")

    # Handle both balanced and imbalanced cases
    if cm.shape == (2, 2):
        print(f"   [[TN={cm[0,0]}, FP={cm[0,1]}],")
        print(f"    [FN={cm[1,0]}, TP={cm[1,1]}]]")
    elif cm.shape == (1, 1):
        # Only one class in test set
        if y_true[0] == 0:
            print(f"   [[TN={cm[0,0]}, FP=0],")
            print(f"    [FN=0, TP=0]]  (No violent samples in test set)")
        else:
            print(f"   [[TN=0, FP=0],")
            print(f"    [FN=0, TP={cm[0,0]}]]  (No normal samples in test set)")
    else:
        print(f"   {cm}")

    print(f"\n📝 Classification Report:")
    try:
        print(classification_report(y_true, y_pred, target_names=['Normal', 'Violent'], zero_division=0))
    except Exception as e:
        print(f"   (Classification report unavailable: {e})")
        print(f"   Predicted: {y_pred}")
        print(f"   Actual: {y_true}")

    return accuracy


def main():
    parser = argparse.ArgumentParser(description="Train Temporal Violence Detector")
    parser.add_argument("--violent", required=True, help="Directory with violent videos")
    parser.add_argument("--normal", required=True, help="Directory with normal videos")
    parser.add_argument("--sequence-length", type=int, default=20, help="Frames per sequence")
    parser.add_argument("--epochs", type=int, default=10, help="Training epochs")
    parser.add_argument("--batch-size", type=int, default=8, help="Batch size")
    parser.add_argument("--max-videos", type=int, default=100, help="Max videos per class")
    parser.add_argument("--output", default="models/temporal_violence_detector.h5", help="Output model path")
    parser.add_argument("--test-split", type=float, default=0.2, help="Test split ratio")

    args = parser.parse_args()

    if not HAS_DEPS:
        print("❌ Please install dependencies first")
        return

    print("╔═══════════════════════════════════════════════════════════╗")
    print("║      TEMPORAL VIOLENCE DETECTOR TRAINING                 ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()
    print(f"Violent videos: {args.violent}")
    print(f"Normal videos: {args.normal}")
    print(f"Sequence length: {args.sequence_length} frames")
    print(f"Epochs: {args.epochs}")
    print(f"Batch size: {args.batch_size}")
    print()

    # Prepare dataset
    X, y = prepare_dataset(
        args.violent,
        args.normal,
        sequence_length=args.sequence_length,
        max_videos_per_class=args.max_videos
    )

    if X is None:
        print("❌ Dataset preparation failed")
        return

    # Split train/validation/test
    from sklearn.model_selection import train_test_split

    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=args.test_split, random_state=42, stratify=np.argmax(y, axis=1)
    )

    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.2, random_state=42, stratify=np.argmax(y_temp, axis=1)
    )

    print(f"\n📊 Dataset split:")
    print(f"   Train: {len(X_train)} sequences")
    print(f"   Validation: {len(X_val)} sequences")
    print(f"   Test: {len(X_test)} sequences")

    # Train
    detector, history = train_model(
        X_train, y_train,
        X_val, y_val,
        epochs=args.epochs,
        batch_size=args.batch_size
    )

    if detector is None:
        print("❌ Training failed")
        return

    # Evaluate
    accuracy = evaluate_model(detector, X_test, y_test)

    # Save model
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    detector.save_model(str(output_path))

    print(f"\n💾 Model saved to: {output_path}")
    print(f"\n🎉 Training complete! Final accuracy: {accuracy:.2%}")

    # Compare to article
    print(f"\n📚 Article Results Comparison:")
    print(f"   Article accuracy: 78% (base RNN)")
    print(f"   Article accuracy: 93% (with pose enhancement)")
    print(f"   Your accuracy: {accuracy:.2%}")

    if accuracy >= 0.78:
        print(f"   ✅ Matched or exceeded article's base performance!")
    else:
        print(f"   ⚠️  Below article performance - try more training data or epochs")


if __name__ == "__main__":
    main()
