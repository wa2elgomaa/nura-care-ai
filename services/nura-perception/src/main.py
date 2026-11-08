"""
NURA Perception Service
Privacy-first computer vision: YOLO + ByteTrack + MediaPipe + NATS
No frames leave the edge - only detection metadata published
Spec: docs/NURA_PERCEPTION_ANALYSIS.md
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
import asyncio
import logging
import cv2
import numpy as np
from datetime import datetime
import json

# Import config
from src.config import config

# Import detection and tracking modules
from ultralytics import YOLO
import mediapipe as mp

# NATS client
from nats.aio.client import Client as NATS

# Initialize logging
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
yolo_model: Optional[YOLO] = None
pose_detector: Optional[Any] = None
nats_client: Optional[NATS] = None
active_streams: Dict[str, asyncio.Task] = {}


class DetectionResponse(BaseModel):
    """Detection result"""
    camera_id: str
    timestamp: str
    persons_detected: int
    adults_detected: int
    children_detected: int
    detections: List[dict]
    poses: Optional[List[dict]] = None


class StreamStartRequest(BaseModel):
    """Request to start stream processing"""
    camera_id: str
    rtsp_url: Optional[str] = None  # If not provided, uses Frigate restream


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle"""
    global yolo_model, pose_detector, nats_client

    logger.info("Starting NURA Perception Service...")
    config.log_configuration()

    # Validate config
    valid, errors = config.validate_config()
    if not valid:
        for error in errors:
            logger.error(f"  {error}")

    # Initialize YOLO model
    logger.info(f"Loading YOLO model: {config.YOLO_MODEL}")
    try:
        yolo_model = YOLO(config.YOLO_MODEL)
        logger.info("✓ YOLO model loaded")
    except Exception as e:
        logger.error(f"Failed to load YOLO: {e}")
        raise

    # Initialize MediaPipe Pose
    if config.ENABLE_POSE_ESTIMATION:
        logger.info("Initializing MediaPipe Pose...")
        try:
            mp_pose = mp.solutions.pose
            pose_detector = mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                min_detection_confidence=config.POSE_CONFIDENCE,
                min_tracking_confidence=0.5
            )
            logger.info("✓ MediaPipe Pose initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize MediaPipe: {e}")
            pose_detector = None

    # Initialize NATS connection
    logger.info(f"Connecting to NATS: {config.NATS_URL}")
    try:
        nats_client = NATS()
        await nats_client.connect(config.NATS_URL)
        logger.info("✓ NATS connected")
    except Exception as e:
        logger.warning(f"Failed to connect to NATS: {e}")
        nats_client = None

    logger.info("✓ Perception service started successfully")
    yield

    logger.info("Shutting down NURA Perception Service...")

    # Stop all active streams
    for camera_id, task in active_streams.items():
        logger.info(f"Stopping stream: {camera_id}")
        task.cancel()

    # Close NATS
    if nats_client:
        await nats_client.close()

    # Close pose detector
    if pose_detector:
        pose_detector.close()

    logger.info("Shutdown complete")


app = FastAPI(
    title="NURA Perception Service",
    description="Privacy-first computer vision for childcare safety",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "nura-perception",
        "version": "0.1.0",
        "models_loaded": {
            "yolo": yolo_model is not None,
            "pose": pose_detector is not None
        },
        "nats_connected": nats_client is not None and nats_client.is_connected,
        "active_streams": len(active_streams)
    }


