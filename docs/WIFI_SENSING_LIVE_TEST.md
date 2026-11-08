# WiFi Sensing - Live Testing on Home Network

**Goal**: Test WiFi sensing with real ESP32 hardware on your home network  
**Time**: 30-60 minutes  
**Cost**: $15-30 for ESP32 boards

---

## Quick Start (What You Need)

### Hardware
- **2-3 ESP32 boards** ($5-10 each on Amazon/AliExpress)
  - ESP32-DevKitC (recommended)
  - ESP32-WROOM-32
  - ESP32-S3
- **USB cables** for power (Micro-USB or USB-C depending on board)
- **WiFi network** (2.4GHz - ESP32 requirement)

### Software (Already Running!)
- ✅ MQTT Broker (mosquitto in Docker)
- ✅ WiFi Sensing Service (nura-wifi-sensing)
- ✅ Database (postgres)
- ✅ NATS (alert pipeline)

---

## Step-by-Step Setup

### Step 1: Expose MQTT to Your Network (5 minutes)

Currently, MQTT runs in Docker and is only accessible from containers. Let's expose it to your home network:

**1. Edit `compose.yaml`:**
```bash
cd '/Users/wgomaa/Work/PixelPlusOne/Nura Childcare AI/nura-care-source'
```

Find the `mosquitto` service and add port mapping:

```yaml
mosquitto:
  image: eclipse-mosquitto:2
  ports:
    - "1883:1883"  # ADD THIS LINE
  volumes:
    - ./edge/mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf
  networks:
    - nura-network
```

**2. Restart mosquitto:**
```bash
docker compose up -d mosquitto
```

**3. Verify MQTT is accessible:**
```bash
# From your Mac
mosquitto_sub -h localhost -t 'ruview/occupancy/#' -v

# You should see: (waiting for messages...)
# Press Ctrl+C to exit
```

### Step 2: Get Your Mac's IP Address (1 minute)

ESP32 boards need to connect to your Mac's IP on your home network:

```bash
# Get WiFi IP address
ipconfig getifaddr en0

# Example output: 192.168.1.100
```

**Save this IP address** - you'll need it for ESP32 configuration.

### Step 3: Test MQTT from Another Device (Optional - 2 minutes)

Verify MQTT is accessible from your network:

```bash
# From another computer on your network (or your phone with MQTT app)
mosquitto_pub -h 192.168.1.100 -t 'ruview/occupancy/test' -m '{"test":"hello"}'

# On your Mac, subscribe to see the message:
mosquitto_sub -h localhost -t 'ruview/occupancy/#' -v
```

### Step 4: Choose & Flash Firmware (20-30 minutes)

**Option 1: RuView (Recommended - FREE & MIT License)**

**GitHub**: https://github.com/ruvnet/ruview

```bash
# Clone RuView
git clone https://github.com/ruvnet/ruview
cd ruview

# Follow RuView setup instructions:
# 1. Install ESP-IDF or Arduino IDE
# 2. Configure WiFi & MQTT settings
# 3. Flash to ESP32
```

**Configuration (in RuView code):**
```c
// WiFi Configuration
#define WIFI_SSID "YourHomeWiFiName"
#define WIFI_PASSWORD "YourWiFiPassword"

// MQTT Configuration
#define MQTT_BROKER "192.168.1.100"  // Your Mac's IP
#define MQTT_PORT 1883
#define MQTT_TOPIC "ruview/occupancy/test_room"
```

**Option 2: ESP-WiFi-CSI (More DIY)**

```bash
# Clone ESP-WiFi-CSI
git clone https://github.com/StevenMHernandez/ESP32-CSI-Tool
cd ESP32-CSI-Tool

# Follow setup instructions
# Build custom CSI processing
# Configure MQTT publishing
```

### Step 5: Deploy ESP32 Boards (5 minutes)

**For Testing (One Room):**

1. **Power on 2-3 ESP32 boards** (USB power from wall adapters or computer)
2. **Place them around a test area**:
   - Corners of a room
   - 6-8 feet high if possible (top of bookshelf, mounted on wall)
   - At least 6 feet apart

**Example Setup (Living Room Test):**
```
┌─────────────────────────────┐
│  [ESP32-1]                  │
│                             │
│       (Your Test Area)      │
│                             │
│                  [ESP32-2]  │
│                             │
│  [ESP32-3]                  │
└─────────────────────────────┘
```

### Step 6: Monitor MQTT Messages (Real-time)

Open a terminal and subscribe to see WiFi events:

```bash
mosquitto_sub -h localhost -t 'ruview/occupancy/#' -v
```

**Expected output when you walk into the room:**
```
ruview/occupancy/test_room {"room_id":"test_room","occupancy_count":1,"device_count":2,"timestamp":"2026-11-08T17:00:00Z"}
```

### Step 7: Check Database

Verify events are being stored:

