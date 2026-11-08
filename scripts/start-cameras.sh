#!/bin/bash
# Start simulated camera feeds (streaming video files to MediaMTX)

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(dirname "$0")/.."

echo -e "${BLUE}Starting camera feed simulators...${NC}"
echo ""

# Start MediaMTX RTSP server and FFmpeg publishers
docker compose -f docker-compose.cameras.yml up -d

echo ""
echo -e "${GREEN}✓ Camera feeds started${NC}"
echo ""
echo -e "${YELLOW}Camera streams available at:${NC}"
echo "  • rtsp://localhost:8554/class_1       (Classroom 1)"
echo "  • rtsp://localhost:8554/class_2       (Classroom 2)"
echo "  • rtsp://localhost:8554/class_3       (Classroom 3)"
echo "  • rtsp://localhost:8554/playground_1  (Playground)"
echo ""
echo -e "${YELLOW}MediaMTX Web UI:${NC}"
echo "  • http://localhost:8889 (WebRTC)"
echo "  • http://localhost:8888 (HLS)"
echo ""
echo -e "${YELLOW}To stop cameras:${NC} ./scripts/stop-cameras.sh"
echo ""
