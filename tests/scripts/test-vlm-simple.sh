#!/bin/bash
# Simple VLM test without images

echo "🔍 Testing VLM Service"
echo "====================="
echo ""

echo "1. Health Check:"
docker run --rm --network nura_core_net curlimages/curl:latest -s http://nura-vlm:8001/health 2>/dev/null
echo ""

echo "2. Check Ollama Models:"
docker exec nura-ollama ollama list
echo ""

echo "3. Pull llava:7b (if not exists):"
docker exec nura-ollama ollama pull llava:7b
echo ""

echo "4. Restart VLM:"
docker compose restart nura-vlm
sleep 5

echo ""
echo "5. Check VLM logs:"
docker logs nura-nura-vlm-1 --tail=10
