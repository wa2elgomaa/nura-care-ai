"""
Face Identification Module - Phase 4B

Identifies persons by face recognition using ArcFace embeddings.
Links tracked person IDs to real identities from enrollment database.

Architecture:
1. Face Detection - Extract face ROI from person bounding box
2. Face Encoding - Generate 512D embedding (ArcFace/FaceNet)
3. Face Matching - Compare with enrollment database
4. Confidence Scoring - Return identity with confidence

Usage:
    identifier = FaceIdentifier(db_connection)

    # Identify person from frame
    identity = identifier.identify(frame, person_bbox)

    if identity:
        print(f"Person: {identity['name']} (confidence: {identity['confidence']:.2f})")
"""

import os
import numpy as np
import cv2
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class FaceIdentity:
    """Face identification result"""
    person_id: str              # e.g., "adam_w"
    full_name: str              # e.g., "Adam Williams"
    display_name: str           # e.g., "Adam W."
    confidence: float           # 0-1
    method: str = "face"        # "face", "appearance", "fusion"
    distance: float = 0.0       # Embedding distance
    face_bbox: Optional[List[float]] = None  # Face location within person ROI


class FaceIdentifier:
    """
    Face-based person identification

    Supports multiple backends:
    1. face_recognition (dlib-based, easy to use)
    2. InsightFace (ArcFace, state-of-the-art)
    3. DeepFace (multiple models)

    Recommended: InsightFace for production (best accuracy + speed)
    """

    def __init__(
        self,
        db_connection=None,
        backend: str = "face_recognition",  # or "insightface", "deepface"
        model_name: str = "arcface_r100",
        min_confidence: float = 0.6,
        min_face_size: int = 40  # Minimum face size in pixels
    ):
        """
        Args:
            db_connection: Database connection for enrollment lookup
            backend: Face recognition backend
            model_name: Specific model (backend-dependent)
            min_confidence: Minimum confidence threshold (0-1)
            min_face_size: Minimum face size to process
        """
        self.db = db_connection
        self.backend = backend
        self.model_name = model_name
        self.min_confidence = min_confidence
        self.min_face_size = min_face_size

        # Face detector
        self.face_detector = None
        self.face_encoder = None

        # In-memory enrollment cache (for speed)
        self.enrollment_cache = {}

        # Initialize backend
        self._init_backend()

        # Load enrollment database into cache
        if self.db:
            self._load_enrollment_cache()

    def _init_backend(self):
        """Initialize face recognition backend"""

        if self.backend == "face_recognition":
            self._init_face_recognition()
        elif self.backend == "insightface":
            self._init_insightface()
        elif self.backend == "deepface":
            self._init_deepface()
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    def _init_face_recognition(self):
        """Initialize face_recognition backend (dlib)"""
        try:
            import face_recognition

            self.face_encoder = face_recognition
            logger.info("✓ face_recognition backend initialized (dlib)")
        except ImportError:
            logger.error("face_recognition not installed. Install: pip install face-recognition")
            raise

    def _init_insightface(self):
        """Initialize InsightFace backend (ArcFace)"""
        try:
            from insightface.app import FaceAnalysis

            # Initialize face analysis app
            self.face_analyzer = FaceAnalysis(
                name=self.model_name,
                providers=['CPUExecutionProvider']  # or CUDAExecutionProvider for GPU
            )
            self.face_analyzer.prepare(ctx_id=0, det_size=(640, 640))

            logger.info(f"✓ InsightFace backend initialized ({self.model_name})")
        except ImportError:
            logger.error("InsightFace not installed. Install: pip install insightface onnxruntime")
            raise

    def _init_deepface(self):
        """Initialize DeepFace backend"""
        try:
            from deepface import DeepFace

            self.deepface = DeepFace
            logger.info(f"✓ DeepFace backend initialized ({self.model_name})")
        except ImportError:
            logger.error("DeepFace not installed. Install: pip install deepface")
            raise

    def _load_enrollment_cache(self):
        """Load enrolled persons into memory cache"""
        if not self.db:
            logger.warning("No database connection, enrollment cache empty")
            return

        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT person_id, full_name, display_name, face_embedding
                FROM enrolled_persons
                WHERE active = TRUE AND face_embedding IS NOT NULL
            """)

            for row in cursor.fetchall():
                person_id, full_name, display_name, embedding_bytes = row

                # Convert bytes to numpy array
                embedding = np.frombuffer(embedding_bytes, dtype=np.float32)

                self.enrollment_cache[person_id] = {
                    'person_id': person_id,
                    'full_name': full_name,
                    'display_name': display_name,
                    'embedding': embedding
                }

            logger.info(f"✓ Loaded {len(self.enrollment_cache)} enrolled persons into cache")
        except Exception as e:
            logger.error(f"Failed to load enrollment cache: {e}")

    def identify(
        self,
        frame: np.ndarray,
        person_bbox: List[float],
        return_all_faces: bool = False
    ) -> Optional[FaceIdentity]:
        """
        Identify person by face within bounding box

        Args:
            frame: Full frame (BGR)
            person_bbox: Person bounding box [x1, y1, x2, y2]
            return_all_faces: If True, return all detected faces (for multi-face cases)

        Returns:
            FaceIdentity if identified, None otherwise
        """
        # Crop person ROI
        x1, y1, x2, y2 = [int(v) for v in person_bbox]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

        if x2 <= x1 or y2 <= y1:
            return None

        person_roi = frame[y1:y2, x1:x2]

        # Detect faces in person ROI
        faces = self._detect_faces(person_roi)

        if not faces:
            return None

        # Use largest face (primary face)
        face = self._get_largest_face(faces)

        # Check face size
        face_width = face['bbox'][2] - face['bbox'][0]
        face_height = face['bbox'][3] - face['bbox'][1]

        if face_width < self.min_face_size or face_height < self.min_face_size:
            logger.debug(f"Face too small: {face_width}x{face_height} < {self.min_face_size}")
            return None

        # Extract face embedding
        embedding = face.get('embedding')

        if embedding is None:
            return None

        # Match against enrollment database
        match = self._find_best_match(embedding)

        if match and match['confidence'] >= self.min_confidence:
            # Convert face bbox to frame coordinates
            face_bbox_roi = face['bbox']
            face_bbox_frame = [
                face_bbox_roi[0] + x1,
                face_bbox_roi[1] + y1,
                face_bbox_roi[2] + x1,
                face_bbox_roi[3] + y1
            ]

            return FaceIdentity(
                person_id=match['person_id'],
                full_name=match['full_name'],
                display_name=match['display_name'],
                confidence=match['confidence'],
                distance=match['distance'],
                face_bbox=face_bbox_frame
            )

        return None

    def _detect_faces(self, image: np.ndarray) -> List[Dict]:
        """
        Detect faces and extract embeddings

        Returns:
            List of face dicts with 'bbox' and 'embedding'
        """
        if self.backend == "face_recognition":
            return self._detect_faces_face_recognition(image)
        elif self.backend == "insightface":
            return self._detect_faces_insightface(image)
        elif self.backend == "deepface":
            return self._detect_faces_deepface(image)

    def _detect_faces_face_recognition(self, image: np.ndarray) -> List[Dict]:
        """Detect faces using face_recognition (dlib)"""
        import face_recognition

        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_image, model="hog")  # or "cnn" for GPU

        if not face_locations:
            return []

        # Extract face encodings (128D embeddings)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

        faces = []
        for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
            faces.append({
                'bbox': [left, top, right, bottom],  # [x1, y1, x2, y2]
                'embedding': encoding
            })

        return faces

    def _detect_faces_insightface(self, image: np.ndarray) -> List[Dict]:
        """Detect faces using InsightFace (ArcFace)"""
        # InsightFace expects RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect and analyze faces
        faces_data = self.face_analyzer.get(rgb_image)

        if not faces_data:
            return []

        faces = []
        for face in faces_data:
            bbox = face.bbox.astype(int)  # [x1, y1, x2, y2]
            embedding = face.embedding  # 512D vector

            faces.append({
                'bbox': bbox.tolist(),
                'embedding': embedding,
                'det_score': face.det_score  # Detection confidence
            })

        return faces

    def _detect_faces_deepface(self, image: np.ndarray) -> List[Dict]:
        """Detect faces using DeepFace"""
        from deepface import DeepFace

        # DeepFace.represent returns embeddings
        try:
            result = DeepFace.represent(
                img_path=image,
                model_name=self.model_name,
                enforce_detection=False
            )

            # DeepFace returns list of face dicts
            faces = []
            for face_data in result:
                # Extract bbox from facial_area
                facial_area = face_data.get('facial_area', {})
                bbox = [
                    facial_area.get('x', 0),
                    facial_area.get('y', 0),
                    facial_area.get('x', 0) + facial_area.get('w', 0),
                    facial_area.get('y', 0) + facial_area.get('h', 0)
                ]

                faces.append({
                    'bbox': bbox,
                    'embedding': np.array(face_data['embedding'])
                })

            return faces
        except Exception as e:
            logger.warning(f"DeepFace detection failed: {e}")
            return []

    def _get_largest_face(self, faces: List[Dict]) -> Dict:
        """Get largest face by area"""
        largest_face = None
        largest_area = 0

        for face in faces:
            bbox = face['bbox']
            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])

            if area > largest_area:
                largest_area = area
                largest_face = face

        return largest_face

    def _find_best_match(self, query_embedding: np.ndarray) -> Optional[Dict]:
        """
        Find best match in enrollment database

        Returns:
            Dict with person_id, full_name, display_name, distance, confidence
        """
        if not self.enrollment_cache:
            return None

        best_match = None
        best_distance = float('inf')

        for person_id, person_data in self.enrollment_cache.items():
            enrolled_embedding = person_data['embedding']

            # Cosine distance (or Euclidean)
            distance = self._compute_distance(query_embedding, enrolled_embedding)

            if distance < best_distance:
                best_distance = distance
                best_match = {
                    'person_id': person_id,
                    'full_name': person_data['full_name'],
                    'display_name': person_data['display_name'],
                    'distance': distance,
                    'confidence': 1.0 - distance  # Convert distance to confidence
                }

        return best_match

    def _compute_distance(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute distance between embeddings

        Uses cosine distance (1 - cosine_similarity)
        """
        # Normalize embeddings
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        embedding2 = embedding2 / np.linalg.norm(embedding2)

        # Cosine similarity
        similarity = np.dot(embedding1, embedding2)

        # Cosine distance
        distance = 1.0 - similarity

        return float(distance)

    def enroll_person(
        self,
        person_id: str,
        full_name: str,
        display_name: str,
        enrollment_images: List[np.ndarray],
        **metadata
    ) -> bool:
        """
        Enroll a new person

        Args:
            person_id: Unique person identifier
            full_name: Full name
            display_name: Display name
            enrollment_images: List of face images (multiple angles)
            **metadata: Additional metadata (age, classroom, etc.)

        Returns:
            True if enrollment successful
        """
        # Extract face embeddings from all images
        embeddings = []

        for image in enrollment_images:
            faces = self._detect_faces(image)

            if faces:
                # Use largest face
                face = self._get_largest_face(faces)
                embeddings.append(face['embedding'])

        if not embeddings:
            logger.error(f"No faces detected in enrollment images for {person_id}")
            return False

        # Average embeddings (or use first one)
        avg_embedding = np.mean(embeddings, axis=0)

        # Store in database
        if self.db:
            try:
                cursor = self.db.cursor()
                cursor.execute("""
                    INSERT INTO enrolled_persons
                    (person_id, full_name, display_name, face_embedding, face_embedding_model, active)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (person_id) DO UPDATE
                    SET face_embedding = EXCLUDED.face_embedding,
                        updated_at = NOW()
                """, (
                    person_id,
                    full_name,
                    display_name,
                    avg_embedding.tobytes(),
                    self.model_name,
                    True
                ))
                self.db.commit()

                # Update cache
                self.enrollment_cache[person_id] = {
                    'person_id': person_id,
                    'full_name': full_name,
                    'display_name': display_name,
                    'embedding': avg_embedding
                }

                logger.info(f"✓ Enrolled {person_id} ({full_name}) with {len(embeddings)} face samples")
                return True
            except Exception as e:
                logger.error(f"Database enrollment failed for {person_id}: {e}")
                return False
        else:
            # No database, just update cache
            self.enrollment_cache[person_id] = {
                'person_id': person_id,
                'full_name': full_name,
                'display_name': display_name,
                'embedding': avg_embedding
            }
            logger.info(f"✓ Enrolled {person_id} (cache only, no database)")
            return True

    def get_enrollment_count(self) -> int:
        """Get number of enrolled persons"""
        return len(self.enrollment_cache)
