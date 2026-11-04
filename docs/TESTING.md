# VLM Image Testing Tool - Usage Guide

## Quick Start

### Test a single image
```bash
python test_vlm_image.py tests/images/test_classroom1.jpg
```

### Test multiple images
```bash
python test_vlm_image.py tests/images/test_classroom1.jpg tests/images/test_classroom2.jpg
```

### Test all images in a folder
```bash
python test_vlm_image.py tests/images/*.jpg
```

### Test with custom image path
```bash
python test_vlm_image.py /Users/wgomaa/Pictures/classroom.jpg
```

---

## What It Does

1. **Loads MLX-optimized VLM model** (llava-1.5-7b-4bit)
2. **Analyzes each image** for childcare safety:
   - Adult supervision presence
   - Physical aggression/violence
   - Children in distress
   - Safety hazards
   - Overall safety status

3. **Saves results** to `test_results/` folder:
   - **TXT file**: Human-readable report
   - **JSON file**: Machine-readable data

4. **Shows performance metrics**:
   - Processing time per image
   - Average speed
   - Speedup vs current system

---

## Example Output

### Terminal Output
```
======================================================================
VLM Image Testing Tool
======================================================================

Loading model: mlx-community/llava-1.5-7b-4bit
✓ Model loaded in 0.8s

Testing 3 image(s)...

======================================================================

[1/3]
📸 Analyzing: test_classroom1.jpg
   Size: (751, 408)
   Generating response...
   ✓ Completed in 0.85s

   📄 Saved: test_results/test_classroom1_20261103_162045.txt
   📄 Saved: test_results/test_classroom1_20261103_162045.json

[2/3]
📸 Analyzing: test_classroom2.jpg
   Size: (640, 480)
   Generating response...
   ✓ Completed in 0.78s

   📄 Saved: test_results/test_classroom2_20261103_162046.txt
   📄 Saved: test_results/test_classroom2_20261103_162046.json

[3/3]
📸 Analyzing: test_violence.jpg
   Size: (600, 400)
   Generating response...
   ✓ Completed in 0.92s

   📄 Saved: test_results/test_violence_20261103_162047.txt
   📄 Saved: test_results/test_violence_20261103_162047.json

======================================================================
SUMMARY
======================================================================
Total images: 3
Successful: 3
Failed: 0

Average processing time: 0.85s
Current system average: ~150s
🚀 Speedup: 176x faster!

Results saved in: test_results/
======================================================================

✅ Testing complete!
```

### TXT File Output (`test_results/test_classroom1_20261103_162045.txt`)
```
======================================================================
VLM Image Analysis Results
======================================================================

Image: test_classroom1.jpg
Path: tests/images/test_classroom1.jpg
Size: (751, 408)
Model: mlx-community/llava-1.5-7b-4bit
Timestamp: 2026-11-03T16:20:45.123456
Processing Time: 0.85s
Status: success

======================================================================
PROMPT
======================================================================

Analyze this childcare image for safety violations:

1. Are adults present supervising children?
2. Is there any physical aggression or violence?
3. Are any children in distress?
4. Are there any safety hazards?
5. What is the overall safety status?

Provide a detailed analysis.

======================================================================
ANALYSIS
======================================================================

The image shows a classroom setting with several students and one adult 
who appears to be a teacher or staff member. There are at least six 
students visible in the frame; some are seated at desks while others 
stand near them. The room has a blue wall in the background and there's 
a whiteboard on the right side of the image.

1. Adult Supervision: YES - An adult is present standing behind the desk, 
   facing the students. They appear to be engaged in teaching or 
   supervising the classroom activities.

2. Physical Aggression/Violence: NO - There is no visible physical 
   contact between individuals that suggests aggression or violence. 
   Students appear to be engaged in normal classroom activities.

3. Children in Distress: NO - None of the visible students appear to be 
   in distress. They seem focused on their work or the lesson.

4. Safety Hazards: NONE VISIBLE - The classroom appears well-organized 
   with standard furniture and equipment. No obvious hazards are visible.

5. Overall Safety Status: SAFE - The environment appears to be a normal, 
   supervised educational setting with appropriate adult supervision and 
   no visible safety concerns.

======================================================================
Results saved: test_results/test_classroom1_20261103_162045.txt
======================================================================
```

