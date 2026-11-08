#!/bin/bash
# Test end-to-end event flow: NATS → Rules Engine → RAG → Violation
# Usage: ./test-event-flow.sh

set -e

echo "🧪 Testing RAG + Rules Integration (End-to-End)"
echo ""

# Test 1: Publish supervision violation event to NATS
echo "📡 [Test 1] Publishing supervision violation event to NATS..."
docker run --rm --network nura_core_net natsio/nats-box \
  nats pub nura.events.detection '{
    "camera_id": "classroom-01",
    "timestamp": "'"$(date -u +"%Y-%m-%dT%H:%M:%SZ")"'",
    "event_type": "no_adults_detected",
    "adults_detected": 0,
    "children_detected": 3,
    "confidence": 0.85,
    "metadata": {}
  }'

echo "✅ Event published"
echo ""

# Wait for processing
echo "⏳ Waiting 2 seconds for event processing..."
sleep 2

# Test 2: Check nura-rules logs
echo "📋 [Test 2] Checking nura-rules logs for event processing..."
echo ""
docker compose logs nura-rules --tail 20 | grep -E "Received detection|Processing detection|Rule matched|threshold" || echo "⚠️  No matching logs found"

echo ""
echo "📊 Current rule stats:"
curl -s http://localhost:3002/rules | jq 'length'
echo " rules loaded in RAG service"

echo ""
echo "✅ Test complete!"
echo ""
echo "Expected flow:"
echo "  1. Event published to nura.events.detection"
echo "  2. nura-rules receives event"
echo "  3. Starts tracking (30s threshold)"
echo "  4. After 30s, queries RAG for matching rules"
echo "  5. Creates violation alert if rule matches"
echo ""
echo "To test with threshold met, publish the SAME event again in 30+ seconds"
