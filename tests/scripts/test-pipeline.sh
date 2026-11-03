#!/bin/bash
# NURA Pipeline Integration Test
# Tests: VLM → RAG → Rules Engine → Violation Detection

set -e

echo "🧪 NURA Pipeline Integration Test"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Service URLs (use Docker network names)
VLM_URL="${VLM_URL:-http://nura-vlm:8001}"
RAG_URL="${RAG_URL:-http://nura-rag:3002}"
RULES_URL="${RULES_URL:-http://nura-rules:3003}"

# Run tests from inside a container on the core_net network
DOCKER_CMD="docker run --rm --network nura_core_net curlimages/curl:latest"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
test_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

test_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

test_info() {
    echo -e "${YELLOW}ℹ INFO${NC}: $1"
}

# Test 1: Check all services are healthy
echo "Test 1: Service Health Checks"
echo "------------------------------"

# VLM Service
VLM_HEALTH=$($DOCKER_CMD -s "$VLM_URL/health" 2>/dev/null || echo '{"status":"error"}')
if echo "$VLM_HEALTH" | grep -q '"status":"healthy"' || echo "$VLM_HEALTH" | grep -q '"status":"degraded"'; then
    test_pass "VLM service is responding"
else
    test_fail "VLM service is not healthy"
fi

# RAG Service
RAG_HEALTH=$($DOCKER_CMD -s "$RAG_URL/health" 2>/dev/null || echo '{"status":"error"}')
if echo "$RAG_HEALTH" | grep -q '"status":"healthy"'; then
    test_pass "RAG service is healthy"
else
    test_fail "RAG service is not healthy"
fi

# Rules Engine
RULES_HEALTH=$($DOCKER_CMD -s "$RULES_URL/health" 2>/dev/null || echo '{"status":"error"}')
if echo "$RULES_HEALTH" | grep -q '"status":"healthy"'; then
    test_pass "Rules engine is healthy"
else
    test_fail "Rules engine is not healthy"
fi

echo ""

# Test 2: RAG - Rule Matching
echo "Test 2: RAG Rule Matching"
echo "-------------------------"

test_info "Querying RAG for supervision violation..."

RAG_RESPONSE=$($DOCKER_CMD -s -X POST "$RAG_URL/match" \
    -H "Content-Type: application/json" \
    -d '{"event_context": "children need adult supervision no adults present", "category": "supervision", "top_k": 3, "similarity_threshold": 0.5}' 2>/dev/null || echo '{}')

# Check if we got matches
MATCH_COUNT=$(echo "$RAG_RESPONSE" | jq '.matches | length')
if [ "$MATCH_COUNT" -gt 0 ]; then
    test_pass "RAG returned $MATCH_COUNT matching rules"

    # Check top match
    TOP_RULE=$(echo "$RAG_RESPONSE" | jq -r '.matches[0].rule_id')
    SIMILARITY=$(echo "$RAG_RESPONSE" | jq -r '.matches[0].similarity')
    test_info "Top match: $TOP_RULE (similarity: $SIMILARITY)"

    if [ "$TOP_RULE" = "RULE-001" ]; then
        test_pass "Correct rule matched (RULE-001 - Supervision)"
    else
        test_fail "Expected RULE-001, got $TOP_RULE"
    fi

    # Check similarity threshold
    if (( $(echo "$SIMILARITY > 0.5" | bc -l) )); then
        test_pass "Similarity score above threshold ($SIMILARITY > 0.5)"
    else
        test_fail "Similarity score too low ($SIMILARITY <= 0.5)"
    fi
else
    test_fail "RAG returned no matches"
fi

QUERY_TIME=$(echo "$RAG_RESPONSE" | jq -r '.query_time_ms')
test_info "Query time: ${QUERY_TIME}ms"

if [ "$QUERY_TIME" -lt 100 ]; then
    test_pass "RAG query time under 100ms target"
else
    test_info "RAG query time ${QUERY_TIME}ms (target: <100ms)"
fi

echo ""

# Test 3: VLM - Scene Analysis (if test image provided)
echo "Test 3: VLM Scene Analysis"
echo "---------------------------"

if [ -f "test_classroom.jpg" ]; then
    test_info "Testing VLM with test_classroom.jpg..."

    IMAGE_B64=$(base64 < test_classroom.jpg | tr -d '\n')

    VLM_START=$(date +%s%3N)
    VLM_RESPONSE=$(curl -s -X POST "$VLM_URL/analyze/supervision" \
        -H "Content-Type: application/json" \
        -d "{\"image_base64\": \"$IMAGE_B64\", \"camera_id\": \"test-camera\"}")
    VLM_END=$(date +%s%3N)
    VLM_TIME=$((VLM_END - VLM_START))

    if echo "$VLM_RESPONSE" | jq -e '.analysis' > /dev/null 2>&1; then
        test_pass "VLM analysis completed"

        ANALYSIS=$(echo "$VLM_RESPONSE" | jq -r '.analysis' | head -c 100)
        test_info "Analysis: $ANALYSIS..."

        if [ "$VLM_TIME" -lt 2000 ]; then
            test_pass "VLM response time under 2s target (${VLM_TIME}ms)"
        else
            test_info "VLM response time ${VLM_TIME}ms (target: <2000ms)"
        fi
    else
        test_fail "VLM analysis failed"
    fi
