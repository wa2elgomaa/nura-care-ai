#!/bin/bash
# Start all Nura services locally
# Run: ./start.sh

set -e  # Exit on error

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

# Function to detect Python 3.11+
detect_python() {
    # Try common Python 3.11 paths
    for py in /opt/homebrew/bin/python3.11 /usr/local/bin/python3.11 python3.11 python3; do
        if command -v "$py" >/dev/null 2>&1; then
            VERSION=$("$py" --version 2>&1 | awk '{print $2}')
            MAJOR=$(echo "$VERSION" | cut -d. -f1)
            MINOR=$(echo "$VERSION" | cut -d. -f2)
            if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 11 ]; then
                echo "$py"
                return 0
            fi
        fi
    done
    return 1
}

# 0. Check prerequisites
echo -e "${BLUE}[0/4] Checking prerequisites...${NC}"

# Check for Homebrew and add to PATH if needed
if [ -f /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
    echo -e "${GREEN}✓ Homebrew found${NC}"
elif ! command -v brew >/dev/null 2>&1; then
    echo -e "${YELLOW}Homebrew not found. Installing...${NC}"
    echo -e "${YELLOW}This will prompt for your password.${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add to PATH
    if [ -f /opt/homebrew/bin/brew ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    echo -e "${GREEN}✓ Homebrew installed${NC}"
else
    echo -e "${GREEN}✓ Homebrew found${NC}"
fi

# Check for Python 3.11+
PYTHON_CMD=$(detect_python)
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Python 3.11+ not found. Installing...${NC}"
    brew install python@3.11
    PYTHON_CMD=/opt/homebrew/bin/python3.11
    echo -e "${GREEN}✓ Python 3.11 installed${NC}"
else
    echo -e "${GREEN}✓ Python 3.11+ found: $PYTHON_CMD${NC}"
fi

# Check for Ollama
if ! command -v ollama >/dev/null 2>&1; then
    echo -e "${YELLOW}Ollama not found. Installing...${NC}"
    brew install ollama
    echo -e "${GREEN}✓ Ollama installed${NC}"
else
    echo -e "${GREEN}✓ Ollama found${NC}"
fi

# Function to check if a port is in use
check_port() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local name=$2
    local max_wait=30
    local count=0

    echo -e "${YELLOW}⏳ Waiting for $name to be ready...${NC}"
    while [ $count -lt $max_wait ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✓ $name is ready${NC}"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done

    echo -e "${RED}✗ $name failed to start within ${max_wait}s${NC}"
    return 1
}

# 1. Check Ollama
echo ""
echo -e "${BLUE}[1/4] Checking Ollama...${NC}"
if ! check_port 11434; then
    echo -e "${YELLOW}Starting Ollama...${NC}"
    ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
fi

if wait_for_service "http://localhost:11434/api/tags" "Ollama"; then
    # Check if required models are available
    echo -e "${YELLOW}Checking VLM models...${NC}"
    MODELS=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | cut -d'"' -f4)

    # Check for qwen3-vl:8b-instruct (primary model)
    if echo "$MODELS" | grep -q "qwen3-vl:8b-instruct"; then
        echo -e "${GREEN}✓ qwen3-vl:8b-instruct model available${NC}"
    else
        echo -e "${YELLOW}⚠ qwen3-vl:8b-instruct not found${NC}"
        echo -e "${YELLOW}Pulling model (this may take 5-10 minutes)...${NC}"
        ollama pull qwen3-vl:8b-instruct
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Model downloaded successfully${NC}"
        else
            echo -e "${RED}✗ Failed to download model${NC}"
            echo -e "${YELLOW}You can manually pull it later with: ollama pull qwen3-vl:8b-instruct${NC}"
        fi
    fi
else
    echo -e "${RED}✗ Failed to start Ollama${NC}"
    exit 1
fi

# 2. NATS (optional - needed for event publishing)
echo ""
echo -e "${BLUE}[2/4] NATS...${NC}"
echo -e "${YELLOW}Skipping NATS (optional for testing)${NC}"
echo -e "${YELLOW}VLM service will work without NATS for direct API calls${NC}"

# 3. Start VLM Service (local Python)
echo ""
echo -e "${BLUE}[3/4] Starting VLM Service...${NC}"

# Check if venv exists
if [ ! -d "services/nura-vlm/.venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    cd services/nura-vlm
    $PYTHON_CMD -m venv .venv
    source .venv/bin/activate
    echo -e "${YELLOW}Installing dependencies (this may take 2-3 minutes)...${NC}"
    pip install -q --upgrade pip setuptools wheel
    pip install -q -r requirements.local.txt
    cd "$PROJECT_ROOT"
    echo -e "${GREEN}✓ Virtual environment created and dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

# Kill any existing VLM service
if check_port 8001; then
    echo -e "${YELLOW}Stopping existing VLM service on port 8001...${NC}"
    kill $(lsof -t -i:8001) 2>/dev/null || true
    sleep 2
fi

# Start VLM service in background
echo -e "${YELLOW}Starting VLM service...${NC}"
cd services/nura-vlm
source .venv/bin/activate

# Load environment variables from .env file if it exists
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a  # Auto-export all variables
    source "$PROJECT_ROOT/.env"
    set +a
    echo -e "${GREEN}✓ Loaded configuration from .env${NC}"
else
    echo -e "${YELLOW}⚠ No .env file found, using defaults${NC}"
    # Set default environment variables
    export OLLAMA_URL="http://localhost:11434"
    export VLM_MODEL="llava:13b"
    export NATS_URL="nats://localhost:4222"
    export VLM_SERVICE_PORT=8001

    # Default thresholds
    export DIRECT_ALERT_VIOLENCE_THRESHOLD=0.65
    export DIRECT_ALERT_BODY_LANGUAGE_THRESHOLD=0.70
    export DIRECT_ALERT_DISTRESS_THRESHOLD=0.70
    export DIRECT_ALERT_SUPERVISION_THRESHOLD=0.80

    export BODY_LANGUAGE_SCORE_THRESHOLD_LOW=2.5
    export BODY_LANGUAGE_SCORE_THRESHOLD_HIGH=3.0
    export BODY_LANGUAGE_INDICATOR_COUNT_LOW=2
    export BODY_LANGUAGE_INDICATOR_COUNT_HIGH=3
fi

# Backwards compatibility: PORT is used in main.py
export PORT=${VLM_SERVICE_PORT:-8001}

# Start service (log to file)
nohup python -m src.main > ../../logs/vlm-service.log 2>&1 &
VLM_PID=$!
echo $VLM_PID > ../../.vlm.pid

cd "$PROJECT_ROOT"

# Wait for VLM to be ready
if wait_for_service "http://localhost:8001/health" "VLM Service"; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          ✓ All Services Started Successfully              ║${NC}"
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo ""
    echo -e "${BLUE}Service Status:${NC}"
    echo -e "  ${GREEN}•${NC} Ollama (VLM):        http://localhost:11434"
    echo -e "  ${GREEN}•${NC} VLM Service (API):   http://localhost:8001"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo -e "  ${YELLOW}1.${NC} Test the system:  ${YELLOW}./test-images.sh${NC}"
    echo -e "  ${YELLOW}2.${NC} Check health:     ${YELLOW}curl http://localhost:8001/health${NC}"
    echo -e "  ${YELLOW}3.${NC} View logs:        ${YELLOW}tail -f logs/vlm-service.log${NC}"
    echo -e "  ${YELLOW}4.${NC} Stop services:    ${YELLOW}./stop.sh${NC}"
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo -e "  ${YELLOW}•${NC} Quick Start: ${YELLOW}less QUICK_START.md${NC}"
    echo -e "  ${YELLOW}•${NC} README:      ${YELLOW}less README.md${NC}"
    echo ""
else
    echo -e "${RED}✗ VLM Service failed to start${NC}"
    echo -e "${YELLOW}Check logs: tail -f logs/vlm-service.log${NC}"
    exit 1
fi
