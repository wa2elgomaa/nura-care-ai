#!/bin/bash
# Stop all Nura services
# Run: ./stop.sh

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       NURA Childcare AI - Stopping Services               ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# Stop VLM Service
echo -e "${BLUE}[1/4] Stopping VLM Service...${NC}"
if [ -f .vlm.pid ]; then
    VLM_PID=$(cat .vlm.pid)
    if kill -0 $VLM_PID 2>/dev/null; then
        kill $VLM_PID
        echo -e "${GREEN}✓ VLM Service stopped (PID: $VLM_PID)${NC}"
    else
        echo -e "${YELLOW}VLM Service not running${NC}"
    fi
    rm -f .vlm.pid
else
    # Try to kill by port
    if lsof -i :8001 >/dev/null 2>&1; then
        kill $(lsof -t -i:8001) 2>/dev/null || true
        echo -e "${GREEN}✓ VLM Service stopped${NC}"
    else
        echo -e "${YELLOW}VLM Service not running${NC}"
    fi
fi

# Stop Enrollment API (Phase 4B)
echo ""
echo -e "${BLUE}[2/4] Stopping Enrollment API...${NC}"
if [ -f .enrollment.pid ]; then
    ENROLLMENT_PID=$(cat .enrollment.pid)
    if kill -0 $ENROLLMENT_PID 2>/dev/null; then
        kill $ENROLLMENT_PID
        echo -e "${GREEN}✓ Enrollment API stopped (PID: $ENROLLMENT_PID)${NC}"
    else
        echo -e "${YELLOW}Enrollment API not running${NC}"
    fi
    rm -f .enrollment.pid
else
    # Try to kill by port
    if lsof -i :8002 >/dev/null 2>&1; then
        kill $(lsof -t -i:8002) 2>/dev/null || true
        echo -e "${GREEN}✓ Enrollment API stopped${NC}"
    else
        echo -e "${YELLOW}Enrollment API not running${NC}"
    fi
fi

# Stop NATS (Docker)
echo ""
echo -e "${BLUE}[3/4] Stopping NATS...${NC}"
docker compose -f compose.yaml stop nats 2>/dev/null || echo -e "${YELLOW}NATS not running in Docker${NC}"

# Ollama (keep running - it's a system service)
echo ""
echo -e "${BLUE}[4/4] Ollama...${NC}"
echo -e "${YELLOW}Keeping Ollama running (system service)${NC}"
echo -e "${YELLOW}To stop Ollama: killall ollama${NC}"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║             Services Stopped Successfully                  ║${NC}"
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""
