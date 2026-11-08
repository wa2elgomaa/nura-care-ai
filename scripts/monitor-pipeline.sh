#!/bin/bash
# Real-time Pipeline Monitoring
# Shows live activity across all services

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          NURA - LIVE PIPELINE MONITOR                     ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}Monitoring pipeline activity...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Monitor all services in parallel with colored output
docker logs -f --tail=10 nura-stream-processor-1 2>&1 | sed "s/^/$(echo -e ${GREEN})[STREAM]$(echo -e ${NC}) /" &
docker logs -f --tail=10 nura-alerts-1 2>&1 | sed "s/^/$(echo -e ${RED})[ALERT]$(echo -e ${NC}) /" &
docker logs -f --tail=10 nura-vlm-1 2>&1 | sed "s/^/$(echo -e ${CYAN})[VLM]$(echo -e ${NC}) /" &
docker logs -f --tail=5 frigate 2>&1 | grep -E "person|motion" | sed "s/^/$(echo -e ${YELLOW})[FRIGATE]$(echo -e ${NC}) /" &

# Wait for all background jobs
wait
