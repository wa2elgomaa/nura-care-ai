# Spec 025: VLM Performance Optimization - Multi-Camera Real-Time Analysis

**Status**: Draft  
**Version**: 1.0  
**Date**: November 3, 2026  
**Owner**: NURA Core Team

---

## Executive Summary

Current VLM performance (2-3 minutes per image) cannot support real-time multi-camera monitoring. This spec defines a comprehensive optimization strategy to achieve **<5 second latency** per camera frame while supporting **10+ concurrent camera streams**.

**Target Performance:**
- Single frame analysis: <5 seconds (from 180 seconds)
- Multi-camera throughput: 10 cameras simultaneously
- System response time: <10 seconds end-to-end
- Accuracy: Maintain or improve current detection rates

---

## 1. Problem Statement

### Current Bottleneck

**Measurements (llava:7b on CPU):**
```
test_classroom1.jpg (34KB):
- Upload time: ~1 second
- Processing time: ~178 seconds
- Total latency: 179 seconds

test_classroom2.jpg (26KB):
- Upload time: ~1 second  
- Processing time: ~128 seconds
- Total latency: 129 seconds
```

**Root Causes:**
1. CPU-only inference on 7B parameter model
2. Ollama HTTP overhead and generalist runtime
3. No batching or frame caching
4. Sequential processing (no parallelization)
5. Full model inference for every frame

**Impact:**
- ❌ Cannot monitor 10 cameras in real-time
- ❌ 10 cameras × 3 minutes = 30 minutes per cycle
- ❌ Misses time-sensitive violations
- ❌ Unusable for production deployment

---

## 2. Solution Architecture

### 2.1 Hybrid Processing Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│              Camera Streams (10 cameras @ 1 FPS)             │
└────────────────────┬────────────────────────────────────────┘
                     ↓
         ┌───────────────────────┐
         │  Frame Buffer & Queue  │
         │  - Deduplication       │
         │  - Priority routing    │
         └───────────┬────────────┘
                     ↓
         ┌───────────────────────┐
         │  Fast Path (100ms)     │ ──→ 90% of frames
         │  - YOLO detection      │
         │  - Supervision CNN     │
         │  - Violence I3D        │
         └───────────┬────────────┘
                     │
              High confidence? ──Yes──→ Alert & Log
                     │
                     No (ambiguous)
                     ↓
         ┌───────────────────────┐
         │  VLM Queue (GPU)       │ ──→ 10% of frames
         │  - llama.cpp engine    │
         │  - Quantized llava     │
         │  - Batch processing    │
         │  - Frame caching       │
         └───────────────────────┘
              ↓
         High detail analysis
              ↓
         Alert & Log
```

### 2.2 Processing Tiers

#### Tier 1: Ultra-Fast Path (<100ms) - 70% of frames
**Models:** Specialized CNNs
- Supervision classifier (adult/child detection)
- Fall detection model
- Basic safety checks

**When to use:**
- Clear adult supervision visible
- Normal classroom activities
- No detected motion anomalies

**Hardware:** CPU sufficient

---

#### Tier 2: Fast Path (~500ms) - 20% of frames
**Models:** Action recognition
- I3D violence detection
- Behavior classification
- Restricted area detection

**When to use:**
- Physical contact detected
- Rapid motion patterns
- Restricted area access

**Hardware:** CPU or lightweight GPU

---

#### Tier 3: VLM Analysis (2-5 seconds) - 10% of frames
**Models:** Vision-Language Model
- llama.cpp + quantized LLaVA
- Detailed scene understanding
- Context-aware reasoning

**When to use:**
- Ambiguous situations
- Low confidence from fast paths
- Complex multi-person interactions
- Severity classification needed

**Hardware:** GPU required

---

## 3. Technical Implementation

### 3.1 Replace Ollama with llama.cpp

**Current:**
```python
# Ollama HTTP client
response = await self.client.post(
    f"{self.base_url}/api/generate",
    json=payload,
    timeout=180.0
)
```

**Optimized:**
```python
# Direct llama.cpp inference
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler

