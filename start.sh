#!/bin/bash
# NURA System - Unified Start Script
# Orchestrates native services (Ollama, VLM) + Docker services (Week 6)
# Usage: ./start.sh [--native-only|--docker-only|--all]

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
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
echo -e "${BLUE}║          NURA Childcare AI - Starting Services            ║${NC}"
echo -e "${BLUE}║              Week 6: Complete System                      ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$MODE" = "native" ]; then
    echo -e "${CYAN}Mode: Native services only (Ollama + VLM)${NC}"
elif [ "$MODE" = "docker" ]; then
    echo -e "${CYAN}Mode: Docker services only${NC}"
else
    echo -e "${CYAN}Mode: Complete system (Native AI + Docker services)${NC}"
fi
echo ""

# ============================================================================
# Phase 1: Native AI Services (Ollama + VLM)
# ============================================================================

if [ "$MODE" = "native" ] || [ "$MODE" = "all" ]; then
    echo -e "${BLUE}[1/2] Starting Native AI Services (Metal GPU)...${NC}"
    echo ""

    echo -e "${YELLOW}  Starting Ollama...${NC}"
    if lsof -i :11434 >/dev/null 2>&1; then
        echo -e "${GREEN}  ✓ Ollama already running${NC}"
    else
        ./runner/run_ollama.sh || {
            echo -e "${YELLOW}  ⚠ Ollama failed to start${NC}"
        }
    fi

    echo -e "${YELLOW}  Starting VLM Service...${NC}"
    if lsof -i :8001 >/dev/null 2>&1; then
        echo -e "${GREEN}  ✓ VLM Service already running${NC}"
    else
        ./runner/run_vlm_service.sh || {
            echo -e "${YELLOW}  ⚠ VLM Service failed to start${NC}"
        }
    fi

    # Optional: Enrollment API
    ENABLE_FACE_ID=$(grep "^ENABLE_FACE_IDENTIFICATION=" .env 2>/dev/null | cut -d'=' -f2)
    if [ "$ENABLE_FACE_ID" = "true" ]; then
        echo -e "${YELLOW}  Starting Enrollment API...${NC}"
        if lsof -i :8002 >/dev/null 2>&1; then
            echo -e "${GREEN}  ✓ Enrollment API already running${NC}"
        else
            ./runner/run_enrollment_api.sh || {
                echo -e "${YELLOW}  ⚠ Enrollment API failed to start${NC}"
            }
        fi
    fi

    echo -e "${GREEN}✓ Native services started${NC}"
    echo ""
fi

# ============================================================================
# Phase 2: Docker Services (Week 6 Stack)
# ============================================================================

if [ "$MODE" = "docker" ] || [ "$MODE" = "all" ]; then
    echo -e "${BLUE}[2/2] Starting Docker Services (Week 6 Stack)...${NC}"
    echo ""

    # Core infrastructure
    echo -e "${YELLOW}  Starting core infrastructure...${NC}"
    docker compose up -d postgres nats mosquitto redis
    sleep 3

    # Week 6 services
    echo -e "${YELLOW}  Starting Week 6 services...${NC}"
    docker compose up -d nura-rag nura-rules nura-face nura-perception
    sleep 5

    # Processing services
    echo -e "${YELLOW}  Starting processing services...${NC}"
    docker compose up -d frigate nura-stream-processor nura-alerts apprise ntfy
    sleep 2

    echo -e "${GREEN}✓ Docker services started${NC}"
    echo ""
fi

# ============================================================================
# Summary
# ============================================================================

echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Services Started Successfully                 ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$MODE" = "native" ] || [ "$MODE" = "all" ]; then
    echo -e "${CYAN}Native AI Services (Metal GPU):${NC}"
    if lsof -i :11434 >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Ollama:          http://localhost:11434"
    else
        echo -e "  ${YELLOW}✗${NC} Ollama:          Not running"
    fi

    if lsof -i :8001 >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} VLM Service:     http://localhost:8001"
    else
        echo -e "  ${YELLOW}✗${NC} VLM Service:     Not running"
    fi

    if lsof -i :8002 >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Enrollment API:  http://localhost:8002"
    fi
    echo ""
fi

if [ "$MODE" = "docker" ] || [ "$MODE" = "all" ]; then
    echo -e "${CYAN}Docker Services Status:${NC}"
    docker compose ps --format "table {{.Service}}\t{{.Status}}" | grep -E "nura-rag|nura-rules|nura-face|nura-perception|postgres|nats" | sed 's/^/  /'
    echo ""

    echo -e "${CYAN}Service URLs:${NC}"
    echo -e "  ${GREEN}•${NC} RAG Service:      http://localhost:3002/health"
    echo -e "  ${GREEN}•${NC} Rules Engine:     http://localhost:3003/health"
    echo -e "  ${GREEN}•${NC} Face Service:     http://localhost:8002/health"
    echo -e "  ${GREEN}•${NC} Perception:       http://localhost:8000/health"
    echo -e "  ${GREEN}•${NC} Frigate:          http://localhost:5000"
    echo ""
fi

echo -e "${CYAN}Next Steps:${NC}"
echo -e "  ${YELLOW}•${NC} Run full test:      ${GREEN}./scripts/test-end-to-end.sh${NC}"
echo -e "  ${YELLOW}•${NC} View logs:          ${GREEN}docker compose logs -f [service]${NC}"
echo -e "  ${YELLOW}•${NC} Check violations:   ${GREEN}docker exec nura-postgres-1 psql -U nura -d nura_db -c 'SELECT * FROM violation_events LIMIT 5;'${NC}"
echo -e "  ${YELLOW}•${NC} Stop all:           ${GREEN}./stop.sh${NC}"
echo ""

echo -e "${CYAN}Modes:${NC}"
echo -e "  ${GREEN}./start.sh${NC}              # Start everything (default)"
echo -e "  ${GREEN}./start.sh --native-only${NC}  # Only Ollama + VLM"
echo -e "  ${GREEN}./start.sh --docker-only${NC}  # Only Docker services"
echo ""
