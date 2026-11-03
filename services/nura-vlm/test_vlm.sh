#!/bin/bash
# Test VLM Service
# Usage: ./test_vlm.sh [base64-image-file]

set -e

VLM_URL="${VLM_URL:-http://localhost:8001}"

echo "Testing NURA VLM Service at $VLM_URL"
echo "======================================="
echo

# Test 1: Health Check
echo "1. Testing health endpoint..."
curl -s "$VLM_URL/health" | jq '.'
echo

# Test 2: List prompts
echo "2. Listing available prompts..."
curl -s "$VLM_URL/prompts" | jq '.prompts | keys'
echo

# Test 3: Analyze with test image (if provided)
if [ -n "$1" ]; then
    echo "3. Analyzing test image: $1"

    if [ ! -f "$1" ]; then
        echo "Error: File not found: $1"
        exit 1
    fi

    # Base64 encode the image
    IMAGE_B64=$(base64 < "$1" | tr -d '\n')

    # Create request
    cat > /tmp/vlm_request.json <<EOF
{
  "image_base64": "$IMAGE_B64",
  "prompt": "Analyze this classroom scene. Are there any adults present? How many children? What are they doing?",
  "camera_id": "test-camera",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

    echo "Sending request to /analyze..."
    curl -s -X POST "$VLM_URL/analyze" \
        -H "Content-Type: application/json" \
        -d @/tmp/vlm_request.json | jq '.'

    echo
    echo "4. Testing supervision quick check..."
    curl -s -X POST "$VLM_URL/analyze/supervision?camera_id=test-camera" \
        -H "Content-Type: application/json" \
        -d "{\"image_base64\": \"$IMAGE_B64\"}" | jq '.'

    rm /tmp/vlm_request.json
else
    echo "3. Skipping image analysis (no test image provided)"
    echo "   Usage: $0 <path-to-test-image.jpg>"
fi

echo
echo "✓ VLM service test complete"