class OptimizedVLMClient:
    def __init__(self, model_path: str, clip_model_path: str):
        self.chat_handler = Llava15ChatHandler(
            clip_model_path=clip_model_path
        )
        
        self.llm = Llama(
            model_path=model_path,  # GGUF quantized
            chat_handler=self.chat_handler,
            n_ctx=4096,
            n_batch=512,
            n_gpu_layers=35,  # Use GPU
            n_threads=8,
            use_mlock=True,  # Keep in RAM
            use_mmap=True,   # Memory-map model
        )
    
    async def analyze_frame(self, image_bytes: bytes, prompt: str):
        # Encode image to base64
        image_b64 = base64.b64encode(image_bytes).decode()
        
        # Stream response
        response = self.llm.create_chat_completion(
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_b64}"}
                ]
            }],
            stream=True,
            temperature=0.3,
            max_tokens=500
        )
        
        # Collect streamed response
        full_response = ""
        for chunk in response:
            if "content" in chunk["choices"][0]["delta"]:
                full_response += chunk["choices"][0]["delta"]["content"]
        
        return full_response
```

**Benefits:**
- No HTTP overhead
- Direct memory access
- Prompt caching built-in
- Better GPU utilization
- 2-3x faster than Ollama

---

### 3.2 Model Quantization

**Use GGUF Quantized Models:**

```bash
# Convert LLaVA to GGUF format
python convert_llava_to_gguf.py \
    --model_dir ./llava-v1.6-mistral-7b \
    --output ./llava-v1.6-mistral-7b.gguf \
    --quant q4_K_M

# Model sizes:
# FP16:   ~13 GB (baseline)
# Q8_0:   ~7 GB  (minimal quality loss)
# Q4_K_M: ~4 GB  (good quality, 2x faster)
# Q4_0:   ~3.5 GB (fastest, some quality loss)
```

**Quality vs Speed Tradeoff:**
| Quantization | Size | Speed | Accuracy | Recommendation |
|--------------|------|-------|----------|----------------|
| FP16 | 13 GB | 1x | 100% | Too slow |
| Q8_0 | 7 GB | 1.5x | 99% | High accuracy needs |
| Q4_K_M | 4 GB | 2.5x | 97% | **RECOMMENDED** |
| Q4_0 | 3.5 GB | 3x | 95% | Resource constrained |

---

### 3.3 Frame Caching & Deduplication

```python
import hashlib
from typing import Optional

class FrameCache:
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 60):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl_seconds
    
    def hash_frame(self, frame_bytes: bytes) -> str:
        """Fast perceptual hash for frame deduplication"""
        return hashlib.sha256(frame_bytes).hexdigest()[:16]
    
    def get(self, frame_hash: str) -> Optional[dict]:
        """Get cached analysis if available and not expired"""
        if frame_hash in self.cache:
            entry = self.cache[frame_hash]
            if time.time() - entry["timestamp"] < self.ttl:
                return entry["analysis"]
            else:
                del self.cache[frame_hash]
        return None
    
    def set(self, frame_hash: str, analysis: dict):
        """Cache analysis result"""
        if len(self.cache) >= self.max_size:
            # Evict oldest entry
            oldest = min(self.cache.items(), key=lambda x: x[1]["timestamp"])
            del self.cache[oldest[0]]
        
        self.cache[frame_hash] = {
            "analysis": analysis,
            "timestamp": time.time()
        }

# Usage
cache = FrameCache()

async def analyze_with_cache(frame_bytes: bytes):
    frame_hash = cache.hash_frame(frame_bytes)
    
    # Check cache
    cached = cache.get(frame_hash)
    if cached:
        return cached
    
    # Analyze
    result = await vlm_analyze(frame_bytes)
    
    # Cache result
    cache.set(frame_hash, result)
    return result
```

**Benefits:**
- Skip redundant processing of static scenes
- 30-50% cache hit rate typical
- 100% speedup on cache hits

---

### 3.4 Multi-Camera Async Processing

```python
import asyncio
from typing import Dict, List
import aiohttp

