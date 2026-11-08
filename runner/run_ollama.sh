#!/bin/bash
# Run Ollama service with VLM models
# Usage: ./scripts/run_ollama.sh

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting Ollama Service...${NC}"

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

# Check if Ollama is installed
if ! command -v ollama >/dev/null 2>&1; then
    echo -e "${RED}✗ Ollama not found${NC}"
    echo -e "${YELLOW}Install with: brew install ollama${NC}"
    exit 1
fi

# Start Ollama if not running
if ! check_port 11434; then
    echo -e "${YELLOW}Starting Ollama on port 11434...${NC}"
    ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
else
    echo -e "${GREEN}✓ Ollama already running on port 11434${NC}"
fi

# Wait for Ollama to be ready
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
            exit 1
        fi
    fi

    echo ""
    echo -e "${GREEN}✓ Ollama Service Ready${NC}"
    echo -e "  URL: http://localhost:11434"
    echo -e "  Logs: tail -f /tmp/ollama.log"
    echo -e "  Stop: killall ollama"
else
    echo -e "${RED}✗ Failed to start Ollama${NC}"
    exit 1
fi
