"""
Configuration Service - nura-vlm

Centralized configuration management using Pydantic
Makes it easy to track all required env vars per service with type validation
"""

import os
import logging
from typing import List, Tuple
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

logger = logging.getLogger(__name__)


class Config(BaseSettings):
    """Centralized configuration from environment variables with Pydantic validation"""

    # ==================== VLM Service Configuration ====================
    PORT: int = Field(default=8001, description="HTTP server port")
    HOST: str = Field(default="0.0.0.0", description="HTTP server host")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # ==================== Model Paths ====================
    YOLO_MODEL_PATH: str = Field(default="models/yolo11n.pt", description="Path to YOLO model")
    EMBEDDING_MODEL: str = Field(
        default="Salesforce/blip-image-captioning-base",
        description="HuggingFace embedding model"
    )
    FACE_RECOGNITION_MODEL: str = Field(default="buffalo_l", description="InsightFace model name")

    # ==================== Ollama Configuration ====================
    OLLAMA_HOST: str = Field(default="http://localhost:11434", description="Ollama server URL")
    OLLAMA_MODEL: str = Field(default="llama3.2-vision", description="Ollama vision model")
    OLLAMA_TIMEOUT: int = Field(default=120, ge=1, le=600, description="Ollama request timeout (seconds)")

    # ==================== PostgreSQL Configuration ====================
    POSTGRES_HOST: str = Field(default="localhost", description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5432, ge=1, le=65535, description="PostgreSQL port")
    POSTGRES_DB: str = Field(default="nura_db", description="PostgreSQL database name")
    POSTGRES_USER: str = Field(default="nura", description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(default="PaSSw0rd!", description="PostgreSQL password")

    # ==================== Storage Service Configuration ====================
    STORAGE_SERVICE_URL: str = Field(
        default="http://localhost:3001",
        description="Storage service base URL"
    )
    STORAGE_API_KEY: str = Field(default="", description="Storage service API key (optional)")

    # ==================== Redis Configuration ====================
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, ge=1, le=65535, description="Redis port")

    # ==================== Face Recognition Configuration ====================
    FACE_RECOGNITION_THRESHOLD: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Face similarity threshold (0-1)"
    )
    FACE_DETECTION_SIZE: Tuple[int, int] = Field(
        default=(640, 640),
        description="Face detection input size"
    )
    FACE_EMBEDDING_DIM: int = Field(default=512, description="Face embedding dimension")

    # ==================== Person Search Configuration ====================
    FUZZY_SEARCH_THRESHOLD: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Fuzzy name search threshold (0-1)"
    )
    VECTOR_SEARCH_LIMIT: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Max results for vector search"
    )

    # ==================== Visitor/Guardian Configuration ====================
    VISITOR_DEFAULT_DURATION_HOURS: int = Field(
        default=8,
        ge=1,
        le=48,
        description="Default visitor pass duration (hours)"
    )
    GUARDIAN_ENROLLMENT_ENABLED: bool = Field(
        default=True,
        description="Enable guardian/parent enrollment"
    )

    # ==================== Analytics Configuration ====================
    ANALYTICS_CACHE_TTL: int = Field(
        default=3600,
        ge=0,
        description="Analytics cache TTL (seconds)"
    )
    DAILY_REPORT_CACHE_ENABLED: bool = Field(
        default=True,
        description="Enable daily report caching"
    )

    # ==================== Performance Configuration ====================
    MAX_WORKERS: int = Field(default=4, ge=1, le=32, description="FastAPI worker processes")
    REQUEST_TIMEOUT: int = Field(default=300, ge=1, le=3600, description="HTTP request timeout")
    DB_POOL_SIZE: int = Field(default=10, ge=1, le=100, description="Database connection pool size")

    # ==================== Image Processing Configuration ====================
    MAX_IMAGE_SIZE_MB: int = Field(default=10, ge=1, le=100, description="Max image upload size (MB)")
    IMAGE_QUALITY: int = Field(default=85, ge=1, le=100, description="JPEG quality (1-100)")
    ALLOWED_IMAGE_FORMATS: str = Field(
        default="jpg,jpeg,png,webp",
        description="Comma-separated allowed image formats"
    )

    # ==================== Detection Configuration ====================
    PERSON_CONFIDENCE_THRESHOLD: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Person detection confidence threshold"
    )
    NMS_IOU_THRESHOLD: float = Field(
        default=0.45,
        ge=0.0,
        le=1.0,
        description="Non-maximum suppression IOU threshold"
    )
    MAX_DETECTIONS: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum detections per image"
    )

    # ==================== Violation Detection Configuration ====================
    VIOLATION_DETECTION_ENABLED: bool = Field(
        default=True,
        description="Enable violation detection"
    )
    STRANGER_DETECTION_ENABLED: bool = Field(
        default=True,
        description="Enable stranger detection"
    )

    # Hybrid Router Thresholds
    DIRECT_ALERT_VIOLENCE_THRESHOLD: float = Field(
        default=0.65,
        ge=0.0,
        le=1.0,
        description="Violence detection threshold for direct alerts"
    )
    DIRECT_ALERT_BODY_LANGUAGE_THRESHOLD: float = Field(
        default=0.70,
        ge=0.0,
        le=1.0,
        description="Body language threshold for direct alerts"
    )
    DIRECT_ALERT_DISTRESS_THRESHOLD: float = Field(
        default=0.70,
        ge=0.0,
        le=1.0,
        description="Distress detection threshold"
    )
    DIRECT_ALERT_SUPERVISION_THRESHOLD: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
        description="Supervision violation threshold"
    )
    VLM_VALIDATION_MIN_THRESHOLD: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum threshold for VLM validation"
    )
    VLM_VALIDATION_VIOLENCE_MAX: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Maximum violence score for VLM validation"
    )
    VLM_VALIDATION_BODY_LANGUAGE_MAX: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Maximum body language score for VLM validation"
    )
    VLM_VALIDATION_DISTRESS_MAX: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Maximum distress score for VLM validation"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @field_validator("POSTGRES_PASSWORD")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Warn if using default password"""
        if v == "PaSSw0rd!":
            logger.warning("⚠️  Using default PostgreSQL password - set POSTGRES_PASSWORD in .env")
        return v

    @field_validator("YOLO_MODEL_PATH")
    @classmethod
    def validate_model_path(cls, v: str) -> str:
        """Warn if YOLO model not found"""
        if not os.path.exists(v):
            logger.warning(f"⚠️  YOLO model not found at {v}")
        return v

    @property
    def database_url(self) -> str:
        """Get PostgreSQL connection URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def database_config(self) -> dict:
        """Get database connection config as dict"""
        return {
            "host": self.POSTGRES_HOST,
            "port": self.POSTGRES_PORT,
            "database": self.POSTGRES_DB,
            "user": self.POSTGRES_USER,
            "password": self.POSTGRES_PASSWORD,
        }

    @property
    def storage_headers(self) -> dict:
        """Get storage service HTTP headers"""
        headers = {"Content-Type": "application/json"}
        if self.STORAGE_API_KEY:
            headers["Authorization"] = f"Bearer {self.STORAGE_API_KEY}"
        return headers

    @property
    def allowed_formats_list(self) -> List[str]:
        """Get allowed image formats as list"""
        return [fmt.strip() for fmt in self.ALLOWED_IMAGE_FORMATS.split(",")]

    def log_configuration(self):
        """Log loaded configuration (without sensitive data)"""
        logger.info("📋 Configuration loaded:")
        logger.info(f"  Server: {self.HOST}:{self.PORT}")
        logger.info(f"  Debug Mode: {'✅' if self.DEBUG else '❌'}")
        logger.info(f"  YOLO Model: {self.YOLO_MODEL_PATH}")
        logger.info(f"  Ollama: {self.OLLAMA_HOST} ({self.OLLAMA_MODEL})")
        logger.info(f"  PostgreSQL: {self.POSTGRES_USER}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")
        logger.info(f"  Storage Service: {self.STORAGE_SERVICE_URL}")
        logger.info(f"  Storage Auth: {'✅' if self.STORAGE_API_KEY else '❌ (no auth)'}")
        logger.info(f"  Face Recognition Threshold: {self.FACE_RECOGNITION_THRESHOLD}")
        logger.info(f"  Fuzzy Search Threshold: {self.FUZZY_SEARCH_THRESHOLD}")
        logger.info(f"  Person Confidence: {self.PERSON_CONFIDENCE_THRESHOLD}")
        logger.info(f"  Violation Detection: {'✅' if self.VIOLATION_DETECTION_ENABLED else '❌'}")
        logger.info(f"  Stranger Detection: {'✅' if self.STRANGER_DETECTION_ENABLED else '❌'}")
        logger.info(f"  Guardian Enrollment: {'✅' if self.GUARDIAN_ENROLLMENT_ENABLED else '❌'}")
        logger.info(f"  Max Workers: {self.MAX_WORKERS}")
        logger.info(f"  DB Pool Size: {self.DB_POOL_SIZE}")
        logger.info(f"  Max Image Size: {self.MAX_IMAGE_SIZE_MB}MB")
        logger.info(f"  Allowed Formats: {', '.join(self.allowed_formats_list)}")

    def validate_all(self) -> Tuple[bool, List[str]]:
        """Additional validation beyond Pydantic"""
        errors = []

        # Check Ollama connection (could add actual ping here)
        if not self.OLLAMA_HOST:
            errors.append("❌ OLLAMA_HOST is required")

        # Check storage service
        if not self.STORAGE_SERVICE_URL:
            errors.append("⚠️  STORAGE_SERVICE_URL not configured")

        # Log errors
        for error in errors:
            if error.startswith("❌"):
                logger.error(error)
            else:
                logger.warning(error)

        # Valid if no critical errors
        critical_errors = [e for e in errors if e.startswith("❌")]
        return len(critical_errors) == 0, errors


# Singleton instance - load from .env
config = Config()