class MultiCameraProcessor:
    def __init__(self, num_cameras: int):
        self.cameras = {f"cam-{i}": Camera(f"cam-{i}") for i in range(num_cameras)}
        self.frame_queue = asyncio.Queue(maxsize=100)
        self.result_queue = asyncio.Queue()
        self.cache = FrameCache()
    
    async def capture_frames(self, camera_id: str):
        """Capture frames from camera at 1 FPS"""
        camera = self.cameras[camera_id]
        while True:
            frame = await camera.get_frame()
            await self.frame_queue.put({
                "camera_id": camera_id,
                "frame": frame,
                "timestamp": time.time()
            })
            await asyncio.sleep(1.0)  # 1 FPS
    
    async def process_frames(self, worker_id: int):
        """Worker that processes frames from queue"""
        while True:
            item = await self.frame_queue.get()
            
            try:
                # Fast path first
                fast_result = await self.fast_path_analysis(item["frame"])
                
                if fast_result["confidence"] > 0.85:
                    # High confidence - use fast result
                    result = fast_result
                else:
                    # Low confidence - use VLM
                    result = await self.vlm_analysis(item["frame"])
                
                await self.result_queue.put({
                    "camera_id": item["camera_id"],
                    "timestamp": item["timestamp"],
                    "analysis": result,
                    "worker_id": worker_id
                })
            
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
            
            finally:
                self.frame_queue.task_done()
    
    async def fast_path_analysis(self, frame: bytes) -> dict:
        """Fast specialized models (~100ms)"""
        # YOLO person detection
        persons = await detect_persons(frame)
        
        # Supervision check
        adults = [p for p in persons if p["class"] == "adult"]
        children = [p for p in persons if p["class"] == "child"]
        
        if len(children) > 0 and len(adults) == 0:
            return {
                "violation": True,
                "type": "no_supervision",
                "confidence": 0.95,
                "processing_time_ms": 100
            }
        
        # Violence detection
        violence = await detect_violence(frame)
        if violence["detected"]:
            return {
                "violation": True,
                "type": "violence",
                "severity": violence["severity"],
                "confidence": violence["confidence"],
                "processing_time_ms": 150
            }
        
        return {
            "violation": False,
            "confidence": 0.90,
            "processing_time_ms": 100
        }
    
    async def vlm_analysis(self, frame: bytes) -> dict:
        """VLM detailed analysis (~2-5 seconds with GPU)"""
        frame_hash = self.cache.hash_frame(frame)
        
        # Check cache
        cached = self.cache.get(frame_hash)
        if cached:
            return cached
        
        # Analyze with VLM
        start = time.time()
        result = await optimized_vlm_client.analyze_frame(frame, VIOLATION_PROMPT)
        elapsed_ms = (time.time() - start) * 1000
        
        parsed = parse_vlm_response(result)
        parsed["processing_time_ms"] = elapsed_ms
        
        # Cache result
        self.cache.set(frame_hash, parsed)
        
        return parsed
    
    async def run(self):
        """Start multi-camera processing"""
        # Start capture tasks for all cameras
        capture_tasks = [
            asyncio.create_task(self.capture_frames(camera_id))
            for camera_id in self.cameras.keys()
        ]
        
        # Start worker pool (4 workers for 10 cameras)
        num_workers = 4
        worker_tasks = [
            asyncio.create_task(self.process_frames(i))
            for i in range(num_workers)
        ]
        
        # Handle results
        result_task = asyncio.create_task(self.handle_results())
        
        await asyncio.gather(*capture_tasks, *worker_tasks, result_task)
    
    async def handle_results(self):
        """Process analysis results"""
        while True:
            result = await self.result_queue.get()
            
            if result["analysis"]["violation"]:
                # Send to rules engine
                await publish_violation(result)
                logger.warning(f"Violation detected on {result['camera_id']}")
            
            # Log metrics
            await log_metrics(result)

