"""
Configuration Service - nura-perception
Centralized configuration management (all .env driven)
"""
import logging
from pydantic_settings import BaseSettings
from pydantic import Field

logger = logging.getLogger(__name__)


class Config(BaseSettings):
    """Centralized configuration from environment variables"""

    # ==================== Service Configuration ====================
    PORT: int = Field(default=8000, description="HTTP server port")
    HOST: str = Field(default="0.0.0.0", description="HTTP server host")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # ==================== NATS Configuration ====================
    NATS_URL: str = Field(default="nats://nats:4222", description="NATS server URL")

    # ==================== Frigate Configuration ====================
    RTSP_BASE: str = Field(default="rtsp://frigate:8554", description="Frigate RTSP base URL")
    FRIGATE_API: str = Field(default="http://frigate:5000", description="Frigate API URL")

    # ==================== Detection Configuration ====================
    DETECTION_CONFIDENCE: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="YOLO detection confidence threshold"
    )
    YOLO_MODEL: str = Field(default="yolov8n.pt", description="YOLO model file")

    # ==================== Pose Estimation Configuration ====================
    ENABLE_POSE_ESTIMATION: bool = Field(default=True, description="Enable MediaPipe pose estimation")
    POSE_CONFIDENCE: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Pose detection confidence"
    )

    # ==================== Tracking Configuration ====================
    ENABLE_BYTETRACK: bool = Field(default=True, description="Enable ByteTrack multi-object tracking")
    TRACK_BUFFER: int = Field(default=30, description="Tracking buffer frames")
    MATCH_THRESHOLD: float = Field(default=0.8, description="Tracking match threshold")

    # ==================== Activity Classification ====================
    FALL_THRESHOLD: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Fall detection threshold based on pose"
    )
    ACTIVITY_WINDOW_FRAMES: int = Field(
        default=30,
        description="Number of frames to consider for activity classification"
    )

    # ==================== Site Configuration ====================
    SITE_ID: str = Field(default="dev-site-001", description="Site identifier")

    # ==================== Performance Configuration ====================
    FRAME_SKIP: int = Field(default=2, description="Process every Nth frame (1=all frames)")
    MAX_FPS: int = Field(default=15, description="Maximum processing FPS")

    class Config:
        env_file = ".env"
        case_sensitive = True

    def log_configuration(self):
        """Log loaded configuration"""
        logger.info("📋 Perception Service Configuration loaded:")
        logger.info(f"  Port: {self.PORT}")
        logger.info(f"  NATS: {self.NATS_URL}")
        logger.info(f"  Frigate API: {self.FRIGATE_API}")
        logger.info(f"  RTSP Base: {self.RTSP_BASE}")
        logger.info(f"  YOLO Model: {self.YOLO_MODEL}")
        logger.info(f"  Detection Confidence: {self.DETECTION_CONFIDENCE}")
        logger.info(f"  Pose Estimation: {self.ENABLE_POSE_ESTIMATION}")
        logger.info(f"  ByteTrack: {self.ENABLE_BYTETRACK}")
        logger.info(f"  Fall Threshold: {self.FALL_THRESHOLD}")
        logger.info(f"  Max FPS: {self.MAX_FPS}")
        logger.info(f"  Site ID: {self.SITE_ID}")

    def validate_config(self) -> tuple[bool, list[str]]:
        """Validate configuration"""
        errors = []

        if self.DETECTION_CONFIDENCE < 0 or self.DETECTION_CONFIDENCE > 1:
            errors.append("❌ DETECTION_CONFIDENCE must be between 0 and 1")

        if self.FALL_THRESHOLD < 0 or self.FALL_THRESHOLD > 1:
            errors.append("❌ FALL_THRESHOLD must be between 0 and 1")

        if self.MAX_FPS < 1 or self.MAX_FPS > 60:
            errors.append("⚠️  MAX_FPS should be between 1 and 60")

        if self.FRAME_SKIP < 1:
            errors.append("❌ FRAME_SKIP must be >= 1")

        return len([e for e in errors if e.startswith("❌")]) == 0, errors


# Global config instance
config = Config()
