#!/bin/bash
# End-to-End Pipeline Test
# Tests complete flow: Video File → Frigate → MQTT → Stream Processor → VLM → Alerts
#
# Architecture (Hybrid - Recommended):
#   - AI services (Ollama + VLM) run NATIVE on Mac with Metal GPU (100x faster)
#   - Other services run in Docker
#   - Containers reach native services via host.docker.internal
#
# Usage:
#   ./scripts/test-end-to-end.sh [--docker-only]
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
if [ "$1" = "--docker-only" ]; then
    DOCKER_ONLY=true
fi

# Change to project root
cd "$(dirname "$0")/.."

# Determine mode from .env
VLM_URL=$(grep "^VLM_SERVICE_URL=" .env 2>/dev/null | cut -d'=' -f2)
OLLAMA_URL=$(grep "^OLLAMA_URL=" .env 2>/dev/null | cut -d'=' -f2)

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
echo -e "${BLUE}║       NURA - END-TO-END PIPELINE TEST                     ║${NC}"
echo -e "${BLUE}║          Mode: $MODE${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Test phases
PHASE=0
TOTAL_PHASES=7

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
    # Check if container exists and status shows "Up"
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

echo -e "${YELLOW}Checking test video...${NC}"
TEST_VIDEO="tests/videos/classroom_6.mp4"
if [ ! -f "$TEST_VIDEO" ]; then
    echo -e "${RED}✗ Test video not found: $TEST_VIDEO${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Test video found: $(basename $TEST_VIDEO)${NC}"

# Phase 2: Start Core Services
print_phase "Starting Core Infrastructure"

echo -e "${YELLOW}Starting PostgreSQL, NATS, MQTT...${NC}"
docker compose up -d postgres nats mosquitto 2>&1 | grep -v "Container.*Running" || true

sleep 5

check_service "postgres" || exit 1
check_service "nats" || exit 1
check_service "mosquitto" || exit 1

# Phase 3: Start Frigate with Video File
print_phase "Starting Frigate (Video File Mode)"

echo -e "${YELLOW}Copying test video to Frigate container...${NC}"
# First ensure Frigate container exists
docker compose up -d frigate 2>&1 | grep -v "Container.*Running" || true
sleep 3

# Copy video file into Frigate
FRIGATE_CONTAINER=$(docker compose ps -q frigate)
if [ -n "$FRIGATE_CONTAINER" ]; then
    docker cp "$TEST_VIDEO" $FRIGATE_CONTAINER:/media/frigate/classroom_6.mp4
    echo -e "${GREEN}✓ Test video copied to Frigate${NC}"
else
    echo -e "${RED}✗ Frigate container not found${NC}"
    exit 1
fi

echo -e "${YELLOW}Restarting Frigate with new video...${NC}"
docker compose restart frigate
sleep 5
check_service "frigate" || exit 1

# Phase 4: Start AI Services
print_phase "Starting AI Services"

if [ "$USE_NATIVE" = true ] && [ "$DOCKER_ONLY" = false ]; then
    echo -e "${GREEN}Using NATIVE AI services (Metal GPU - 100x faster!)${NC}"
    echo ""

    # Check if Ollama is running
    if lsof -i :11434 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama is running natively${NC}"
    else
        echo -e "${YELLOW}Starting Ollama natively...${NC}"
        ./runner/run_ollama.sh || {
            echo -e "${RED}✗ Failed to start Ollama${NC}"
            echo -e "${YELLOW}Run manually: ./runner/run_ollama.sh${NC}"
            exit 1
        }
    fi

    # Check if VLM service is running
    if lsof -i :8001 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ VLM Service is running natively${NC}"
    else
        echo -e "${YELLOW}Starting VLM Service natively...${NC}"
        ./runner/run_vlm_service.sh || {
            echo -e "${RED}✗ Failed to start VLM Service${NC}"
            echo -e "${YELLOW}Run manually: ./runner/run_vlm_service.sh${NC}"
            exit 1
        }
    fi

    # Wait for services to be ready
    sleep 3
    if curl -s http://localhost:8001/health >/dev/null 2>&1; then
        echo -e "${GREEN}✓ VLM Service health check passed${NC}"
    else
        echo -e "${RED}✗ VLM Service health check failed${NC}"
        echo -e "${YELLOW}Check logs: tail -f logs/vlm-service.log${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Using DOCKER AI services (CPU inference - slower)${NC}"
    echo ""

    echo -e "${YELLOW}Starting Ollama...${NC}"
    docker compose --profile app up -d ollama 2>&1 | grep -v "Container.*Running" || true
    sleep 5
    check_service "ollama" || exit 1

    echo -e "${YELLOW}Starting VLM Service...${NC}"
    docker compose --profile app up -d nura-vlm 2>&1 | grep -v "Container.*Running" || true
    sleep 8

    if check_service "nura-vlm"; then
        echo -e "${GREEN}✓ VLM Service is running${NC}"
    else
        echo -e "${RED}✗ VLM Service failed to start${NC}"
        echo -e "${YELLOW}Check logs: docker logs nura-nura-vlm-1${NC}"
        exit 1
    fi