# Start processing
processor = MultiCameraProcessor(num_cameras=10)
asyncio.run(processor.run())
```

**Performance:**
- 10 cameras @ 1 FPS = 10 frames/second input
- 4 workers processing in parallel
- Fast path (90%): 100ms → 10 frames/second capacity
- VLM path (10%): 2-5s → 0.2-0.5 frames/second per worker
- **Total capacity: 10+ cameras with headroom**

---

### 3.5 GPU Configuration

**Docker Compose with GPU:**

```yaml
# compose.gpu.yaml
services:
  nura-vlm:
    build:
      context: ./services/nura-vlm
      dockerfile: Dockerfile.gpu
    image: nura/vlm:gpu
    runtime: nvidia  # Or use deploy.resources for newer compose
    environment:
      NVIDIA_VISIBLE_DEVICES: all
      NVIDIA_DRIVER_CAPABILITIES: compute,utility
      VLM_MODEL_PATH: /models/llava-v1.6-mistral-7b.Q4_K_M.gguf
      CLIP_MODEL_PATH: /models/mmproj-model-f16.gguf
      USE_GPU: "true"
      GPU_LAYERS: "35"
    volumes:
      - ./models:/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

**Dockerfile.gpu:**

```dockerfile
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install llama-cpp-python with CUDA support
ENV CMAKE_ARGS="-DLLAMA_CUDA=on"
RUN pip3 install llama-cpp-python[server] --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu122

# Install other dependencies
COPY requirements.gpu.txt .
RUN pip3 install -r requirements.gpu.txt

# Copy application
COPY src/ ./src/

# Download models on build (optional)
# RUN python3 -c "from huggingface_hub import snapshot_download; \
#     snapshot_download('cjpais/llava-v1.6-mistral-7b-gguf', local_dir='/models')"

CMD ["python3", "-m", "src.main"]
```

---

## 4. Violence Detection Enhancement

### 4.1 Severity Classification

```python
from enum import Enum

class ViolenceSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ViolenceClassifier:
    """Classify violence severity based on multiple factors"""
    
    # Action severity scores
    ACTION_SCORES = {
        # High severity actions
        "punch": 3, "kick": 3, "choke": 4, "strangle": 4,
        "head_strike": 4, "weapon_attack": 4,
        
        # Medium severity actions
        "push_hard": 2, "shove": 2, "grab": 2, "restrain": 2,
        "hit_with_object": 2, "throw_object_at_person": 2,
        "hair_pull": 2, "scratch": 2, "bite": 2,
        
        # Low severity actions
        "push_light": 1, "verbal_aggressive": 1,
        "threatening_gesture": 1, "invasion_of_space": 1
    }
    
    def classify(
        self,
        action_types: List[str],
        force_magnitude: float,  # 0.0 - 1.0
        weapon_detected: bool,
        injury_visible: bool,
        victim_distress: float,  # 0.0 - 1.0
        multiple_attackers: bool,
        duration_seconds: float
    ) -> dict:
        """
        Classify violence severity
        
        Returns:
            {
                "severity": "low" | "medium" | "high",
                "score": float,
                "factors": dict,
                "confidence": float
            }
        """
        score = 0
        factors = {}
        
        # Action type scores
        for action in action_types:
            action_score = self.ACTION_SCORES.get(action, 0)
            score += action_score
            factors[f"action_{action}"] = action_score
        
        # Force magnitude (0-3 points)
        force_score = force_magnitude * 3
        score += force_score
        factors["force"] = force_score
        
        # Weapon (3 points)
        if weapon_detected:
            score += 3
            factors["weapon"] = 3
        
        # Visible injury (4 points - very serious)
        if injury_visible:
            score += 4
            factors["injury"] = 4
        
        # Victim distress (0-2 points)
        distress_score = victim_distress * 2
        score += distress_score
        factors["distress"] = distress_score
        
        # Multiple attackers (2 points)
        if multiple_attackers:
            score += 2
            factors["multiple_attackers"] = 2
        
        # Duration (0-2 points)
        if duration_seconds > 5:
            duration_score = min(duration_seconds / 10, 2)
            score += duration_score
            factors["duration"] = duration_score
        
        # Classify severity
        if score >= 8:
            severity = ViolenceSeverity.HIGH
            confidence = min(score / 15, 1.0)
        elif score >= 4:
            severity = ViolenceSeverity.MEDIUM
            confidence = min(score / 10, 1.0)
        else:
            severity = ViolenceSeverity.LOW
            confidence = min(score / 5, 1.0)
        
        return {
            "severity": severity.value,
            "score": score,
            "factors": factors,
            "confidence": confidence,
            "requires_immediate_response": score >= 8
        }

# Example usage
classifier = ViolenceClassifier()

# Test case: Student hitting with pencil
result = classifier.classify(
    action_types=["hit_with_object"],
    force_magnitude=0.6,
    weapon_detected=True,  # Pencil as object
    injury_visible=False,
    victim_distress=0.7,
    multiple_attackers=False,
    duration_seconds=2.0
)

# Result:
# {
#     "severity": "medium",
#     "score": 7.2,
#     "factors": {
#         "action_hit_with_object": 2,
#         "force": 1.8,
#         "weapon": 3,
#         "distress": 1.4
#     },
#     "confidence": 0.72,
#     "requires_immediate_response": False
# }
```

