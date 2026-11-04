# VLM Performance Optimization Plan

**Current Status**: 2-3 minutes per image (llava:7b on CPU)  
**Target**: <5 seconds per image for real-time multi-camera processing  
**Date**: November 3, 2026

---

## 🚨 Current Bottleneck Analysis

### Problem: 3 Minutes Per Image is Unacceptable

**Current Setup:**
- Model: llava:7b (4.7 GB)
- Hardware: CPU-only inference
- Time: 120-180 seconds per image
- Deployment: Ollama in Docker container

**Why It's Slow:**
1. **No GPU Acceleration**: Running 7B parameter model on CPU
2. **Model Size**: 4.7 GB model requires significant compute
3. **Ollama Overhead**: General-purpose runtime not optimized for edge deployment
4. **Sequential Processing**: One image at a time, no batching

**Impact on Multi-Camera:**
- 10 cameras × 3 minutes = 30 minutes to process one frame from each camera
- Real-time monitoring impossible
- Violates <5 second detection requirement

---

## 🎯 Optimization Options

### Option 1: GPU Acceleration (Fastest - Recommended)

**Approach**: Add NVIDIA GPU support to Ollama

**Expected Performance:**
- llava:7b: ~3-5 seconds per image
- llava:13b: ~5-10 seconds per image
- **10-20x speedup**

**Hardware Requirements:**
- NVIDIA GPU (RTX 3060/4060 or better)
- 8GB+ VRAM for llava:7b
- 12GB+ VRAM for llava:13b
- NVIDIA Container Toolkit

**Implementation:**
```yaml
# compose.gpu.yaml
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

**Cost:**
- Edge Box GPU: ~$300-500 (one-time)
- Cloud GPU (Railway): ~$0.50/hour
- **Best ROI for production deployment**

**Pros:**
- ✅ Massive speedup (10-20x)
- ✅ Keep existing architecture
- ✅ Support multiple cameras easily
- ✅ Better model quality (can use 13b)

**Cons:**
- ❌ Hardware cost
- ❌ Power consumption (~200W)

---

### Option 2: Smaller/Faster Models

**Approach**: Switch to smaller vision models

**Candidates:**
1. **llava:7b-v1.6** (optimized variant)
2. **bakllava:7b** (faster llava variant)
3. **moondream2** (1.8B parameters - very fast)
4. **CLIP + GPT-2** (lightweight, specialized)

**Expected Performance:**
- moondream2: ~30-60 seconds on CPU
- CLIP pipeline: ~10-20 seconds on CPU

**Implementation:**
```bash
# Test moondream2
docker exec nura-ollama ollama pull moondream2
# Update VLM_MODEL=moondream2 in .env
```

**Pros:**
- ✅ No hardware changes needed
- ✅ Faster inference (2-3x improvement)
- ✅ Lower memory footprint

**Cons:**
- ⚠️ Reduced accuracy
- ⚠️ Still too slow for real-time
- ❌ May miss subtle violations

---

### Option 3: Native Python Inference (LlamaCPP/GGUF)

**Approach**: Replace Ollama with optimized inference engines

**Options:**
1. **llama.cpp** - Optimized C++ inference, GGUF quantization
2. **vLLM** - High-throughput serving
3. **TensorRT-LLM** - NVIDIA optimized
4. **ONNX Runtime** - Cross-platform optimization

**Expected Performance:**
- llama.cpp + quantization: ~60-90 seconds on CPU
- With GPU: ~2-4 seconds

**Implementation:**
```python
# Replace Ollama client with llama-cpp-python
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler

chat_handler = Llava15ChatHandler(clip_model_path="clip-model.gguf")
llm = Llama(
    model_path="llava-7b-q4.gguf",  # Quantized model
    chat_handler=chat_handler,
    n_ctx=2048,
    n_gpu_layers=35  # Use GPU layers if available
)
```

**Pros:**
- ✅ Better performance than Ollama
- ✅ Quantization support (4-bit, 8-bit)
- ✅ Lower memory usage
- ✅ More control over inference

**Cons:**
- ⚠️ Requires code rewrite
- ⚠️ Model conversion needed
- ⚠️ Still benefits most from GPU

---

### Option 4: Specialized Vision Models

**Approach**: Use task-specific models instead of general VLM

**Architecture:**
```
Camera Frame
    ↓
