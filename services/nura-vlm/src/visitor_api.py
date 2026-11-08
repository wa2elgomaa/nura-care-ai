"""
Visitor Management API - Week 3
Temporary visitor enrollment for stranger detection whitelist
"""
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
import psycopg2
import cv2
import numpy as np

from src.config import config
from src.storage_client import get_storage_client

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/visitors", tags=["visitors"])


class VisitorResponse(BaseModel):
    visitor_id: str
    name: str
    valid_from: str
    valid_until: str
    purpose: str
    approved_by: str
    checked_out: Optional[str] = None


class VisitorEnrollRequest(BaseModel):
    name: str
    valid_until: str
    purpose: str
    approved_by: str


def get_db_connection():
    """Get PostgreSQL connection using centralized config"""
    return psycopg2.connect(**config.database_config)


@router.post("/enroll", response_model=VisitorResponse)
async def enroll_visitor(
    name: str = Form(...),
    valid_until: str = Form(...),  # ISO timestamp
    purpose: str = Form(...),
    approved_by: str = Form(...),
    photo: UploadFile = File(...)
):
    """
    Enroll a temporary visitor

    Visitor will be added to whitelist and won't trigger stranger alerts
    during their valid time window
    """
    try:
        # Parse valid_until
        valid_until_dt = datetime.fromisoformat(valid_until.replace('Z', '+00:00'))
        valid_from_dt = datetime.now()

        # Read and process photo
        content = await photo.read()
        nparr = np.frombuffer(content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
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
                logger.info(f"✓ Face embedding extracted for {name}")
            else:
                logger.warning(f"No face detected in visitor photo: {name}")
        except Exception as e:
            logger.error(f"Failed to extract face embedding: {e}")

        # Save photo to storage
        storage_client = get_storage_client()
        filename = f"visitor_{name.replace(' ', '_')}_{int(valid_from_dt.timestamp())}.jpg"

        await photo.seek(0)  # Reset
        result = await storage_client.save_file(content, "visitors", filename)
        photo_path = result['path']

        # Insert into database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO visitors (
                name, face_encoding, photo_path, valid_from, valid_until,
                purpose, approved_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING visitor_id, created_at
        """, (
            name,
            face_embedding.tolist() if face_embedding is not None else None,
            photo_path,
            valid_from_dt,
            valid_until_dt,
            purpose,
            approved_by
        ))

        visitor_id, created_at = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"✓ Visitor enrolled: {name} (valid until {valid_until_dt})")

        return VisitorResponse(
            visitor_id=str(visitor_id),
            name=name,
            valid_from=valid_from_dt.isoformat(),
            valid_until=valid_until_dt.isoformat(),
            purpose=purpose,
            approved_by=approved_by
        )

    except Exception as e:
        logger.error(f"Failed to enroll visitor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{visitor_id}/checkout")
async def checkout_visitor(visitor_id: str):
    """
    Check out a visitor (removes from whitelist immediately)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE visitors
            SET checked_out = NOW()
            WHERE visitor_id = %s AND checked_out IS NULL
            RETURNING name
        """, (visitor_id,))

        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if not result:
            raise HTTPException(status_code=404, detail="Visitor not found or already checked out")

        name = result[0]
        logger.info(f"✓ Visitor checked out: {name}")

        return {"success": True, "message": f"Visitor {name} checked out"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to checkout visitor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active", response_model=List[VisitorResponse])
async def list_active_visitors():
    """
    List all active visitors (not checked out, within valid window)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT visitor_id, name, valid_from, valid_until, purpose, approved_by, checked_out
            FROM visitors
            WHERE checked_out IS NULL
              AND valid_from <= NOW()
              AND valid_until >= NOW()
            ORDER BY valid_from DESC
        """)

        visitors = []
        for row in cursor.fetchall():
            visitors.append(VisitorResponse(
                visitor_id=str(row[0]),
                name=row[1],
                valid_from=row[2].isoformat(),
                valid_until=row[3].isoformat(),
                purpose=row[4],
                approved_by=row[5],
                checked_out=row[6].isoformat() if row[6] else None
            ))

        cursor.close()
        conn.close()

        return visitors

    except Exception as e:
        logger.error(f"Failed to list visitors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{visitor_id}", response_model=VisitorResponse)
async def get_visitor(visitor_id: str):
    """Get visitor details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT visitor_id, name, valid_from, valid_until, purpose, approved_by, checked_out
            FROM visitors
            WHERE visitor_id = %s
        """, (visitor_id,))

        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Visitor not found")

        return VisitorResponse(
            visitor_id=str(row[0]),
            name=row[1],
            valid_from=row[2].isoformat(),
            valid_until=row[3].isoformat(),
            purpose=row[4],
            approved_by=row[5],
            checked_out=row[6].isoformat() if row[6] else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get visitor: {e}")
        raise HTTPException(status_code=500, detail=str(e))