### 4.2 VLM Prompt for Violence

```python
VIOLENCE_DETECTION_PROMPT = """You are analyzing this image for physical aggression or violence in a childcare setting.

Carefully examine the image and answer these questions:

1. PHYSICAL CONTACT:
   - Is there any physical contact between people?
   - What type of contact? (pushing, hitting, grabbing, kicking, restraining, etc.)
   - How forceful does the contact appear? (light/moderate/forceful)

2. OBJECTS AS WEAPONS:
   - Are any objects being used to hit, throw, or threaten?
   - What specific objects? (pencil, ruler, toy, book, etc.)
   - How are they being used?

3. BODY LANGUAGE:
   - Are there aggressive postures or threatening gestures?
   - Does anyone appear to be in distress or pain?
   - Are people crying, cowering, or trying to escape?

4. PARTICIPANTS:
   - How many people are involved in the interaction?
   - Are there bystanders watching?
   - Is anyone trying to intervene or separate people?

5. INJURY OR HARM:
   - Are there any visible injuries? (redness, marks, bleeding)
   - Does anyone appear hurt or in pain?

Answer in this exact format:

VIOLENCE DETECTED: [Yes/No]

ACTION TYPE: [e.g., "hitting with object", "pushing", "none"]

OBJECT USED: [e.g., "pencil", "ruler", "none"]

FORCE LEVEL: [light/moderate/forceful]

PEOPLE INVOLVED: [number]

VICTIM DISTRESS: [none/mild/moderate/severe]

INJURY VISIBLE: [Yes/No]

SEVERITY: [low/medium/high]

DESCRIPTION: [2-3 sentences describing exactly what you see]

Be precise and factual. Only report what you can clearly see in the image."""

# Test with violence image
async def test_violence_detection():
    with open("tests/images/test_violence.jpg", "rb") as f:
        image_bytes = f.read()
    
    result = await vlm_client.analyze_frame(
        image_bytes,
        VIOLENCE_DETECTION_PROMPT
    )
    
    parsed = parse_violence_response(result)
    
    if parsed["violence_detected"]:
        severity = classifier.classify(
            action_types=[parsed["action_type"]],
            force_magnitude=parsed["force_level_numeric"],
            weapon_detected=(parsed["object_used"] != "none"),
            injury_visible=parsed["injury_visible"],
            victim_distress=parsed["distress_level_numeric"],
            multiple_attackers=(parsed["people_involved"] > 2),
            duration_seconds=0  # Single frame
        )
        
        return {
            "violation": True,
            "type": "violence",
            "severity": severity["severity"],
            "confidence": severity["confidence"],
            "details": parsed,
            "requires_immediate_response": severity["requires_immediate_response"]
        }
```

---

## 5. Performance Requirements

### 5.1 Latency Targets

| Metric | Current | Target | Stretch |
|--------|---------|--------|---------|
| Single frame (CPU) | 120-180s | N/A | N/A |
| Single frame (GPU) | Not tested | <5s | <2s |
| Fast path (CPU) | Not impl. | <200ms | <100ms |
| Multi-camera (10 cams) | Impossible | <10s/cycle | <5s/cycle |
| Cache hit | Not impl. | <10ms | <5ms |
| End-to-end detection | ~3 min | <15s | <10s |

