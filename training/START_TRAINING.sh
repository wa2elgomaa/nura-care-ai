#!/bin/bash
# Quick Start Script for Distress Detector Training
# Run: ./training/START_TRAINING.sh

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  NURA - Distress Detector Training (ToddlerActions)     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Change to project root
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

# Check dataset exists
if [ ! -d "tests/data/ToddlerActions" ]; then
    echo -e "${RED}✗ Error: ToddlerActions dataset not found${NC}"
    echo -e "${YELLOW}  Expected at: tests/data/ToddlerActions/${NC}"
    exit 1
fi

echo -e "${GREEN}✓ ToddlerActions dataset found${NC}"

# Check Python environment
if [ ! -d "services/nura-vlm/.venv" ]; then
    echo -e "${RED}✗ Error: Python virtual environment not found${NC}"
    echo -e "${YELLOW}  Run: ./runner/run_vlm_service.sh (to create venv)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python virtual environment found${NC}"

# Activate environment
cd services/nura-vlm
source .venv/bin/activate
cd ../..

# Install additional training dependencies if needed
echo -e "${YELLOW}Checking training dependencies...${NC}"
pip install -q matplotlib tqdm >/dev/null 2>&1 || {
    echo -e "${YELLOW}Installing matplotlib and tqdm...${NC}"
    pip install matplotlib tqdm
}
echo -e "${GREEN}✓ Training dependencies ready${NC}"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 1/3: Preparing Dataset${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

python training/prepare_distress_dataset.py

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Dataset preparation failed${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 2/3: Training Model${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Training with:${NC}"
echo -e "  - Epochs: 30"
echo -e "  - Batch size: 32"
echo -e "  - Learning rate: 1e-4"
echo -e "  - Method: Fine-tuning existing model"
echo ""
echo -e "${YELLOW}Expected time: 5-15 minutes (depending on hardware)${NC}"
echo ""

python training/train_distress_detector.py \
    --epochs 30 \
    --batch-size 32 \
    --learning-rate 1e-4 \
    --output models/distress_detector_v2.keras

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Training failed${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 3/3: Deployment${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if model was created
if [ -f "models/distress_detector_v2.keras" ]; then
    echo -e "${GREEN}✓ Model trained successfully!${NC}"
    echo ""
    echo -e "${YELLOW}Model location: models/distress_detector_v2.keras${NC}"
    echo ""

    # Show training results
    LATEST_SUMMARY=$(ls -t logs/training/training_summary_*.txt 2>/dev/null | head -1)
    if [ -f "$LATEST_SUMMARY" ]; then
        echo -e "${BLUE}Training Results:${NC}"
        grep -A 10 "Final Validation Metrics:" "$LATEST_SUMMARY" || echo "Summary not found"
        echo ""
    fi

    # Show training plot
    LATEST_PLOT=$(ls -t logs/training/training_history_*.png 2>/dev/null | head -1)
    if [ -f "$LATEST_PLOT" ]; then
        echo -e "${GREEN}✓ Training plots: $LATEST_PLOT${NC}"
        echo -e "${YELLOW}  View with: open \"$LATEST_PLOT\"${NC}"
        echo ""
    fi

    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  🎉 TRAINING COMPLETE!                                   ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo ""
    echo -e "${YELLOW}1. View training plot:${NC}"
    echo -e "   open \"$LATEST_PLOT\""
    echo ""
    echo -e "${YELLOW}2. Test the model:${NC}"
    echo -e "   python tools/test_distress_detector.py \\"
    echo -e "     --model models/distress_detector_v2.keras \\"
    echo -e "     --test-dir datasets/distress_binary/valid/"
    echo ""
    echo -e "${YELLOW}3. Deploy to VLM service:${NC}"
    echo -e "   # Stop VLM service"
    echo -e "   ./runner/stop_services.sh vlm"
    echo ""
    echo -e "   # Update model path in VLM code (or use environment variable)"
    echo -e "   # Then restart"
    echo -e "   ./runner/run_vlm_service.sh"
    echo ""
    echo -e "${YELLOW}4. Test end-to-end pipeline:${NC}"
    echo -e "   ./scripts/test-end-to-end.sh"
    echo ""
else
    echo -e "${RED}✗ Error: Model file not found${NC}"
    echo -e "${YELLOW}  Check logs for errors${NC}"
    exit 1
fi