else
    test_info "Skipping VLM test (no test_classroom.jpg found)"
    test_info "Create a test image: curl -o test_classroom.jpg 'https://via.placeholder.com/640x480.jpg?text=Classroom'"
fi

echo ""

# Test 4: Rules Engine - Detection Event Processing
echo "Test 4: Rules Engine - Detection Event"
echo "---------------------------------------"

test_info "Sending detection event via NATS..."

# Check if NATS is accessible
if command -v docker &> /dev/null; then
    NATS_RESULT=$(docker run --rm --network nura_core_net natsio/nats-box nats pub nura.events.detection '{
        "camera_id": "test-camera",
        "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
        "event_type": "no_adults_detected",
        "children_detected": 2,
        "adults_detected": 0,
        "confidence": 0.95
    }' 2>&1)

    if echo "$NATS_RESULT" | grep -q "Published"; then
        test_pass "Detection event published to NATS"
        test_info "Event tracking started (waiting for 30s threshold)"
    else
        test_fail "Failed to publish to NATS: $NATS_RESULT"
    fi
else
    test_info "Skipping NATS test (Docker not available)"
fi

echo ""

# Test 5: Check Violations Were Created
echo "Test 5: Violations Storage"
echo "--------------------------"

test_info "Checking for stored violations..."

VIOLATIONS=$(curl -s "$RULES_URL/violations?limit=10")
VIOLATION_COUNT=$(echo "$VIOLATIONS" | jq '. | length')

test_info "Found $VIOLATION_COUNT violations in database"

if [ "$VIOLATION_COUNT" -gt 0 ]; then
    test_pass "Violations are being stored"

    # Show latest violation
    LATEST=$(echo "$VIOLATIONS" | jq -r '.[0]')
    EVENT_ID=$(echo "$LATEST" | jq -r '.event_id')
    RULE_ID=$(echo "$LATEST" | jq -r '.rule_id')
    SEVERITY=$(echo "$LATEST" | jq -r '.severity')

    test_info "Latest violation: $EVENT_ID ($RULE_ID - $SEVERITY)"
else
    test_info "No violations yet (this is normal if threshold not met)"
fi

echo ""

# Test 6: Database Schema Check
echo "Test 6: Database Schema"
echo "-----------------------"

if command -v docker &> /dev/null; then
    # Check rules table
    RULES_COUNT=$(docker compose exec -T postgres psql -U nura -d nura -tAc "SELECT COUNT(*) FROM rules" 2>/dev/null || echo "0")

    if [ "$RULES_COUNT" -gt 0 ]; then
        test_pass "Rules table has $RULES_COUNT rules"
    else
        test_fail "Rules table is empty or doesn't exist"
    fi

    # Check pgvector extension
    PGVECTOR_CHECK=$(docker compose exec -T postgres psql -U nura -d nura -tAc "SELECT 1 FROM pg_extension WHERE extname='vector'" 2>/dev/null || echo "")

    if [ "$PGVECTOR_CHECK" = "1" ]; then
        test_pass "pgvector extension is installed"
    else
        test_fail "pgvector extension not found"
    fi

    # Check violation_events table exists
    VIOLATIONS_TABLE=$(docker compose exec -T postgres psql -U nura -d nura -tAc "SELECT 1 FROM information_schema.tables WHERE table_name='violation_events'" 2>/dev/null || echo "")

    if [ "$VIOLATIONS_TABLE" = "1" ]; then
        test_pass "violation_events table exists"
    else
        test_fail "violation_events table not found"
    fi
else
    test_info "Skipping database tests (Docker not available)"
fi

echo ""

# Test 7: End-to-End Latency
echo "Test 7: End-to-End Latency Check"
echo "---------------------------------"

test_info "Simulating full pipeline latency..."

E2E_START=$(date +%s%3N)

# Step 1: RAG query (simulate rule matching)
RAG_LATENCY=$(curl -s -X POST "$RAG_URL/match" \
    -H "Content-Type: application/json" \
    -d '{"event_context": "children alone"}' \
    -w "%{time_total}" -o /dev/null)

E2E_END=$(date +%s%3N)
E2E_TIME=$((E2E_END - E2E_START))

test_info "RAG query: ${RAG_LATENCY}s"
test_info "Total E2E simulation: ${E2E_TIME}ms"

# Note: Real E2E includes threshold tracking (30s) + processing (~2s)
ESTIMATED_TOTAL=$((30000 + E2E_TIME))
test_info "Estimated full pipeline: ${ESTIMATED_TOTAL}ms (~30s threshold + ${E2E_TIME}ms processing)"

if [ "$E2E_TIME" -lt 10000 ]; then
    test_pass "Processing time under 10s target (excluding threshold wait)"
else
    test_info "Processing time: ${E2E_TIME}ms"
fi

echo ""

# Summary
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Pipeline Status: ✅ OPERATIONAL"
    echo ""
    echo "Next steps:"
    echo "  1. Monitor logs: docker compose logs -f nura-vlm nura-rag nura-rules"
    echo "  2. Test with real camera: Connect to Frigate RTSP stream"
    echo "  3. Build nura-notifier: Complete the alert delivery"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check service logs: docker compose logs <service-name>"
    echo "  2. Verify all services running: docker compose ps"
    echo "  3. Check database: docker compose exec postgres psql -U nura -d nura"
    exit 1
fi