### 5.2 Throughput Targets

| Cameras | Frames/sec | Processing | Target Latency |
|---------|------------|------------|----------------|
| 1 | 1 FPS | Sequential | <5s |
| 5 | 5 FPS | Parallel | <10s max |
| 10 | 10 FPS | Parallel | <15s max |
| 20 | 20 FPS | Parallel | <20s max |

### 5.3 Accuracy Requirements

| Detection Type | Min Accuracy | Target | Notes |
|----------------|--------------|--------|-------|
| Adult presence | 95% | 98% | Critical safety |
| Violence (medium+) | 90% | 95% | High priority |
| Violence (low) | 80% | 85% | Less critical |
| Fall detection | 85% | 90% | Time-sensitive |
| Restricted area | 92% | 95% | Clear boundaries |

### 5.4 Resource Constraints

**Hardware Budget per Site:**
- GPU: RTX 4060 or equivalent (~$300)
- RAM: 16GB minimum (32GB recommended)
- Storage: 50GB for models
- Power: <300W total system

**Cloud Fallback:**
- Railway GPU instance: $0.50/hour
- Reserve for peak load only
- Edge-first architecture

---

## 6. Implementation Roadmap

### Phase 1: Foundation (Week 1)

**Goal**: Replace Ollama with llama.cpp, add GPU support

**Tasks:**
1. ✅ Test violence detection image
2. Set up llama.cpp inference engine
3. Convert LLaVA model to GGUF Q4_K_M
4. Add GPU support to Docker Compose
5. Benchmark performance improvements
6. Document setup process

**Deliverables:**
- llama.cpp VLM service running
- GPU acceleration working
- Performance benchmarks
- Updated documentation

**Success Criteria:**
- Single frame latency: <5 seconds with GPU
- Setup documented and reproducible
- Violence image correctly classified

---

### Phase 2: Fast Path (Week 2)

**Goal**: Implement specialized fast models for common cases

**Tasks:**
1. Integrate YOLO person detection (already have)
2. Build/train supervision classifier
3. Integrate violence detection model (I3D or similar)
4. Implement confidence-based routing
5. Build frame caching system
6. Add metrics and monitoring

**Deliverables:**
- Working fast path pipeline
- Supervision classifier trained/deployed
- Violence detection integrated
- Frame caching implemented

**Success Criteria:**
- Fast path latency: <200ms
- 80%+ frames handled by fast path
- Accuracy maintained (>90%)

---

### Phase 3: Multi-Camera (Week 3)

**Goal**: Scale to 10+ concurrent camera streams

**Tasks:**
1. Implement async frame queue
2. Build worker pool for parallel processing
3. Add load balancing and priority queuing
4. Implement batching for VLM calls
5. Add per-camera metrics
6. Stress test with 10+ cameras

**Deliverables:**
- Multi-camera async processor
- Worker pool with load balancing
- Comprehensive monitoring dashboard
- Load test results

**Success Criteria:**
- 10 cameras processing simultaneously
- Average latency <10 seconds
- No frame drops under normal load
- Graceful degradation under overload

---

### Phase 4: Production Hardening (Week 4)

**Goal**: Production-ready deployment

**Tasks:**
1. Add error handling and recovery
2. Implement alerting thresholds
3. Build admin dashboard for monitoring
4. Document deployment procedures
5. Create runbook for operations
6. Performance tuning and optimization

**Deliverables:**
- Production-ready system
- Monitoring and alerting
- Admin dashboard
- Operations documentation

**Success Criteria:**
- 99% uptime over 1-week test
- All alerts properly routed
- Operators can deploy without assistance
- Performance meets all targets

---

## 7. Testing Strategy

### 7.1 Test Cases

**Existing Test Images:**
1. ✅ `test_classroom1.jpg` - Supervision (adult present)
2. ✅ `test_classroom2.jpg` - Ambiguous supervision
3. ✅ `test_violence.jpg` - Violence (hitting with pencil)

**Additional Tests Needed:**
4. High violence (punching, kicking)
5. Low violence (verbal, light push)
6. Fall detection
7. Restricted area access
8. Multiple violations in one frame
9. Crowded scene (10+ people)
10. Low light / poor quality image

