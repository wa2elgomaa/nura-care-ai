"""
NURA VLM Service
Vision-Language Model for scene understanding and context analysis
Spec: specs/022-vlm-scene-understanding/spec.md
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from contextlib import asynccontextmanager
from typing import Optional, List
import logging
import base64
import time
from io import BytesIO
from PIL import Image

# Import VLM client
from src.vlm_client import OllamaVLMClient, PROMPT_TEMPLATES

# Import hybrid router
from src.hybrid_router import HybridRouter, ViolationAlert
from src.prompts.childcare_prompts import get_prompt_with_context
import numpy as np
import cv2

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Environment configuration"""
    nats_url: str = "nats://nats:4222"
    ollama_url: str = "http://ollama:11434"
    vlm_model: str = "llava:13b"  # or "llava:7b" or "moondream"
    site_id: str = "dev-site-001"
    log_level: str = "info"

    # VLM parameters
    vlm_temperature: float = 0.3  # Lower = more consistent
    vlm_max_tokens: int = 500

    class Config:
        env_file = ".env"

# Global VLM client and hybrid router
vlm_client: Optional[OllamaVLMClient] = None
hybrid_router: Optional[HybridRouter] = None


class SceneAnalysisRequest(BaseModel):
    """Request to analyze a scene"""
    image_base64: str = Field(..., description="Base64-encoded image")
    prompt: str = Field(
        default="Analyze this classroom scene. Are there any adults present? How many children? What are they doing? Is the situation safe or concerning?",
        description="Analysis prompt"
    )
    camera_id: Optional[str] = Field(None, description="Camera identifier")
    timestamp: Optional[str] = Field(None, description="ISO timestamp")


class SceneAnalysisResponse(BaseModel):
    """Response from scene analysis"""
    analysis: str = Field(..., description="VLM analysis text")
    adults_detected: Optional[bool] = Field(None, description="Parsed: adults present")
    children_count: Optional[int] = Field(None, description="Parsed: number of children")
    safety_concern: Optional[bool] = Field(None, description="Parsed: safety concern detected")
    confidence: Optional[float] = Field(None, description="Analysis confidence")