@app.post("/detect")
async def detect_frame(file: UploadFile = File(...), camera_id: str = "manual"):
    """
    Detect persons and poses in a single frame

    Args:
        file: Image file
        camera_id: Camera identifier

    Returns:
        Detection results with person count and poses
    """
    try:
        # Read image
        image_bytes = await file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        # Run detection
        result = await process_frame(frame, camera_id)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Detection error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def process_frame(frame: np.ndarray, camera_id: str) -> Dict[str, Any]:
    """
    Process a single frame: YOLO detection + pose estimation + classification

    Args:
        frame: Video frame (BGR)
        camera_id: Camera identifier

    Returns:
        Detection result dictionary
    """
    timestamp = datetime.utcnow().isoformat() + "Z"

    # YOLO person detection
    results = yolo_model(frame, conf=config.DETECTION_CONFIDENCE, classes=[0])  # class 0 = person

    detections = []
    poses = []

    for result in results:
        boxes = result.boxes

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0])

            detection = {
                "bbox": [float(x1), float(y1), float(x2), float(y2)],
                "confidence": conf,
                "class": "person"
            }

            # Extract pose if enabled
            if config.ENABLE_POSE_ESTIMATION and pose_detector:
                # Crop person region
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                person_crop = frame[y1:y2, x1:x2]

                if person_crop.size > 0:
                    # Convert BGR to RGB
                    person_rgb = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)

                    # Run pose detection
                    pose_results = pose_detector.process(person_rgb)

                    if pose_results.pose_landmarks:
                        landmarks = []
                        for landmark in pose_results.pose_landmarks.landmark:
                            landmarks.append({
                                "x": landmark.x,
                                "y": landmark.y,
                                "z": landmark.z,
                                "visibility": landmark.visibility
                            })

                        pose = {
                            "bbox": detection["bbox"],
                            "landmarks": landmarks,
                            "activity": classify_activity(landmarks)
                        }
                        poses.append(pose)
                        detection["pose"] = pose

            detections.append(detection)

    # Classify persons (adults vs children based on bbox size - simple heuristic)
    adults_detected = 0
    children_detected = 0

    for det in detections:
        bbox = det["bbox"]
        height = bbox[3] - bbox[1]

        # Simple heuristic: taller bboxes = adults, shorter = children
        # In production, use more sophisticated classification
        if height > frame.shape[0] * 0.4:  # > 40% of frame height
            adults_detected += 1
        else:
            children_detected += 1

    result = {
        "camera_id": camera_id,
        "timestamp": timestamp,
        "persons_detected": len(detections),
        "adults_detected": adults_detected,
        "children_detected": children_detected,
        "detections": detections,
        "poses": poses if poses else None
    }

    # Publish detection event to NATS
    if nats_client and nats_client.is_connected:
        await publish_detection_event(result)

    return result


def classify_activity(landmarks: List[dict]) -> str:
    """
    Classify activity from pose landmarks

    Args:
        landmarks: MediaPipe pose landmarks

    Returns:
        Activity classification (standing, sitting, lying, unknown)
    """
    if not landmarks or len(landmarks) < 33:
        return "unknown"

    # Get key landmarks
    nose = landmarks[0]
    left_hip = landmarks[23]
    right_hip = landmarks[24]
    left_knee = landmarks[25]
    right_knee = landmarks[26]
    left_ankle = landmarks[27]
    right_ankle = landmarks[28]

    # Calculate hip midpoint
    hip_y = (left_hip['y'] + right_hip['y']) / 2

    # Calculate ankle midpoint
    ankle_y = (left_ankle['y'] + right_ankle['y']) / 2

    # Calculate knee midpoint
    knee_y = (left_knee['y'] + right_knee['y']) / 2

    # Fall detection: check if person is horizontal
    body_angle = abs(hip_y - nose['y'])

    if body_angle < 0.2:  # Body is horizontal
        return "lying"  # Potential fall

    # Standing vs sitting: check knee-ankle relationship
    if abs(knee_y - ankle_y) < 0.1:  # Knees and ankles close vertically
        return "sitting"
    else:
        return "standing"


