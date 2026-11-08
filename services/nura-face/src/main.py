"""
NURA Face Recognition Service
Centralized face recognition API for enrollment, identification, and search
Spec: docs/NURA_FACE_SERVICE_SPEC.md
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from contextlib import asynccontextmanager
from typing import Optional, List
import logging
import numpy as np
from PIL import Image
import io
import psycopg2
from psycopg2.pool import SimpleConnectionPool

from src.config import config
from src.face_service import FaceService

# Initialize logging
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
face_service: Optional[FaceService] = None
db_pool: Optional[SimpleConnectionPool] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle"""
    global face_service, db_pool

    logger.info("Starting NURA Face Recognition Service...")

    # Initialize Face Service
    logger.info("Initializing InsightFace model...")
    face_service = FaceService(
        model_name=config.FACE_RECOGNITION_MODEL,
        enable_gpu=config.ENABLE_GPU,
        gpu_device_id=config.GPU_DEVICE_ID
    )
    logger.info("✓ Face service initialized")

    # Initialize database connection pool
    logger.info("Initializing database connection pool...")
    try:
        db_pool = SimpleConnectionPool(
            minconn=1,
            maxconn=config.DB_POOL_SIZE,
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT,
            database=config.POSTGRES_DB,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD
        )
        logger.info(f"✓ Database pool initialized ({config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB})")
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")
        raise

    logger.info("Face Recognition Service started successfully")
    yield

    logger.info("Shutting down NURA Face Recognition Service...")
    if db_pool:
        db_pool.closeall()
    logger.info("Shutdown complete")


app = FastAPI(
    title="NURA Face Recognition Service",
    description="Centralized face recognition API for enrollment, identification, and search",
    version="0.1.0",
    lifespan=lifespan
)

# Log configuration on startup
config.log_configuration()
valid, errors = config.validate_config()
if not valid:
    logger.error("Configuration validation failed")
    for error in errors:
        logger.error(f"  {error}")


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "nura-face",
        "version": "0.1.0",
        "model": config.FACE_RECOGNITION_MODEL,
        "gpu_enabled": config.ENABLE_GPU
    }


@app.post("/api/face/enroll")
async def enroll_face(
    person_id: str = Form(...),
    person_name: str = Form(...),
    person_type: str = Form(...),
    photo: UploadFile = File(...)
):
    """
    Enroll a new face

    Args:
        person_id: Unique person identifier
        person_name: Person's full name
        person_type: Person type (student, staff, parent, visitor)
        photo: Face photo file

    Returns:
        Enrollment result with embedding ID
    """
    try:
        # Validate person_type
        valid_types = ["student", "staff", "parent", "visitor", "unknown"]
        if person_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid person_type. Must be one of: {valid_types}")

        # Read and decode image
        image_bytes = await photo.read()
        image = Image.open(io.BytesIO(image_bytes))
        image_array = np.array(image)

        # Extract face embedding
        embedding = face_service.extract_embedding(image_array)
        if embedding is None:
            raise HTTPException(status_code=400, detail="No face detected in photo")

        # Store in database
        conn = db_pool.getconn()
        try:
            cursor = conn.cursor()

            # Convert embedding to PostgreSQL vector format
            embedding_str = f"[{','.join(map(str, embedding))}]"

            cursor.execute("""
                INSERT INTO face_embeddings (
                    person_id, person_name, person_type, embedding,
                    site_id, confidence, metadata
                )
                VALUES (%s, %s, %s, %s::vector, %s, %s, %s)
                RETURNING id
            """, (
                person_id,
                person_name,
                person_type,
                embedding_str,
                config.SITE_ID,
                1.0,  # Enrollment confidence (can be improved with quality metrics)
                {}  # Metadata
            ))

            embedding_id = cursor.fetchone()[0]
            conn.commit()

            logger.info(f"✓ Enrolled face: {person_name} ({person_id}) - ID: {embedding_id}")

            return {
                "success": True,
                "embedding_id": embedding_id,
                "person_id": person_id,
                "person_name": person_name,
                "person_type": person_type,
                "message": "Face enrolled successfully"
            }

        finally:
            cursor.close()
            db_pool.putconn(conn)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enrollment error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/face/identify")
