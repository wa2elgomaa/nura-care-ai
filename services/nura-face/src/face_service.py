"""
Face Recognition Service
InsightFace wrapper for face detection and recognition
"""
import numpy as np
import cv2
from typing import Optional, List, Tuple
import logging
from insightface.app import FaceAnalysis
from insightface.data import get_image as ins_get_image

logger = logging.getLogger(__name__)


class FaceService:
    """
    Face recognition service using InsightFace
    Handles detection, embedding generation, and similarity comparison
    """

    def __init__(
        self,
        model_name: str = "buffalo_l",
        enable_gpu: bool = False,
        gpu_device_id: int = 0
    ):
        """
        Initialize InsightFace model

        Args:
            model_name: InsightFace model (buffalo_l, buffalo_m, buffalo_s)
            enable_gpu: Enable GPU acceleration (CUDA)
            gpu_device_id: GPU device ID
        """
        self.model_name = model_name
        self.enable_gpu = enable_gpu
        self.gpu_device_id = gpu_device_id
        self.app: Optional[FaceAnalysis] = None

        logger.info(f"Initializing FaceService with model: {model_name}")
        self._initialize_model()

    def _initialize_model(self):
        """Initialize InsightFace model"""
        try:
            # Set device context
            ctx_id = self.gpu_device_id if self.enable_gpu else -1

            # Initialize FaceAnalysis
            self.app = FaceAnalysis(
                name=self.model_name,
                providers=['CUDAExecutionProvider', 'CPUExecutionProvider'] if self.enable_gpu else ['CPUExecutionProvider']
            )

            # Prepare model with detection size
            self.app.prepare(ctx_id=ctx_id, det_size=(640, 640))

            logger.info(f"✓ InsightFace model loaded: {self.model_name} (GPU: {self.enable_gpu})")

        except Exception as e:
            logger.error(f"Failed to initialize InsightFace: {e}")
            raise

    def detect_faces(self, image: np.ndarray) -> List[dict]:
        """
        Detect faces in image

        Args:
            image: Image array (BGR format from cv2.imread or RGB from PIL)

        Returns:
            List of detected faces with embeddings and metadata
        """
        if self.app is None:
            raise RuntimeError("FaceService not initialized")

        # Ensure image is in BGR format for InsightFace
        if len(image.shape) == 2:  # Grayscale
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        elif image.shape[2] == 4:  # RGBA
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

        # Detect faces
        faces = self.app.get(image)

        results = []
        for face in faces:
            results.append({
                "bbox": face.bbox.tolist(),  # [x1, y1, x2, y2]
                "kps": face.kps.tolist() if hasattr(face, 'kps') else None,  # 5 keypoints
                "det_score": float(face.det_score),  # Detection confidence
                "embedding": face.normed_embedding.tolist(),  # Normalized embedding (512-dim)
                "age": int(face.age) if hasattr(face, 'age') else None,
                "gender": int(face.gender) if hasattr(face, 'gender') else None
            })

        logger.debug(f"Detected {len(results)} face(s)")
        return results

    def extract_embedding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face embedding from image (single face)

        Args:
            image: Image array

        Returns:
            Face embedding vector (512-dim) or None if no face detected
        """
        faces = self.detect_faces(image)

        if len(faces) == 0:
            logger.warning("No face detected in image")
            return None

        if len(faces) > 1:
            logger.warning(f"Multiple faces detected ({len(faces)}), using largest")
            # Use face with largest bounding box
            faces = sorted(faces, key=lambda f: (f['bbox'][2] - f['bbox'][0]) * (f['bbox'][3] - f['bbox'][1]), reverse=True)

        return np.array(faces[0]['embedding'])

    def compare_embeddings(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Compare two face embeddings using cosine similarity

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score (0-1, higher = more similar)
        """
        # Normalize embeddings
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        embedding2 = embedding2 / np.linalg.norm(embedding2)

        # Cosine similarity
        similarity = np.dot(embedding1, embedding2)

        return float(similarity)

    def identify_face(
        self,
        query_embedding: np.ndarray,
        known_embeddings: List[Tuple[str, np.ndarray]],
        threshold: float = 0.6
    ) -> Optional[Tuple[str, float]]:
        """
        Identify a face by comparing against known embeddings

        Args:
            query_embedding: Query face embedding
            known_embeddings: List of (person_id, embedding) tuples
            threshold: Similarity threshold (0-1)

        Returns:
            (person_id, similarity) if match found, else None
        """
        if len(known_embeddings) == 0:
            return None

        best_match = None
        best_similarity = 0.0

        for person_id, known_embedding in known_embeddings:
            similarity = self.compare_embeddings(query_embedding, known_embedding)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = person_id

        if best_similarity >= threshold:
            logger.debug(f"Face identified: {best_match} (similarity: {best_similarity:.3f})")
            return (best_match, best_similarity)

        logger.debug(f"No match found (best: {best_similarity:.3f}, threshold: {threshold})")
        return None

    def get_embedding_dimension(self) -> int:
        """Get embedding vector dimension"""
        return 512  # InsightFace buffalo_l embedding dimension
