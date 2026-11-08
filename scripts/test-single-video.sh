#!/bin/bash
# Test a single video through the complete Week 6 pipeline
# Usage: ./scripts/test-single-video.sh <video-path> <test-name>

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

VIDEO_PATH="$1"
TEST_NAME="${2:-test}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
RESULTS_DIR="test-results/${TEST_NAME}-${TIMESTAMP}"

if [ -z "$VIDEO_PATH" ]; then
    echo "Usage: $0 <video-path> [test-name]"
    exit 1
fi

if [ ! -f "$VIDEO_PATH" ]; then
    echo "Error: Video file not found: $VIDEO_PATH"
    exit 1
fi

mkdir -p "$RESULTS_DIR"
LOG_FILE="$RESULTS_DIR/test.log"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}║       NURA Week 6 - Single Video Pipeline Test         ║${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Video: $VIDEO_PATH" | tee -a "$LOG_FILE"
echo "Results: $RESULTS_DIR" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Test Phase 1: Health Checks
echo -e "${YELLOW}[Phase 1] Health Checks...${NC}" | tee -a "$LOG_FILE"
echo "Testing service health endpoints..." | tee -a "$LOG_FILE"

echo "  • VLM Service..." | tee -a "$LOG_FILE"
curl -s http://localhost:8001/health > "$RESULTS_DIR/vlm-health.json" 2>&1 && \
    echo -e "${GREEN}    ✓ VLM healthy${NC}" | tee -a "$LOG_FILE" || \
    echo -e "${RED}    ✗ VLM failed${NC}" | tee -a "$LOG_FILE"

echo "  • RAG Service..." | tee -a "$LOG_FILE"
curl -s http://localhost:3002/health > "$RESULTS_DIR/rag-health.json" 2>&1 && \
    echo -e "${GREEN}    ✓ RAG healthy${NC}" | tee -a "$LOG_FILE" || \
    echo -e "${RED}    ✗ RAG failed${NC}" | tee -a "$LOG_FILE"

echo "  • Rules Engine..." | tee -a "$LOG_FILE"
curl -s http://localhost:3003/health > "$RESULTS_DIR/rules-health.json" 2>&1 && \
    echo -e "${GREEN}    ✓ Rules healthy${NC}" | tee -a "$LOG_FILE" || \
    echo -e "${RED}    ✗ Rules failed${NC}" | tee -a "$LOG_FILE"

echo "  • Face Service..." | tee -a "$LOG_FILE"
curl -s http://localhost:8002/health > "$RESULTS_DIR/face-health.json" 2>&1 && \
    echo -e "${GREEN}    ✓ Face healthy${NC}" | tee -a "$LOG_FILE" || \
    echo -e "${RED}    ✗ Face failed${NC}" | tee -a "$LOG_FILE"

echo "  • Perception Service..." | tee -a "$LOG_FILE"
curl -s http://localhost:8000/health > "$RESULTS_DIR/perception-health.json" 2>&1 && \
    echo -e "${GREEN}    ✓ Perception healthy${NC}" | tee -a "$LOG_FILE" || \
    echo -e "${RED}    ✗ Perception failed${NC}" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"

# Test Phase 2: Database State
echo -e "${YELLOW}[Phase 2] Database State (Before)...${NC}" | tee -a "$LOG_FILE"

echo "  • Checking rules..." | tee -a "$LOG_FILE"
docker exec nura-postgres-1 psql -U nura -d nura_db -c \
    "SELECT COUNT(*) as rule_count FROM rules WHERE enabled = true;" \
    > "$RESULTS_DIR/rules-before.txt" 2>&1
RULE_COUNT=$(grep -E "^\s*[0-9]+" "$RESULTS_DIR/rules-before.txt" | tr -d ' ')
echo "    Found $RULE_COUNT enabled rules" | tee -a "$LOG_FILE"

echo "  • Checking violations (before)..." | tee -a "$LOG_FILE"
docker exec nura-postgres-1 psql -U nura -d nura_db -c \
    "SELECT COUNT(*) as violation_count FROM violation_events;" \
    > "$RESULTS_DIR/violations-before.txt" 2>&1
VIOLATIONS_BEFORE=$(grep -E "^\s*[0-9]+" "$RESULTS_DIR/violations-before.txt" | tr -d ' ' | head -1)
echo "    Current violations: $VIOLATIONS_BEFORE" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"

# Test Phase 3: Extract Frame and Run VLM
echo -e "${YELLOW}[Phase 3] VLM Analysis...${NC}" | tee -a "$LOG_FILE"

FRAME_PATH="$RESULTS_DIR/frame.jpg"
echo "  • Extracting frame from video..." | tee -a "$LOG_FILE"
ffmpeg -i "$VIDEO_PATH" -vframes 1 -q:v 2 "$FRAME_PATH" -y 2>&1 | grep -E "(Duration|frame=)" > "$RESULTS_DIR/ffmpeg.log" || true

if [ -f "$FRAME_PATH" ]; then
    echo -e "${GREEN}    ✓ Frame extracted${NC}" | tee -a "$LOG_FILE"

    echo "  • Running VLM analysis..." | tee -a "$LOG_FILE"
    START_TIME=$(date +%s)

    curl -X POST http://localhost:8001/analyze \
        -F "image=@$FRAME_PATH" \
        -F "prompt=Describe the scene in detail. Count people. Identify any safety concerns." \
        > "$RESULTS_DIR/vlm-response.json" 2>&1

    END_TIME=$(date +%s)
    VLM_DURATION=$((END_TIME - START_TIME))

    if [ -f "$RESULTS_DIR/vlm-response.json" ]; then
        echo -e "${GREEN}    ✓ VLM analysis complete (${VLM_DURATION}s)${NC}" | tee -a "$LOG_FILE"
        echo "    Response saved to vlm-response.json" | tee -a "$LOG_FILE"
    else
        echo -e "${RED}    ✗ VLM analysis failed${NC}" | tee -a "$LOG_FILE"
    fi
else
    echo -e "${RED}    ✗ Frame extraction failed${NC}" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"

# Test Phase 4: YOLO Detection (Perception)
echo -e "${YELLOW}[Phase 4] YOLO Detection...${NC}" | tee -a "$LOG_FILE"
echo "  • Checking perception logs for detections..." | tee -a "$LOG_FILE"

docker logs nura-nura-perception-1 2>&1 | tail -50 > "$RESULTS_DIR/perception-logs.txt"
DETECTION_COUNT=$(grep -c "Person detected" "$RESULTS_DIR/perception-logs.txt" 2>/dev/null || echo "0")
echo "    Recent person detections: $DETECTION_COUNT" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"

# Test Phase 5: Wait for threshold tracking
echo -e "${YELLOW}[Phase 5] Threshold Tracking (30s supervision rule)...${NC}" | tee -a "$LOG_FILE"
echo "  • Monitoring rules engine for 35 seconds..." | tee -a "$LOG_FILE"

for i in {1..7}; do
    echo "    Tick $i/7 (${i}0s elapsed)..." | tee -a "$LOG_FILE"
    sleep 5
done

echo "" | tee -a "$LOG_FILE"

# Test Phase 6: Check RAG Matching
echo -e "${YELLOW}[Phase 6] RAG Policy Matching...${NC}" | tee -a "$LOG_FILE"
echo "  • Checking RAG service logs..." | tee -a "$LOG_FILE"

docker logs nura-nura-rag-1 2>&1 | tail -100 > "$RESULTS_DIR/rag-logs.txt"
MATCH_COUNT=$(grep -c "similarity" "$RESULTS_DIR/rag-logs.txt" 2>/dev/null || echo "0")
echo "    RAG match queries: $MATCH_COUNT" | tee -a "$LOG_FILE"

if [ "$MATCH_COUNT" -gt 0 ]; then
    echo "  • Top matches:" | tee -a "$LOG_FILE"
    grep "similarity" "$RESULTS_DIR/rag-logs.txt" | tail -3 | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"

# Test Phase 7: Check Violations Generated
echo -e "${YELLOW}[Phase 7] Violation Detection...${NC}" | tee -a "$LOG_FILE"
echo "  • Checking violation_events table..." | tee -a "$LOG_FILE"

docker exec nura-postgres-1 psql -U nura -d nura_db -c \
    "SELECT event_id, rule_id, severity, title, similarity_score, duration_seconds, created_at
     FROM violation_events
     ORDER BY created_at DESC
     LIMIT 10;" \
    > "$RESULTS_DIR/violations-after.txt" 2>&1

VIOLATIONS_AFTER=$(docker exec nura-postgres-1 psql -U nura -d nura_db -t -c \
    "SELECT COUNT(*) FROM violation_events;" | tr -d ' ')

NEW_VIOLATIONS=$((VIOLATIONS_AFTER - VIOLATIONS_BEFORE))

if [ "$NEW_VIOLATIONS" -gt 0 ]; then
    echo -e "${GREEN}    ✓ ${NEW_VIOLATIONS} new violation(s) detected${NC}" | tee -a "$LOG_FILE"
    echo "    Details in violations-after.txt" | tee -a "$LOG_FILE"
else
    echo -e "${YELLOW}    ⚠ No new violations (may need longer wait)${NC}" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"

# Test Phase 8: Service Logs Summary
echo -e "${YELLOW}[Phase 8] Collecting Service Logs...${NC}" | tee -a "$LOG_FILE"

docker logs nura-nura-rules-1 2>&1 | tail -100 > "$RESULTS_DIR/rules-logs.txt"
docker logs nura-nura-face-1 2>&1 | tail -100 > "$RESULTS_DIR/face-logs.txt"
echo -e "${GREEN}    ✓ Logs collected${NC}" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"

# Summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}║                  Test Complete                          ║${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Results saved to: $RESULTS_DIR" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Summary:" | tee -a "$LOG_FILE"
echo "  • Active rules: $RULE_COUNT" | tee -a "$LOG_FILE"
echo "  • Violations before: $VIOLATIONS_BEFORE" | tee -a "$LOG_FILE"
echo "  • Violations after: $VIOLATIONS_AFTER" | tee -a "$LOG_FILE"
echo "  • New violations: $NEW_VIOLATIONS" | tee -a "$LOG_FILE"
if [ -n "$VLM_DURATION" ]; then
    echo "  • VLM inference time: ${VLM_DURATION}s" | tee -a "$LOG_FILE"
fi
echo "" | tee -a "$LOG_FILE"

# Create summary JSON
cat > "$RESULTS_DIR/summary.json" <<EOF
{
  "test_name": "$TEST_NAME",
  "timestamp": "$TIMESTAMP",
  "video_path": "$VIDEO_PATH",
  "results": {
    "active_rules": $RULE_COUNT,
    "violations_before": $VIOLATIONS_BEFORE,
    "violations_after": $VIOLATIONS_AFTER,
    "new_violations": $NEW_VIOLATIONS,
    "vlm_duration_seconds": ${VLM_DURATION:-0},
    "recent_detections": $DETECTION_COUNT,
    "rag_queries": $MATCH_COUNT
  }
}
EOF

echo "Summary JSON: $RESULTS_DIR/summary.json" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
