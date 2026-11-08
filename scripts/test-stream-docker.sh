#!/bin/bash
# Test RTSP Stream via Docker
# This runs FFmpeg inside a Docker container on the same network as MediaMTX

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

VIDEO_FILE="${1:-tests/videos/classroom_8.mp4}"

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       NURA - RTSP Stream Test (via Docker)                ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ ! -f "$VIDEO_FILE" ]; then
    echo -e "${RED}✗ Video file not found: $VIDEO_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Video file: $VIDEO_FILE${NC}"
echo -e "${YELLOW}Starting FFmpeg stream inside Docker network...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Run FFmpeg in a Docker container on the same network as MediaMTX
# Re-encode to H.264 baseline profile for RTSP compatibility
docker run --rm -i \
  --network nura_camera_net \
  -v "$(pwd)/$VIDEO_FILE:/video.mp4:ro" \
  linuxserver/ffmpeg:latest \
  -re -stream_loop -1 \
  -i /video.mp4 \
  -c:v libx264 \
  -preset ultrafast \
  -tune zerolatency \
  -profile:v baseline \
  -level 3.0 \
  -pix_fmt yuv420p \
  -s 1920x1080 \
  -r 30 \
  -b:v 2M \
  -an \
  -f rtsp \
  -rtsp_transport tcp \
  rtsp://mediamtx:8554/classroom_test
