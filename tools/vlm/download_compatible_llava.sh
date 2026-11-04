#!/bin/bash
# Download compatible LLaVA models for llama.cpp 0.8.0

echo "=========================================="
echo "Downloading Compatible LLaVA Models"
echo "For llama.cpp 0.8.0 with M4 Max"
echo "=========================================="
echo ""

cd models/gguf

# Try newer llava-v1.6 format which should be compatible
echo "Downloading LLaVA v1.6 models..."
echo "Model: llava-v1.6-mistral-7b"
echo ""

# Download main model (Q4_K_M quantization)
if [ ! -f "llava-v1.6-mistral-7b.Q4_K_M.gguf" ]; then
    echo "1/2: Downloading main model (~4GB)..."
    curl -L --progress-bar -o llava-v1.6-mistral-7b.Q4_K_M.gguf \
        "https://huggingface.co/cjpais/llava-v1.6-mistral-7b-gguf/resolve/main/llava-v1.6-mistral-7b.Q4_K_M.gguf"

    if [ $? -eq 0 ]; then
        echo "✓ Main model downloaded"
    else
        echo "❌ Failed to download main model"
        exit 1
    fi
else
    echo "✓ Main model already exists"
fi

echo ""

# Download mmproj (vision encoder)
if [ ! -f "llava-v1.6-mistral-7b-mmproj.gguf" ]; then
    echo "2/2: Downloading vision encoder (~600MB)..."
    curl -L --progress-bar -o llava-v1.6-mistral-7b-mmproj.gguf \
        "https://huggingface.co/cjpais/llava-v1.6-mistral-7b-gguf/resolve/main/mmproj-model-f16.gguf"

    if [ $? -eq 0 ]; then
        echo "✓ Vision encoder downloaded"
    else
        echo "❌ Failed to download vision encoder"
        exit 1
    fi
else
    echo "✓ Vision encoder already exists"
fi

echo ""
echo "=========================================="
echo "✅ Download Complete!"
echo "=========================================="
echo ""
echo "Models saved:"
echo "  - llava-v1.6-mistral-7b.Q4_K_M.gguf"
echo "  - llava-v1.6-mistral-7b-mmproj.gguf"
echo ""
echo "Total size: ~4.6GB"
echo ""
echo "Next: python test_llama_cpp_v16.py"
echo "=========================================="