YOLO (people detection) ← Already have this
    ↓
Supervision Classifier (lightweight CNN)
    ↓
Violence Detection (action recognition model)
    ↓
VLM (only for complex cases)
```

**Models:**
1. **Supervision**: Simple ResNet classifier (adult vs child)
2. **Violence**: I3D or SlowFast action recognition
3. **VLM**: Only for ambiguous cases

**Expected Performance:**
- YOLO: ~50ms (already running)
- Supervision classifier: ~10ms
- Violence detection: ~100-200ms
- VLM fallback: 2-3 minutes (rare)

**Implementation:**
```python
# Fast path: no VLM needed
if person_count > 0:
    adults = supervision_classifier(crops)
    if len(adults) == 0:
        return "VIOLATION: No adult supervision"
    
# Violence detection
actions = violence_detector(frame_sequence)
if actions.max_confidence > 0.7:
    severity = classify_violence_severity(actions)
    return f"VIOLATION: Violence detected - {severity}"

# Only use VLM for ambiguous cases
if confidence < 0.7:
    return vlm_analyze(frame)  # Slow but accurate
```

**Pros:**
- ✅ Very fast (<500ms total)
- ✅ Purpose-built for our use case
- ✅ Can run on CPU
- ✅ Lower cost

**Cons:**
- ⚠️ Requires training custom models
- ⚠️ Less flexible than VLM
- ⚠️ May need labeled data

---

### Option 5: Edge AI Accelerators

**Approach**: Use specialized AI hardware

**Options:**
1. **NVIDIA Jetson** (Nano/Xavier/Orin)
2. **Google Coral TPU**
3. **Intel Neural Compute Stick**
4. **Hailo-8 AI Processor**

**Expected Performance:**
- Jetson Orin: ~2-3 seconds (llava:7b)
- Coral TPU: ~50-100ms (specialized models)
- Hailo-8: ~100-200ms (specialized models)

**Best for Edge Deployment:**
```
Jetson Orin NX (16GB)
- Cost: ~$500
- Power: 15-25W
- Performance: 100 TOPS
- Perfect for edge boxes
```

**Pros:**
- ✅ Low power consumption
- ✅ Purpose-built for AI inference
- ✅ Good price/performance
- ✅ Edge-optimized

**Cons:**
- ⚠️ Hardware cost per site
- ⚠️ May need model optimization
- ⚠️ ARM architecture considerations

---

## 🔍 Parlor Project Analysis - Key Learnings

### What Parlor Does Right

**Performance Achievement:**
- **0.7-1.5 seconds** end-to-end response time on Apple M3 Pro
- Runs **Gemma 4E2B** (4GB model) via **llama.cpp**
- Multimodal (audio + vision) with sub-second latency

**Key Techniques We Can Adopt:**

1. **llama.cpp Instead of Ollama**
   - Direct inference engine (no HTTP overhead)
   - Prompt caching for speed
   - Quantized models (q4_0) for efficiency
   - Better control over inference parameters

2. **Prompt Caching Strategy**
   - Pre-process frames while other tasks run
   - Cache image embeddings to avoid recomputation
   - Reuse context across similar queries

3. **Streaming Architecture**
   - Don't wait for full response
   - Start processing as soon as first tokens arrive
   - Pipeline multiple stages

4. **Quantization**
   - 4-bit quantized models (q4_0)
   - 2-3x faster inference
   - 50% memory reduction
   - Minimal accuracy loss

5. **Right-Sized Models**
   - Gemma 4E2B (4GB) vs llava:7b (4.7GB)
   - Similar size, optimized for edge
   - Task-specific is better than general-purpose

### Applying to NURA

**Immediate Opportunities:**

1. **Replace Ollama with llama.cpp**
   ```python
   # Instead of: ollama HTTP API
   # Use: llama-cpp-python with GGUF models
   from llama_cpp import Llama
   from llama_cpp.llama_chat_format import Llava15ChatHandler
   
   # Load quantized model
   llm = Llama(
       model_path="llava-v1.6-mistral-7b.Q4_K_M.gguf",
       chat_handler=Llava15ChatHandler(clip_model_path="..."),
       n_ctx=4096,
       n_batch=512,
       n_gpu_layers=35,  # Offload to GPU if available
       n_threads=8,  # CPU threads
   )
   ```

2. **Frame Caching**
   ```python
   # Cache processed frames to avoid reprocessing
   frame_cache = {}
   
   def get_cached_embedding(frame_hash):
       if frame_hash in frame_cache:
           return frame_cache[frame_hash]
       embedding = process_frame(frame)
       frame_cache[frame_hash] = embedding
       return embedding
   ```

3. **Async Pipeline**
   ```python
   # Process multiple cameras concurrently
   async def process_camera_stream(camera_id):
       while True:
           frame = await get_frame(camera_id)
           # Non-blocking analysis
           asyncio.create_task(analyze_frame(frame))
   ```

**Expected Improvement:**
- llama.cpp: **2-3x faster** than Ollama
- Quantization: **2x faster** inference
- GPU: **10x faster** than CPU
- **Combined: 5-10 seconds → <1 second per frame**

---

## 🎯 Recommended Architecture

### Hybrid Approach: Fast Path + VLM Fallback

```
┌─────────────────────────────────────────────────────────┐
│                   Camera Frame (30 FPS)                  │
└────────────────────┬────────────────────────────────────┘
                     ↓
         ┌───────────────────────┐
         │  YOLO Person Detection │  ~50ms
         │  (Already Running)     │
         └───────────┬────────────┘
                     ↓
         ┌───────────────────────┐
         │  Fast Classifiers      │  ~100ms
         │  - Supervision (CNN)   │
         │  - Violence (I3D)      │
         │  - Fall Detection      │
         └───────────┬────────────┘
                     ↓
              ┌──────────┐
              │ High     │ Yes ──→ Alert + Log
              │ Confidence?│
              └──────┬───┘
                     │ No (ambiguous)
                     ↓
         ┌───────────────────────┐
         │  VLM Analysis          │  2-3 sec
         │  (GPU-accelerated)     │  (queued)
         │  - llava:7b on GPU     │
         └───────────────────────┘
