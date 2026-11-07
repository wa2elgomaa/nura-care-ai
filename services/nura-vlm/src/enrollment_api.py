"""
Enrollment API - Phase 4B

FastAPI endpoints for person enrollment and management.

Endpoints:
- POST /api/persons/enroll - Enroll a new person with face photos
- GET /api/persons - List all enrolled persons
- GET /api/persons/{person_id} - Get person details
- GET /api/persons/{person_id}/location - Get current location
- PUT /api/persons/{person_id} - Update person info
- DELETE /api/persons/{person_id} - Delete enrollment (soft delete)
- GET /api/persons/{person_id}/timeline - Get movement history
- POST /api/persons/{person_id}/consent - Update consent status
"""

import os
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import psycopg2
import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Nura Person Enrollment API",
    description="API for enrolling and managing persons in the childcare monitoring system",
    version="1.0.0"
)

# CORS middleware (for web UI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ============================================================================
# Database Connection
# ============================================================================

def get_db():
    """Get database connection (optional - returns None if unavailable)"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "nura_db"),
            user=os.getenv("POSTGRES_USER", "nura"),
            password=os.getenv("POSTGRES_PASSWORD", "Pa$$w0rd!"),
            connect_timeout=3
        )
        try:
            yield conn
        finally:
            conn.close()
    except Exception as e:
        logger.warning(f"Database connection failed: {e}")
        logger.warning("Running in demo mode without database")
        yield None


# ============================================================================
# Pydantic Models
# ============================================================================

class PersonEnrollmentRequest(BaseModel):
    """Person enrollment request"""
    person_id: str
    full_name: str
    display_name: Optional[str] = None
    age_years: Optional[int] = None
    grade_level: Optional[str] = None
    classroom: Optional[str] = None
    parental_consent: bool = False
    enrolled_by: Optional[str] = None


class PersonInfo(BaseModel):
    """Person information"""
    person_id: str
    full_name: str
    display_name: Optional[str]
    age_years: Optional[int]
    grade_level: Optional[str]
    classroom: Optional[str]
    parental_consent: bool
    active: bool
    enrolled_at: datetime
    enrollment_quality_score: Optional[float]


class PersonLocation(BaseModel):
    """Current person location"""
    person_id: str
    camera_id: Optional[str]
    last_seen: Optional[datetime]
    bbox: Optional[List[float]]
    status: str  # "visible", "not_seen", "never_enrolled"


class TimelineEntry(BaseModel):
    """Movement timeline entry"""
    camera_id: str
    first_seen: datetime
    last_seen: datetime
    num_sightings: int


class ConsentUpdate(BaseModel):
    """Consent status update"""
    parental_consent: bool
    consent_document_url: Optional[str] = None


# ============================================================================
# Helper Functions
# ============================================================================

async def save_upload_file(upload_file: UploadFile, destination: Path) -> Path:
    """Save uploaded file to disk"""
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("wb") as buffer:
        content = await upload_file.read()
        buffer.write(content)

    return destination


def load_face_identifier():
    """Load FaceIdentifier (lazy initialization) - optional database"""
    global _face_identifier

    if '_face_identifier' not in globals():
        from nura_detectors import FaceIdentifier

        # Try to get database connection (optional)
        db_conn = None
        try:
            db_conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=os.getenv("POSTGRES_PORT", "5432"),
                database=os.getenv("POSTGRES_DB", "nura_db"),
                user=os.getenv("POSTGRES_USER", "nura"),
                password=os.getenv("POSTGRES_PASSWORD", "Pa$$w0rd!"),
                connect_timeout=3
            )
            logger.info("✓ Database connection established")
        except Exception as e:
            logger.warning(f"Database unavailable: {e}")
            logger.warning("Running in DEMO MODE - enrollments will be in-memory only")

        # Try InsightFace first, fall back to face_recognition if it fails
        backend = os.getenv("FACE_RECOGNITION_BACKEND", "insightface")
        model_name = "buffalo_l"  # Use buffalo_l model (available in InsightFace v0.7)

        try:
            _face_identifier = FaceIdentifier(
                db_connection=db_conn,
                backend=backend,
                model_name=model_name,
                min_confidence=float(os.getenv("FACE_RECOGNITION_MIN_CONFIDENCE", "0.6"))
            )
        except Exception as e:
            if backend == "insightface":
                logger.warning(f"InsightFace initialization failed: {e}")
                logger.info("Trying face_recognition backend instead...")
                _face_identifier = FaceIdentifier(
                    db_connection=db_conn,
                    backend="face_recognition",
                    min_confidence=float(os.getenv("FACE_RECOGNITION_MIN_CONFIDENCE", "0.6"))
                )
            else:
                raise

        logger.info(f"✓ FaceIdentifier loaded (backend={backend})")

    return _face_identifier


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """API root - redirect to enrollment UI"""
    return {
        "name": "Nura Person Enrollment API",
        "version": "1.0.0",
        "status": "running",
        "enrollment_ui": "/static/enrollment.html",
        "api_docs": "/docs",
        "health": "/health"
    }


@app.post("/api/persons/enroll")
async def enroll_person(
    person_id: str = Form(...),
    full_name: str = Form(...),
    display_name: Optional[str] = Form(None),
    age_years: Optional[int] = Form(None),
    grade_level: Optional[str] = Form(None),
    classroom: Optional[str] = Form(None),
    parental_consent: bool = Form(False),
    enrolled_by: Optional[str] = Form(None),
    photos: List[UploadFile] = File(...)
):
    """
    Enroll a new person with face photos

    Requires 2-5 photos of the person from different angles.
    """
    try:
        # Validate input - now accepts 1-5 photos
        if len(photos) < 1:
            raise HTTPException(status_code=400, detail="At least 1 photo required")

        if len(photos) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 photos allowed")

        # Try to get database connection (optional)
        db = None
        try:
            db_gen = get_db()
            db = next(db_gen)
        except:
            logger.warning("Database not available - running in demo mode")
        
        # Check if person already enrolled (if database available)
        if db:
            try:
                cursor = db.cursor()
                cursor.execute("SELECT person_id FROM enrolled_persons WHERE person_id = %s", (person_id,))
                if cursor.fetchone():
                    raise HTTPException(status_code=409, detail=f"Person {person_id} already enrolled")
            except:
                pass

        # Save uploaded photos
        upload_dir = Path(os.getenv("UPLOAD_DIR", "/tmp/nura_uploads")) / person_id
        upload_dir.mkdir(parents=True, exist_ok=True)

        enrollment_images = []
        saved_paths = []

        for i, photo in enumerate(photos):
            # Save file
            file_path = upload_dir / f"enrollment_{i}.jpg"
            await save_upload_file(photo, file_path)
            saved_paths.append(str(file_path))

            # Load image
            img = cv2.imread(str(file_path))
            if img is None:
                raise HTTPException(status_code=400, detail=f"Invalid image: {photo.filename}")

            enrollment_images.append(img)

        # Auto-augment if only 1 photo provided (for ID card enrollment)
        if len(enrollment_images) == 1:
            logger.info(f"Single photo enrollment - generating 4 augmented variations for {person_id}")
            from nura_detectors.face_identifier import augment_face_image

            # Generate augmented versions
            augmented_images = augment_face_image(enrollment_images[0], num_variations=4)
            enrollment_images = augmented_images

            logger.info(f"✓ Generated {len(enrollment_images)} total images (1 original + {len(enrollment_images)-1} augmented)")

        # Load FaceIdentifier
        identifier = load_face_identifier()

        # Enroll person
        success = identifier.enroll_person(
            person_id=person_id,
            full_name=full_name,
            display_name=display_name or full_name,
            enrollment_images=enrollment_images,
            age_years=age_years,
            grade_level=grade_level,
            classroom=classroom
        )

        if not success:
            raise HTTPException(status_code=400, detail="Enrollment failed - no faces detected in photos")

        # Update database with additional metadata (if database available)
        if db:
            try:
                cursor = db.cursor()
                cursor.execute("""
                    UPDATE enrolled_persons
                    SET age_years = %s,
                        grade_level = %s,
                        classroom = %s,
                        parental_consent = %s,
                        enrolled_by = %s,
                        enrollment_photo_url = %s
                    WHERE person_id = %s
                """, (age_years, grade_level, classroom, parental_consent, enrolled_by, saved_paths[0], person_id))
                db.commit()
            except Exception as e:
                logger.warning(f"Failed to update database metadata: {e}")

        # Determine actual number of images used (after augmentation)
        actual_images_used = len(enrollment_images)

        logger.info(f"✓ Enrolled {person_id} ({full_name}) with {len(photos)} uploaded photo(s), processed {actual_images_used} images total")

        message = f"Successfully enrolled {display_name or full_name}"
        if len(photos) == 1 and actual_images_used > 1:
            message += f" (1 photo auto-augmented to {actual_images_used} variations)"

        return {
            "success": True,
            "person_id": person_id,
            "full_name": full_name,
            "photos_uploaded": len(photos),
            "photos_processed": actual_images_used,
            "message": message
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enrollment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/persons", response_model=List[PersonInfo])
async def list_persons(
    active_only: bool = True,
    classroom: Optional[str] = None,
    db=Depends(get_db)
):
    """List all enrolled persons"""
    cursor = db.cursor()

    query = """
        SELECT person_id, full_name, display_name, age_years, grade_level,
               classroom, parental_consent, active, enrolled_at, enrollment_quality_score
        FROM enrolled_persons
        WHERE 1=1
    """
    params = []

    if active_only:
        query += " AND active = TRUE"

    if classroom:
        query += " AND classroom = %s"
        params.append(classroom)

    query += " ORDER BY enrolled_at DESC"

    cursor.execute(query, params)

    persons = []
    for row in cursor.fetchall():
        persons.append(PersonInfo(
            person_id=row[0],
            full_name=row[1],
            display_name=row[2],
            age_years=row[3],
            grade_level=row[4],
            classroom=row[5],
            parental_consent=row[6],
            active=row[7],
            enrolled_at=row[8],
            enrollment_quality_score=row[9]
        ))

    return persons


@app.get("/api/persons/{person_id}", response_model=PersonInfo)
async def get_person(person_id: str, db=Depends(get_db)):
    """Get person details"""
    cursor = db.cursor()
    cursor.execute("""
        SELECT person_id, full_name, display_name, age_years, grade_level,
               classroom, parental_consent, active, enrolled_at, enrollment_quality_score
        FROM enrolled_persons
        WHERE person_id = %s
    """, (person_id,))

    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found")

    return PersonInfo(
        person_id=row[0],
        full_name=row[1],
        display_name=row[2],
        age_years=row[3],
        grade_level=row[4],
        classroom=row[5],
        parental_consent=row[6],
        active=row[7],
        enrolled_at=row[8],
        enrollment_quality_score=row[9]
    )


@app.get("/api/persons/{person_id}/location", response_model=PersonLocation)
async def get_person_location(person_id: str, db=Depends(get_db)):
    """Get person's current location"""
    cursor = db.cursor()

    # Check if person exists
    cursor.execute("SELECT person_id FROM enrolled_persons WHERE person_id = %s", (person_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found")

    # Get latest sighting
    cursor.execute("""
        SELECT camera_id, timestamp, bbox
        FROM person_sightings
        WHERE global_id = %s
        ORDER BY timestamp DESC
        LIMIT 1
    """, (person_id,))

    row = cursor.fetchone()

    if row:
        camera_id, last_seen, bbox = row

        # Check if recent (within last 5 minutes)
        if datetime.now() - last_seen < timedelta(minutes=5):
            status = "visible"
        else:
            status = "not_seen"

        return PersonLocation(
            person_id=person_id,
            camera_id=camera_id,
            last_seen=last_seen,
            bbox=bbox,
            status=status
        )
    else:
        return PersonLocation(
            person_id=person_id,
            camera_id=None,
            last_seen=None,
            bbox=None,
            status="never_seen"
        )


@app.get("/api/persons/{person_id}/timeline", response_model=List[TimelineEntry])
async def get_person_timeline(
    person_id: str,
    hours: int = 24,
    db=Depends(get_db)
):
    """Get person's movement timeline"""
    cursor = db.cursor()

    cursor.execute("""
        SELECT camera_id, MIN(timestamp) as first_seen, MAX(timestamp) as last_seen, COUNT(*) as num_sightings
        FROM person_sightings
        WHERE global_id = %s AND timestamp > NOW() - INTERVAL '%s hours'
        GROUP BY camera_id
        ORDER BY first_seen ASC
    """, (person_id, hours))

    timeline = []
    for row in cursor.fetchall():
        timeline.append(TimelineEntry(
            camera_id=row[0],
            first_seen=row[1],
            last_seen=row[2],
            num_sightings=row[3]
        ))

    return timeline


@app.put("/api/persons/{person_id}")
async def update_person(
    person_id: str,
    full_name: Optional[str] = None,
    display_name: Optional[str] = None,
    age_years: Optional[int] = None,
    grade_level: Optional[str] = None,
    classroom: Optional[str] = None,
    db=Depends(get_db)
):
    """Update person information"""
    cursor = db.cursor()

    # Check if person exists
    cursor.execute("SELECT person_id FROM enrolled_persons WHERE person_id = %s", (person_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found")

    # Build update query
    updates = []
    params = []

    if full_name:
        updates.append("full_name = %s")
        params.append(full_name)
    if display_name:
        updates.append("display_name = %s")
        params.append(display_name)
    if age_years is not None:
        updates.append("age_years = %s")
        params.append(age_years)
    if grade_level:
        updates.append("grade_level = %s")
        params.append(grade_level)
    if classroom:
        updates.append("classroom = %s")
        params.append(classroom)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(person_id)

    cursor.execute(f"""
        UPDATE enrolled_persons
        SET {', '.join(updates)}
        WHERE person_id = %s
    """, params)

    db.commit()

    return {"success": True, "message": f"Updated {person_id}"}


@app.post("/api/persons/{person_id}/consent")
async def update_consent(
    person_id: str,
    consent: ConsentUpdate,
    db=Depends(get_db)
):
    """Update parental consent status"""
    cursor = db.cursor()

    cursor.execute("""
        UPDATE enrolled_persons
        SET parental_consent = %s,
            consent_document_url = %s,
            consent_date = NOW()
        WHERE person_id = %s
    """, (consent.parental_consent, consent.consent_document_url, person_id))

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found")

    db.commit()

    return {"success": True, "message": f"Consent updated for {person_id}"}


@app.delete("/api/persons/{person_id}")
async def delete_person(
    person_id: str,
    permanent: bool = False,
    db=Depends(get_db)
):
    """
    Delete person enrollment

    By default, performs soft delete (sets deleted_at).
    Set permanent=True for hard delete (GDPR right to be forgotten).
    """
    cursor = db.cursor()

    if permanent:
        # Hard delete (GDPR right to be forgotten)
        cursor.execute("DELETE FROM enrolled_persons WHERE person_id = %s", (person_id,))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Person {person_id} not found")

        db.commit()
        logger.warning(f"PERMANENT DELETE: {person_id}")
        return {"success": True, "message": f"Permanently deleted {person_id}"}
    else:
        # Soft delete
        cursor.execute("""
            UPDATE enrolled_persons
            SET active = FALSE, deleted_at = NOW()
            WHERE person_id = %s
        """, (person_id,))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Person {person_id} not found")

        db.commit()
        logger.info(f"Soft delete: {person_id}")
        return {"success": True, "message": f"Deactivated {person_id}"}


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "nura_db"),
            user=os.getenv("POSTGRES_USER", "nura"),
            password=os.getenv("POSTGRES_PASSWORD", "Pa$$w0rd!")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()

        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("ENROLLMENT_API_PORT", "8002"))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
