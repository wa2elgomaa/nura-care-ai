#!/bin/bash
# Start all Nura services locally using modular runner scripts
# Run: ./start.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       NURA Childcare AI - Starting Services               ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# 0. Check prerequisites
echo -e "${BLUE}[0/4] Checking prerequisites...${NC}"

# Check for Homebrew
if [ -f /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
    echo -e "${GREEN}✓ Homebrew found${NC}"
elif ! command -v brew >/dev/null 2>&1; then
    echo -e "${YELLOW}Homebrew not found. Installing...${NC}"
    echo -e "${YELLOW}This will prompt for your password.${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    if [ -f /opt/homebrew/bin/brew ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    echo -e "${GREEN}✓ Homebrew installed${NC}"
else
    echo -e "${GREEN}✓ Homebrew found${NC}"
fi

# Check for Python 3.11+ (runner script will handle installation)
if command -v python3.11 >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Python 3.11+ found${NC}"
elif command -v python3 >/dev/null 2>&1; then
    VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    MAJOR=$(echo "$VERSION" | cut -d. -f1)
    MINOR=$(echo "$VERSION" | cut -d. -f2)
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 11 ]; then
        echo -e "${GREEN}✓ Python 3.11+ found: python3${NC}"
    else
        echo -e "${YELLOW}Python 3.11+ not found. Installing...${NC}"
        brew install python@3.11
        echo -e "${GREEN}✓ Python 3.11 installed${NC}"
    fi
else
    echo -e "${YELLOW}Python not found. Installing...${NC}"
    brew install python@3.11
    echo -e "${GREEN}✓ Python 3.11 installed${NC}"
fi

# Check for Ollama (runner script will handle installation)
if ! command -v ollama >/dev/null 2>&1; then
    echo -e "${YELLOW}Ollama not found. Installing...${NC}"
    brew install ollama
    echo -e "${GREEN}✓ Ollama installed${NC}"
else
    echo -e "${GREEN}✓ Ollama found${NC}"
fi

# Check and download models if needed
echo ""
echo -e "${BLUE}[0.5/4] Checking models...${NC}"
if [ ! -f "models/temporal_violence.keras" ] || [ ! -f "models/distress_classifier.keras" ]; then
    echo -e "${YELLOW}⚠ Production models not found${NC}"
    echo -e "${YELLOW}Downloading models from registry...${NC}"
    if [ -f "scripts/download-models.sh" ]; then
        bash scripts/download-models.sh || {
            echo -e "${YELLOW}⚠ Model download failed, but continuing...${NC}"
            echo -e "${YELLOW}  Services will start, but detection may not work${NC}"
        }
    else
        echo -e "${YELLOW}⚠ Model download script not found${NC}"
        echo -e "${YELLOW}  Please run: bash scripts/download-models.sh${NC}"
    fi
else
    echo -e "${GREEN}✓ Production models found${NC}"
fi

# 1. Start Ollama using runner script
echo ""
echo -e "${BLUE}[1/4] Starting Ollama...${NC}"
if ! ./runner/run_ollama.sh; then
    echo -e "${RED}✗ Failed to start Ollama${NC}"
    exit 1
fi

# 2. NATS (optional - needed for event publishing)
echo ""
echo -e "${BLUE}[2/4] NATS...${NC}"
echo -e "${YELLOW}Skipping NATS (optional for testing)${NC}"
echo -e "${YELLOW}VLM service will work without NATS for direct API calls${NC}"

# 3. Start VLM Service using runner script
echo ""
echo -e "${BLUE}[3/4] Starting VLM Service...${NC}"
if ! ./runner/run_vlm_service.sh; then
    echo -e "${RED}✗ Failed to start VLM Service${NC}"
    exit 1
fi

# 4. Start Enrollment API (Phase 4B) - if enabled
echo ""
echo -e "${BLUE}[4/4] Starting Enrollment API (Phase 4B)...${NC}"

# Check if face identification is enabled
ENABLE_FACE_ID=$(grep "^ENABLE_FACE_IDENTIFICATION=" "$PROJECT_ROOT/.env" 2>/dev/null | cut -d'=' -f2)

if [ "$ENABLE_FACE_ID" = "true" ]; then
    if ./runner/run_enrollment_api.sh; then
        ENROLLMENT_RUNNING=true
        ENROLLMENT_PORT=${ENROLLMENT_API_PORT:-8002}
    else
        echo -e "${YELLOW}⚠ Enrollment API failed to start${NC}"
        echo -e "${YELLOW}  Check logs: tail -f logs/enrollment-api.log${NC}"
        ENROLLMENT_RUNNING=false
    fi
else
    echo -e "${YELLOW}Face identification disabled (ENABLE_FACE_IDENTIFICATION=false)${NC}"
    echo -e "${YELLOW}Skipping enrollment API startup${NC}"
    ENROLLMENT_RUNNING=false
fi

# Summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          ✓ All Services Started Successfully              ║${NC}"
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""
echo -e "${BLUE}Service Status:${NC}"
echo -e "  ${GREEN}•${NC} Ollama (VLM):        http://localhost:11434"
echo -e "  ${GREEN}•${NC} VLM Service (API):   http://localhost:8001"

if [ "$ENROLLMENT_RUNNING" = true ]; then
    echo -e "  ${GREEN}•${NC} Enrollment API:      http://localhost:$ENROLLMENT_PORT"
    echo -e "  ${GREEN}•${NC} Enrollment UI:       http://localhost:$ENROLLMENT_PORT/static/enrollment.html"
else
    echo -e "  ${YELLOW}•${NC} Enrollment API:      Not running"
fi

echo ""
echo -e "${BLUE}Phase 4B Features:${NC}"
if [ "$ENROLLMENT_RUNNING" = true ]; then
    echo -e "  ${GREEN}✓${NC} Person Tracking:     Enabled"
    echo -e "  ${GREEN}✓${NC} Face Identification: Enabled"
    echo -e "  ${GREEN}✓${NC} Named Alerts:        Enabled"
else
    echo -e "  ${YELLOW}•${NC} Face Identification: Disabled (set ENABLE_FACE_IDENTIFICATION=true)"
fi

echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo -e "  ${YELLOW}1.${NC} Test the system:  ${YELLOW}./test-images.sh${NC}"

if [ "$ENROLLMENT_RUNNING" = true ]; then
    echo -e "  ${YELLOW}2.${NC} Enroll persons:   ${YELLOW}open http://localhost:$ENROLLMENT_PORT/static/enrollment.html${NC}"
    echo -e "  ${YELLOW}3.${NC} Test integration: ${YELLOW}python3 tools/testing/test_full_integration.py${NC}"
fi

echo -e "  ${YELLOW}4.${NC} Check health:     ${YELLOW}curl http://localhost:8001/health${NC}"
echo -e "  ${YELLOW}5.${NC} View logs:        ${YELLOW}tail -f logs/vlm-service.log${NC}"
echo -e "  ${YELLOW}6.${NC} Stop services:    ${YELLOW}./runner/stop_services.sh${NC}"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo -e "  ${YELLOW}•${NC} Runner Scripts:   ${YELLOW}less runner/README.md${NC}"
echo -e "  ${YELLOW}•${NC} Quick Start:      ${YELLOW}less QUICK_START.md${NC}"
echo -e "  ${YELLOW}•${NC} Phase 4B Guide:   ${YELLOW}less docs/phases/PHASE4B_QUICKSTART.md${NC}"
echo -e "  ${YELLOW}•${NC} README:           ${YELLOW}less README.md${NC}"
echo ""