```

**Key Features:**
1. **Fast Path** (150ms): Handle 95% of cases with specialized models
2. **VLM Fallback**: High accuracy for complex/ambiguous scenes
3. **GPU for VLM only**: Cost-effective hardware use
4. **Async Processing**: Don't block real-time stream

**Expected Performance:**
- Fast path: <200ms (95% of frames)
- VLM fallback: 2-3 seconds (5% of frames)
- Multi-camera: 10 cameras × 200ms = 2 seconds for all

---

## 📊 Violence Severity Classification

### Severity Levels

**Low Severity:**
- Pushing without force
- Verbal argument (loud voices)
- Play fighting (detected as rough play)
- Accidental contact

**Medium Severity:**
- Intentional pushing with force
- Grabbing/restraining
- Throwing objects at person
- Hair pulling
- **Hitting with object (pencil, ruler, etc.)** ← Your test case

**High Severity:**
- Punching/kicking with force
- Choking/strangulation
- Use of weapons
- Multiple attackers
- Head injuries

### Implementation

```python
class ViolenceSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

def classify_violence_severity(
    action_type: str,
    force_magnitude: float,
    weapon_detected: bool,
    injury_visible: bool,
    multiple_attackers: bool
) -> ViolenceSeverity:
    """
    Classify violence severity based on multiple factors
    """
    score = 0
    
    # Action type
    if action_type in ["punch", "kick", "choke"]:
        score += 3
    elif action_type in ["push_hard", "grab", "hit_with_object"]:
        score += 2
    elif action_type in ["push_light", "verbal"]:
        score += 1
    
    # Force
    if force_magnitude > 0.8:
        score += 2
    elif force_magnitude > 0.5:
        score += 1
    
    # Weapon
    if weapon_detected:
        score += 2
    
    # Injury
    if injury_visible:
        score += 3
    
    # Multiple attackers
    if multiple_attackers:
        score += 1
    
    # Classify
    if score >= 6:
        return ViolenceSeverity.HIGH
    elif score >= 3:
        return ViolenceSeverity.MEDIUM
    else:
        return ViolenceSeverity.LOW
