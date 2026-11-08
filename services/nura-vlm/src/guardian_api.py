"""
Guardian/Parent Management API - Week 3+
Permanent enrollment of students' parents/guardians (whitelisted persons)
Linked to enrolled students for authorized pickup and access
"""
import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
import psycopg2
import cv2
import numpy as np

from src.config import config
from src.storage_client import get_storage_client

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/guardians", tags=["guardians"])


class GuardianResponse(BaseModel):
    guardian_id: str
    full_name: str
    relationship: str  # mother, father, grandmother, etc
    linked_students: List[str]  # person_ids of students
    phone: Optional[str] = None
    email: Optional[str] = None
    authorized_pickup: bool
    photo_path: Optional[str] = None
    created_at: str
    active: bool


class GuardianEnrollRequest(BaseModel):
    full_name: str
    relationship: str
    linked_students: List[str]
    phone: Optional[str] = None
    email: Optional[str] = None
    authorized_pickup: bool = True


def get_db_connection():
    """Get PostgreSQL connection using centralized config"""
    return psycopg2.connect(**config.database_config)


@router.post("/enroll", response_model=GuardianResponse)
async def enroll_guardian(
    full_name: str = Form(...),
    relationship: str = Form(...),  # mother, father, grandmother, guardian, etc
    linked_students: str = Form(...),  # Comma-separated person_ids
    phone: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    authorized_pickup: bool = Form(True),
    photo: UploadFile = File(...)
):
    """
    Enroll a parent/guardian

    Guardian will be added to enrolled_persons as a whitelisted person
    and linked to their children/students for authorized access
    """
    try:
        # Parse linked students
        student_ids = [s.strip() for s in linked_students.split(',')]

        # Verify students exist
        conn = get_db_connection()
        cursor = conn.cursor()

        for student_id in student_ids:
            cursor.execute("""
                SELECT person_id FROM enrolled_persons
                WHERE person_id = %s AND active = true
            """, (student_id,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                raise HTTPException(
                    status_code=400,
                    detail=f"Student not found or inactive: {student_id}"
                )

        # Read and process photo
        content = await photo.read()
        nparr = np.frombuffer(content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Invalid image")

        # Extract face embedding using InsightFace
        face_embedding = None
        try:
            import insightface
            face_model = insightface.app.FaceAnalysis(
                name='buffalo_l',
                providers=['CPUExecutionProvider']
            )
            face_model.prepare(ctx_id=0, det_size=(640, 640))

            faces = face_model.get(img)
            if faces:
                face_embedding = faces[0].embedding  # 512D vector
                logger.info(f"✓ Face embedding extracted for {full_name}")
            else:
                logger.warning(f"No face detected in guardian photo: {full_name}")
                cursor.close()
                conn.close()
                raise HTTPException(status_code=400, detail="No face detected in photo")
        except Exception as e:
            logger.error(f"Failed to extract face embedding: {e}")
            cursor.close()
            conn.close()
            raise HTTPException(status_code=500, detail=f"Face extraction failed: {e}")

        # Generate guardian person_id
        guardian_id = f"guardian_{full_name.lower().replace(' ', '_')}"

        # Save photo to storage
        storage_client = get_storage_client()
        filename = f"{guardian_id}_{int(datetime.now().timestamp())}.jpg"

        await photo.seek(0)  # Reset
        result = await storage_client.save_file(content, "guardians", filename)
        photo_path = result['path']

        # Insert into enrolled_persons (as a guardian/parent)
        cursor.execute("""
            INSERT INTO enrolled_persons (
                person_id, full_name, display_name, face_embedding,
                face_embedding_model, enrollment_photo_url,
                parental_consent, active, notes, is_visitor
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, enrolled_at
        """, (
            guardian_id,
            full_name,
            full_name,  # display_name = full_name for guardians
            face_embedding.tolist() if face_embedding is not None else None,
            'insightface_buffalo_l',
            photo_path,
            True,  # parental_consent (guardian is the parent)
            True,  # active
            f"Relationship: {relationship}, Students: {', '.join(student_ids)}, Phone: {phone}, Email: {email}, Authorized Pickup: {authorized_pickup}",
            False  # is_visitor = False (permanent guardian)
        ))

        guardian_db_id, enrolled_at = cursor.fetchone()

        # Create guardian metadata table entry (if table exists)
        # For now, store in notes field above

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"✓ Guardian enrolled: {full_name} (linked to {len(student_ids)} students)")

        return GuardianResponse(
            guardian_id=guardian_id,
            full_name=full_name,
            relationship=relationship,
            linked_students=student_ids,
            phone=phone,
            email=email,
            authorized_pickup=authorized_pickup,
            photo_path=photo_path,
            created_at=enrolled_at.isoformat(),
            active=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enroll guardian: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[GuardianResponse])
async def list_guardians(active_only: bool = True):
    """
    List all enrolled guardians/parents
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT person_id, full_name, enrollment_photo_url, notes, enrolled_at, active
            FROM enrolled_persons
            WHERE person_id LIKE 'guardian_%'
        """

        if active_only:
            query += " AND active = true"

        query += " ORDER BY enrolled_at DESC"

        cursor.execute(query)

        guardians = []
        for row in cursor.fetchall():
            person_id, full_name, photo_path, notes, enrolled_at, active = row

            # Parse notes field for guardian metadata
            relationship = "guardian"
            linked_students = []
            phone = None
            email = None
            authorized_pickup = True

            if notes:
                # Parse notes: "Relationship: mother, Students: alice_j, bob_k, Phone: 555-1234, ..."
                for part in notes.split(','):
                    part = part.strip()
                    if part.startswith('Relationship:'):
                        relationship = part.split(':', 1)[1].strip()
                    elif part.startswith('Students:'):
                        students_str = part.split(':', 1)[1].strip()
                        linked_students = [s.strip() for s in students_str.split(',') if s.strip()]
                    elif part.startswith('Phone:'):
                        phone = part.split(':', 1)[1].strip()
                    elif part.startswith('Email:'):
                        email = part.split(':', 1)[1].strip()
                    elif part.startswith('Authorized Pickup:'):
                        authorized_pickup = part.split(':', 1)[1].strip().lower() == 'true'

            guardians.append(GuardianResponse(
                guardian_id=person_id,
                full_name=full_name,
                relationship=relationship,
                linked_students=linked_students,
                phone=phone,
                email=email,
                authorized_pickup=authorized_pickup,
                photo_path=photo_path,
                created_at=enrolled_at.isoformat() if enrolled_at else None,
                active=active
            ))

        cursor.close()
        conn.close()

        return guardians

    except Exception as e:
        logger.error(f"Failed to list guardians: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{guardian_id}", response_model=GuardianResponse)
async def get_guardian(guardian_id: str):
    """Get guardian details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT person_id, full_name, enrollment_photo_url, notes, enrolled_at, active
            FROM enrolled_persons
            WHERE person_id = %s
        """, (guardian_id,))

        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Guardian not found")

        person_id, full_name, photo_path, notes, enrolled_at, active = row

        # Parse notes
        relationship = "guardian"
        linked_students = []
        phone = None
        email = None
        authorized_pickup = True

        if notes:
            for part in notes.split(','):
                part = part.strip()
                if part.startswith('Relationship:'):
                    relationship = part.split(':', 1)[1].strip()
                elif part.startswith('Students:'):
                    students_str = part.split(':', 1)[1].strip()
                    linked_students = [s.strip() for s in students_str.split(',') if s.strip()]
                elif part.startswith('Phone:'):
                    phone = part.split(':', 1)[1].strip()
                elif part.startswith('Email:'):
                    email = part.split(':', 1)[1].strip()
                elif part.startswith('Authorized Pickup:'):
                    authorized_pickup = part.split(':', 1)[1].strip().lower() == 'true'

        return GuardianResponse(
            guardian_id=person_id,
            full_name=full_name,
            relationship=relationship,
            linked_students=linked_students,
            phone=phone,
            email=email,
            authorized_pickup=authorized_pickup,
            photo_path=photo_path,
            created_at=enrolled_at.isoformat() if enrolled_at else None,
            active=active
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get guardian: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-student/{student_id}", response_model=List[GuardianResponse])
async def get_guardians_by_student(student_id: str):
    """
    Get all guardians linked to a specific student
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT person_id, full_name, enrollment_photo_url, notes, enrolled_at, active
            FROM enrolled_persons
            WHERE person_id LIKE 'guardian_%'
              AND notes LIKE %s
              AND active = true
            ORDER BY enrolled_at DESC
        """, (f'%Students:%{student_id}%',))

        guardians = []
        for row in cursor.fetchall():
            person_id, full_name, photo_path, notes, enrolled_at, active = row

            # Parse notes
            relationship = "guardian"
            linked_students = []
            phone = None
            email = None
            authorized_pickup = True

            if notes:
                for part in notes.split(','):
                    part = part.strip()
                    if part.startswith('Relationship:'):
                        relationship = part.split(':', 1)[1].strip()
                    elif part.startswith('Students:'):
                        students_str = part.split(':', 1)[1].strip()
                        linked_students = [s.strip() for s in students_str.split(',') if s.strip()]
                    elif part.startswith('Phone:'):
                        phone = part.split(':', 1)[1].strip()
                    elif part.startswith('Email:'):
                        email = part.split(':', 1)[1].strip()
                    elif part.startswith('Authorized Pickup:'):
                        authorized_pickup = part.split(':', 1)[1].strip().lower() == 'true'

            guardians.append(GuardianResponse(
                guardian_id=person_id,
                full_name=full_name,
                relationship=relationship,
                linked_students=linked_students,
                phone=phone,
                email=email,
                authorized_pickup=authorized_pickup,
                photo_path=photo_path,
                created_at=enrolled_at.isoformat() if enrolled_at else None,
                active=active
            ))

        cursor.close()
        conn.close()

        return guardians

    except Exception as e:
        logger.error(f"Failed to get guardians by student: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{guardian_id}/deactivate")
async def deactivate_guardian(guardian_id: str):
    """
    Deactivate a guardian (soft delete - won't trigger stranger alerts but won't be recognized)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE enrolled_persons
            SET active = false
            WHERE person_id = %s
            RETURNING full_name
        """, (guardian_id,))

        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if not result:
            raise HTTPException(status_code=404, detail="Guardian not found")

        full_name = result[0]
        logger.info(f"✓ Guardian deactivated: {full_name}")

        return {"success": True, "message": f"Guardian {full_name} deactivated"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deactivate guardian: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{guardian_id}/reactivate")
async def reactivate_guardian(guardian_id: str):
    """
    Reactivate a guardian
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE enrolled_persons
            SET active = true
            WHERE person_id = %s
            RETURNING full_name
        """, (guardian_id,))

        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if not result:
            raise HTTPException(status_code=404, detail="Guardian not found")

        full_name = result[0]
        logger.info(f"✓ Guardian reactivated: {full_name}")

        return {"success": True, "message": f"Guardian {full_name} reactivated"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reactivate guardian: {e}")
        raise HTTPException(status_code=500, detail=str(e))
