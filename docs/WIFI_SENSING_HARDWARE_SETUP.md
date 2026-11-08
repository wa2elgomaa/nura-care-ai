# WiFi Sensing Hardware Setup Guide

**Service**: nura-wifi-sensing  
**Hardware**: ESP32 + RuView WiFi Sensing  
**Purpose**: Real-time occupancy detection using WiFi signals

## Overview

The nura-wifi-sensing service receives real-time occupancy data from **ESP32 devices running RuView WiFi sensing firmware**. This provides coverage in camera-free zones like bathrooms, storage rooms, and kitchens.

## Architecture

```
Your WiFi Network
  ↓
ESP32 Nodes (WiFi Sensing)
  ↓
RuView Firmware (CSI processing)
  ↓
MQTT Broker (mosquitto)
  ↓
nura-wifi-sensing Service
  ↓
Database + NATS Alerts
```

## Hardware Requirements

### ESP32 Nodes (Per Room)
- **Minimum**: 2 ESP32 boards per room (for triangulation)
- **Recommended**: 3-4 ESP32 boards per room (better accuracy)
- **Supported Models**:
  - ESP32-WROOM-32
  - ESP32-DevKitC
  - ESP32-S3
  - Any ESP32 with WiFi CSI support

### What You Need
- ESP32 development boards (2-4 per room)
- USB cables for power
- WiFi network (2.4GHz - ESP32 requirement)
- MQTT broker (already running in Docker: mosquitto)

## Software Setup

### Option 1: RuView Firmware (Recommended)
RuView is **open source** WiFi sensing firmware for ESP32 (MIT License - FREE!).

**GitHub**: https://github.com/ruvnet/ruview

**Steps:**
1. Clone RuView repository: `git clone https://github.com/ruvnet/ruview`
2. Flash RuView firmware to ESP32 boards
3. Configure MQTT broker connection
4. Configure room zones

**MQTT Configuration (on ESP32):**
```ini
MQTT_BROKER=<your-server-ip>  # e.g., 192.168.1.100
MQTT_PORT=1883
MQTT_TOPIC_PREFIX=ruview/occupancy/
```

**Room Configuration:**
Each ESP32 publishes to: `ruview/occupancy/<room_id>`

Example topics:
- `ruview/occupancy/bathroom_boys_1f`
- `ruview/occupancy/bathroom_girls_1f`
- `ruview/occupancy/storage_main`
- `ruview/occupancy/kitchen`

### Option 2: ESP-WiFi-CSI (Alternative Open Source)

If you prefer a different open source implementation:

**GitHub**: https://github.com/StevenMHernandez/ESP32-CSI-Tool

**Steps:**
1. Clone the repo
2. Flash to ESP32 boards
3. Build custom CSI processing pipeline
4. Publish to MQTT in RuView-compatible format

**Message Format (JSON):**
```json
{
  "room_id": "bathroom_boys_1f",
  "room_type": "bathroom",
  "occupancy_count": 2,
  "device_count": 3,
  "timestamp": "2026-11-08T10:30:00Z",
  "esp32_nodes": ["AA:BB:CC:DD:EE:01", "AA:BB:CC:DD:EE:02"]
}
```

## Network Configuration

### 1. Expose MQTT Broker to Local Network

Currently, mosquitto runs in Docker and is only accessible from containers. To allow ESP32 devices to connect:

**Edit `compose.yaml`:**
```yaml
mosquitto:
  image: eclipse-mosquitto:2
  ports:
    - "1883:1883"  # Expose MQTT port to host network
    - "9001:9001"  # Optional: WebSocket
  volumes:
    - ./edge/mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf
  networks:
    - nura-network
```

**Create/Update `edge/mosquitto/mosquitto.conf`:**
```conf
listener 1883
allow_anonymous true

# For production, add authentication:
# allow_anonymous false
# password_file /mosquitto/config/passwd
```

**Restart mosquitto:**
```bash
docker compose up -d mosquitto
```

**Test MQTT is accessible:**
```bash
# From your laptop (not Docker)
mosquitto_sub -h localhost -t 'ruview/occupancy/#' -v

# From ESP32, use your server's IP:
# mosquitto_sub -h 192.168.1.100 -t 'ruview/occupancy/#' -v
```