```

### VLM Prompt for Violence Detection

```python
VIOLENCE_DETECTION_PROMPT = """Analyze this image for physical aggression or violence.

Look for:
1. Physical contact between people (pushing, hitting, kicking, grabbing)
2. Objects being used as weapons (pencils, rulers, toys, etc.)
3. Aggressive body language or threatening postures
4. Visible distress or pain in any person
5. Multiple people involved in confrontation

Answer these questions:
1. Is there any physical aggression or violence? (Yes/No)
2. What specific actions are occurring? (be precise)
3. Are any objects being used? (specify what)
4. How many people are involved?
5. Does anyone appear injured or in distress?
6. Severity level: Low / Medium / High

Be factual and specific. Describe exactly what you see."""
```

---

## 🚀 Implementation Plan

### Phase 1: Quick Wins (This Week)

**1. Test Smaller Models**
```bash
# Try faster models on current hardware
ollama pull moondream2
ollama pull bakllava
# Benchmark each
```

**2. Add Violence Test Case**
- Test image downloaded: `tests/images/test_violence.jpg`
- Add violence detection prompt
- Implement severity classification
- Validate detection

**3. Profile Current Performance**
- Measure exact bottlenecks
- Token generation speed
- Image encoding time
- Network latency

### Phase 2: GPU Acceleration (Next Week)

**1. Add GPU Support to Ollama**
```yaml
# compose.gpu.yaml
services:
  ollama:
    image: ollama/ollama:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
```

**2. Benchmark GPU Performance**
- Test llava:7b with GPU
- Test llava:13b with GPU
- Measure speedup

**3. Multi-Camera Load Testing**
- Simulate 10 concurrent camera streams
- Test queuing and batching
- Measure throughput

### Phase 3: Hybrid Architecture (2 Weeks)

**1. Build Fast Classifiers**
- Train supervision classifier
- Integrate violence detection model
- Test accuracy vs VLM

**2. Implement Smart Routing**
- Fast path for high-confidence cases
- VLM queue for ambiguous cases
- Async processing pipeline

**3. Production Deployment**
- Edge box with GPU
- Multi-camera testing
- Real-world validation

---

## 💰 Cost Analysis

### Option Comparison

| Option | Hardware Cost | Performance | Multi-Camera | Recommendation |
|--------|--------------|-------------|--------------|----------------|
| **CPU Only** | $0 | ❌ 3 min | ❌ No | Testing only |
| **GPU (RTX 4060)** | $300 | ✅ 3-5 sec | ✅ Yes (10+ cameras) | **BEST** |
| **Smaller Models** | $0 | ⚠️ 60 sec | ⚠️ Limited (2-3) | Budget option |
| **Native Inference** | $0 (+GPU: $300) | ✅ 2-4 sec | ✅ Yes | Advanced |
| **Specialized Models** | $0 | ✅✅ <500ms | ✅✅ Yes (20+) | Production |
| **Jetson Orin** | $500/site | ✅ 2-3 sec | ✅ Yes | Edge deployment |
| **Hybrid** | $300 | ✅✅ 200ms avg | ✅✅ Yes (20+) | **RECOMMENDED** |

---

## 🎯 Final Recommendation

### Best Approach: Hybrid Fast Path + GPU VLM

**Why:**
1. **Fast**: 200ms average latency (fast classifiers)
2. **Accurate**: VLM fallback for complex cases
3. **Scalable**: Handle 10+ cameras easily
4. **Cost-effective**: One GPU serves all cameras
5. **Future-proof**: Can upgrade models as needed

**Implementation Steps:**
1. ✅ **Immediate**: Test violence detection with current setup
2. 🔧 **Week 1**: Add GPU support to Ollama (RTX 4060)
3. 🚀 **Week 2**: Implement fast classifiers for supervision/violence
4. 🎯 **Week 3**: Deploy hybrid architecture with smart routing
5. 📊 **Week 4**: Multi-camera load testing and optimization

**Expected Results:**
- 95% of frames: <200ms (fast path)
- 5% of frames: 2-3 seconds (VLM on GPU)
- Support for 10-20 concurrent cameras
- Total system latency: <5 seconds target **ACHIEVED**

---

**Next Steps:**
1. Test violence detection image
2. Research GPU options for edge box
3. Benchmark fast classification models
4. Build prototype hybrid pipeline
