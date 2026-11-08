#!/bin/bash
# Quick Demo Test Script
# Tests a specific video/image through the AI pipeline for demos
#
# Usage:
#   ./tools/demo_test.sh tests/videos/classroom_6.mp4
#   ./tools/demo_test.sh path/to/image.jpg

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check input
if [ -z "$1" ]; then
    echo -e "${RED}Usage: $0 <video_or_image_path>${NC}"
    echo ""
    echo "Examples:"
    echo "  $0 tests/videos/classroom_6.mp4"
    echo "  $0 tests/images/test_frame.jpg"
    echo "  $0 tests/data/ToddlerActions/train/Toddler\ crying/image001.jpg"
    exit 1
fi

INPUT_FILE="$1"

if [ ! -f "$INPUT_FILE" ]; then
    echo -e "${RED}✗ File not found: $INPUT_FILE${NC}"
    exit 1
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     NURA AI - Demo Test (Single Input)                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Change to project root
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

# Check if VLM service is running
echo -e "${YELLOW}Checking services...${NC}"
if ! lsof -i :8001 >/dev/null 2>&1; then
    echo -e "${RED}✗ VLM Service not running${NC}"
    echo -e "${YELLOW}  Start with: ./runner/run_vlm_service.sh${NC}"
    exit 1
fi
echo -e "${GREEN}✓ VLM Service is running${NC}"

# Check if Ollama is running
if ! lsof -i :11434 >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Ollama not running (VLM may fail)${NC}"
    echo -e "${YELLOW}  Start with: ./runner/run_ollama.sh${NC}"
fi

# Activate VLM virtual environment (has all dependencies)
if [ -d "services/nura-vlm/.venv" ]; then
    echo -e "${GREEN}✓ Using VLM virtual environment${NC}"
    source services/nura-vlm/.venv/bin/activate

    # Install test tool dependencies if needed
    if ! python -c "import rich" 2>/dev/null; then
        echo -e "${YELLOW}Installing test tool dependencies in venv...${NC}"
        pip install -q -r tools/requirements.txt
    fi
else
    echo -e "${RED}✗ VLM virtual environment not found${NC}"
    echo -e "${YELLOW}  Run: ./runner/run_vlm_service.sh (to create venv)${NC}"
    exit 1
fi

# Determine file type
EXT="${INPUT_FILE##*.}"
if [[ "$EXT" =~ ^(mp4|avi|mov|mkv|webm)$ ]]; then
    INPUT_TYPE="video"
else
    INPUT_TYPE="image"
fi

echo ""
echo -e "${BLUE}Input:[/blue] $INPUT_FILE"
echo -e "${BLUE}Type:[/blue] $INPUT_TYPE"
echo ""

# Run test (using python from venv)
if [ "$INPUT_TYPE" = "video" ]; then
    python tools/test_single_input.py \
        --video "$INPUT_FILE" \
        --camera "demo_camera" \
        --sample-rate 30 \
        --max-frames 3 \
        --save-annotated "demo_annotated.jpg"
else
    python tools/test_single_input.py \
        --image "$INPUT_FILE" \
        --camera "demo_camera" \
        --save-annotated "demo_annotated.jpg"
fi

echo ""
echo -e "${GREEN}✓ Demo test complete!${NC}"
echo ""

if [ -f "demo_annotated.jpg" ]; then
    echo -e "${YELLOW}Annotated frame saved: demo_annotated.jpg${NC}"
    echo -e "${YELLOW}View with: open demo_annotated.jpg${NC}"
fi
