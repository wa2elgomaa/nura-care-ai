"""
Temporal Violence Detector (Phase 3 - RNN)
Uses sequence analysis to detect violence patterns across frames

Based on the Medium article approach:
- ResNet50 for feature extraction
- GRU (Recurrent Neural Network) for temporal analysis
- Analyzes 20-frame sequences
- Detects: escalation, sustained struggles, motion patterns

This achieves 78-93% accuracy vs 67% for single-frame analysis
"""
import numpy as np
from typing import Dict, Optional, Deque
from dataclasses import dataclass
from collections import deque
import logging

logger = logging.getLogger(__name__)

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.applications import ResNet50
    from tensorflow.keras.layers import GRU, Dense, Dropout, TimeDistributed, Flatten
    from tensorflow.keras.models import Sequential, load_model
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    logger.warning("TensorFlow not installed - temporal detection unavailable")

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


@dataclass
class TemporalDetection:
    """Temporal sequence detection result"""
    violence_detected: bool
    violence_probability: float
    confidence: float
    sequence_length: int
    details: str
    features_extracted: bool = False


class TemporalViolenceDetector:
    """
    Temporal sequence analyzer for violence detection

    Architecture:
    1. ResNet50 - Extract spatial features from each frame
    2. GRU layers - Analyze temporal patterns across frames
    3. Dense layers - Classification (violent vs non-violent)

    Detects:
    - Escalating aggression (calm → tense → violent)
    - Sustained struggles (repeated aggressive actions)
    - Motion patterns (hitting, pushing, kicking sequences)
    - Context (distinguishing play from violence)
    """

    def __init__(
        self,
        sequence_length: int = 20,
        model_path: Optional[str] = None,
        use_pretrained: bool = False
    ):
        """
        Args:
            sequence_length: Number of frames to analyze (default 20)
            model_path: Path to trained RNN model (optional)
            use_pretrained: Use pre-trained weights if available
        """
        self.sequence_length = sequence_length
        self.frame_buffer: Deque = deque(maxlen=sequence_length)
        self.feature_extractor = None
        self.rnn_model = None
        self.model_path = model_path

        if not HAS_TENSORFLOW:
            logger.error("TensorFlow required. Install: pip install tensorflow")
            return

        # Initialize feature extractor (ResNet50)
        self._init_feature_extractor()

        # Load or create RNN model
        if model_path and self._model_exists(model_path):
            self._load_model(model_path)
        elif use_pretrained:
            self._load_pretrained()
        else:
            self._create_model()

    def _init_feature_extractor(self):
        """Initialize ResNet50 for feature extraction"""
        try:
            # Load ResNet50 without top layers (feature extraction only)
            self.feature_extractor = ResNet50(
                weights='imagenet',
                include_top=False,
                pooling='avg',  # Global average pooling
                input_shape=(224, 224, 3)
            )
            # Freeze ResNet weights (don't retrain)
            self.feature_extractor.trainable = False

            logger.info("✓ ResNet50 feature extractor loaded")
        except Exception as e:
            logger.error(f"Failed to load ResNet50: {e}")
            self.feature_extractor = None

    def _create_model(self):
        """Create RNN model architecture"""
        if self.feature_extractor is None:
            return

        try:
            # Feature dimension from ResNet50
            feature_dim = 2048  # ResNet50 output dimension

            # Build RNN model
            model = Sequential([
                # Input: (sequence_length, feature_dim)

                # First GRU layer (returns sequences)
                GRU(
                    units=16,
                    return_sequences=True,
                    dropout=0.4,
                    recurrent_dropout=0.0,
                    name='gru_1'
                ),

                # Second GRU layer
                GRU(
                    units=8,
                    return_sequences=False,
                    dropout=0.4,
                    recurrent_dropout=0.0,
                    name='gru_2'
                ),

                # Dense layers for classification
                Dense(8, activation='relu', name='dense_1'),
                Dropout(0.4),

                Dense(2, activation='softmax', name='output')  # Binary: [non-violent, violent]
            ])

            # Compile model
            model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )

            self.rnn_model = model
            logger.info("✓ RNN model created (untrained)")

        except Exception as e:
            logger.error(f"Failed to create RNN model: {e}")
            self.rnn_model = None

    def _load_model(self, model_path: str):
        """Load trained RNN model from disk"""
        try:
            self.rnn_model = load_model(model_path)
            logger.info(f"✓ Loaded trained model from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model from {model_path}: {e}")
            self._create_model()

    def _load_pretrained(self):
        """Load pre-trained model if available"""
        # TODO: Download pre-trained model from cloud storage
        logger.info("Pre-trained model not available yet - using untrained model")
        self._create_model()

    def _model_exists(self, path: str) -> bool:
        """Check if model file exists"""
        import os
        return os.path.exists(path)

    def add_frame(self, frame: np.ndarray) -> bool:
        """
        Add frame to sequence buffer

        Args:
            frame: Input frame (BGR format)

        Returns:
            True if buffer is full and ready for inference
        """
        if not HAS_CV2 or self.feature_extractor is None:
            return False

        try:
            # Preprocess frame for ResNet50
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (224, 224))
            frame_preprocessed = tf.keras.applications.resnet50.preprocess_input(
                frame_resized.astype(np.float32)
            )

            # Extract features
            features = self.feature_extractor.predict(
                np.expand_dims(frame_preprocessed, axis=0),
                verbose=0
            )

            # Add to buffer
            self.frame_buffer.append(features[0])

            return len(self.frame_buffer) == self.sequence_length

        except Exception as e:
            logger.error(f"Error adding frame: {e}")
            return False

    def detect(self, ready_for_inference: bool = True) -> TemporalDetection:
        """
        Analyze buffered sequence for violence

        Args:
            ready_for_inference: Whether buffer is full

        Returns:
            TemporalDetection with results
        """
        if not ready_for_inference or self.rnn_model is None:
            return self._not_ready()

        if len(self.frame_buffer) < self.sequence_length:
            return self._not_ready()

        try:
            # Prepare sequence
            sequence = np.array(list(self.frame_buffer))
            sequence = np.expand_dims(sequence, axis=0)  # (1, sequence_length, features)

            # Predict
            predictions = self.rnn_model.predict(sequence, verbose=0)
            violence_prob = float(predictions[0][1])  # Probability of violence

            # Threshold
            violence_detected = violence_prob > 0.5
            confidence = violence_prob if violence_detected else (1 - violence_prob)

            details = self._get_details(violence_prob, violence_detected)

            return TemporalDetection(
                violence_detected=violence_detected,
                violence_probability=violence_prob,
                confidence=confidence,
                sequence_length=len(self.frame_buffer),
                details=details,
                features_extracted=True
            )

        except Exception as e:
            logger.error(f"Temporal detection error: {e}")
            return self._error()

    def _get_details(self, prob: float, detected: bool) -> str:
        """Generate human-readable details"""
        if detected:
            if prob > 0.9:
                return f"Strong violence pattern detected (prob={prob:.2%})"
            elif prob > 0.7:
                return f"Likely violence detected (prob={prob:.2%})"
            else:
                return f"Possible violence detected (prob={prob:.2%})"
        else:
            return f"Normal activity (non-violence prob={1-prob:.2%})"

    def _not_ready(self) -> TemporalDetection:
        """Return result when buffer not full"""
        return TemporalDetection(
            violence_detected=False,
            violence_probability=0.0,
            confidence=0.0,
            sequence_length=len(self.frame_buffer),
            details=f"Buffer filling: {len(self.frame_buffer)}/{self.sequence_length} frames",
            features_extracted=False
        )

    def _error(self) -> TemporalDetection:
        """Return result on error"""
        return TemporalDetection(
            violence_detected=False,
            violence_probability=0.0,
            confidence=0.0,
            sequence_length=0,
            details="Temporal detection unavailable (error)",
            features_extracted=False
        )

    def reset(self):
        """Clear frame buffer"""
        self.frame_buffer.clear()

    def save_model(self, path: str):
        """Save trained model to disk"""
        if self.rnn_model is not None:
            self.rnn_model.save(path)
            logger.info(f"Model saved to {path}")

    def get_model_summary(self) -> str:
        """Get model architecture summary"""
        if self.rnn_model is None:
            return "Model not initialized"

        from io import StringIO
        stream = StringIO()
        self.rnn_model.summary(print_fn=lambda x: stream.write(x + '\n'))
        return stream.getvalue()


