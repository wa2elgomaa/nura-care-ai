#!/bin/bash
# NURA AI Demo - Test any image or video through the AI pipeline
# Simulates camera feed analysis
#
# Usage:
#   ./demo.sh <image_or_video_path>
#
# Examples:
#   ./demo.sh tests/videos/classroom_1.mp4
#   ./demo.sh path/to/image.jpg
#   ./demo.sh "tests/data/ToddlerActions/train/Toddler crying/image.jpg"

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}Usage: $0 <image_or_video_path>${NC}"
    echo ""
    echo "Examples:"
    echo "  $0 tests/videos/classroom_1.mp4"
    echo "  $0 path/to/test_image.jpg"
    echo ""
    echo "Quick tests:"
    echo "  $0 crying    # Test crying detection"
    echo "  $0 smiling   # Test happy child"
    echo "  $0 video     # Test video analysis"
    exit 1
fi

INPUT="$1"

# Handle shortcuts
case "$INPUT" in
    crying)
        INPUT="tests/data/ToddlerActions/train/Toddler crying/$(ls 'tests/data/ToddlerActions/train/Toddler crying/' | head -1)"
        ;;
    smiling)
        INPUT="tests/data/ToddlerActions/train/Toddler smiling/$(ls 'tests/data/ToddlerActions/train/Toddler smiling/' | head -1)"
        ;;
    knife)
        INPUT="tests/data/ToddlerActions/train/Toddler with knife/$(ls 'tests/data/ToddlerActions/train/Toddler with knife/' | head -1)"
        ;;
    video)
        INPUT="tests/videos/classroom_1.mp4"
        ;;
esac

# Check file exists
if [ ! -f "$INPUT" ]; then
    echo -e "${RED}✗ File not found: $INPUT${NC}"
    exit 1
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     NURA AI - Camera Feed Simulator                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check VLM service
echo -e "${YELLOW}Checking AI services...${NC}"
if ! lsof -i :8001 >/dev/null 2>&1; then
    echo -e "${RED}✗ VLM Service not running${NC}"
    echo -e "${YELLOW}  Start with: ./runner/run_vlm_service.sh${NC}"
    exit 1
fi
echo -e "${GREEN}✓ VLM Service is running${NC}"

# Activate VLM environment
if [ ! -d "services/nura-vlm/.venv" ]; then
    echo -e "${RED}✗ VLM virtual environment not found${NC}"
    echo -e "${YELLOW}  Run: ./runner/run_vlm_service.sh${NC}"
    exit 1
fi

source services/nura-vlm/.venv/bin/activate

# Install dependencies if needed
if ! python -c "import rich" 2>/dev/null; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -q opencv-python rich requests
fi

echo ""
echo -e "${GREEN}✓ Running AI analysis...${NC}"
echo ""

# Determine file type
EXT="${INPUT##*.}"
if [[ "$EXT" =~ ^(mp4|avi|mov|mkv|webm)$ ]]; then
    # Video - analyze 3 frames
    python tools/test_single_input.py \
        --video "$INPUT" \
        --camera "demo_camera" \
        --sample-rate 30 \
        --max-frames 3 \
        --save-annotated "demo_output.jpg"
else
    # Image
    python tools/test_single_input.py \
        --image "$INPUT" \
        --camera "demo_camera" \
        --save-annotated "demo_output.jpg"
fi

echo ""
echo -e "${GREEN}✓ Analysis complete!${NC}"
echo ""

if [ -f "demo_output.jpg" ]; then
    echo -e "${YELLOW}Annotated output: demo_output.jpg${NC}"
    echo -e "${YELLOW}View with: open demo_output.jpg${NC}"
fi

echo ""
echo -e "${BLUE}Quick test shortcuts:${NC}"
echo -e "  ${YELLOW}./demo.sh crying${NC}   - Test crying detection"
echo -e "  ${YELLOW}./demo.sh smiling${NC}  - Test happy child"
echo -e "  ${YELLOW}./demo.sh video${NC}    - Test video analysis"