```bash
docker exec -it $(docker ps -q -f name=postgres) psql -U nura -d nura_db

# Run SQL query
SELECT * FROM wifi_sensing_events 
WHERE room_id = 'test_room' 
ORDER BY timestamp DESC 
LIMIT 10;
```

**Expected output:**
```
 event_id | room_id   | occupancy_count | device_count | timestamp
----------+-----------+-----------------+--------------+---------------------------
 uuid...  | test_room | 1               | 2            | 2026-11-08 17:00:00+00
```

### Step 8: Trigger Multi-Occupancy Alert (Testing)

To test multi-occupancy detection:

1. **Add test room to database:**
```sql
docker exec -it $(docker ps -q -f name=postgres) psql -U nura -d nura_db

INSERT INTO wifi_rooms (
  room_id, room_name, room_type,
  multi_occupancy_threshold, multi_occupancy_duration_seconds
) VALUES (
  'test_room',
  'Test Room',
  'bathroom',
  2,        -- Alert if 2+ people
  30        -- For more than 30 seconds (reduced for testing)
);
```

2. **Simulate 2+ people** (walk into room with someone else, or use simulation):
```bash
# Simulate 2 people for 1 minute
for i in {1..12}; do
  mosquitto_pub -h localhost -t 'ruview/occupancy/test_room' \
    -m "{\"room_id\":\"test_room\",\"occupancy_count\":2,\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
  sleep 5
  echo "Event $i/12 sent"
done
```

3. **Check for alert in NATS:**
```bash
docker exec -it $(docker ps -q -f name=nats) nats sub violations.detected

# Expected alert after 30+ seconds:
# {
#   "type": "wifi_anomaly",
#   "data_source": "wifi",
#   "severity": "high",
#   "wifi_event": {
#     "room_id": "test_room",
#     "anomaly_type": "multi_occupancy",
#     "occupancy_count": 2,
#     "duration_seconds": 35
#   }
# }
```

---

## Troubleshooting

### ESP32 Not Connecting to WiFi
```bash
# Check serial output from ESP32
# Use Arduino IDE Serial Monitor or screen command:
screen /dev/tty.usbserial-* 115200

# Look for WiFi connection messages
```

### No MQTT Messages
```bash
# Test MQTT from ESP32's perspective
# SSH to another device on your network and test:
mosquitto_sub -h 192.168.1.100 -t 'ruview/occupancy/#' -v

# If no connection, check:
# 1. Firewall on Mac (allow port 1883)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/mosquitto
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblock /usr/local/bin/mosquitto

# 2. Verify mosquitto is listening on all interfaces
docker exec -it $(docker ps -q -f name=mosquitto) netstat -an | grep 1883
```

### Events Not in Database
```bash
# Check WiFi sensing service logs
docker compose logs nura-wifi-sensing -f

# Look for:
# "WiFi event received: test_room"
# "Stored WiFi event: uuid..."
```

### False Positives/Negatives

**Too many false positives:**
```sql
-- Increase threshold or duration
UPDATE wifi_rooms 
SET multi_occupancy_threshold = 3,
    multi_occupancy_duration_seconds = 60
WHERE room_id = 'test_room';
```

**Missing detections:**
- Add more ESP32 boards
- Check ESP32 placement (spread them out more)
- Lower threshold temporarily for testing

---

## Quick Commands Summary

```bash
# Get your IP
ipconfig getifaddr en0

# Subscribe to MQTT
mosquitto_sub -h localhost -t 'ruview/occupancy/#' -v

# Check database
docker exec -it $(docker ps -q -f name=postgres) psql -U nura -d nura_db \
  -c "SELECT * FROM wifi_sensing_events ORDER BY timestamp DESC LIMIT 10;"

# Check logs
docker compose logs nura-wifi-sensing -f

# Monitor alerts
docker exec -it $(docker ps -q -f name=nats) nats sub violations.detected

# Simulate event
mosquitto_pub -h localhost -t 'ruview/occupancy/test_room' \
  -m '{"room_id":"test_room","occupancy_count":1}'
```

---

## Shopping List

**Amazon/AliExpress:**
- ESP32-DevKitC boards × 3 (~$20)
- USB cables × 3 (~$10)
- **Total: ~$30**

**Recommended Boards:**
- ESP32-DevKitC V4
- HiLetgo ESP32 Development Board
- AZDelivery ESP32 Dev Kit C

---

## Next Steps After Testing

1. ✅ **Verify WiFi sensing works** in test room
2. 🏠 **Deploy to real rooms** (bathroom, storage)
3. 📊 **Calibrate thresholds** based on real usage
4. 🔧 **Add more rooms** as needed
5. 🚀 **Production deployment**

---

**Ready to Test!**  
**WiFi Sensing Service: ✅ RUNNING**  
**MQTT Exposed: Ready for ESP32**  
**Buy ESP32 boards and start testing!** 🎉
