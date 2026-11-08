"""
Person Search API - Week 4
Search for persons by name or photo, get current location and movement history
"""
import logging
from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from pydantic import BaseModel
import psycopg2
import redis
import json
import cv2
import numpy as np

from src.config import config

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/persons", tags=["person-search"])

# Redis client (lazy init)
_redis_client = None

def get_redis_client():
    """Get Redis client (singleton) using centralized config"""
    global _redis_client
    if _redis_client is None:
        redis_url = f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}"
        _redis_client = redis.from_url(redis_url, decode_responses=True)
        logger.info(f"✓ Connected to Redis: {redis_url}")
    return _redis_client


def get_db_connection():
    """Get PostgreSQL connection using centralized config"""
    return psycopg2.connect(**config.database_config)


# Response Models
class PersonLocation(BaseModel):
    person_id: str
    full_name: str
    display_name: Optional[str] = None
    
    camera_id: Optional[str] = None
    zone_name: Optional[str] = None
    last_seen: Optional[datetime] = None
    confidence: Optional[float] = None
    source: str  # "redis_cache" or "database"


class MovementRecord(BaseModel):
    camera_id: str
    zone_name: str
    entered_at: datetime
    exited_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    detection_count: int


class SearchStats(BaseModel):
    total_persons: int
    online_count: int  # Persons in Redis cache (seen recently)
    query_time_ms: float