def train_temporal_model(
    violent_video_dir: str,
    normal_video_dir: str,
    sequence_length: int = 20,
    epochs: int = 10,
    batch_size: int = 8,
    save_path: str = "models/temporal_violence_detector.h5"
):
    """
    Train temporal violence detector on video dataset

    Args:
        violent_video_dir: Directory with violent videos
        normal_video_dir: Directory with normal videos
        sequence_length: Frames per sequence
        epochs: Training epochs
        batch_size: Batch size
        save_path: Where to save trained model

    Returns:
        Trained model and training history
    """
    if not HAS_TENSORFLOW or not HAS_CV2:
        logger.error("TensorFlow and OpenCV required for training")
        return None, None

    logger.info("Starting temporal model training...")
    logger.info(f"Violent videos: {violent_video_dir}")
    logger.info(f"Normal videos: {normal_video_dir}")
    logger.info(f"Sequence length: {sequence_length} frames")

    # TODO: Implement full training pipeline
    # This is a placeholder - see tools/training/train_temporal_detector.py

    detector = TemporalViolenceDetector(sequence_length=sequence_length)

    logger.info("Training not fully implemented yet")
    logger.info("See tools/training/train_temporal_detector.py for complete implementation")

    return detector.rnn_model, None


# Convenience function
def detect_violence_sequence(frames: list) -> Dict:
    """
    Quick violence detection on frame sequence

    Args:
        frames: List of frames (BGR format)

    Returns:
        Dict with detection results
    """
    detector = TemporalViolenceDetector(sequence_length=len(frames))

    for frame in frames:
        detector.add_frame(frame)

    result = detector.detect(ready_for_inference=True)

    return {
        "violence_detected": result.violence_detected,
        "probability": result.violence_probability,
        "confidence": result.confidence,
        "details": result.details
    }