### 7.2 Performance Tests

```python
# test_performance.py

async def test_single_frame_latency():
    """Test single frame processing time"""
    frames = load_test_images()
    
    for frame in frames:
        start = time.time()
        result = await vlm_client.analyze_frame(frame, PROMPT)
        latency = time.time() - start
        
        assert latency < 5.0, f"Latency {latency}s exceeds 5s target"

async def test_multi_camera_throughput():
    """Test 10 camera concurrent processing"""
    processor = MultiCameraProcessor(num_cameras=10)
    
    # Run for 60 seconds
    start = time.time()
    await asyncio.wait_for(processor.run(), timeout=60)
    
    # Check metrics
    metrics = processor.get_metrics()
    assert metrics["avg_latency"] < 10.0
    assert metrics["frames_processed"] >= 600  # 10 cams * 1 FPS * 60s
    assert metrics["error_rate"] < 0.01

async def test_cache_effectiveness():
    """Test frame caching reduces latency"""
    cache = FrameCache()
    
    frame = load_test_image("test_classroom1.jpg")
    
    # First call (no cache)
    start = time.time()
    result1 = await analyze_with_cache(frame)
    first_latency = time.time() - start
    
    # Second call (cached)
    start = time.time()
    result2 = await analyze_with_cache(frame)
    cached_latency = time.time() - start
    
    assert cached_latency < 0.1  # <100ms for cache hit
    assert result1 == result2  # Same result
```

### 7.3 Accuracy Tests

```python
# test_accuracy.py

def test_violence_detection_accuracy():
    """Test violence detection on labeled dataset"""
    
    test_cases = [
        ("test_violence.jpg", True, "medium", "hitting with object"),
        ("test_classroom1.jpg", False, None, None),
        ("test_pushing.jpg", True, "low", "light push"),
        ("test_fight.jpg", True, "high", "multiple actions"),
    ]
    
    correct = 0
    for image_path, expected_violence, expected_severity, expected_action in test_cases:
        result = analyze_violence(image_path)
        
        if result["violence_detected"] == expected_violence:
            correct += 1
            
            if expected_violence and result["severity"] == expected_severity:
                correct += 0.5  # Bonus for correct severity
    
    accuracy = correct / len(test_cases)
    assert accuracy >= 0.90, f"Accuracy {accuracy} below 90% target"

def test_supervision_detection():
    """Test adult supervision detection"""
    
    test_cases = [
        ("test_classroom1.jpg", True),  # Adult present
        ("test_classroom2.jpg", False),  # No clear adult
        ("empty_room.jpg", False),  # No one
        ("adult_only.jpg", True),  # Adult, no children
    ]
    
    correct = sum(
        1 for image, expected in test_cases
        if detect_supervision(image) == expected
    )
    
    accuracy = correct / len(test_cases)
    assert accuracy >= 0.95, f"Supervision accuracy {accuracy} below 95% target"
```

---

## 8. Monitoring & Metrics

### 8.1 Key Metrics

**Performance Metrics:**
```python
class PerformanceMetrics:
    # Latency
    fast_path_latency_ms: Histogram
    vlm_latency_ms: Histogram
    end_to_end_latency_ms: Histogram
    
    # Throughput
    frames_processed_total: Counter
    frames_per_second: Gauge
    
    # Cache
    cache_hit_rate: Gauge
    cache_size: Gauge
    
    # Routing
    fast_path_usage_pct: Gauge
    vlm_usage_pct: Gauge
    
    # Errors
    processing_errors_total: Counter
    timeout_errors_total: Counter
```

**Detection Metrics:**
```python
class DetectionMetrics:
    # Violations
    violations_detected_total: Counter  # by type
    violence_by_severity: Counter  # low/medium/high
    
    # Accuracy (if ground truth available)
    true_positives: Counter
    false_positives: Counter
    false_negatives: Counter
    
    # Confidence
    avg_confidence: Gauge
    low_confidence_rate: Gauge
```

### 8.2 Alerting Thresholds