# 1. Search by Name (Fuzzy)
@router.get("/search", response_model=List[PersonLocation])
async def search_by_name(
    name: str = Query(..., min_length=2, description="Name to search (fuzzy matching)"),
    limit: int = Query(10, ge=1, le=50, description="Max results to return")
):
    """
    Search for persons by name using fuzzy matching

    Examples:
    - "adam" finds "Adam West"
    - "jan" finds "Jane Doe"
    - "smith" finds "John Smith"

    Returns current location from Redis cache or database
    """
    start_time = datetime.now()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # PostgreSQL fuzzy search using pg_trgm extension
        # SIMILARITY() returns 0-1 score based on trigram matching
        cursor.execute("""
            SELECT person_id, full_name, display_name,
                   SIMILARITY(full_name, %s) as name_score,
                   SIMILARITY(COALESCE(display_name, ''), %s) as display_score
            FROM enrolled_persons
            WHERE active = true
              AND (SIMILARITY(full_name, %s) > 0.3
                   OR SIMILARITY(COALESCE(display_name, ''), %s) > 0.3)
            ORDER BY GREATEST(
                SIMILARITY(full_name, %s),
                SIMILARITY(COALESCE(display_name, ''), %s)
            ) DESC
            LIMIT %s
        """, (name, name, name, name, name, name, limit))

        results = []
        redis_client = get_redis_client()

        for row in cursor.fetchall():
            person_id, full_name, display_name, name_score, display_score = row
            score = max(name_score, display_score)

            # Try to get location from Redis cache
            location_key = f"person:location:{person_id}"
            location_data = redis_client.get(location_key)

            if location_data:
                # Found in Redis cache (seen recently)
                try:
                    location = json.loads(location_data)
                    results.append(PersonLocation(
                        person_id=person_id,
                        full_name=full_name,
                        display_name=display_name,
                        
                        camera_id=location.get('camera_id'),
                        zone_name=location.get('zone_name'),
                        last_seen=datetime.fromisoformat(location['last_seen']),
                        confidence=location.get('confidence', score),
                        source="redis_cache"
                    ))
                except Exception as e:
                    logger.error(f"Failed to parse Redis location for {person_id}: {e}")
                    # Continue without location data
                    results.append(PersonLocation(
                        person_id=person_id,
                        full_name=full_name,
                        display_name=display_name,
                        
                        source="database"
                    ))
            else:
                # Not in Redis, just return person info without location
                results.append(PersonLocation(
                    person_id=person_id,
                    full_name=full_name,
                    display_name=display_name,
                    
                    source="database"
                ))

        cursor.close()
        conn.close()

        query_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        logger.info(f"Name search '{name}' returned {len(results)} results in {query_time_ms:.0f}ms")

        return results

    except Exception as e:
        logger.error(f"Search by name failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 2. Search by Image
@router.post("/search/by-image", response_model=PersonLocation)
async def search_by_image(
    photo: UploadFile = File(..., description="Photo containing person's face"),
    threshold: float = Query(0.6, ge=0.0, le=1.0, description="Face matching threshold")
):
    """
    Search for person by uploading their photo

    Uses InsightFace for face recognition and pgvector for similarity search
    Returns the best matching person with their current location
    """
    start_time = datetime.now()

    try:
        # Read and decode image
        content = await photo.read()
        nparr = np.frombuffer(content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Extract face embedding using InsightFace
        try:
            import insightface
            face_model = insightface.app.FaceAnalysis(
                name='buffalo_l',
                providers=['CPUExecutionProvider']
            )
            face_model.prepare(ctx_id=0, det_size=(640, 640))

            faces = face_model.get(img)
            if not faces:
                raise HTTPException(status_code=400, detail="No face detected in image")

            # Use the largest face (most prominent)
            largest_face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
            query_embedding = largest_face.embedding  # 512D vector

            logger.info(f"Face extracted from uploaded image (confidence: {largest_face.det_score:.2f})")

        except Exception as e:
            logger.error(f"Face extraction failed: {e}")
            raise HTTPException(status_code=500, detail=f"Face extraction failed: {e}")

        # Search in enrolled_persons using pgvector
        conn = get_db_connection()
        cursor = conn.cursor()

        # Convert to list for PostgreSQL
        embedding_list = query_embedding.tolist()

        # Vector similarity search (cosine distance)
        # Lower distance = more similar (0 = identical, 2 = opposite)
        # We convert to similarity: 1 - (distance / 2)
        cursor.execute("""
            SELECT person_id, full_name, display_name,
                   1 - (face_embedding <=> %s::vector) / 2 as similarity
            FROM enrolled_persons
            WHERE active = true
              AND face_embedding IS NOT NULL
              AND 1 - (face_embedding <=> %s::vector) / 2 >= %s
            ORDER BY face_embedding <=> %s::vector
            LIMIT 1
        """, (embedding_list, embedding_list, threshold, embedding_list))

        row = cursor.fetchone()

        if not row:
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=404,
                detail=f"No matching person found (threshold={threshold})"
            )

        person_id, full_name, display_name, similarity = row

        logger.info(f"Image search matched: {full_name} (similarity: {similarity:.3f})")

        # Get location from Redis
        redis_client = get_redis_client()
        location_key = f"person:location:{person_id}"
        location_data = redis_client.get(location_key)

        if location_data:
            try:
                location = json.loads(location_data)
                result = PersonLocation(
                    person_id=person_id,
                    full_name=full_name,
                    display_name=display_name,
                    
                    camera_id=location.get('camera_id'),
                    zone_name=location.get('zone_name'),
                    last_seen=datetime.fromisoformat(location['last_seen']),
                    confidence=float(similarity),
                    source="redis_cache"
                )
            except Exception as e:
                logger.error(f"Failed to parse Redis location: {e}")
                result = PersonLocation(
                    person_id=person_id,
                    full_name=full_name,
                    display_name=display_name,
                    
                    confidence=float(similarity),
                    source="database"
                )
        else:
            result = PersonLocation(
                person_id=person_id,
                full_name=full_name,
                display_name=display_name,
                
                confidence=float(similarity),
                source="database"
            )

        cursor.close()
        conn.close()

        query_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        logger.info(f"Image search completed in {query_time_ms:.0f}ms")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search by image failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 3. Movement History
@router.get("/{person_id}/movements", response_model=List[MovementRecord])
async def get_movement_history(
    person_id: str,
    from_time: Optional[datetime] = Query(None, description="Start time (default: 24h ago)"),
    to_time: Optional[datetime] = Query(None, description="End time (default: now)"),
    min_duration: int = Query(5, ge=0, description="Minimum duration in seconds to include")
):
    """
    Get movement history for a person

    Shows camera/zone transitions over time with duration in each location.
    Groups consecutive detections in the same camera into movements.

    NOTE: Requires person_detections table to be populated by stream processor.
    Currently this table doesn't exist, so this endpoint will return empty results.
    """
    try:
        # Default time range: last 24 hours
        if not from_time:
            from_time = datetime.now() - timedelta(hours=24)
        if not to_time:
            to_time = datetime.now()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if person_detections table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'person_detections'
            )
        """)

        table_exists = cursor.fetchone()[0]

        if not table_exists:
            logger.warning("person_detections table does not exist yet")
            cursor.close()
            conn.close()
            return []  # Return empty list, table will be created when stream processor runs

        # Get all detections in time range
        cursor.execute("""
            SELECT camera_id, detected_at, confidence
            FROM person_detections
            WHERE person_id = %s
              AND detected_at BETWEEN %s AND %s
            ORDER BY detected_at ASC
        """, (person_id, from_time, to_time))

        detections = cursor.fetchall()
        cursor.close()
        conn.close()

        if not detections:
            return []

        # Aggregate into movements (consecutive detections in same camera = one movement)
        movements = []
        current_camera = None
        current_entry = None
        detection_count = 0

        for camera_id, detected_at, confidence in detections:
            if camera_id != current_camera:
                # Camera changed - new movement
                if current_camera and (detected_at - current_entry).total_seconds() >= min_duration:
                    # Close previous movement (if it meets minimum duration)
                    movements.append(MovementRecord(
                        camera_id=current_camera,
                        zone_name='unknown',  # TODO: Map camera_id to zone_name
                        entered_at=current_entry,
                        exited_at=detected_at,
                        duration_seconds=int((detected_at - current_entry).total_seconds()),
                        detection_count=detection_count
                    ))

                # Start new movement
                current_camera = camera_id
                current_entry = detected_at
                detection_count = 1
            else:
                # Same camera, count detection
                detection_count += 1

        # Close last movement (still in this location)
        if current_camera and (datetime.now() - current_entry).total_seconds() >= min_duration:
            movements.append(MovementRecord(
                camera_id=current_camera,
                zone_name='unknown',
                entered_at=current_entry,
                exited_at=None,  # Still there
                duration_seconds=None,
                detection_count=detection_count
            ))

        logger.info(f"Movement history for {person_id}: {len(movements)} movements from {len(detections)} detections")

        return movements

    except Exception as e:
        logger.error(f"Get movement history failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 4. Get Current Locations (All Persons)
@router.get("/locations/current", response_model=List[PersonLocation])
async def get_current_locations(
    limit: int = Query(100, ge=1, le=500, description="Max results to return")
):
    """
    Get current locations of all persons from Redis cache

    Returns only persons who have been seen recently (within Redis TTL)
    Useful for "who's on campus right now" queries
    """
    try:
        redis_client = get_redis_client()

        # Get all location keys from Redis
        location_keys = redis_client.keys('person:location:*')

        if not location_keys:
            return []

        # Get person details from database
        person_ids = [key.split(':')[-1] for key in location_keys[:limit]]

        conn = get_db_connection()
        cursor = conn.cursor()

        # Batch query for person details
        cursor.execute("""
            SELECT person_id, full_name, display_name
            FROM enrolled_persons
            WHERE person_id = ANY(%s)
              AND active = true
        """, (person_ids,))

        person_map = {row[0]: row for row in cursor.fetchall()}
        cursor.close()
        conn.close()

        # Combine with location data
        results = []
        for key in location_keys[:limit]:
            person_id = key.split(':')[-1]
            location_data = redis_client.get(key)

            if location_data and person_id in person_map:
                try:
                    location = json.loads(location_data)
                    _, full_name, display_name = person_map[person_id]

                    results.append(PersonLocation(
                        person_id=person_id,
                        full_name=full_name,
                        display_name=display_name,
                        
                        camera_id=location.get('camera_id'),
                        zone_name=location.get('zone_name'),
                        last_seen=datetime.fromisoformat(location['last_seen']),
                        confidence=location.get('confidence'),
                        source="redis_cache"
                    ))
                except Exception as e:
                    logger.error(f"Failed to parse location for {person_id}: {e}")
                    continue

        logger.info(f"Current locations: {len(results)} persons online")

        return results

    except Exception as e:
        logger.error(f"Get current locations failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 5. Search Stats
@router.get("/stats", response_model=SearchStats)
async def get_search_stats():
    """
    Get statistics about the person search system

    Returns:
    - Total enrolled persons
    - Number currently online (in Redis cache)
    - Query performance
    """
    start_time = datetime.now()

    try:
        # Count total persons
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM enrolled_persons WHERE active = true")
        total_persons = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        # Count online persons (in Redis cache)
        redis_client = get_redis_client()
        location_keys = redis_client.keys('person:location:*')
        online_count = len(location_keys)

        query_time_ms = (datetime.now() - start_time).total_seconds() * 1000

        return SearchStats(
            total_persons=total_persons,
            online_count=online_count,
            query_time_ms=query_time_ms
        )

    except Exception as e:
        logger.error(f"Get stats failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
