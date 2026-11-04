# MLX Version Compatibility Fix

## The Issue

There's a version incompatibility between:
- `transformers` 5.8.0
- `mlx-vlm` (latest)
- `huggingface-hub` 1.13.0

Error: `ImagesKwargs.__init__() got an unexpected keyword argument 'padding'`

## Quick Fixes (Choose One)

### Option 1: Downgrade transformers (Fastest - 2 minutes)

```bash
# Use the Python with MLX installed
~/.pyenv/versions/3.13.7/bin/pip install transformers==4.45.0

# Test again
~/.pyenv/versions/3.13.7/bin/python3 test_vlm_image.py tests/images/test_classroom1.jpg
```

### Option 2: Use llama.cpp instead (Alternative - 15 minutes)

```bash
# Install llama.cpp with Metal support
brew install llama.cpp

# Download GGUF model
curl -L -o models/llava-7b-q4.gguf \
  https://huggingface.co/mys/ggml_llava-v1.5-7b/resolve/main/ggml-model-q4_k.gguf

# Test with llama.cpp
llama-cli --model models/llava-7b-q4.gguf \
  --image tests/images/test_classroom1.jpg \
  --prompt "Describe this classroom scene"
```

### Option 3: Test with Current System (Immediate)

While we fix MLX, you can test with your current Ollama setup:

```bash
# Make sure VLM service is running
docker compose up -d nura-vlm

# Test with current system
~/.pyenv/versions/3.13.7/bin/python3 test_image_simple.py tests/images/test_classroom1.jpg

# Expected: 120-180 seconds (slow, but confirms it works)
```

## Recommended Approach

**Do Option 1 right now (2 minutes):**

```bash
cd "/Users/wgomaa/Work/PixelPlusOne/Nura Childcare AI/nura-care-source"

# Fix version
~/.pyenv/versions/3.13.7/bin/pip install transformers==4.45.0

# Test
~/.pyenv/versions/3.13.7/bin/python3 test_vlm_image.py tests/images/test_classroom1.jpg

# Expected: 0.5-2.0 seconds 🚀
```

Results will be in `test_results/` folder!

---

## If Option 1 Works

You're done! Use this command going forward:

```bash
# Create alias for convenience
echo 'alias test-vlm="~/.pyenv/versions/3.13.7/bin/python3 test_vlm_image.py"' >> ~/.zshrc
source ~/.zshrc

# Now you can just use:
test-vlm tests/images/test_classroom1.jpg
```

## If Option 1 Doesn't Work

Try Option 2 (llama.cpp) - it's more stable but requires different setup.

See: `docs/QUICKSTART_M4_MAX.md` for llama.cpp instructions.

---

## Why This Happened

MLX-VLM is actively developed and has strict version requirements. The versions in your environment are slightly mismatched. This is a common issue in ML development and easy to fix!

---

**Next: Run Option 1 fix above** ⬆️
