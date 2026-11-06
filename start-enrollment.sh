#!/bin/bash
# Start Enrollment API (Phase 4B)
# Quick start script for testing enrollment system

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Starting Enrollment API (Phase 4B)                  ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# Check dependencies
echo -e "${BLUE}[1/3] Checking dependencies...${NC}"

if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}Installing FastAPI dependencies...${NC}"
    pip3 install fastapi uvicorn python-multipart psycopg2-binary
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Dependencies already installed${NC}"
fi

# Load environment
echo ""
echo -e "${BLUE}[2/3] Loading configuration...${NC}"

if [ -f ".env" ]; then
    set -a
    source .env
    set +a
    echo -e "${GREEN}✓ Loaded .env configuration${NC}"
else
    echo -e "${YELLOW}⚠ No .env file found, using defaults${NC}"
    export POSTGRES_HOST=localhost
    export POSTGRES_PORT=5432
    export POSTGRES_DB=nura_db
    export POSTGRES_USER=nura
    export POSTGRES_PASSWORD='Pa$$w0rd!'
fi

# Stop existing instance
if lsof -i :8002 >/dev/null 2>&1; then
    echo -e "${YELLOW}Stopping existing instance on port 8002...${NC}"
    kill $(lsof -t -i:8002) 2>/dev/null || true
    sleep 2
fi

# Start API
echo ""
echo -e "${BLUE}[3/3] Starting enrollment API...${NC}"

cd services/nura-vlm

# Create logs directory
mkdir -p ../../logs

# Start with uvicorn
nohup python3 -m uvicorn src.enrollment_api:app \
    --host 0.0.0.0 \
    --port 8002 \
    --log-level info \
    > ../../logs/enrollment-api.log 2>&1 &

API_PID=$!
echo $API_PID > ../../.enrollment.pid

cd "$PROJECT_ROOT"

# Wait for startup
sleep 3

# Check if running
if lsof -i :8002 >/dev/null 2>&1; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         ✓ Enrollment API Started Successfully             ║${NC}"
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo ""
    echo -e "${BLUE}Service URLs:${NC}"
    echo -e "  ${GREEN}•${NC} API Root:        ${YELLOW}http://localhost:8002${NC}"
    echo -e "  ${GREEN}•${NC} Enrollment UI:   ${YELLOW}http://localhost:8002/static/enrollment.html${NC}"
    echo -e "  ${GREEN}•${NC} API Docs:        ${YELLOW}http://localhost:8002/docs${NC}"
    echo -e "  ${GREEN}•${NC} Health Check:    ${YELLOW}http://localhost:8002/health${NC}"
    echo ""
    echo -e "${BLUE}Quick Actions:${NC}"
    echo -e "  ${YELLOW}1.${NC} Open enrollment UI:  ${YELLOW}open http://localhost:8002/static/enrollment.html${NC}"
    echo -e "  ${YELLOW}2.${NC} View API docs:       ${YELLOW}open http://localhost:8002/docs${NC}"
    echo -e "  ${YELLOW}3.${NC} View logs:           ${YELLOW}tail -f logs/enrollment-api.log${NC}"
    echo -e "  ${YELLOW}4.${NC} Stop API:            ${YELLOW}kill \$(cat .enrollment.pid)${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo -e "  ${GREEN}1.${NC} Make sure database is set up:"
    echo -e "     ${YELLOW}psql -U nura -d nura_db -f services/nura-vlm/migrations/001_person_enrollment.sql${NC}"
    echo -e "  ${GREEN}2.${NC} Enroll persons via the web UI"
    echo -e "  ${GREEN}3.${NC} Test with: ${YELLOW}python3 tools/testing/test_full_integration.py${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}✗ Failed to start enrollment API${NC}"
    echo -e "${YELLOW}Check logs: tail -f logs/enrollment-api.log${NC}"
    exit 1
fi