fi

# Phase 5: Start Processing Services
print_phase "Starting Stream Processor & Alert Services"

echo -e "${YELLOW}Starting Stream Processor...${NC}"
docker compose up -d nura-stream-processor 2>&1 | grep -v "Container.*Running" || true
sleep 3

if check_service "nura-stream-processor"; then
    wait_for_service "Stream Processor" "http://localhost:3010/health" || true
fi

echo -e "${YELLOW}Starting Notification Services...${NC}"
docker compose up -d apprise ntfy 2>&1 | grep -v "Container.*Running" || true
sleep 3

check_service "apprise" || true
check_service "ntfy" || true

echo -e "${YELLOW}Starting Alert Service...${NC}"
docker compose up -d nura-alerts 2>&1 | grep -v "Container.*Running" || true
sleep 3

if check_service "nura-alerts"; then
    wait_for_service "Alert Service" "http://localhost:3011/health" || true
fi

# Phase 6: Run Database Migrations
print_phase "Database Setup"

echo -e "${YELLOW}Running alert schema migration...${NC}"
POSTGRES_CONTAINER=$(docker compose ps -q postgres)
if [ -n "$POSTGRES_CONTAINER" ]; then
    docker exec -i $POSTGRES_CONTAINER psql -U nura -d nura_db < edge/postgres/migrations/001_alerts_schema.sql 2>&1 | grep -v "already exists" || true
    echo -e "${GREEN}✓ Database schema ready${NC}"
else
    echo -e "${RED}✗ PostgreSQL container not found${NC}"
    exit 1
fi

# Phase 7: Monitor Pipeline
print_phase "Monitoring Pipeline Activity"

if [ "$USE_NATIVE" = true ]; then
    echo -e "${CYAN}Pipeline Flow (Hybrid):${NC}"
    echo -e "${CYAN}  📹 Video File → Frigate (CPU detection) → MQTT${NC}"
    echo -e "${CYAN}  🔄 MQTT → Stream Processor (Docker) → NATS${NC}"
    echo -e "${CYAN}  🤖 Stream Processor → VLM Service (NATIVE + Metal GPU) → Ollama (NATIVE)${NC}"
    echo -e "${CYAN}  🧠 VLM/HybridRouter → AI Detection (fast-path + VLM validation)${NC}"
    echo -e "${CYAN}  🚨 Violations → Alert Service → Notifications${NC}"
else
    echo -e "${CYAN}Pipeline Flow (All Docker):${NC}"
    echo -e "${CYAN}  📹 Video File → Frigate (CPU detection) → MQTT${NC}"
    echo -e "${CYAN}  🔄 MQTT → Stream Processor → NATS${NC}"
    echo -e "${CYAN}  🤖 Stream Processor → VLM Service (Docker CPU) → Ollama (Docker CPU)${NC}"
    echo -e "${CYAN}  🧠 VLM/HybridRouter → AI Detection (fast-path + VLM validation)${NC}"
    echo -e "${CYAN}  🚨 Violations → Alert Service → Notifications${NC}"
fi
echo ""

echo -e "${YELLOW}Triggering manual test event (Frigate CPU detection is slow)...${NC}"
MQTT_CONTAINER=$(docker compose ps -q mosquitto)
docker exec $MQTT_CONTAINER mosquitto_pub -h localhost -t 'frigate/classroom_test/person' \
  -m '{"before":{"id":"e2e-test","camera":"classroom_test","label":"person","score":0.95},"after":{"id":"e2e-test","camera":"classroom_test","label":"person","score":0.95}}'
echo -e "${GREEN}✓ Test event published${NC}"
echo ""

echo -e "${YELLOW}Monitoring logs for 60 seconds...${NC}"
echo -e "${YELLOW}(Press Ctrl+C to stop monitoring early)${NC}"
echo ""

