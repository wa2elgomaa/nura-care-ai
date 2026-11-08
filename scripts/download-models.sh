#!/bin/bash
# Download production models from registry
# Automatically run by start.sh if models missing

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MODELS_DIR="$PROJECT_ROOT/models"
REGISTRY_FILE="$MODELS_DIR/model_registry.json"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Downloading Production Models                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if model registry exists
if [ ! -f "$REGISTRY_FILE" ]; then
    echo -e "${RED}✗ Model registry not found: $REGISTRY_FILE${NC}"
    exit 1
fi

# Check if jq is installed for JSON parsing
if ! command -v jq >/dev/null 2>&1; then
    echo -e "${YELLOW}Installing jq for JSON parsing...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install jq
    else
        sudo apt-get install -y jq
    fi
fi

# Create models directory if it doesn't exist
mkdir -p "$MODELS_DIR"

# Parse model registry
echo -e "${BLUE}Reading model registry...${NC}"
MODELS=$(jq -r '.models | keys[]' "$REGISTRY_FILE")

DOWNLOAD_COUNT=0
SKIP_COUNT=0
ERROR_COUNT=0

for MODEL_NAME in $MODELS; do
    # Get model metadata
    FILENAME=$(jq -r ".models.\"$MODEL_NAME\".filename" "$REGISTRY_FILE")
    URL=$(jq -r ".models.\"$MODEL_NAME\".download_url" "$REGISTRY_FILE")
    SHA256=$(jq -r ".models.\"$MODEL_NAME\".sha256" "$REGISTRY_FILE")
    REQUIRED=$(jq -r ".models.\"$MODEL_NAME\".required" "$REGISTRY_FILE")
    SIZE_MB=$(jq -r ".models.\"$MODEL_NAME\".size_mb" "$REGISTRY_FILE")
    VERSION=$(jq -r ".models.\"$MODEL_NAME\".version" "$REGISTRY_FILE")

    MODEL_PATH="$MODELS_DIR/$FILENAME"

    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Model: $MODEL_NAME${NC} (v$VERSION, $SIZE_MB MB)"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Check if model already exists and is valid
    if [ -f "$MODEL_PATH" ]; then
        echo -e "${YELLOW}  Verifying existing model...${NC}"

        # Skip checksum verification if placeholder
        if [ "$SHA256" = "PLACEHOLDER" ] || [ "$SHA256" = "PLACEHOLDER_UPDATE_AFTER_UPLOAD" ]; then
            echo -e "${GREEN}  ✓ Model exists (checksum verification skipped - placeholder)${NC}"
            SKIP_COUNT=$((SKIP_COUNT + 1))
            continue
        fi

        CURRENT_SHA256=$(shasum -a 256 "$MODEL_PATH" | awk '{print $1}')

        if [ "$CURRENT_SHA256" = "$SHA256" ]; then
            echo -e "${GREEN}  ✓ Model already downloaded and verified${NC}"
            SKIP_COUNT=$((SKIP_COUNT + 1))
            continue
        else
            echo -e "${YELLOW}  ⚠ Checksum mismatch, re-downloading...${NC}"
            echo -e "${YELLOW}    Expected: $SHA256${NC}"
            echo -e "${YELLOW}    Got:      $CURRENT_SHA256${NC}"
            rm "$MODEL_PATH"
        fi
    fi

    # Skip download if URL is placeholder
    if [[ "$URL" == *"YOUR_ORG"* ]] || [ "$URL" = "null" ]; then
        echo -e "${YELLOW}  ⚠ Model URL not configured (placeholder)${NC}"
        if [ "$REQUIRED" = "true" ]; then
            echo -e "${YELLOW}    This is a required model. Please:${NC}"
            echo -e "${YELLOW}    1. Upload model to GitHub Releases${NC}"
            echo -e "${YELLOW}    2. Update download_url in model_registry.json${NC}"
            echo -e "${YELLOW}    3. Run this script again${NC}"
            echo ""
            echo -e "${YELLOW}    For now, skipping (assuming model exists locally)...${NC}"
        fi
        SKIP_COUNT=$((SKIP_COUNT + 1))
        continue
    fi

    # Download model
    if [ "$REQUIRED" = "true" ]; then
        echo -e "${YELLOW}  ⬇ Downloading required model: $FILENAME ($SIZE_MB MB)...${NC}"
    else
        echo -e "${YELLOW}  ⬇ Downloading optional model: $FILENAME ($SIZE_MB MB)...${NC}"
        echo -e "${YELLOW}    Press Ctrl+C within 3s to skip...${NC}"
        sleep 3
    fi

    # Use curl with progress bar
    if ! curl -L --progress-bar "$URL" -o "$MODEL_PATH"; then
        if [ "$REQUIRED" = "true" ]; then
            echo -e "${RED}  ✗ Failed to download required model${NC}"
            ERROR_COUNT=$((ERROR_COUNT + 1))
        else
            echo -e "${YELLOW}  ⚠ Failed to download optional model (skipping)${NC}"
            SKIP_COUNT=$((SKIP_COUNT + 1))
        fi
        continue
    fi

    # Verify checksum (skip if placeholder)
    if [ "$SHA256" != "PLACEHOLDER" ] && [ "$SHA256" != "PLACEHOLDER_UPDATE_AFTER_UPLOAD" ]; then
        echo -e "${YELLOW}  Verifying checksum...${NC}"
        DOWNLOADED_SHA256=$(shasum -a 256 "$MODEL_PATH" | awk '{print $1}')

        if [ "$DOWNLOADED_SHA256" != "$SHA256" ]; then
            echo -e "${RED}  ✗ Checksum verification failed!${NC}"
            echo -e "${RED}    Expected: $SHA256${NC}"
            echo -e "${RED}    Got:      $DOWNLOADED_SHA256${NC}"
            rm "$MODEL_PATH"
            ERROR_COUNT=$((ERROR_COUNT + 1))

            if [ "$REQUIRED" = "true" ]; then
                echo -e "${RED}  ✗ Required model failed verification${NC}"
            fi
            continue
        fi
    fi

    echo -e "${GREEN}  ✓ Model downloaded successfully${NC}"
    DOWNLOAD_COUNT=$((DOWNLOAD_COUNT + 1))
done

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Summary                                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Downloaded: ${GREEN}$DOWNLOAD_COUNT${NC}"
echo -e "  Skipped:    ${YELLOW}$SKIP_COUNT${NC} (already exists or placeholder)"
echo -e "  Errors:     ${RED}$ERROR_COUNT${NC}"
echo ""

if [ $ERROR_COUNT -gt 0 ]; then
    echo -e "${YELLOW}⚠ Some models failed to download${NC}"
    echo -e "${YELLOW}  Check errors above and retry${NC}"
    exit 1
elif [ $DOWNLOAD_COUNT -gt 0 ]; then
    echo -e "${GREEN}✓ All required models downloaded successfully${NC}"
else
    echo -e "${GREEN}✓ All models already present${NC}"
fi