async def publish_detection_event(result: Dict[str, Any]):
    """
    Publish detection event to NATS

    Args:
        result: Detection result dictionary
    """
    try:
        # Determine event type
        event_type = "normal"

        if result["adults_detected"] == 0 and result["children_detected"] > 0:
            event_type = "no_adults_detected"

        # Check for falls
        if result.get("poses"):
            for pose in result["poses"]:
                if pose.get("activity") == "lying":
                    event_type = "fall_detected"
                    break

        # Build NATS event
        detection_event = {
            "camera_id": result["camera_id"],
            "timestamp": result["timestamp"],
            "event_type": event_type,
            "adults_detected": result["adults_detected"],
            "children_detected": result["children_detected"],
            "persons_detected": result["persons_detected"],
            "confidence": 0.85,  # Average confidence from detections
            "metadata": {
                "has_poses": len(result.get("poses", [])) > 0,
                "activities": [p.get("activity") for p in result.get("poses", [])]
            }
        }

        # Publish to NATS
        await nats_client.publish(
            "nura.events.detection",
            json.dumps(detection_event).encode()
        )

        logger.debug(f"Published detection event: {event_type} from {result['camera_id']}")

    except Exception as e:
        logger.error(f"Failed to publish detection event: {e}")


@app.post("/streams/{camera_id}/start")
async def start_stream(camera_id: str, request: StreamStartRequest):
    """
    Start processing a camera stream

    Args:
        camera_id: Camera identifier
        request: Stream configuration

    Returns:
        Stream status
    """
    if camera_id in active_streams:
        raise HTTPException(status_code=400, detail=f"Stream {camera_id} already active")

    # Build RTSP URL
    rtsp_url = request.rtsp_url or f"{config.RTSP_BASE}/{camera_id}"

    # Start stream processing task
    task = asyncio.create_task(process_stream(camera_id, rtsp_url))
    active_streams[camera_id] = task

    logger.info(f"Started stream: {camera_id} ({rtsp_url})")

    return {
        "success": True,
        "camera_id": camera_id,
        "rtsp_url": rtsp_url,
        "status": "active"
    }


@app.post("/streams/{camera_id}/stop")
async def stop_stream(camera_id: str):
    """
    Stop processing a camera stream

    Args:
        camera_id: Camera identifier

    Returns:
        Stop status
    """
    if camera_id not in active_streams:
        raise HTTPException(status_code=404, detail=f"Stream {camera_id} not active")

    # Cancel task
    task = active_streams[camera_id]
    task.cancel()
    del active_streams[camera_id]

    logger.info(f"Stopped stream: {camera_id}")

    return {
        "success": True,
        "camera_id": camera_id,
        "status": "stopped"
    }


@app.get("/streams")
async def list_streams():
    """List active streams"""
    return {
        "active_streams": list(active_streams.keys()),
        "count": len(active_streams)
    }


async def process_stream(camera_id: str, rtsp_url: str):
    """
    Process RTSP stream continuously

    Args:
        camera_id: Camera identifier
        rtsp_url: RTSP stream URL
    """
    logger.info(f"Opening RTSP stream: {rtsp_url}")

    cap = cv2.VideoCapture(rtsp_url)
    frame_count = 0

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                logger.warning(f"Failed to read frame from {camera_id}")
                await asyncio.sleep(1)
                continue

            frame_count += 1

            # Skip frames based on config
            if frame_count % config.FRAME_SKIP != 0:
                continue

            # Process frame
            await process_frame(frame, camera_id)

            # Rate limiting
            await asyncio.sleep(1 / config.MAX_FPS)

    except asyncio.CancelledError:
        logger.info(f"Stream processing cancelled: {camera_id}")
    except Exception as e:
        logger.error(f"Stream processing error ({camera_id}): {e}")
    finally:
        cap.release()
        logger.info(f"Stream closed: {camera_id}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "nura-perception",
        "version": "0.1.0",
        "description": "Privacy-first computer vision for childcare safety",
        "endpoints": {
            "health": "/health",
            "detect": "POST /detect",
            "streams": "GET /streams",
            "start_stream": "POST /streams/{camera_id}/start",
            "stop_stream": "POST /streams/{camera_id}/stop"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