# Monitor logs in parallel
if [ "$USE_NATIVE" = true ]; then
    timeout 60 bash -c '
        docker logs -f --tail=20 nura-nura-stream-processor-1 2>&1 | grep --line-buffered -E "Forwarded|Published|Processing|AI|ERROR" | sed "s/^/[STREAM] /" &
        docker logs -f --tail=20 nura-nura-alerts-1 2>&1 | grep --line-buffered -E "Alert|notification|sent|error|violation" | sed "s/^/[ALERT] /" &
        tail -f logs/vlm-service.log 2>&1 | grep --line-buffered -E "POST|Fast-path|Loading|analyze|Hybrid|violation" | sed "s/^/[VLM-NATIVE] /" &
        wait
    ' || true
else
    timeout 60 bash -c '
        docker logs -f --tail=20 nura-nura-stream-processor-1 2>&1 | grep --line-buffered -E "Forwarded|Published|Processing|AI|ERROR" | sed "s/^/[STREAM] /" &
        docker logs -f --tail=20 nura-nura-alerts-1 2>&1 | grep --line-buffered -E "Alert|notification|sent|error|violation" | sed "s/^/[ALERT] /" &
        docker logs -f --tail=10 nura-nura-vlm-1 2>&1 | grep --line-buffered -E "POST|Fast-path|Loading|analyze" | sed "s/^/[VLM-DOCKER] /" &
        wait
    ' || true
fi

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Summary
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    TEST SUMMARY                           ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check service status
echo -e "${CYAN}Services Status:${NC}"
echo ""
echo -e "${CYAN}Docker Services:${NC}"
check_service "postgres" && echo "" || echo ""
check_service "nats" && echo "" || echo ""
check_service "mosquitto" && echo "" || echo ""
check_service "frigate" && echo "" || echo ""

if [ "$USE_NATIVE" = true ]; then
    echo -e "${CYAN}Native AI Services:${NC}"
    if lsof -i :11434 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama is running (native - Metal GPU)${NC}"
    else
        echo -e "${RED}✗ Ollama is not running${NC}"
    fi
    if lsof -i :8001 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ VLM Service is running (native - Metal GPU)${NC}"
    else
        echo -e "${RED}✗ VLM Service is not running${NC}"
    fi
else
    echo -e "${CYAN}Docker AI Services:${NC}"
    check_service "ollama" && echo "" || echo ""
    check_service "nura-vlm" && echo "" || echo ""
fi

echo ""
echo -e "${CYAN}Docker Processing Services:${NC}"
check_service "nura-stream-processor" && echo "" || echo ""
check_service "nura-alerts" && echo "" || echo ""

echo ""
echo -e "${CYAN}Useful URLs:${NC}"
echo -e "  Frigate:           ${GREEN}http://localhost:5000${NC}"
echo -e "  Stream Processor:  ${GREEN}http://localhost:3010/health${NC}"
echo -e "  Alert Service:     ${GREEN}http://localhost:3011/health${NC}"
echo -e "  NATS Monitor:      ${GREEN}http://localhost:8222${NC}"

echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo -e "  1. Check Frigate UI: ${GREEN}http://localhost:5000${NC}"
echo -e "  2. Monitor logs:"
echo -e "     ${YELLOW}docker logs -f nura-nura-stream-processor-1${NC}"
echo -e "     ${YELLOW}docker logs -f nura-nura-vlm-1${NC}"
echo -e "     ${YELLOW}docker logs -f nura-nura-alerts-1${NC}"
echo -e "  3. Check for alerts in PostgreSQL:"
echo -e "     ${YELLOW}docker exec nura-postgres-1 psql -U nura -d nura_db -c 'SELECT * FROM alerts;'${NC}"
echo -e "  4. Manually trigger test event:"
echo -e "     ${YELLOW}docker exec nura-mosquitto-1 mosquitto_pub -h localhost -t 'frigate/classroom_test/person' \\${NC}"
echo -e "     ${YELLOW}  -m '{\"before\":{\"id\":\"test\",\"camera\":\"classroom_test\",\"label\":\"person\",\"score\":0.99},\"after\":{\"id\":\"test\",\"camera\":\"classroom_test\",\"label\":\"person\",\"score\":0.99}}'${NC}"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Pipeline is running! Monitor above URLs for activity.${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}To stop the test:${NC}"
if [ "$USE_NATIVE" = true ]; then
    echo -e "  ${CYAN}./runner/stop_services.sh${NC}     # Stop native AI services"
    echo -e "  ${CYAN}docker compose down${NC}            # Stop Docker services"
else
    echo -e "  ${CYAN}docker compose --profile app down${NC}  # Stop all Docker services"
fi
echo ""
