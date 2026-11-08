#!/bin/bash
# NURA System - Unified Stop Script
# Stops native services + Docker services
# Usage: ./stop.sh [--native-only|--docker-only|--all]

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

cd "$(dirname "$0")"

# Parse mode
MODE="all"
if [ "$1" = "--native-only" ]; then
    MODE="native"
elif [ "$1" = "--docker-only" ]; then
    MODE="docker"
fi

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          NURA Childcare AI - Stopping Services            ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# Phase 1: Stop Native Services
# ============================================================================

if [ "$MODE" = "native" ] || [ "$MODE" = "all" ]; then
    echo -e "${YELLOW}[1/2] Stopping Native Services...${NC}"

    # Use runner stop script if available
    if [ -f "runner/stop_services.sh" ]; then
        ./runner/stop_services.sh
    else
        # Manual stop
        echo -e "${YELLOW}  Stopping VLM Service...${NC}"
        if [ -f .vlm.pid ]; then
            VLM_PID=$(cat .vlm.pid)
            kill $VLM_PID 2>/dev/null || true
            rm -f .vlm.pid
            echo -e "${GREEN}  ✓ VLM Service stopped${NC}"
        elif lsof -i :8001 >/dev/null 2>&1; then
            kill $(lsof -t -i:8001) 2>/dev/null || true
            echo -e "${GREEN}  ✓ VLM Service stopped${NC}"
        else
            echo -e "${YELLOW}  VLM Service not running${NC}"
        fi

        echo -e "${YELLOW}  Stopping Enrollment API...${NC}"
        if [ -f .enrollment.pid ]; then
            ENROLLMENT_PID=$(cat .enrollment.pid)
            kill $ENROLLMENT_PID 2>/dev/null || true
            rm -f .enrollment.pid
            echo -e "${GREEN}  ✓ Enrollment API stopped${NC}"
        elif lsof -i :8002 >/dev/null 2>&1; then
            kill $(lsof -t -i:8002) 2>/dev/null || true
            echo -e "${GREEN}  ✓ Enrollment API stopped${NC}"
        else
            echo -e "${YELLOW}  Enrollment API not running${NC}"
        fi

        echo -e "${YELLOW}  Ollama...${NC}"
        echo -e "${YELLOW}  Keeping Ollama running (system service)${NC}"
        echo -e "${YELLOW}  To stop: killall ollama${NC}"
    fi

    echo -e "${GREEN}✓ Native services stopped${NC}"
    echo ""
fi

# ============================================================================
# Phase 2: Stop Docker Services
# ============================================================================

if [ "$MODE" = "docker" ] || [ "$MODE" = "all" ]; then
    echo -e "${YELLOW}[2/2] Stopping Docker Services...${NC}"

    echo -e "${YELLOW}  Stopping all Docker services...${NC}"
    docker compose --profile app down
    echo -e "${GREEN}  ✓ Docker services stopped${NC}"
    echo ""
fi

# ============================================================================
# Summary
# ============================================================================

echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Services Stopped Successfully                 ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}Status:${NC}"

if [ "$MODE" = "native" ] || [ "$MODE" = "all" ]; then
    if lsof -i :8001 >/dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠${NC} VLM Service still running"
    else
        echo -e "  ${GREEN}✓${NC} VLM Service stopped"
    fi

    if lsof -i :8002 >/dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠${NC} Enrollment API still running"
    else
        echo -e "  ${GREEN}✓${NC} Enrollment API stopped"
    fi

    if lsof -i :11434 >/dev/null 2>&1; then
        echo -e "  ${YELLOW}•${NC} Ollama still running (as intended)"
    fi
fi

if [ "$MODE" = "docker" ] || [ "$MODE" = "all" ]; then
    RUNNING=$(docker compose ps -q 2>/dev/null | wc -l | tr -d ' ')
    if [ "$RUNNING" -gt 0 ]; then
        echo -e "  ${YELLOW}⚠${NC} $RUNNING Docker containers still running"
        echo -e "     Run: ${GREEN}docker compose ps${NC}"
    else
        echo -e "  ${GREEN}✓${NC} All Docker services stopped"
    fi
fi

echo ""
echo -e "${CYAN}Notes:${NC}"
echo -e "  ${YELLOW}•${NC} Data is preserved in Docker volumes"
echo -e "  ${YELLOW}•${NC} To remove all data: ${GREEN}docker compose down -v${NC}"
echo -e "  ${YELLOW}•${NC} To stop Ollama: ${GREEN}killall ollama${NC}"
echo ""
