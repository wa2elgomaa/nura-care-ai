# Testing VLM with Your Own Images

Quick guide to test the VLM service with your own images and see the results.

---

## Quick Test (2 minutes)

### 1. Make sure VLM service is running

```bash
# Check service status
docker compose ps | grep vlm

# Should show:
# nura-vlm    Up    (or similar)

# Check health
curl http://localhost:8001/health
# Should return: {"status":"ok"}
```

### 2. Test with an image

```bash
# Test with sample image
python tools/testing/test_vlm_service.py tests/images/test_classroom1.jpg

# Test with your own image
python tools/testing/test_vlm_service.py /path/to/your/image.jpg
```

### 3. See results

Results are automatically saved in `test_results/` folder:
- **TXT file**: Human-readable analysis
- **JSON file**: Machine-readable data with timestamps

```bash
# View latest result
ls -lt test_results/ | head -5
cat test_results/test_classroom1_*.txt
```

---

## Detailed Usage

### Basic Test

```bash
python tools/testing/test_vlm_service.py <image_path>
```

**Example:**
```bash
python tools/testing/test_vlm_service.py tests/images/test_classroom1.jpg
```

**Output:**
```
======================================================================
Testing VLM Service
======================================================================
Image: test_classroom1.jpg
Path: tests/images/test_classroom1.jpg
VLM URL: http://localhost:8001

📸 Encoding image...
   ✓ Image encoded (123456 bytes)

🤖 Sending to VLM service...
   (This may take 30-180 seconds depending on your setup)

✅ Analysis complete in 45.2s

======================================================================
ANALYSIS RESULT
======================================================================

1. Supervision: Two adults present supervising 5 children (ratio 1:2.5).
   Adults are actively engaged and within arm's reach of children.

2. Physical Safety: No signs of aggression or violence observed.
   Children appear to be engaged in cooperative play.

[... detailed analysis ...]

📄 Results saved:
   TXT: test_results/test_classroom1_20261104_143052.txt
   JSON: test_results/test_classroom1_20261104_143052.json
```

### Custom Prompt

```bash
# Simple description
python tools/testing/test_vlm_service.py image.jpg "Describe this classroom scene in detail"

# Specific question
python tools/testing/test_vlm_service.py image.jpg "How many children are visible and what are they doing?"

# Safety focus
python tools/testing/test_vlm_service.py image.jpg "Is this environment safe for children? List any concerns."
```

### Test Multiple Images

Create a simple script:

```bash
# test_all_images.sh
for img in tests/images/*.jpg; do
    echo "Testing $img..."
    python tools/testing/test_vlm_service.py "$img"
    echo ""
done
```

Run it:
```bash
chmod +x test_all_images.sh
./test_all_images.sh
```

---

## Understanding Results

### TXT File Format

```
======================================================================
VLM Service Analysis Results
======================================================================

Image: test_classroom1.jpg
Path: /full/path/to/image.jpg
Timestamp: 2026-11-04T14:30:52
Processing Time: 45.2s

======================================================================
PROMPT
======================================================================

Analyze this childcare image for safety violations...

======================================================================
ANALYSIS
======================================================================

[Detailed VLM analysis here]

======================================================================
```

### JSON File Format

```json
{
  "image_path": "/full/path/to/image.jpg",
  "image_name": "test_classroom1.jpg",
  "timestamp": "2026-11-04T14:30:52",
  "processing_time_seconds": 45.2,
  "prompt": "Analyze this childcare image...",
  "analysis": "Detailed VLM analysis...",
  "model": "llava:7b",
  "status": "success"
}
```

---

## Troubleshooting

### "Cannot connect to VLM service"

**Problem:** VLM service is not running

**Solution:**
```bash
# Check if running
docker compose ps | grep vlm

# If not running, start services
docker compose -f compose.yaml -f compose.mac.yaml --env-file .env --profile app up -d

# Check logs
docker compose logs -f nura-vlm
```

### "Request timed out"

**Problem:** VLM is taking too long (>300s)

**Solution:**
```bash
# Check if Ollama is running (Mac only)
ollama ps

# If not running
ollama serve

# Increase timeout in .env
echo "VLM_TIMEOUT=300" >> .env

# Restart service
docker compose restart nura-vlm
```

### Mac: "Connection refused"

**Problem:** Native Ollama not running

**Solution:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve

# In new terminal, load model
ollama pull llava:7b

