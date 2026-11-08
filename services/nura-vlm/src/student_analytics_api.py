"""
Student Analytics API - Week 5
Track student activities to enhance education and understand development
Focus: Educational insights, developmental progress, social connections
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import psycopg2
import psycopg2.extras
from collections import defaultdict

from src.config import config

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/analytics", tags=["student-analytics"])


def get_db_connection():
    """Get PostgreSQL connection using centralized config"""
    return psycopg2.connect(
        **config.database_config,
        cursor_factory=psycopg2.extras.RealDictCursor
    )


# Response Models
class ActivityBreakdown(BaseModel):
    activity: str
    minutes: int
    percentage: float
    engagement_level: str


class ZoneDistribution(BaseModel):
    zone_name: str
    minutes: int
    percentage: float
    primary_activities: List[str]


class SocialInteraction(BaseModel):
    student_id: str
    student_name: Optional[str] = None
    interaction_minutes: int


class DailyStudentReport(BaseModel):
    student_id: str
    student_name: str
    report_date: date
    age_years: Optional[int] = None
    classroom: Optional[str] = None

    # Attendance
    arrival_time: Optional[str] = None
    departure_time: Optional[str] = None
    time_on_campus_hours: Optional[float] = None

    # Activities
    activities: Dict[str, Dict[str, Any]]

    # Zones
    zones: Dict[str, Dict[str, Any]]

    # Social
    social: Dict[str, Any]

    # Insights
    developmental_insights: Dict[str, List[str]]
    parent_summary: str


class CurrentActivity(BaseModel):
    student_id: str
    student_name: str
    current_location: Optional[str] = None
    current_activity: Optional[str] = None
    activity_started: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    last_seen: Optional[datetime] = None


# ============================================================================
# STUDENT ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/student/{student_id}/daily", response_model=DailyStudentReport)
async def get_student_daily_report(
    student_id: str,
    date_str: str = Query(..., alias="date", description="Date in YYYY-MM-DD format")
):
    """
    Get comprehensive daily report for a student

    Includes:
    - Activity breakdown (what they did all day)
    - Zone distribution (where they spent time)
    - Social interactions (who they played with)
    - Developmental insights (strengths & growth areas)
    - Parent-friendly summary
    """
    try:
        report_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get student info
        cursor.execute("""
            SELECT person_id, full_name, display_name, age_years, classroom
            FROM enrolled_persons
            WHERE person_id = %s AND active = true
        """, (student_id,))

        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # Check if report already exists in behavior_reports table
        cursor.execute("""
            SELECT report_data
            FROM behavior_reports
            WHERE person_id = %s AND report_date = %s
        """, (student_id, report_date))

        existing_report = cursor.fetchone()
        if existing_report:
            # Return cached report
            cursor.close()
            conn.close()

            report_data = existing_report['report_data']
            return DailyStudentReport(
                student_id=student_id,
                student_name=student['full_name'],
                report_date=report_date,
                age_years=student.get('age_years'),
                classroom=student.get('classroom'),
                **report_data
            )

        # Generate report on-demand
        start_of_day = datetime.combine(report_date, datetime.min.time())
        end_of_day = datetime.combine(report_date, datetime.max.time())

        # Get all detections for this student on this day
        cursor.execute("""
            SELECT
                detected_at,
                camera_id,
                zone_name,
                activity,
                activity_confidence
            FROM person_detections
            WHERE person_id = %s
              AND detected_at BETWEEN %s AND %s
            ORDER BY detected_at ASC
        """, (student_id, start_of_day, end_of_day))

        detections = cursor.fetchall()

        if not detections:
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=404,
                detail=f"No detection data for {student_id} on {report_date}"
            )

        # Generate report
        report = _generate_student_report(student, detections, report_date)

        # Store report for future requests
        cursor.execute("""
            INSERT INTO behavior_reports (person_id, report_date, report_data)
            VALUES (%s, %s, %s)
            ON CONFLICT (person_id, report_date)
            DO UPDATE SET report_data = EXCLUDED.report_data, generated_at = NOW()
        """, (student_id, report_date, psycopg2.extras.Json(report)))

        conn.commit()
        cursor.close()
        conn.close()

        return DailyStudentReport(
            student_id=student_id,
            student_name=student['full_name'],
            report_date=report_date,
            age_years=student.get('age_years'),
            classroom=student.get('classroom'),
            **report
        )

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate daily report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/student/{student_id}/current", response_model=CurrentActivity)
async def get_student_current_activity(student_id: str):
    """
    Get student's current activity and location (real-time)

    Useful for:
    - "Where is Emma right now?"
    - Teacher dashboard showing current student locations
    - Parent pickup queries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get student info
        cursor.execute("""
            SELECT person_id, full_name, display_name
            FROM enrolled_persons
            WHERE person_id = %s AND active = true
        """, (student_id,))

        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # Check Redis cache first (from person search API)
        try:
            import redis
            redis_client = redis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379"),
                decode_responses=True
            )
            location_key = f"person:location:{student_id}"
            location_data = redis_client.get(location_key)

            if location_data:
                import json
                location = json.loads(location_data)

                cursor.close()
                conn.close()

                return CurrentActivity(
                    student_id=student_id,
                    student_name=student['full_name'],
                    current_location=location.get('zone_name') or location.get('camera_id'),
                    current_activity=location.get('activity'),
                    last_seen=datetime.fromisoformat(location['last_seen']),
                    duration_minutes=None  # Could calculate from last_seen
                )
        except Exception as e:
            logger.warning(f"Redis lookup failed: {e}")

        # Fallback to database (last detection)
        cursor.execute("""
            SELECT
                camera_id,
                zone_name,
                activity,
                detected_at
            FROM person_detections
            WHERE person_id = %s
            ORDER BY detected_at DESC
            LIMIT 1
        """, (student_id,))

        last_detection = cursor.fetchone()

        cursor.close()
        conn.close()

        if not last_detection:
            return CurrentActivity(
                student_id=student_id,
                student_name=student['full_name']
            )

        return CurrentActivity(
            student_id=student_id,
            student_name=student['full_name'],
            current_location=last_detection['zone_name'] or last_detection['camera_id'],
            current_activity=last_detection.get('activity'),
            last_seen=last_detection['detected_at']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get current activity: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classroom/{classroom_id}/overview")
async def get_classroom_overview(
    classroom_id: str,
    date_str: Optional[str] = Query(None, alias="date", description="Date (default: today)")
):
    """
    Get classroom overview - all students and their current activities

    Teacher dashboard showing:
    - Who is present
    - What they're doing
    - Who needs attention
    """
    try:
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = datetime.now().date()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all students in this classroom
        cursor.execute("""
            SELECT person_id, full_name
            FROM enrolled_persons
            WHERE classroom = %s AND active = true
        """, (classroom_id,))

        students = cursor.fetchall()

        if not students:
            cursor.close()
            conn.close()
            return {
                "classroom": classroom_id,
                "date": target_date.isoformat(),
                "students_present": 0,
                "students_absent": 0,
                "current_activities": {},
                "needs_attention": []
            }

        # Check who's present today (has detections)
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())

        student_ids = [s['person_id'] for s in students]
        cursor.execute("""
            SELECT DISTINCT person_id
            FROM person_detections
            WHERE person_id = ANY(%s)
              AND detected_at BETWEEN %s AND %s
        """, (student_ids, start_of_day, end_of_day))

        present_ids = [row['person_id'] for row in cursor.fetchall()]

        # Get current activities (last detection for each present student)
        current_activities = {}
        if present_ids:
            cursor.execute("""
                SELECT DISTINCT ON (person_id)
                    person_id, activity
                FROM person_detections
                WHERE person_id = ANY(%s)
                  AND detected_at BETWEEN %s AND %s
                ORDER BY person_id, detected_at DESC
            """, (present_ids, start_of_day, end_of_day))

            activity_counts = defaultdict(int)
            for row in cursor.fetchall():
                if row['activity']:
                    activity_counts[row['activity']] += 1

            current_activities = dict(activity_counts)

        cursor.close()
        conn.close()

        return {
            "classroom": classroom_id,
            "date": target_date.isoformat(),
            "students_enrolled": len(students),
            "students_present": len(present_ids),
            "students_absent": len(students) - len(present_ids),
            "current_activities": current_activities,
            "needs_attention": []  # TODO: Implement attention detection
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Failed to get classroom overview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _generate_student_report(student: dict, detections: list, report_date: date) -> dict:
    """
    Generate comprehensive daily report from detection data
    """
    if not detections:
        return {}

    total_detections = len(detections)
    first_seen = detections[0]['detected_at']
    last_seen = detections[-1]['detected_at']
    time_on_campus = (last_seen - first_seen).total_seconds() / 3600  # hours

    # Aggregate activities
    activity_counts = defaultdict(int)
    for d in detections:
        if d.get('activity'):
            activity_counts[d['activity']] += 1

    total_activity_detections = sum(activity_counts.values()) or 1
    activities = {}
    for activity, count in activity_counts.items():
        percentage = (count / total_activity_detections) * 100
        activities[activity] = {
            "count": count,
            "percentage": round(percentage, 1),
            "engagement_level": "high" if percentage > 20 else "medium" if percentage > 10 else "low"
        }

    # Aggregate zones
    zone_counts = defaultdict(int)
    for d in detections:
        if d.get('zone_name'):
            zone_counts[d['zone_name']] += 1

    total_zone_detections = sum(zone_counts.values()) or 1
    zones = {}
    for zone, count in zone_counts.items():
        percentage = (count / total_zone_detections) * 100
        zones[zone] = {
            "detections": count,
            "percentage": round(percentage, 1)
        }

    # Developmental insights
    strengths = []
    if activity_counts.get('playing', 0) > total_detections * 0.2:
        strengths.append("Active and engaged in play")
    if activity_counts.get('reading', 0) > total_detections * 0.1:
        strengths.append("Shows interest in reading")
    if activity_counts.get('interacting', 0) > total_detections * 0.3:
        strengths.append("Strong social skills")

    areas_for_growth = []
    if activity_counts.get('alone', 0) > total_detections * 0.3:
        areas_for_growth.append("Consider more group activities")

    # Parent summary
    top_activity = max(activity_counts.items(), key=lambda x: x[1])[0] if activity_counts else "various activities"
    parent_summary = f"{student['full_name']} had a great day! " \
                    f"They were primarily engaged in {top_activity} " \
                    f"and spent {time_on_campus:.1f} hours on campus."

    return {
        "arrival_time": first_seen.strftime("%H:%M"),
        "departure_time": last_seen.strftime("%H:%M"),
        "time_on_campus_hours": round(time_on_campus, 2),
        "activities": activities,
        "zones": zones,
        "social": {
            "interaction_partners": [],  # TODO: Implement from proximity detection
            "teacher_interactions": 0  # TODO: Implement
        },
        "developmental_insights": {
            "strengths": strengths or ["Participated in daily activities"],
            "areas_for_growth": areas_for_growth or ["Continue current progress"],
            "recommended_activities": []
        },
        "parent_summary": parent_summary
    }
