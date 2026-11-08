"""
Stranger Detector - Week 3
Detects unknown persons (not in enrolled_persons or visitors tables)
"""
import logging
from typing import Optional, List, Tuple
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class StrangerDetection:
    """Stranger detection result"""
    is_stranger: bool
    person_id: Optional[str]  # Track ID
    confidence: float
    face_embedding: Optional[np.ndarray] = None
    bbox: Optional[List[int]] = None
    closest_match: Optional[str] = None  # Closest enrolled person (for logging)
    match_distance: Optional[float] = None


class StrangerDetector:
    """
    Detects unknown/stranger persons by checking against:
    1. enrolled_persons table (permanent enrollments)
    2. visitors table (temporary whitelisted visitors)

    If face not recognized in either → Stranger
    """

    def __init__(
        self,
        db_connection,
        min_confidence: float = 0.6,
        backend: str = "insightface"
    ):
        """
        Args:
            db_connection: PostgreSQL connection
            min_confidence: Minimum face recognition confidence (default 0.6)
            backend: Face recognition backend (insightface, facenet, arcface)
        """
        self.db_connection = db_connection
        self.min_confidence = min_confidence
        self.backend = backend

        # Load face recognition model
        if backend == "insightface":
            try:
                import insightface
                self.face_model = insightface.app.FaceAnalysis(
                    name='buffalo_l',
                    providers=['CPUExecutionProvider']
                )
                self.face_model.prepare(ctx_id=0, det_size=(640, 640))
                logger.info(f"✓ Stranger detector initialized (InsightFace)")
            except Exception as e:
                logger.warning(f"Failed to load InsightFace: {e}")
                self.face_model = None
        else:
            logger.warning(f"Backend {backend} not implemented, using fallback")
            self.face_model = None

    def detect(
        self,
        frame: np.ndarray,
        person_tracks: List[dict],
        face_identifier=None
    ) -> List[StrangerDetection]:
        """
        Detect strangers in frame

        Args:
            frame: Input image (BGR)
            person_tracks: List of tracked persons from PersonTracker
            face_identifier: FaceIdentifier instance (to check enrollments & visitors)

        Returns:
            List of StrangerDetection results
        """
        if not self.face_model:
            logger.warning("Face model not loaded, cannot detect strangers")
            return []

        if not face_identifier:
            logger.warning("FaceIdentifier not provided, cannot detect strangers")
            return []

        results = []

        for track in person_tracks:
            person_id = track['id']
            bbox = track['bbox']

            # Check if already identified
            if track.get('identity'):
                # Known person - not a stranger
                results.append(StrangerDetection(
                    is_stranger=False,
                    person_id=str(person_id),
                    confidence=track.get('identity_confidence', 1.0),
                    bbox=bbox,
                    closest_match=track['identity']
                ))
                continue

            # Try to identify against enrolled persons + visitors
            identity = face_identifier.identify(frame, bbox)

            if identity and identity.confidence >= self.min_confidence:
                # Person identified (enrolled or visitor)
                results.append(StrangerDetection(
                    is_stranger=False,
                    person_id=str(person_id),
                    confidence=identity.confidence,
                    bbox=bbox,
                    closest_match=identity.person_id
                ))
            else:
                # Unknown person - STRANGER!
                results.append(StrangerDetection(
                    is_stranger=True,
                    person_id=str(person_id),
                    confidence=0.95,  # High confidence it's unknown
                    bbox=bbox,
                    closest_match=identity.person_id if identity else None,
                    match_distance=1.0 - identity.confidence if identity else None
                ))

                logger.warning(f"⚠️ Stranger detected: Person {person_id}")

        return results

    def check_visitor_whitelist(self, face_embedding: np.ndarray) -> Optional[Tuple[str, float]]:
        """
        Check if face matches active visitor

        Args:
            face_embedding: Face embedding vector

        Returns:
            (visitor_name, confidence) if match found, else None
        """
        try:
            cursor = self.db_connection.cursor()

            # Get active visitors (not checked out, within valid time window)
            cursor.execute("""
                SELECT visitor_id, name, face_encoding
                FROM visitors
                WHERE checked_out IS NULL
                  AND valid_from <= NOW()
                  AND valid_until >= NOW()
            """)

            visitors = cursor.fetchall()
            cursor.close()

            if not visitors:
                return None

            # Find closest match
            best_match = None
            best_distance = float('inf')

            for visitor_id, name, face_enc in visitors:
                if face_enc is None:
                    continue

                # Convert pgvector to numpy
                visitor_embedding = np.array(face_enc)

                # Cosine distance
                distance = 1.0 - np.dot(face_embedding, visitor_embedding) / (
                    np.linalg.norm(face_embedding) * np.linalg.norm(visitor_embedding)
                )

                if distance < best_distance:
                    best_distance = distance
                    best_match = name

            if best_match and best_distance < (1.0 - self.min_confidence):
                confidence = 1.0 - best_distance
                logger.info(f"✓ Visitor match: {best_match} (confidence: {confidence:.2%})")
                return (best_match, confidence)

            return None

        except Exception as e:
            logger.error(f"Failed to check visitor whitelist: {e}")
            return None
