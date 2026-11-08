"""
Configuration Service - nura-face
Centralized configuration management (all .env driven)
"""
import os
import logging
from pydantic_settings import BaseSettings
from pydantic import Field

logger = logging.getLogger(__name__)


class Config(BaseSettings):
    """Centralized configuration from environment variables with Pydantic validation"""

    # ==================== Service Configuration ====================
    PORT: int = Field(default=8002, description="HTTP server port")
    HOST: str = Field(default="0.0.0.0", description="HTTP server host")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # ==================== PostgreSQL Configuration ====================
    POSTGRES_HOST: str = Field(default="postgres", description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5432, ge=1, le=65535, description="PostgreSQL port")
    POSTGRES_DB: str = Field(default="nura_db", description="PostgreSQL database name")
    POSTGRES_USER: str = Field(default="nura", description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(default="PaSSw0rd!", description="PostgreSQL password")

    # ==================== Face Recognition Configuration ====================
    FACE_RECOGNITION_MODEL: str = Field(
        default="buffalo_l",
        description="InsightFace model name (buffalo_l, buffalo_m, buffalo_s)"
    )
    FACE_RECOGNITION_THRESHOLD: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Face similarity threshold (0-1, lower = stricter)"
    )
    FACE_EMBEDDING_DIM: int = Field(default=512, description="Face embedding dimension")

    # ==================== Performance Configuration ====================
    ENABLE_GPU: bool = Field(default=False, description="Enable GPU acceleration")
    GPU_DEVICE_ID: int = Field(default=0, description="GPU device ID")
    DB_POOL_SIZE: int = Field(default=10, description="Database connection pool size")

    # ==================== Storage Configuration ====================
    FACE_PHOTOS_PATH: str = Field(
        default="/data/face-photos",
        description="Path to store face photos"
    )

    # ==================== Site Configuration ====================
    SITE_ID: str = Field(default="dev-site-001", description="Site identifier")

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def database_url(self) -> str:
        """Build PostgreSQL connection URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def log_configuration(self):
        """Log loaded configuration"""
        logger.info("📋 Face Service Configuration loaded:")
        logger.info(f"  Port: {self.PORT}")
        logger.info(f"  Database: {self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")
        logger.info(f"  Face Model: {self.FACE_RECOGNITION_MODEL}")
        logger.info(f"  Similarity Threshold: {self.FACE_RECOGNITION_THRESHOLD}")
        logger.info(f"  Embedding Dimension: {self.FACE_EMBEDDING_DIM}")
        logger.info(f"  GPU Enabled: {self.ENABLE_GPU}")
        logger.info(f"  Site ID: {self.SITE_ID}")

    def validate_config(self) -> tuple[bool, list[str]]:
        """Validate configuration"""
        errors = []

        if self.FACE_RECOGNITION_THRESHOLD < 0 or self.FACE_RECOGNITION_THRESHOLD > 1:
            errors.append("❌ FACE_RECOGNITION_THRESHOLD must be between 0 and 1")

        if self.FACE_EMBEDDING_DIM not in [128, 256, 512]:
            errors.append("⚠️  FACE_EMBEDDING_DIM should be 128, 256, or 512")

        if not os.path.exists(self.FACE_PHOTOS_PATH):
            logger.warning(f"Face photos path does not exist: {self.FACE_PHOTOS_PATH}")
            errors.append(f"⚠️  Face photos path will be created: {self.FACE_PHOTOS_PATH}")

        return len([e for e in errors if e.startswith("❌")]) == 0, errors


# Global config instance
config = Config()