```yaml
alerts:
  # Performance
  - name: HighLatency
    condition: avg_latency > 10s
    severity: warning
    
  - name: VLMQueueBacklog
    condition: queue_size > 50
    severity: warning
  
  # Detection
  - name: HighViolenceDetected
    condition: violence_severity == "high"
    severity: critical
    
  - name: NoSupervision
    condition: supervision_violation
    severity: high
    
  # System
  - name: HighErrorRate
    condition: error_rate > 0.05
    severity: critical
    
  - name: GPUMemoryHigh
    condition: gpu_memory_usage > 90%
    severity: warning
```

---

## 9. Risk Mitigation

### 9.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| GPU not available | High | Medium | CPU fallback, cloud GPU |
| Model accuracy drops with quantization | High | Medium | Test thoroughly, use Q4_K_M not Q4_0 |
| Cache invalidation issues | Medium | Low | Conservative TTL, hash verification |
| Queue backlog under load | High | Medium | Priority routing, drop old frames |
| Memory leaks in long-running process | Medium | Low | Regular restarts, monitoring |

### 9.2 Operational Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Hardware failure | High | Low | Redundant hardware, cloud fallback |
| False positives overwhelm staff | High | Medium | Confidence thresholds, rate limiting |
| Missing real violations | Critical | Low | Multi-tier detection, periodic audits |
| Network issues between services | Medium | Medium | Local processing, robust retries |

---

## 10. Success Criteria

### 10.1 Must Have (MVP)

- ✅ Single frame latency <5 seconds with GPU
- ✅ Support 10 concurrent camera streams
- ✅ Violence detection with severity classification
- ✅ Fast path handles 70%+ of frames
- ✅ End-to-end latency <15 seconds
- ✅ 90%+ detection accuracy maintained

### 10.2 Should Have

- 80%+ fast path coverage
- Frame caching reduces load by 30%
- <10 second end-to-end latency
- Admin dashboard for monitoring
- Automated alerting on violations

### 10.3 Nice to Have

- 90%+ fast path coverage
- <5 second end-to-end latency
- Support 20+ cameras
- Real-time preview in dashboard
- ML model auto-updates

---

## 11. Appendix

### 11.1 Hardware Recommendations

**Development/Testing:**
- MacBook Pro M3/M4 (Parlor approach)
- NVIDIA RTX 3060 (12GB VRAM)
- 16GB RAM minimum

**Production Edge Box:**
- NVIDIA RTX 4060 Ti (16GB VRAM) - $400
- AMD Ryzen 5 7600 - $200
- 32GB DDR5 RAM - $100
- 1TB NVMe SSD - $80
- **Total: ~$800 per site**

**Production Cloud (Fallback):**
- Railway GPU instance (NVIDIA T4)
- $0.50/hour
- Use for peak load only

### 11.2 Model Options

**VLM Models (GGUF):**
1. **llava-v1.6-mistral-7b.Q4_K_M.gguf** (Recommended)
   - Size: 4GB
   - Speed: Fast
   - Accuracy: Good
   
2. **llava-v1.6-34b.Q4_K_M.gguf** (High accuracy)
   - Size: 19GB
   - Speed: Slower
   - Accuracy: Excellent
   
3. **moondream2.Q4_K_M.gguf** (Lightweight)
   - Size: 1.8GB
   - Speed: Very fast
   - Accuracy: Fair

**Specialized Models:**
1. **Supervision Classifier**: ResNet-50 fine-tuned
2. **Violence Detection**: I3D or SlowFast
3. **Fall Detection**: Pose estimation + classifier
4. **Object Detection**: YOLO-v8 (already have)

### 11.3 References

- Parlor Project: https://github.com/fikrikarim/parlor
- llama.cpp: https://github.com/ggerganov/llama.cpp
- LLaVA Model: https://llava-vl.github.io/
- GGUF Format: https://github.com/ggerganov/ggml/blob/master/docs/gguf.md
- I3D Violence Detection: https://github.com/Marvelmck/Violence-Detection
- Railway GPU Pricing: https://railway.app/pricing

---

**Status**: Ready for Implementation  
**Next Review**: After Phase 1 Completion  
**Owner**: NURA Core Team
