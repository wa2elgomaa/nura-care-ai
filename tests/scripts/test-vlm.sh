#!/bin/bash
# Test VLM with classroom images

echo "🔍 Testing VLM Scene Analysis"
echo "=============================="
echo ""

# Test image 1
echo "📸 Testing with classroom image 1..."
IMAGE_B64=$(base64 -i test_classroom1.jpg | tr -d '\n')

RESPONSE=$(docker run --rm --network nura_core_net curlimages/curl:latest \
  -s -X POST http://nura-vlm:8001/analyze/supervision \
  -H "Content-Type: application/json" \
  --data-binary @- <<EOF
{
  "image_base64": "$IMAGE_B64",
  "camera_id": "classroom-1"
}
EOF
)

echo "Response:"
echo "$RESPONSE" | head -500
echo ""
echo "---"
echo ""

# Test image 2
echo "📸 Testing with classroom image 2..."
IMAGE_B64_2=$(base64 -i test_classroom2.jpg | tr -d '\n')

RESPONSE2=$(docker run --rm --network nura_core_net curlimages/curl:latest \
  -s -X POST http://nura-vlm:8001/analyze/supervision \
  -H "Content-Type: application/json" \
  --data-binary @- <<EOF
{
  "image_base64": "$IMAGE_B64_2",
  "camera_id": "classroom-2"
}
EOF
)

echo "Response:"
echo "$RESPONSE2" | head -500
