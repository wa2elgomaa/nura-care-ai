#!/bin/bash
# Run Enrollment API (Phase 4B - Face Identification)
# Usage: ./scripts/run_enrollment_api.sh

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}Starting Enrollment API...${NC}"

# Function to check if a port is in use
check_port() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local name=$2
    local max_wait=30
    local count=0

    echo -e "${YELLOW}⏳ Waiting for $name to be ready...${NC}"
    while [ $count -lt $max_wait ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✓ $name is ready${NC}"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done

    echo -e "${RED}✗ $name failed to start within ${max_wait}s${NC}"
    return 1
}

# Load environment
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

# Check if face identification is enabled
if [ "${ENABLE_FACE_IDENTIFICATION}" != "true" ]; then
    echo -e "${YELLOW}⚠ Face identification disabled (ENABLE_FACE_IDENTIFICATION != true)${NC}"
    echo -e "${YELLOW}Enable it in .env to use the enrollment API${NC}"
    exit 1
fi

# Check if venv exists
if [ ! -d "services/nura-vlm/.venv" ]; then
    echo -e "${RED}✗ Virtual environment not found${NC}"
    echo -e "${YELLOW}Run ./scripts/run_vlm_service.sh first to create it${NC}"
    exit 1
fi

ENROLLMENT_PORT=${ENROLLMENT_API_PORT:-8002}

# Kill existing service
if check_port $ENROLLMENT_PORT; then
    echo -e "${YELLOW}Stopping existing enrollment API on port $ENROLLMENT_PORT...${NC}"
    kill $(lsof -t -i:$ENROLLMENT_PORT) 2>/dev/null || true
    sleep 2
fi

# Create logs directory
mkdir -p logs

# Start enrollment API
echo -e "${YELLOW}Starting enrollment API on port $ENROLLMENT_PORT...${NC}"
cd services/nura-vlm

env POSTGRES_HOST="${POSTGRES_HOST:-localhost}" \
    POSTGRES_PORT="${POSTGRES_PORT:-5432}" \
    POSTGRES_DB="${POSTGRES_DB:-nura_db}" \
    POSTGRES_USER="${POSTGRES_USER:-nura}" \
    POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
    FACE_RECOGNITION_BACKEND="${FACE_RECOGNITION_BACKEND:-insightface}" \
    nohup .venv/bin/python -m uvicorn src.enrollment_api:app --host 0.0.0.0 --port $ENROLLMENT_PORT --log-level info > ../../logs/enrollment-api.log 2>&1 &

ENROLLMENT_PID=$!
echo $ENROLLMENT_PID > ../../.enrollment.pid
cd "$PROJECT_ROOT"

# Wait for service
if wait_for_service "http://localhost:$ENROLLMENT_PORT/health" "Enrollment API"; then
    echo ""
    echo -e "${GREEN}✓ Enrollment API Started Successfully${NC}"
    echo -e "  URL: http://localhost:$ENROLLMENT_PORT"
    echo -e "  UI: http://localhost:$ENROLLMENT_PORT/static/enrollment.html"
    echo -e "  Health: http://localhost:$ENROLLMENT_PORT/health"
    echo -e "  Logs: tail -f logs/enrollment-api.log"
    echo -e "  PID: $ENROLLMENT_PID (saved to .enrollment.pid)"
    echo -e "  Stop: kill \$(cat .enrollment.pid)"
else
    echo -e "${RED}✗ Enrollment API failed to start${NC}"
    echo -e "${YELLOW}Check logs: tail -f logs/enrollment-api.log${NC}"
    exit 1
fi
