#!/bin/bash
# Stop simulated camera feeds

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(dirname "$0")/.."

echo -e "${BLUE}Stopping camera feed simulators...${NC}"
echo ""

docker compose -f docker-compose.cameras.yml down

echo ""
echo -e "${GREEN}✓ Camera feeds stopped${NC}"
echo ""
