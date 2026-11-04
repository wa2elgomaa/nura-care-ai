#!/bin/bash
# Download LLaVA GGUF model for llama.cpp

echo "Downloading LLaVA GGUF model..."
echo "Model: llava-v1.5-7b-Q4_K.gguf (~4GB)"
echo "This may take 5-10 minutes depending on your connection"
echo ""

cd "models/gguf"

# Download LLaVA model (Q4_K quantization - good balance of speed/quality)
if [ ! -f "llava-v1.5-7b-Q4_K.gguf" ]; then
    echo "Downloading model file..."
    curl -L -o llava-v1.5-7b-Q4_K.gguf \
        "https://huggingface.co/mys/ggml_llava-v1.5-7b/resolve/main/ggml-model-q4_k.gguf"
    echo "✓ Model downloaded"
else
    echo "✓ Model already exists"
fi

# Download CLIP vision model
if [ ! -f "llava-v1.5-7b-mmproj.gguf" ]; then
    echo "Downloading vision model..."
    curl -L -o llava-v1.5-7b-mmproj.gguf \
        "https://huggingface.co/mys/ggml_llava-v1.5-7b/resolve/main/mmproj-model-f16.gguf"
    echo "✓ Vision model downloaded"
else
    echo "✓ Vision model already exists"
fi

echo ""
echo "✅ Download complete!"
echo ""
echo "Models saved in: models/gguf/"
echo "- llava-v1.5-7b-Q4_K.gguf (~4GB) - Main model"
echo "- llava-v1.5-7b-mmproj.gguf (~1GB) - Vision encoder"
echo ""
echo "Next: Run test_llama_cpp.py to test performance"