# Verify
ollama ps
```

### "Image not found"

**Problem:** Wrong path to image

**Solution:**
```bash
# Use full path
python tools/testing/test_vlm_service.py /Users/username/Pictures/image.jpg

# Or relative path from project root
python tools/testing/test_vlm_service.py ./my_images/photo.jpg
```

---

## Testing Tips

### 1. Use Good Quality Images

- **Resolution**: At least 640x480 (higher is better)
- **Format**: JPG, PNG
- **Lighting**: Clear, well-lit scenes work best
- **Focus**: Sharp, not blurry

### 2. Relevant Prompts

Good prompts for childcare testing:

```bash
# Supervision check
"Are children being supervised? What is the adult-to-child ratio?"

# Safety assessment
"Identify any safety hazards or violations in this classroom"

# Behavior analysis
"Describe the children's behavior and interactions"

# Environment check
"Is this environment appropriate for the age group shown?"

# Violence detection
"Is there any physical aggression or violence? Rate the severity."
```

### 3. Organize Your Test Images

```bash
# Create folders
mkdir -p my_test_images/{classrooms,playgrounds,violations}

# Test by category
python tools/testing/test_vlm_service.py my_test_images/classrooms/room1.jpg
python tools/testing/test_vlm_service.py my_test_images/violations/incident1.jpg
```

### 4. Compare Results

```bash
# View all results
ls -lt test_results/

# Compare two analyses
diff test_results/image1_*.txt test_results/image2_*.txt

# Search results
grep -r "MEDIUM severity" test_results/
```

---

## Performance Benchmarks

### Expected Response Times

| Platform | Single Image | Notes |
|----------|--------------|-------|
| **Mac M4 Max (native Ollama)** | 30-60s | First run may be slower |
| **Mac M4 Max (4 parallel)** | 7-15s avg | Via load balancer |
| **RTX 3080** | 10-20s | With GPU acceleration |
| **RTX 4090** | 3-8s | With GPU acceleration |

### First Run vs Subsequent

- **First run**: Slower (model loading into memory)
- **Subsequent runs**: Faster (model already loaded)

**Mac example:**
```bash
# First image: 60s
python tools/testing/test_vlm_service.py image1.jpg

# Second image: 35s (model already loaded)
python tools/testing/test_vlm_service.py image2.jpg
```

---

## Advanced: Using Load Balancer (Parallel Mode)

If you started services with `--profile vlm-parallel`:

```bash
# Test through load balancer (port 8000)
python tools/testing/test_vlm_service.py image.jpg

# Or specify load balancer URL
python -c "
import sys
sys.path.append('tools/testing')
from test_vlm_service import test_vlm_service
test_vlm_service('image.jpg', vlm_url='http://localhost:8000')
"
```

**Benefits:**
- Requests distributed across 4 VLM instances
- Faster average response time (7-15s vs 30-60s)
- Higher throughput for multiple images

---

## Batch Testing Script

Create `batch_test.py`:

```python
#!/usr/bin/env python3
import glob
import time
from pathlib import Path

# Add tools to path
import sys
sys.path.append('tools/testing')
from test_vlm_service import test_vlm_service

# Test all images in folder
images = glob.glob('my_test_images/**/*.jpg', recursive=True)

print(f"Testing {len(images)} images...")

results = []
for i, img in enumerate(images, 1):
    print(f"\n[{i}/{len(images)}] Testing {Path(img).name}")
    result = test_vlm_service(img)
    results.append(result)
    time.sleep(2)  # Brief pause between requests

print(f"\n✅ Completed {len(results)} tests")
print(f"Results saved in: test_results/")
```

Run it:
```bash
chmod +x batch_test.py
python batch_test.py
```

---

## Next Steps

1. **Test with your images**: Try the script with your own childcare photos
2. **Review results**: Check `test_results/` folder
3. **Adjust prompts**: Customize prompts for your specific needs
4. **Monitor performance**: Track processing times
5. **Scale up**: Try parallel mode for faster processing

---

## Quick Reference

```bash
# Single test
python tools/testing/test_vlm_service.py image.jpg

# Custom prompt
python tools/testing/test_vlm_service.py image.jpg "Your question here"

# Check service
curl http://localhost:8001/health

# View results
ls -lt test_results/
cat test_results/latest.txt

# Check logs
docker compose logs -f nura-vlm

# Mac: Check Ollama
ollama ps
```

---

*For more information, see [docs/TESTING.md](docs/TESTING.md)*
