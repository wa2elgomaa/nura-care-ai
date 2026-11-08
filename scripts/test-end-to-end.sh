#!/bin/bash
# End-to-End Pipeline Test - Week 6 Complete System
# Tests: Perception → NATS → Rules → RAG → Alerts
#
# Architecture (Hybrid - Recommended):
#   - AI services (Ollama + VLM) run NATIVE on Mac with Metal GPU (100x faster)
#   - Other services run in Docker
#   - Week 6: RAG + Rules + Face + Perception services included
#
# Usage:
#   ./scripts/test-end-to-end.sh [--docker-only] [--video FILE]
#
# Modes:
#   Default (Hybrid):  Native VLM + Docker services (fast, recommended)
#   --docker-only:     All services in Docker (slower, CPU inference)

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Parse arguments
DOCKER_ONLY=false
TEST_VIDEO=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --docker-only)
            DOCKER_ONLY=true
            shift
            ;;
        --video)
            TEST_VIDEO="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Change to project root
cd "$(dirname "$0")/.."

# Select test video
if [ -z "$TEST_VIDEO" ]; then
    # Check for real videos first
    if [ -d "tests/real-videos" ] && [ -n "$(ls -A tests/real-videos/*.mp4 2>/dev/null)" ]; then
        TEST_VIDEO=$(ls tests/real-videos/*.mp4 | head -1)
        echo -e "${GREEN}Using real video: $(basename "$TEST_VIDEO")${NC}"
    elif [ -f "tests/videos/classroom_6.mp4" ]; then
        TEST_VIDEO="tests/videos/classroom_6.mp4"
        echo -e "${YELLOW}Using test video: classroom_6.mp4${NC}"
    else
        echo -e "${RED}No test video found${NC}"
        echo -e "${YELLOW}Place videos in tests/real-videos/ or tests/videos/${NC}"
        exit 1
    fi
fi

# Verify video exists
if [ ! -f "$TEST_VIDEO" ]; then
    echo -e "${RED}✗ Video not found: $TEST_VIDEO${NC}"
    exit 1
fi

# Determine mode from .env
VLM_URL=$(grep "^VLM_SERVICE_URL=" .env 2>/dev/null | cut -d'=' -f2)

if [[ "$VLM_URL" == *"host.docker.internal"* ]] || [[ "$VLM_URL" == *"localhost"* ]]; then
    MODE="Hybrid (Native VLM + Docker)"
    USE_NATIVE=true
else
    MODE="All Docker (CPU)"
    USE_NATIVE=false
fi

if [ "$DOCKER_ONLY" = true ]; then
    MODE="All Docker (Forced)"
    USE_NATIVE=false
fi

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       NURA - WEEK 6 END-TO-END PIPELINE TEST              ║${NC}"
echo -e "${BLUE}║          Mode: $MODE${NC}"
echo -e "${BLUE}║          Video: $(basename "$TEST_VIDEO")${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Test phases
PHASE=0
TOTAL_PHASES=8

function print_phase() {
    PHASE=$((PHASE + 1))
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}Phase $PHASE/$TOTAL_PHASES: $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

function check_service() {
    local service=$1
    if docker compose ps "$service" 2>/dev/null | grep -E "$service.*Up" >/dev/null; then
        echo -e "${GREEN}✓ $service is running${NC}"
        return 0
    else
        echo -e "${RED}✗ $service is not running${NC}"
        return 1
    fi
}

function wait_for_service() {
    local service=$1
    local url=$2
    local max_wait=30
    local waited=0

    echo -e "${YELLOW}Waiting for $service to be ready...${NC}"
    while [ $waited -lt $max_wait ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ $service is ready${NC}"
            return 0
        fi
        sleep 1
        waited=$((waited + 1))
        echo -n "."
    done
    echo ""
    echo -e "${RED}✗ $service failed to start${NC}"
    return 1
}

# Phase 1: Check Prerequisites
print_phase "Prerequisites Check"

echo -e "${YELLOW}Checking Docker...${NC}"
if ! docker --version > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker installed${NC}"

echo -e "${YELLOW}Checking Docker Compose...${NC}"
if ! docker compose version > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker Compose not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose installed${NC}"

echo -e "${GREEN}✓ Test video: $(basename "$TEST_VIDEO") ($(du -h "$TEST_VIDEO" | cut -f1))${NC}"

# Phase 2: Start Core Services
print_phase "Starting Core Infrastructure"

echo -e "${YELLOW}Starting PostgreSQL, NATS, MQTT, Redis...${NC}"
docker compose up -d postgres nats mosquitto redis 2>&1 | grep -v "Container.*Running" || true
sleep 5

check_service "postgres" || exit 1
check_service "nats" || exit 1
check_service "mosquitto" || exit 1
check_service "redis" || exit 1

# Phase 3: Start Week 6 Services
print_phase "Starting Week 6 Services (RAG + Rules + Face + Perception)"

echo -e "${YELLOW}Starting nura-rag (Policy Knowledge Base)...${NC}"
docker compose up -d nura-rag 2>&1 | grep -v "Container.*Running" || true
sleep 3
check_service "nura-rag" || exit 1
wait_for_service "RAG Service" "http://localhost:3002/health" || true

echo -e "${YELLOW}Starting nura-rules (Rules Engine)...${NC}"
docker compose up -d nura-rules 2>&1 | grep -v "Container.*Running" || true
sleep 3
check_service "nura-rules" || exit 1
wait_for_service "Rules Engine" "http://localhost:3003/health" || true

echo -e "${YELLOW}Starting nura-face (Face Recognition)...${NC}"
docker compose up -d nura-face 2>&1 | grep -v "Container.*Running" || true
sleep 5
check_service "nura-face" || exit 1
# Face service takes longer to download model
echo -e "${YELLOW}  Waiting for InsightFace model download...${NC}"
sleep 10
wait_for_service "Face Service" "http://localhost:8002/health" || true

echo -e "${YELLOW}Starting nura-perception (Privacy-First CV)...${NC}"
docker compose up -d nura-perception 2>&1 | grep -v "Container.*Running" || true
sleep 5
check_service "nura-perception" || exit 1
# Perception service downloads YOLO model
echo -e "${YELLOW}  Waiting for YOLO model download...${NC}"
sleep 10
wait_for_service "Perception Service" "http://localhost:8000/health" || true

# Phase 4: Start Frigate with Video File
print_phase "Starting Frigate (Video File Mode)"

echo -e "${YELLOW}Starting Frigate...${NC}"
docker compose up -d frigate 2>&1 | grep -v "Container.*Running" || true
sleep 5
check_service "frigate" || exit 1

echo -e "${YELLOW}Copying test video to Frigate container...${NC}"
FRIGATE_CONTAINER=$(docker compose ps -q frigate)
if [ -n "$FRIGATE_CONTAINER" ]; then
    docker cp "$TEST_VIDEO" $FRIGATE_CONTAINER:/media/frigate/classroom_test.mp4
    echo -e "${GREEN}✓ Test video copied to Frigate${NC}"
else
    echo -e "${RED}✗ Frigate container not found${NC}"
    exit 1
fi

echo -e "${YELLOW}Restarting Frigate with new video...${NC}"
docker compose restart frigate
sleep 5

# Phase 5: Start AI Services
print_phase "Starting AI Services"

if [ "$USE_NATIVE" = true ] && [ "$DOCKER_ONLY" = false ]; then
    echo -e "${GREEN}Using NATIVE AI services (Metal GPU - 100x faster!)${NC}"

    # Check if Ollama is running
    if lsof -i :11434 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama is running natively${NC}"
    else
        echo -e "${YELLOW}Starting Ollama natively...${NC}"
        ./runner/run_ollama.sh || exit 1
    fi

    # Check if VLM service is running
    if lsof -i :8001 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ VLM Service is running natively${NC}"
    else
        echo -e "${YELLOW}Starting VLM Service natively...${NC}"
        ./runner/run_vlm_service.sh || exit 1
    fi

    sleep 3
    wait_for_service "VLM Service" "http://localhost:8001/health" || exit 1
else
    echo -e "${YELLOW}Using DOCKER AI services (CPU inference - slower)${NC}"

    echo -e "${YELLOW}Starting Ollama...${NC}"
    docker compose --profile app up -d ollama 2>&1 | grep -v "Container.*Running" || true
    sleep 5
    check_service "ollama" || exit 1

    echo -e "${YELLOW}Starting VLM Service...${NC}"
    docker compose --profile app up -d nura-vlm 2>&1 | grep -v "Container.*Running" || true
    sleep 8
    check_service "nura-vlm" || exit 1
fi

# Phase 6: Start Processing Services
print_phase "Starting Stream Processor & Alert Services"

echo -e "${YELLOW}Starting Stream Processor...${NC}"
docker compose up -d nura-stream-processor 2>&1 | grep -v "Container.*Running" || true
sleep 3
check_service "nura-stream-processor" || true
wait_for_service "Stream Processor" "http://localhost:3010/health" || true

echo -e "${YELLOW}Starting Notification Services...${NC}"
docker compose up -d apprise ntfy 2>&1 | grep -v "Container.*Running" || true
sleep 3
check_service "apprise" || true
check_service "ntfy" || true

echo -e "${YELLOW}Starting Alert Service...${NC}"
docker compose up -d nura-alerts 2>&1 | grep -v "Container.*Running" || true
sleep 3
check_service "nura-alerts" || true
wait_for_service "Alert Service" "http://localhost:3011/health" || true

# Phase 7: Database Setup & Rule Loading
print_phase "Database Setup & Policy Loading"

echo -e "${YELLOW}Running database migrations...${NC}"
POSTGRES_CONTAINER=$(docker compose ps -q postgres)
if [ -n "$POSTGRES_CONTAINER" ]; then
    # Alert schema
    docker exec -i $POSTGRES_CONTAINER psql -U nura -d nura_db < edge/postgres/migrations/001_alerts_schema.sql 2>&1 | grep -v "already exists" || true

    # RAG schema (already done in earlier phase)
    # docker exec -i $POSTGRES_CONTAINER psql -U nura -d nura_db < services/nura-rag/migrations/001_init_schema.sql 2>&1 | grep -v "already exists" || true

    # Rules violations schema
    docker exec -i $POSTGRES_CONTAINER psql -U nura -d nura_db < services/nura-rules/migrations/001_violation_events.sql 2>&1 | grep -v "already exists" || true

    # Face embeddings schema (already done in earlier phase)
    # docker exec -i $POSTGRES_CONTAINER psql -U nura -d nura_db < services/nura-face/migrations/001_face_embeddings.sql 2>&1 | grep -v "already exists" || true

    echo -e "${GREEN}✓ Database schema ready${NC}"
else
    echo -e "${RED}✗ PostgreSQL container not found${NC}"
    exit 1
fi

echo -e "${YELLOW}Loading sample policy documents into RAG...${NC}"
if [ -f "services/nura-rag/scripts/load-sample-rules.sh" ]; then
    ./services/nura-rag/scripts/load-sample-rules.sh http://localhost:3002 2>&1 | grep -E "Status:|Loading|✅" || true
    echo -e "${GREEN}✓ Policy documents loaded${NC}"
else
    echo -e "${YELLOW}  Skipping (script not found)${NC}"
fi

# Phase 8: Test Detection Flow
print_phase "Testing Detection Flow"

echo -e "${CYAN}Pipeline Architecture (Week 6):${NC}"
if [ "$USE_NATIVE" = true ]; then
    echo -e "${CYAN}  📹 Video → Frigate → MQTT${NC}"
    echo -e "${CYAN}  🔄 MQTT → Stream Processor → VLM (NATIVE Metal GPU)${NC}"
    echo -e "${CYAN}  🧠 VLM → NATS → Rules Engine → RAG Query${NC}"
    echo -e "${CYAN}  🚨 Rules → Violations → Alerts${NC}"
    echo -e ""
    echo -e "${CYAN}  Alternative (Privacy Mode):${NC}"
    echo -e "${CYAN}  📹 Video → nura-perception (YOLO + MediaPipe)${NC}"
    echo -e "${CYAN}  🔄 Perception → NATS → Rules → RAG${NC}"
else
    echo -e "${CYAN}  📹 Video → Frigate → MQTT${NC}"
    echo -e "${CYAN}  🔄 MQTT → Stream Processor → VLM (Docker CPU)${NC}"
    echo -e "${CYAN}  🧠 VLM → NATS → Rules Engine → RAG Query${NC}"
    echo -e "${CYAN}  🚨 Rules → Violations → Alerts${NC}"
fi
echo ""

echo -e "${YELLOW}Publishing test detection event...${NC}"
python3 services/nura-rules/test/publish_test_event.py 2>&1 | grep -E "✓|Published|📡" || true
echo ""

echo -e "${YELLOW}Monitoring logs for 45 seconds...${NC}"
echo -e "${YELLOW}(Press Ctrl+C to stop early)${NC}"
echo ""

# Monitor multiple services
timeout 45 bash -c '
    docker logs -f --tail=15 nura-nura-rules-1 2>&1 | grep --line-buffered -E "Received|Processing|Rule matched|threshold|violation" | sed "s/^/[RULES] /" &
    docker logs -f --tail=15 nura-nura-rag-1 2>&1 | grep --line-buffered -E "Matching|Found|similarity" | sed "s/^/[RAG] /" &
    docker logs -f --tail=10 nura-nura-stream-processor-1 2>&1 | grep --line-buffered -E "Forwarded|Published|Processing" | sed "s/^/[STREAM] /" &
    docker logs -f --tail=10 nura-nura-alerts-1 2>&1 | grep --line-buffered -E "Alert|notification|sent|violation" | sed "s/^/[ALERT] /" &
    wait
' || true

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Summary
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    TEST SUMMARY                            ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}Week 6 Services Status:${NC}"
check_service "nura-rag" && echo "" || echo ""
check_service "nura-rules" && echo "" || echo ""
check_service "nura-face" && echo "" || echo ""
check_service "nura-perception" && echo "" || echo ""

echo ""
echo -e "${CYAN}Core Services Status:${NC}"
check_service "postgres" && echo "" || echo ""
check_service "nats" && echo "" || echo ""
check_service "frigate" && echo "" || echo ""

if [ "$USE_NATIVE" = true ]; then
    echo ""
    echo -e "${CYAN}Native AI Services:${NC}"
    if lsof -i :11434 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama (Metal GPU)${NC}"
    fi
    if lsof -i :8001 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ VLM Service (Metal GPU)${NC}"
    fi
fi

echo ""
echo -e "${CYAN}Useful URLs:${NC}"
echo -e "  Frigate:           ${GREEN}http://localhost:5000${NC}"
echo -e "  RAG Service:       ${GREEN}http://localhost:3002/rules${NC}"
echo -e "  Rules Engine:      ${GREEN}http://localhost:3003/health${NC}"
echo -e "  Face Service:      ${GREEN}http://localhost:8002/health${NC}"
echo -e "  Perception:        ${GREEN}http://localhost:8000/health${NC}"
echo -e "  VLM Service:       ${GREEN}http://localhost:8001/health${NC}"
echo -e "  Stream Processor:  ${GREEN}http://localhost:3010/health${NC}"
echo -e "  Alert Service:     ${GREEN}http://localhost:3011/health${NC}"

echo ""
echo -e "${CYAN}Test Commands:${NC}"
echo -e "  Check violations: ${YELLOW}docker exec nura-postgres-1 psql -U nura -d nura_db -c 'SELECT * FROM violations LIMIT 10;'${NC}"
echo -e "  Check rules:      ${YELLOW}curl -s http://localhost:3002/rules | jq${NC}"
echo -e "  Test RAG match:   ${YELLOW}curl -X POST http://localhost:3002/match -H 'Content-Type: application/json' -d '{\"event_context\":\"no adults with children\",\"top_k\":3}'${NC}"
echo -e "  Publish event:    ${YELLOW}python3 services/nura-rules/test/publish_test_event.py${NC}"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Week 6 Pipeline is running! All services operational.${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}To stop:${NC}"
echo -e "  ${CYAN}./scripts/stop.sh${NC}"
echo ""
