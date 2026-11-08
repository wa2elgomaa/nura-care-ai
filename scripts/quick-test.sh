#!/bin/bash
# Quick Test - No background redirects, show all output

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       NURA - QUICK PIPELINE TEST                          ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

cd "$(dirname "$0")/.."

# Phase 1: Start Core Services
echo -e "${YELLOW}Starting core services...${NC}"
docker compose up -d postgres nats mosquitto

echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 10

# Phase 2: Start Streaming
echo -e "${YELLOW}Starting streaming services...${NC}"
docker compose up -d mediamtx frigate

sleep 5

# Phase 3: Start AI
echo -e "${YELLOW}Starting AI services...${NC}"
docker compose -f compose.yaml -f compose.mac.yaml up -d nura-vlm

sleep 5

# Phase 4: Start Processing
echo -e "${YELLOW}Starting processing services...${NC}"
docker compose up -d nura-stream-processor nura-alerts apprise ntfy

sleep 5

# Phase 5: Check Status
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Service Status:${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
docker compose ps

echo ""
echo -e "${GREEN}✓ Services started!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Check Frigate: ${GREEN}http://localhost:5000${NC}"
echo -e "  2. Start test stream: ${GREEN}./scripts/test-rtsp-stream.sh${NC}"
echo -e "  3. Monitor logs: ${GREEN}./scripts/monitor-pipeline.sh${NC}"
echo ""
