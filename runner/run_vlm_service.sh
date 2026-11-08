#!/bin/bash
# Run VLM Service (Vision-Language Model AI Service)
# Usage: ./scripts/run_vlm_service.sh

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}Starting VLM Service...${NC}"

# Function to detect Python 3.11+
detect_python() {
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

# Check for Python 3.11+
PYTHON_CMD=$(detect_python)
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Python 3.11+ not found${NC}"
    echo -e "${YELLOW}Install with: brew install python@3.11${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python found: $PYTHON_CMD${NC}"

# Check if Ollama is running
if ! check_port 11434; then
    echo -e "${YELLOW}⚠ Ollama not running on port 11434${NC}"
    echo -e "${YELLOW}Start Ollama first: ./scripts/run_ollama.sh${NC}"
    exit 1
fi

# Create venv if needed
if [ ! -d "services/nura-vlm/.venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    cd services/nura-vlm
    $PYTHON_CMD -m venv .venv
    source .venv/bin/activate

    echo -e "${YELLOW}Installing dependencies (this may take 2-3 minutes)...${NC}"
    pip install -q --upgrade pip setuptools wheel
    pip install -q -r requirements.local.txt

    # Install nura-detectors package
    echo -e "${YELLOW}Installing nura-detectors package...${NC}"
    pip install -q -e ../../packages/nura-detectors
    pip install -q "numpy==1.26.4" "protobuf==4.25.5" "ml-dtypes==0.2.0" "onnxruntime==1.16.3" "onnx==1.15.0"

    # Install Phase 4B dependencies
    pip install -q psycopg2-binary pgvector fastapi uvicorn python-multipart

    # Try InsightFace (best accuracy)
    if pip install -q insightface onnxruntime 2>/dev/null; then
        echo -e "${GREEN}✓ InsightFace installed (best accuracy)${NC}"
    elif pip install -q face-recognition 2>/dev/null; then
        echo -e "${GREEN}✓ face_recognition installed${NC}"
    else
        echo -e "${YELLOW}⚠ Face recognition backends unavailable${NC}"
    fi

    cd "$PROJECT_ROOT"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

# Load environment from .env
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
    echo -e "${GREEN}✓ Loaded configuration from .env${NC}"
else
    echo -e "${YELLOW}⚠ No .env file found, using defaults${NC}"
    export OLLAMA_URL="http://localhost:11434"
    export VLM_MODEL="qwen3-vl:8b-instruct"
    export NATS_URL="nats://localhost:4222"
    export VLM_SERVICE_PORT=8001
fi

# Backwards compatibility
export PORT=${VLM_SERVICE_PORT:-8001}

# Kill existing service
if check_port $PORT; then
    echo -e "${YELLOW}Stopping existing VLM service on port $PORT...${NC}"
    kill $(lsof -t -i:$PORT) 2>/dev/null || true
    sleep 2
fi

# Create logs directory
mkdir -p logs

# Start VLM service
echo -e "${YELLOW}Starting VLM service on port $PORT...${NC}"
cd services/nura-vlm
source .venv/bin/activate
nohup python -m src.main > ../../logs/vlm-service.log 2>&1 &
VLM_PID=$!
echo $VLM_PID > ../../.vlm.pid
cd "$PROJECT_ROOT"

# Wait for service
if wait_for_service "http://localhost:$PORT/health" "VLM Service"; then
    echo ""
    echo -e "${GREEN}✓ VLM Service Started Successfully${NC}"
    echo -e "  URL: http://localhost:$PORT"
    echo -e "  Health: http://localhost:$PORT/health"
    echo -e "  Logs: tail -f logs/vlm-service.log"
    echo -e "  PID: $VLM_PID (saved to .vlm.pid)"
    echo -e "  Stop: kill \$(cat .vlm.pid)"
else
    echo -e "${RED}✗ VLM Service failed to start${NC}"
    echo -e "${YELLOW}Check logs: tail -f logs/vlm-service.log${NC}"
    exit 1
fi
