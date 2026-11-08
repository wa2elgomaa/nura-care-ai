#!/bin/bash
# Test RTSP streaming setup
# This script starts a local RTSP stream for testing the complete pipeline

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          NURA - RTSP Stream Test Script                  ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if video file exists
VIDEO_FILE="${1:-tests/videos/classroom_8.mp4}"

if [ ! -f "$VIDEO_FILE" ]; then
    echo -e "${RED}✗ Video file not found: $VIDEO_FILE${NC}"
    echo -e "${YELLOW}Usage: $0 [path/to/video.mp4]${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Video file found: $VIDEO_FILE${NC}"
echo ""

# Check if MediaMTX is running
echo -e "${BLUE}Checking MediaMTX...${NC}"
if ! docker ps | grep -q mediamtx; then
    echo -e "${YELLOW}⚠️  MediaMTX not running. Starting docker-compose...${NC}"
    cd "$(dirname "$0")/.."
    docker compose -f compose.yaml -f compose.mac.yaml --env-file .env up -d mediamtx
    sleep 3
fi

echo -e "${GREEN}✓ MediaMTX is running${NC}"
echo ""

# Get MediaMTX container ID
MEDIAMTX_PORT=$(docker compose ps mediamtx --format json 2>/dev/null | grep -o '8554:[0-9]*' | cut -d: -f2 || echo "8554")

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Starting RTSP stream...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}Video: $VIDEO_FILE${NC}"
echo -e "${YELLOW}RTSP URL: rtsp://localhost:8554/classroom_test${NC}"
echo -e "${YELLOW}HLS URL: http://localhost:8888/classroom_test${NC}"
echo -e "${YELLOW}WebRTC URL: http://localhost:8889/classroom_test${NC}"
echo ""

echo -e "${GREEN}Starting FFmpeg stream (loop)...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Stream video to MediaMTX
ffmpeg -re -stream_loop -1 \
  -i "$VIDEO_FILE" \
  -c copy \
  -f rtsp \
  rtsp://localhost:8554/classroom_test

# If FFmpeg exits
echo ""
echo -e "${YELLOW}Stream stopped${NC}"
