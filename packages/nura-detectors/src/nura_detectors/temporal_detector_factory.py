"""
Temporal Detector Factory - Model Type Switching

Supports multiple temporal detection architectures:
- resnet50_gru: ResNet50 + GRU (default, CPU-optimized, 95.83% accuracy)
- mvit: MViT V2 (high accuracy, requires more compute, 97.50% accuracy)
- tsm: Temporal Shift Module (edge-optimized, real-time capable)
- x3d: X3D-S (efficient, low-latency)

Configuration via .env:
    TEMPORAL_MODEL_TYPE=resnet50_gru
    TEMPORAL_MODEL_PATH=/path/to/model
    TEMPORAL_DEVICE=cpu
"""
import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Model configuration"""
    model_type: str
    model_path: str
    device: str
    sequence_length: int
    input_size: tuple
    batch_size: int = 1


class TemporalDetectorFactory:
    """
    Factory for creating temporal detection models based on configuration.

    Supports:
    - ResNet50+GRU (Keras/TensorFlow)
    - MViT V2 (PyTorch)
    - TSM ResNet50 (PyTorch)
    - X3D-S (PyTorch)
    """

    SUPPORTED_MODELS = {
        'resnet50_gru': {
            'framework': 'tensorflow',
            'sequence_length': 20,
            'input_size': (224, 224),
            'description': 'ResNet50+GRU (CPU-optimized, 95.83% accuracy)',
            'speed': '~150ms CPU',
            'size': '1.2MB'
        },
        'mvit': {
            'framework': 'pytorch',
            'sequence_length': 16,
            'input_size': (224, 224),
            'description': 'MViT V2 (High accuracy, 97.50% accuracy)',
            'speed': '~298ms CPU, ~15ms GPU',
            'size': '392MB'
        },
        'tsm': {
            'framework': 'pytorch',
            'sequence_length': 8,
            'input_size': (224, 224),
            'description': 'TSM ResNet50 (Edge-optimized, real-time)',
            'speed': '~50-80ms CPU (estimated)',
            'size': '~20MB'
        },
        'x3d': {
            'framework': 'pytorch',
            'sequence_length': 13,
            'input_size': (224, 224),
            'description': 'X3D-S (Efficient, low-latency)',
            'speed': '~100-120ms CPU (estimated)',
            'size': '~15MB'
        }
    }

    @classmethod
    def load_config_from_env(cls) -> ModelConfig:
        """Load model configuration from environment variables"""
        model_type = os.getenv('TEMPORAL_MODEL_TYPE', 'resnet50_gru')
        model_path = os.getenv('TEMPORAL_MODEL_PATH', '')
        device = os.getenv('TEMPORAL_DEVICE', 'cpu')

        # Validate model type
        if model_type not in cls.SUPPORTED_MODELS:
            logger.warning(
                f"Unknown model type '{model_type}', falling back to 'resnet50_gru'. "
                f"Supported: {list(cls.SUPPORTED_MODELS.keys())}"
            )
            model_type = 'resnet50_gru'

        # Get model-specific config
        model_info = cls.SUPPORTED_MODELS[model_type]

        # Set default model path if not specified
        if not model_path:
            if model_type == 'resnet50_gru':
                model_path = 'models/temporal_violence.keras'
            elif model_type == 'mvit':
                model_path = 'models/mvit_violence.pth'
            elif model_type == 'tsm':
                model_path = 'models/tsm_violence.pth'
            elif model_type == 'x3d':
                model_path = 'models/x3d_violence.pth'

        return ModelConfig(
            model_type=model_type,
            model_path=model_path,
            device=device,
            sequence_length=model_info['sequence_length'],
            input_size=model_info['input_size']
        )

    @classmethod
    def create(cls, config: Optional[ModelConfig] = None):
        """
        Create temporal detector based on configuration.

        Args:
            config: Model configuration (if None, loads from .env)

        Returns:
            Temporal detector instance
        """
        if config is None:
            config = cls.load_config_from_env()

        logger.info(f"Creating temporal detector: {config.model_type}")
        logger.info(f"  Model path: {config.model_path}")
        logger.info(f"  Device: {config.device}")
        logger.info(f"  Sequence length: {config.sequence_length}")

        model_info = cls.SUPPORTED_MODELS[config.model_type]
        logger.info(f"  {model_info['description']}")
        logger.info(f"  Expected speed: {model_info['speed']}")

        # Create appropriate detector based on type
        if config.model_type == 'resnet50_gru':
            return cls._create_resnet50_gru(config)
        elif config.model_type == 'mvit':
            return cls._create_mvit(config)
        elif config.model_type == 'tsm':
            return cls._create_tsm(config)
        elif config.model_type == 'x3d':
            return cls._create_x3d(config)
        else:
            raise ValueError(f"Unsupported model type: {config.model_type}")

    @classmethod
    def _create_resnet50_gru(cls, config: ModelConfig):
        """Create ResNet50+GRU detector (Keras/TensorFlow)"""
        from .temporal_detector import TemporalViolenceDetector

        return TemporalViolenceDetector(
            sequence_length=config.sequence_length,
            model_path=config.model_path,
            use_pretrained=False
        )

    @classmethod
    def _create_mvit(cls, config: ModelConfig):
        """Create MViT V2 detector (PyTorch)"""
        try:
            from .temporal_detector_mvit import MViTDetector

            return MViTDetector(
                model_path=config.model_path,
                device=config.device,
                sequence_length=config.sequence_length
            )
        except ImportError as e:
            logger.error(f"Failed to load MViT detector: {e}")
            logger.info("Falling back to ResNet50+GRU")
            return cls._create_resnet50_gru(config)

    @classmethod
    def _create_tsm(cls, config: ModelConfig):
        """Create TSM ResNet50 detector (PyTorch)"""
        try:
            from .temporal_detector_tsm import TSMDetector

            return TSMDetector(
                model_path=config.model_path,
                device=config.device,
                sequence_length=config.sequence_length
            )
        except ImportError as e:
            logger.error(f"Failed to load TSM detector: {e}")
            logger.info("Falling back to ResNet50+GRU")
            return cls._create_resnet50_gru(config)

    @classmethod
    def _create_x3d(cls, config: ModelConfig):
        """Create X3D-S detector (PyTorch)"""
        try:
            from .temporal_detector_x3d import X3DDetector

            return X3DDetector(
                model_path=config.model_path,
                device=config.device,
                sequence_length=config.sequence_length
            )
        except ImportError as e:
            logger.error(f"Failed to load X3D detector: {e}")
            logger.info("Falling back to ResNet50+GRU")
            return cls._create_resnet50_gru(config)

    @classmethod
    def list_available_models(cls) -> Dict[str, Any]:
        """List all available model types and their specs"""
        return cls.SUPPORTED_MODELS

    @classmethod
    def print_model_info(cls):
        """Print information about all available models"""
        print("Available Temporal Detection Models:")
        print("=" * 80)

        for model_type, info in cls.SUPPORTED_MODELS.items():
            print(f"\n{model_type.upper()}")
            print(f"  Framework: {info['framework']}")
            print(f"  Description: {info['description']}")
            print(f"  Speed: {info['speed']}")
            print(f"  Size: {info['size']}")
            print(f"  Sequence: {info['sequence_length']} frames")
            print(f"  Input: {info['input_size']}")

        print("\n" + "=" * 80)
        print("\nConfiguration via .env:")
        print("  TEMPORAL_MODEL_TYPE=resnet50_gru|mvit|tsm|x3d")
        print("  TEMPORAL_MODEL_PATH=/path/to/model.keras|.pth")
        print("  TEMPORAL_DEVICE=cpu|cuda")


# Convenience function
def create_temporal_detector(model_type: Optional[str] = None,
                            model_path: Optional[str] = None,
                            device: Optional[str] = None):
    """
    Create temporal detector with optional overrides.

    Args:
        model_type: Override TEMPORAL_MODEL_TYPE env var
        model_path: Override TEMPORAL_MODEL_PATH env var
        device: Override TEMPORAL_DEVICE env var

    Returns:
        Temporal detector instance

    Example:
        # Use .env configuration
        detector = create_temporal_detector()

        # Override model type
        detector = create_temporal_detector(model_type='mvit')

        # Full override
        detector = create_temporal_detector(
            model_type='tsm',
            model_path='models/tsm_violence.pth',
            device='cuda'
        )
    """
    config = TemporalDetectorFactory.load_config_from_env()

    # Apply overrides
    if model_type:
        config.model_type = model_type
        model_info = TemporalDetectorFactory.SUPPORTED_MODELS.get(model_type)
        if model_info:
            config.sequence_length = model_info['sequence_length']
            config.input_size = model_info['input_size']

    if model_path:
        config.model_path = model_path

    if device:
        config.device = device

    return TemporalDetectorFactory.create(config)


if __name__ == '__main__':
    # Print model information
    TemporalDetectorFactory.print_model_info()