### 2. Find Your Server IP

```bash
# macOS
ipconfig getifaddr en0

# Linux
ip addr show | grep inet

# Example: 192.168.1.100
```

### 3. Configure ESP32 to Connect

In RuView or your custom firmware:
```ini
WIFI_SSID=YourWiFiNetwork
WIFI_PASSWORD=YourWiFiPassword
MQTT_BROKER=192.168.1.100  # Your server IP
MQTT_PORT=1883
MQTT_TOPIC=ruview/occupancy/bathroom_boys_1f
```

## Room Configuration in Database

The database already has sample rooms configured. To add your own:

```sql
-- Connect to database
docker exec -it $(docker ps -q -f name=postgres) psql -U nura -d nura_db

-- Add new room
INSERT INTO wifi_rooms (
  room_id, room_name, room_type,
  multi_occupancy_threshold, multi_occupancy_duration_seconds,
  operating_hours_start, operating_hours_end
) VALUES (
  'bathroom_boys_2f',           -- Unique room ID (matches MQTT topic)
  'Boys Bathroom 2F',            -- Display name
  'bathroom',                    -- Type
  2,                             -- Alert if 2+ people
  120,                           -- For more than 2 minutes
  '06:00:00',                    -- Operating hours start
  '18:00:00'                     -- Operating hours end
);
```

**Room Types:**
- `bathroom` - Multi-occupancy alerts enabled
- `storage` - After-hours alerts only
- `kitchen` - Both alerts
- `mechanical` - After-hours only

## Testing

### Simulate MQTT Messages (Without Hardware)

Test the system before buying ESP32 boards:

```bash
# Publish simulated occupancy event
mosquitto_pub -h localhost -t 'ruview/occupancy/bathroom_boys_1f' \
  -m '{
    "room_id": "bathroom_boys_1f",
    "room_type": "bathroom",
    "occupancy_count": 2,
    "device_count": 3,
    "timestamp": "2026-11-08T10:30:00Z",
    "esp32_nodes": ["AA:BB:CC:DD:EE:01", "AA:BB:CC:DD:EE:02"]
  }'

# Check WiFi sensing logs
docker compose logs nura-wifi-sensing -f

# Expected output:
# [WiFiSensingService] Multi-occupancy detected: bathroom_boys_1f (2 people)
```

### Publish Multiple Events (Simulate 2+ Minutes)

```bash
# Send events every 5 seconds for 3 minutes
for i in {1..36}; do
  mosquitto_pub -h localhost -t 'ruview/occupancy/bathroom_boys_1f' \
    -m "{\"room_id\":\"bathroom_boys_1f\",\"occupancy_count\":2,\"device_count\":3,\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
  sleep 5
done

# After 2 minutes (24 events), alert should be published to NATS
```

### Check Database for Events

```sql
-- View WiFi events
SELECT * FROM wifi_sensing_events 
ORDER BY timestamp DESC 
LIMIT 10;

-- Check alerts generated
SELECT * FROM alerts 
WHERE data_source = 'wifi' 
ORDER BY created_at DESC 
LIMIT 5;
```

### Monitor NATS Alerts

```bash
# Subscribe to NATS violations channel
docker exec -it $(docker ps -q -f name=nats) \
  nats sub violations.detected

# Expected alert format:
# {
#   "type": "wifi_anomaly",
#   "data_source": "wifi",
#   "severity": "high",
#   "confidence": 0.9,
#   "wifi_event": {
#     "room_id": "bathroom_boys_1f",
#     "anomaly_type": "multi_occupancy",
#     "occupancy_count": 2,
#     "duration_seconds": 125
#   }
# }
```

## Real Hardware Deployment

### Step-by-Step Deployment

**1. Purchase Hardware**
- 2-4 ESP32 boards per room
- USB power adapters
- Optional: 3D-printed enclosures

**2. Flash Firmware**
Choose RuView (commercial) or ESP-WiFi-CSI (open source)

**3. Mount ESP32 Boards**
- Place 2-4 boards around room perimeter
- Height: 6-8 feet (ceiling or high walls)
- Power: USB adapters or PoE injectors

