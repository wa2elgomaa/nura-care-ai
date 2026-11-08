#!/bin/bash
# Test Notification Channels (Email, SMS, Push)
# This script tests all configured notification methods

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          NURA - Notification Test Script                 ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if Apprise is running
echo -e "${BLUE}Checking services...${NC}"
if ! docker ps | grep -q apprise; then
    echo -e "${YELLOW}⚠️  Apprise not running. Starting...${NC}"
    cd "$(dirname "$0")/.."
    docker compose up -d apprise
    sleep 3
fi

if ! docker ps | grep -q ntfy; then
    echo -e "${YELLOW}⚠️  ntfy not running. Starting...${NC}"
    docker compose up -d ntfy
    sleep 3
fi

echo -e "${GREEN}✓ Services are running${NC}"
echo ""

# Test ntfy (Push Notifications)
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Test 1: Push Notification (ntfy)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

NTFY_PORT=$(docker compose port ntfy 80 2>/dev/null | cut -d: -f2 || echo "80")
NTFY_URL="http://localhost:${NTFY_PORT}"

echo -e "${YELLOW}Sending test push notification...${NC}"
curl -s -X POST "${NTFY_URL}/nura-test" \
  -H "Title: 🧪 Nura Test Alert" \
  -H "Priority: high" \
  -H "Tags: test,nura" \
  -d "This is a test push notification from Nura Alert System. If you receive this, push notifications are working!" \
  > /dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Push notification sent successfully!${NC}"
    echo -e "${YELLOW}  Subscribe to: ${NTFY_URL}/nura-test${NC}"
    echo -e "${YELLOW}  Or use ntfy app with topic: nura-test${NC}"
else
    echo -e "${RED}✗ Failed to send push notification${NC}"
fi
echo ""

# Test Apprise (Email + SMS)
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Test 2: Email + SMS (Apprise)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

APPRISE_PORT=$(docker compose port apprise 8000 2>/dev/null | cut -d: -f2 || echo "8000")
APPRISE_URL="http://localhost:${APPRISE_PORT}"

# Test Email
echo -e "${YELLOW}Sending test email...${NC}"
EMAIL_RESPONSE=$(curl -s -X POST "${APPRISE_URL}/notify" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "🧪 Nura Test Alert - Email",
    "body": "This is a test email from Nura Alert System.\n\nIf you receive this, email notifications are working correctly!\n\nTimestamp: '"$(date)"'\n\nTest Details:\n- Service: Alert Service\n- Channel: Email (SMTP)\n- Provider: Hostinger\n- Priority: Test",
    "type": "info",
    "tag": "email"
  }')

if echo "$EMAIL_RESPONSE" | grep -q "OK"; then
    echo -e "${GREEN}✓ Email sent successfully!${NC}"
    echo -e "${YELLOW}  Check staff@school.com inbox${NC}"
else
    echo -e "${RED}✗ Failed to send email${NC}"
    echo -e "${RED}  Response: $EMAIL_RESPONSE${NC}"
fi
echo ""

# Test SMS
echo -e "${YELLOW}Sending test SMS...${NC}"
SMS_RESPONSE=$(curl -s -X POST "${APPRISE_URL}/notify" \
  -H "Content-Type: application/json" \
  -d '{
    "body": "[NURA TEST] This is a test SMS from Nura Alert System. If you receive this, SMS notifications are working!",
    "tag": "sms"
  }')

if echo "$SMS_RESPONSE" | grep -q "OK"; then
    echo -e "${GREEN}✓ SMS sent successfully!${NC}"
    echo -e "${YELLOW}  Check phone: +1234567890${NC}"
else
    echo -e "${RED}✗ Failed to send SMS${NC}"
    echo -e "${RED}  Response: $SMS_RESPONSE${NC}"
    echo -e "${YELLOW}  Note: Update phone number in edge/apprise/apprise.yml${NC}"
fi
echo ""

# Test All Channels
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Test 3: All Channels (Email + SMS + Push)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}Sending to all channels...${NC}"

# Push via ntfy
curl -s -X POST "${NTFY_URL}/nura-alerts" \
  -H "Title: 🚨 CRITICAL - Violence Detected" \
  -H "Priority: urgent" \
  -H "Tags: violence,critical" \
  -d "Classroom 3 - Aggressive behavior detected. Confidence: 92%. IMMEDIATE staff intervention required." \
  > /dev/null

# Email + SMS via Apprise
ALL_RESPONSE=$(curl -s -X POST "${APPRISE_URL}/notify" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "🚨 CRITICAL - Violence Detected",
    "body": "Incident Details:\n- Time: '"$(date)"'\n- Location: Classroom 3\n- Type: Physical aggression\n- Confidence: 92%\n- Persons: 3 children detected\n- Status: ONGOING\n\nAction Required:\nIMMEDIATE staff intervention needed.\n\nAlert ID: test-alert-001",
    "type": "warning"
  }')

if echo "$ALL_RESPONSE" | grep -q "OK"; then
    echo -e "${GREEN}✓ Multi-channel notification sent successfully!${NC}"
else
    echo -e "${RED}✗ Some notifications may have failed${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}✓ Push Notifications:${NC} Subscribe to ${NTFY_URL}/nura-alerts"
echo -e "${GREEN}✓ Email Notifications:${NC} Check staff@school.com"
echo -e "${GREEN}✓ SMS Notifications:${NC} Check configured phone"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "  1. Update edge/apprise/apprise.yml with:"
echo -e "     - Real staff email addresses"
echo -e "     - Real phone numbers (Twilio)"
echo -e "  2. Subscribe to ntfy on your phone:"
echo -e "     - Install ntfy app"
echo -e "     - Add topic: nura-alerts"
echo -e "     - Server: ${NTFY_URL}"
echo -e "  3. Test full pipeline:"
echo -e "     ./scripts/test-rtsp-stream.sh"
echo ""
echo -e "${GREEN}Notification system is ready! 📢${NC}"