async def identify_face(
    photo: UploadFile = File(...),
    threshold: Optional[float] = None
):
    """
    Identify a face from photo

    Args:
        photo: Face photo file
        threshold: Optional similarity threshold (default from config)

    Returns:
        Identification result with person info and confidence
    """
    try:
        # Use config threshold if not provided
        similarity_threshold = threshold if threshold is not None else config.FACE_RECOGNITION_THRESHOLD

        # Read and decode image
        image_bytes = await photo.read()
        image = Image.open(io.BytesIO(image_bytes))
        image_array = np.array(image)

        # Extract face embedding
        query_embedding = face_service.extract_embedding(image_array)
        if query_embedding is None:
            raise HTTPException(status_code=400, detail="No face detected in photo")

        # Query database for similar faces
        conn = db_pool.getconn()
        try:
            cursor = conn.cursor()

            # Convert query embedding to PostgreSQL vector
            query_embedding_str = f"[{','.join(map(str, query_embedding))}]"

            # Find most similar face using cosine similarity
            cursor.execute("""
                SELECT
                    id, person_id, person_name, person_type, embedding,
                    1 - (embedding <=> %s::vector) as similarity
                FROM face_embeddings
                WHERE site_id = %s
                ORDER BY embedding <=> %s::vector
                LIMIT 1
            """, (query_embedding_str, config.SITE_ID, query_embedding_str))

            result = cursor.fetchone()

            if result is None:
                return {
                    "success": False,
                    "identified": False,
                    "message": "No faces enrolled in database"
                }

            embedding_id, person_id, person_name, person_type, _, similarity = result

            if similarity >= similarity_threshold:
                logger.info(f"✓ Face identified: {person_name} ({person_id}) - Similarity: {similarity:.3f}")

                return {
                    "success": True,
                    "identified": True,
                    "embedding_id": embedding_id,
                    "person_id": person_id,
                    "person_name": person_name,
                    "person_type": person_type,
                    "similarity": float(similarity),
                    "threshold": similarity_threshold
                }
            else:
                logger.info(f"Face not identified - Best match: {similarity:.3f} < threshold: {similarity_threshold}")

                return {
                    "success": True,
                    "identified": False,
                    "best_similarity": float(similarity),
                    "threshold": similarity_threshold,
                    "message": "No matching face found above threshold"
                }

        finally:
            cursor.close()
            db_pool.putconn(conn)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Identification error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/face/search")
async def search_faces(
    person_name: Optional[str] = None,
    person_id: Optional[str] = None,
    person_type: Optional[str] = None,
    limit: int = 10
):
    """
    Search for enrolled faces

    Args:
        person_name: Filter by name (partial match)
        person_id: Filter by person ID (exact match)
        person_type: Filter by person type
        limit: Maximum results to return

    Returns:
        List of matching faces
    """
    try:
        conn = db_pool.getconn()
        try:
            cursor = conn.cursor()

            query = """
                SELECT id, person_id, person_name, person_type, created_at
                FROM face_embeddings
                WHERE site_id = %s
            """
            params = [config.SITE_ID]

            if person_id:
                query += " AND person_id = %s"
                params.append(person_id)

            if person_name:
                query += " AND person_name ILIKE %s"
                params.append(f"%{person_name}%")

            if person_type:
                query += " AND person_type = %s"
                params.append(person_type)

            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)

            cursor.execute(query, params)
            results = cursor.fetchall()

            faces = []
            for row in results:
                faces.append({
                    "id": row[0],
                    "person_id": row[1],
                    "person_name": row[2],
                    "person_type": row[3],
                    "created_at": row[4].isoformat()
                })

            logger.debug(f"Search returned {len(faces)} face(s)")

            return {
                "success": True,
                "count": len(faces),
                "faces": faces
            }

        finally:
            cursor.close()
            db_pool.putconn(conn)

    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "nura-face",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "enroll": "POST /api/face/enroll",
            "identify": "POST /api/face/identify",
            "search": "GET /api/face/search"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