**4. Configure MQTT Connection**
- Set your server IP
- Set room_id to match database

**5. Test Each Room**
```bash
# Subscribe to all room topics
mosquitto_sub -h localhost -t 'ruview/occupancy/#' -v

# Walk into room, verify occupancy_count increases
# Walk out, verify occupancy_count decreases
```

**6. Calibrate Thresholds**
Adjust per room in database:
```sql
UPDATE wifi_rooms 
SET multi_occupancy_threshold = 3  -- Adjust based on false positives
WHERE room_id = 'bathroom_boys_1f';
```

## Example Room Layouts

### Bathroom (2-4 ESP32 boards)
```
┌─────────────────────┐
│  [ESP32]            │
│                     │
│    🚽  🚽  🚽      │
│                     │
│            [ESP32]  │
└─────────────────────┘
```

### Storage Room (2 ESP32 boards)
```
┌─────────────────────┐
│ [ESP32]             │
│                     │
│   📦 📦 📦         │
│   📦 📦 📦         │
│                     │
│             [ESP32] │
└─────────────────────┘
```

### Kitchen (3-4 ESP32 boards)
```
┌─────────────────────────┐
│ [ESP32]       [ESP32]   │
│                         │
│   🍳  🍳  🍳           │
│                         │
│ [ESP32]                 │
└─────────────────────────┘
```

## Troubleshooting

### ESP32 Not Connecting to MQTT
```bash
# Check mosquitto is listening
netstat -an | grep 1883

# Check firewall allows port 1883
sudo ufw allow 1883

# Test from ESP32's network
mosquitto_pub -h <your-server-ip> -t 'test' -m 'hello'
```

### No Events in Database
```bash
# Check WiFi sensing service logs
docker compose logs nura-wifi-sensing -f

# Check MQTT subscription
docker exec -it $(docker ps -q -f name=mosquitto) \
  mosquitto_sub -t 'ruview/occupancy/#' -v

# Verify room exists in database
docker exec -it $(docker ps -q -f name=postgres) psql -U nura -d nura_db \
  -c "SELECT * FROM wifi_rooms;"
```

### False Positives
- Adjust `multi_occupancy_threshold` higher
- Increase `multi_occupancy_duration_seconds`
- Add more ESP32 boards for better triangulation

### False Negatives
- Lower `multi_occupancy_threshold`
- Add more ESP32 boards
- Check ESP32 placement (too close together)

## Production Recommendations

### Security
```yaml
# compose.yaml - Add authentication
mosquitto:
  environment:
    - MOSQUITTO_USERNAME=nura
    - MOSQUITTO_PASSWORD=${MQTT_PASSWORD}  # From .env
```

### Monitoring
```bash
# Monitor WiFi events/minute
watch -n 5 'docker exec -it $(docker ps -q -f name=postgres) psql -U nura -d nura_db \
  -c "SELECT COUNT(*) FROM wifi_sensing_events WHERE timestamp > NOW() - INTERVAL '\''1 minute'\'';"'
```

### Alerts
- Multi-occupancy: 2+ people in bathroom >2 min
- After-hours: Movement outside 6am-6pm
- No activity: ESP32 offline (implement heartbeat check)

## Cost Estimate

**ESP32 Boards:**
- $5-10 per board
- 2-4 boards per room
- Example: 4 rooms × 3 boards = 12 boards × $7 = **~$84**

**Software (Both FREE!):**
- **RuView**: https://github.com/ruvnet/ruview (MIT License - FREE)
- **ESP-WiFi-CSI**: https://github.com/StevenMHernandez/ESP32-CSI-Tool (FREE)

**Total for 4 Rooms:**
- **Hardware only: ~$84** (both software options are free!)

## Next Steps

1. **Test with simulation** (mosquitto_pub) - No hardware needed
2. **Buy 2-3 ESP32 boards** - Test one room (~$15-30)
3. **Choose firmware** - RuView (recommended, MIT license) or ESP-WiFi-CSI (more DIY)
4. **Deploy to one room** - Verify alerts work
5. **Scale to all rooms** - Purchase more boards

---

**WiFi Sensing Status: ✅ SERVICE RUNNING**  
**Ready for Hardware Integration!**  
**Simulation Testing Available Now!**