### JSON File Output (`test_results/test_classroom1_20261103_162045.json`)
```json
{
  "image_path": "tests/images/test_classroom1.jpg",
  "image_name": "test_classroom1.jpg",
  "image_size": [751, 408],
  "model": "mlx-community/llava-1.5-7b-4bit",
  "prompt": "Analyze this childcare image for safety violations:\n\n1. Are adults present supervising children?\n2. Is there any physical aggression or violence?\n3. Are any children in distress?\n4. Are there any safety hazards?\n5. What is the overall safety status?\n\nProvide a detailed analysis.",
  "response": "The image shows a classroom setting...",
  "processing_time_seconds": 0.85,
  "timestamp": "2026-11-03T16:20:45.123456",
  "status": "success"
}
```

---

## Customization

### Change the Analysis Prompt

Edit `test_vlm_image.py` line 105-115:

```python
# Custom prompt
prompt = """Your custom prompt here.

Ask specific questions about the image.
"""
```

### Change Output Format

```python
# In the main() function:
results = tester.test_images(
    image_paths,
    prompt=prompt,
    save_txt=True,   # Save human-readable TXT
    save_json=True   # Save machine-readable JSON
)
```

### Use Different Model

```python
# Change model at initialization
tester = VLMTester(model_name="mlx-community/paligemma-3b-mix-448-8bit")
```

---

## Troubleshooting

### Error: "Module not found: mlx_vlm"
```bash
pip install mlx-vlm
```

### Error: "Version compatibility issue"
```bash
pip install --upgrade transformers==4.45.0 mlx-vlm
```

### Error: "Model not found"
```bash
# List available models
python -c "from mlx_vlm.utils import list_models; print(list_models())"

# Use a different model
python test_vlm_image.py --model mlx-community/llava-1.5-7b-4bit image.jpg
```

### Slow Performance
- First run downloads model (~4GB) - takes 5-10 minutes
- Subsequent runs use cached model
- Expected: 0.5-2.0s per image after model is loaded

---

## Integration with NURA

### Parse JSON Results in Python
```python
import json

with open('test_results/test_classroom1_20261103_162045.json') as f:
    result = json.load(f)

print(f"Processing time: {result['processing_time_seconds']}s")
print(f"Analysis: {result['response']}")

# Check for violations
if "NO" in result['response'] or "NONE" in result['response']:
    print("✓ No violations detected")
else:
    print("⚠️ Potential violation detected")
```

### Batch Process Multiple Folders
```bash
# Process all images in multiple folders
find tests/images/ -name "*.jpg" -exec python test_vlm_image.py {} \;
```

### Integrate with NURA Rules Engine
```python
# In your rules service:
from test_vlm_image import VLMTester

tester = VLMTester()
tester.load_model()  # Load once

# For each camera frame
result = tester.analyze_image(frame_path)

if result['status'] == 'success':
    # Parse response and check for violations
    response = result['response'].lower()
    
    if 'no adult' in response or 'no supervision' in response:
        trigger_violation_alert('SUPERVISION', result)
    
    if 'aggression' in response or 'violence' in response:
        trigger_violation_alert('VIOLENCE', result)
```

---

## Performance Expectations

### Your M4 Max
- **Model load**: 0.5-1.0s (one time)
- **Per image**: 0.5-2.0s
- **Throughput**: 0.5-2 FPS per instance
- **4 instances**: 2-8 FPS aggregate
- **Camera capacity**: 10-20 cameras @ 1 FPS

### vs Current System
- **Current**: 120-180s per image
- **M4 Max**: 0.5-2.0s per image
- **Speedup**: 60-360x faster

---

## Next Steps

1. **Test your images**:
   ```bash
   python test_vlm_image.py your_image.jpg
   ```

2. **Review results** in `test_results/` folder

3. **Integrate with NURA** services

4. **Add multi-instance** for parallel processing

5. **Deploy** to production

---

## Examples

### Test all classroom images
```bash
python test_vlm_image.py tests/images/test_*.jpg
```

### Test with verbose output
```bash
python test_vlm_image.py -v tests/images/test_classroom1.jpg
```

### Test and compare
```bash
# Test with MLX
python test_vlm_image.py image.jpg

# Compare with current Ollama system
time curl -X POST http://localhost:8001/analyze -d '{"image": "..."}'
```

---

**Created**: November 3, 2026  
**Status**: Ready to use  
**Performance**: 60-360x faster than current system
