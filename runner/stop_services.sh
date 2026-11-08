#!/bin/bash
# Stop all locally running Nura services
# Usage: ./scripts/stop_services.sh [service_name]
#   service_name: ollama, vlm, enrollment, or leave empty to stop all

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

SERVICE=$1

stop_vlm() {
    if [ -f ".vlm.pid" ]; then
        VLM_PID=$(cat .vlm.pid)
        if kill -0 $VLM_PID 2>/dev/null; then
            echo -e "${YELLOW}Stopping VLM service (PID: $VLM_PID)...${NC}"
            kill $VLM_PID
            rm .vlm.pid
            echo -e "${GREEN}✓ VLM service stopped${NC}"
        else
            echo -e "${YELLOW}VLM service not running (stale PID file)${NC}"
            rm .vlm.pid
        fi
    else
        echo -e "${YELLOW}VLM service not running (no PID file)${NC}"
    fi
}

stop_enrollment() {
    if [ -f ".enrollment.pid" ]; then
        ENROLLMENT_PID=$(cat .enrollment.pid)
        if kill -0 $ENROLLMENT_PID 2>/dev/null; then
            echo -e "${YELLOW}Stopping Enrollment API (PID: $ENROLLMENT_PID)...${NC}"
            kill $ENROLLMENT_PID
            rm .enrollment.pid
            echo -e "${GREEN}✓ Enrollment API stopped${NC}"
        else
            echo -e "${YELLOW}Enrollment API not running (stale PID file)${NC}"
            rm .enrollment.pid
        fi
    else
        echo -e "${YELLOW}Enrollment API not running (no PID file)${NC}"
    fi
}

stop_ollama() {
    if pgrep ollama >/dev/null 2>&1; then
        echo -e "${YELLOW}Stopping Ollama...${NC}"
        killall ollama 2>/dev/null || true
        sleep 2
        echo -e "${GREEN}✓ Ollama stopped${NC}"
    else
        echo -e "${YELLOW}Ollama not running${NC}"
    fi
}

if [ -z "$SERVICE" ]; then
    echo -e "${BLUE}Stopping all Nura services...${NC}"
    stop_enrollment
    stop_vlm
    stop_ollama
elif [ "$SERVICE" = "vlm" ]; then
    stop_vlm
elif [ "$SERVICE" = "enrollment" ]; then
    stop_enrollment
elif [ "$SERVICE" = "ollama" ]; then
    stop_ollama
else
    echo -e "${RED}Unknown service: $SERVICE${NC}"
    echo -e "${YELLOW}Usage: $0 [ollama|vlm|enrollment]${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Stop complete${NC}"