class HealthResponse(BaseModel):
    status: str
    version: str
    vlm_model: str
    model_loaded: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle"""
    global vlm_client, hybrid_router

    logger.info("Starting NURA VLM Service...")
    logger.info(f"Ollama URL: {settings.ollama_url}")
    logger.info(f"VLM Model: {settings.vlm_model}")

    # Initialize Ollama VLM client
    vlm_client = OllamaVLMClient(
        base_url=settings.ollama_url,
        model=settings.vlm_model
    )

    # Check Ollama connectivity
    is_healthy = await vlm_client.health_check()
    if is_healthy:
        logger.info("✓ Ollama connection successful")
        models = await vlm_client.list_models()
        logger.info(f"✓ Available models: {models}")

        if settings.vlm_model not in models:
            logger.warning(f"⚠ Model {settings.vlm_model} not found in Ollama!")
            logger.warning(f"Run: ollama pull {settings.vlm_model}")
    else:
        logger.error("✗ Ollama connection failed!")
        logger.error("VLM service will start but analyses will fail")

    # Initialize hybrid router with VLM client (lazy init - will load on first use)
    logger.info("Initializing hybrid fast-path router (lazy)...")
    hybrid_router = HybridRouter(vlm_client=vlm_client)
    logger.info("✓ Hybrid router initialized (detectors will load on first request)")

    # TODO: Initialize NATS connection for event publishing

    logger.info("VLM service started successfully")

    yield

    logger.info("Shutting down NURA VLM Service...")
    if vlm_client:
        await vlm_client.close()
    logger.info("Shutdown complete")


app = FastAPI(
    title="NURA VLM Service",
    description="Vision-Language Model for scene understanding and violation context analysis",
    version="0.1.0",
    lifespan=lifespan
)

settings = Settings()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    model_loaded = False

    if vlm_client:
        is_healthy = await vlm_client.health_check()
        if is_healthy:
            models = await vlm_client.list_models()
            model_loaded = settings.vlm_model in models

    status = "healthy" if model_loaded else "degraded"

    return HealthResponse(
        status=status,
        version="0.1.0",
        vlm_model=settings.vlm_model,
        model_loaded=model_loaded
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "nura-vlm",
        "version": "0.1.0",
        "description": "Vision-Language Model for childcare safety monitoring",
        "models_available": [
            "llava:13b",    # High quality, 24GB VRAM
            "llava:7b",     # Medium quality, 16GB VRAM
            "moondream",    # Lightweight, 8GB VRAM
        ]
    }


@app.post("/analyze", response_model=SceneAnalysisResponse)
async def analyze_scene(request: SceneAnalysisRequest):
    """
    Analyze a camera frame for safety violations (FR-001, FR-002, FR-003)

    Example prompts:
    - "Is there an adult supervising the children in this classroom?"
    - "How many children are visible? Are they engaged in appropriate activities?"
    - "Is there any concerning physical contact or aggressive behavior?"
    - "What safety hazards are visible in this scene?"
    """
    if not vlm_client:
        raise HTTPException(status_code=503, detail="VLM client not initialized")

    start_time = time.time()

    try:
        logger.info(f"Analyzing frame from camera: {request.camera_id}")
        logger.debug(f"Prompt: {request.prompt[:100]}...")

        # Validate image format (FR-012)
        try:
            image_bytes = base64.b64decode(request.image_base64)
            image = Image.open(BytesIO(image_bytes))
            logger.debug(f"Image size: {image.size}, format: {image.format}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image format: {e}")

        # Analyze with VLM
        result = await vlm_client.analyze_scene(
            image_base64=request.image_base64,
            prompt=request.prompt,
            temperature=settings.vlm_temperature
        )

        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        inference_time_ms = int((time.time() - start_time) * 1000)

        # Log analysis (FR-007) - no full images
        logger.info(f"Analysis complete in {inference_time_ms}ms")
        logger.debug(f"Parsed results: {result['parsed']}")

        # TODO: Publish to NATS (FR-010)

        response = SceneAnalysisResponse(
            analysis=result["raw_response"] or "No response from VLM",
            adults_detected=result["parsed"].get("adults_detected"),
            children_count=result["parsed"].get("count"),
            safety_concern=result["parsed"].get("safety_concern"),
            confidence=0.85  # TODO: Calculate actual confidence
        )

        # Check latency target (FR-004: <2s for P0)
        if inference_time_ms > 2000:
            logger.warning(f"⚠ Slow inference: {inference_time_ms}ms (target <2000ms)")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/batch")
async def analyze_batch(images: List[UploadFile] = File(...)):
    """Batch analyze multiple frames (for testing)"""
    results = []
    for image in images:
        # TODO: Process each image
        results.append({
            "filename": image.filename,
            "status": "pending_implementation"
        })
    return {"count": len(results), "results": results}


# Predefined safety analysis prompts
SAFETY_PROMPTS = {
    "supervision": "Are there any adults visible in this classroom supervising the children? Answer with yes or no, then explain what you see.",
    "count": "How many children are visible in this image? Count carefully and provide a number.",
    "activity": "What activities are the children engaged in? Are these appropriate for a childcare setting?",
    "behavior": "Is there any concerning behavior visible? Look for aggression, distress, inappropriate physical contact, or safety hazards.",
    "restricted_area": "Is this a restricted area like a kitchen, storage room, or staff area? Are there any children present where they shouldn't be?",
    "capacity": "Based on visible space and furniture, does this room appear overcrowded?",
}


@app.get("/prompts")
async def list_prompts():
    """List available predefined safety analysis prompts"""
    return {
        "prompts": SAFETY_PROMPTS,
        "custom_prompt_supported": True
    }


@app.post("/analyze/supervision")
async def analyze_supervision(image_base64: str, camera_id: Optional[str] = None):
    """Quick check: Is an adult supervising? (FR-005 predefined template)"""
    return await analyze_scene(SceneAnalysisRequest(
        image_base64=image_base64,
        prompt=PROMPT_TEMPLATES["supervision"],
        camera_id=camera_id
    ))


@app.post("/analyze/count")
async def analyze_count(image_base64: str, camera_id: Optional[str] = None):
    """Quick check: How many children? (FR-005 predefined template)"""
    return await analyze_scene(SceneAnalysisRequest(
        image_base64=image_base64,
        prompt=PROMPT_TEMPLATES["count_children"],
        camera_id=camera_id
    ))


class HybridAnalysisRequest(BaseModel):
    """Request for hybrid fast-path + VLM analysis"""
    image_base64: str = Field(..., description="Base64-encoded image")
    camera_id: Optional[str] = Field(None, description="Camera identifier")


class HybridAnalysisResponse(BaseModel):
    """Response from hybrid analysis"""
    violation_detected: bool
    violation_type: str
    severity: str
    confidence: float
    source: str  # "fast_path", "vlm", or "hybrid"
    details: str
    processing_time_ms: float
    immediate_action_required: bool
    fast_path_results: Optional[dict] = None
    vlm_result: Optional[str] = None


@app.post("/analyze/hybrid", response_model=HybridAnalysisResponse)
async def analyze_hybrid(request: HybridAnalysisRequest):
    """
    Hybrid analysis using fast-path detectors + VLM validation

    This is the NEW endpoint that uses:
    1. Fast-path detectors (violence, distress, supervision)
    2. Intelligent routing based on confidence
    3. VLM validation for ambiguous cases
    4. Improved context-aware prompts

    Performance:
    - Fast-path only: <100ms (70% of cases)
    - Hybrid (fast-path + VLM): ~3s average (30% of cases)

    Accuracy:
    - Target: >90% precision, >85% recall
    - Previous VLM-only: 0% detection rate on test images
    """
    if not hybrid_router:
        raise HTTPException(status_code=503, detail="Hybrid router not initialized")

    try:
        # Decode image to numpy array
        image_bytes = base64.b64decode(request.image_base64)
        image = Image.open(BytesIO(image_bytes))
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Run hybrid analysis
        alert = await hybrid_router.analyze_frame(frame, camera_id=request.camera_id)

        # Simplify fast_path_results to avoid circular references
        fast_path_summary = None
        if alert.fast_path_results:
            fast_path_summary = {
                "violence_detected": alert.fast_path_results.get("violence", {}).get("violence_detected", False),
                "distress_detected": alert.fast_path_results.get("distress", {}).get("distress_detected", False),
                "supervision_violation": alert.fast_path_results.get("supervision", {}).get("violation_detected", False),
                "intimidation_detected": alert.fast_path_results.get("body_language", {}).get("intimidation_detected", False),
            }

        return HybridAnalysisResponse(
            violation_detected=alert.violation_detected,
            violation_type=alert.violation_type,
            severity=alert.severity,
            confidence=float(alert.confidence),
            source=alert.source,
            details=alert.details,
            processing_time_ms=float(alert.processing_time_ms),
            immediate_action_required=alert.immediate_action_required,
            fast_path_results=fast_path_summary,
            vlm_result=alert.vlm_result
        )

    except Exception as e:
        logger.error(f"Hybrid analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# TODO: Implement endpoints:
# - POST /analyze/video-clip - Analyze multiple frames from a clip
# - GET /models - List available VLM models
# - POST /models/switch - Switch VLM model
# - GET /metrics - Prometheus metrics


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level=settings.log_level.lower()
    )
