# WiFi Sensing Quick Start

**For Real Testing Without Hardware** → Use Simulation  
**For Production** → See [WIFI_SENSING_HARDWARE_SETUP.md](WIFI_SENSING_HARDWARE_SETUP.md)

## Quick Test (5 Minutes)

### 1. Verify Service Running
```bash
docker compose ps nura-wifi-sensing

# Expected: nura-nura-wifi-sensing-1  running
```

### 2. Send Test Event
```bash
mosquitto_pub -h localhost -t 'ruview/occupancy/bathroom_boys_1f' \
  -m '{"room_id":"bathroom_boys_1f","occupancy_count":1,"device_count":2,"timestamp":"2026-11-08T12:00:00Z"}'
```

### 3. Check Logs
```bash
docker compose logs nura-wifi-sensing --tail 10

# Expected:
# ✓ Subscribed to: ruview/occupancy/#
# WiFi event received: bathroom_boys_1f
```

### 4. Check Database
```bash
docker exec -it $(docker ps -q -f name=postgres) psql -U nura -d nura_db \
  -c "SELECT * FROM wifi_sensing_events ORDER BY timestamp DESC LIMIT 3;"
```

## Trigger Multi-Occupancy Alert (2 Minutes)

```bash
# Send 2+ people for 2+ minutes
for i in {1..30}; do
  mosquitto_pub -h localhost -t 'ruview/occupancy/bathroom_boys_1f' \
    -m "{\"room_id\":\"bathroom_boys_1f\",\"occupancy_count\":2,\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
  sleep 5
  echo "Event $i/30"
done

# Alert published to NATS after ~24 events (2 min)
```

## Real Hardware Setup (30 Minutes)

### Option 1: RuView (Recommended - FREE!)
**GitHub**: https://github.com/ruvnet/ruview (MIT License)

1. Clone RuView: `git clone https://github.com/ruvnet/ruview`
2. Flash firmware to 2-3 ESP32 boards
3. Configure MQTT: `mqtt://YOUR_IP:1883`
4. Set topic: `ruview/occupancy/bathroom_boys_1f`
5. Done! ✅

### Option 2: ESP-WiFi-CSI (Alternative - Also FREE!)
**GitHub**: https://github.com/StevenMHernandez/ESP32-CSI-Tool

1. Buy ESP32 boards ($5-10 each, need 2-3 per room)
2. Clone repository
3. Build CSI processing pipeline
4. Publish to MQTT in JSON format
5. Test & calibrate

## Expose MQTT to ESP32 (Required for Real Hardware)

**Edit `compose.yaml`:**
```yaml
mosquitto:
  ports:
    - "1883:1883"  # ADD THIS LINE
```

**Restart:**
```bash
docker compose up -d mosquitto
```

**Get Your Server IP:**
```bash
# macOS
ipconfig getifaddr en0

# Linux
ip addr show | grep "inet "

# Example: 192.168.1.100
```

**Configure ESP32:**
```ini
MQTT_BROKER=192.168.1.100  # Your server IP
MQTT_PORT=1883
MQTT_TOPIC=ruview/occupancy/bathroom_boys_1f
```

## Test from Another Computer

```bash
# Install mosquitto client
brew install mosquitto  # macOS
sudo apt install mosquitto-clients  # Linux

# Subscribe
mosquitto_sub -h YOUR_SERVER_IP -t 'ruview/occupancy/#' -v

# Publish test
mosquitto_pub -h YOUR_SERVER_IP -t 'ruview/occupancy/test' -m 'hello'
```

## Configured Rooms (Default)

| Room ID | Name | Type | Threshold | Duration |
|---------|------|------|-----------|----------|
| bathroom_boys_1f | Boys Bathroom 1F | bathroom | 2 people | 2 min |
| bathroom_girls_1f | Girls Bathroom 1F | bathroom | 2 people | 2 min |
| storage_main | Main Storage | storage | N/A | After-hours |
| kitchen | Kitchen | kitchen | 2 people | 2 min |

## Add New Room

```sql
docker exec -it $(docker ps -q -f name=postgres) psql -U nura -d nura_db

INSERT INTO wifi_rooms (
  room_id, room_name, room_type,
  multi_occupancy_threshold, multi_occupancy_duration_seconds
) VALUES (
  'bathroom_boys_2f',
  'Boys Bathroom 2F',
  'bathroom',
  2,
  120
);
```

## Message Format

ESP32 must publish JSON to `ruview/occupancy/<room_id>`:

```json
{
  "room_id": "bathroom_boys_1f",
  "room_type": "bathroom",
  "occupancy_count": 2,
  "device_count": 3,
  "timestamp": "2026-11-08T12:30:00Z",
  "esp32_nodes": ["AA:BB:CC:DD:EE:01"]
}
```

**Required Fields:**
- `room_id` - Must match database
- `occupancy_count` - Number of people detected
- `timestamp` - ISO 8601 format

**Optional Fields:**
- `room_type`, `device_count`, `esp32_nodes`

## Alert Types

### Multi-Occupancy
- **Trigger**: 2+ people in bathroom for 2+ minutes
- **Severity**: High
- **Data Source**: wifi

### After-Hours
- **Trigger**: Movement outside 6am-6pm
- **Severity**: Medium
- **Data Source**: wifi

## Costs

### Hardware Only (Software is FREE!)
- ESP32 boards: $5-10 each
- 2-3 boards per room
- **Per room**: ~$15-30
- **Example: 4 rooms**: ~$60-120

### Software (Both FREE!)
- **RuView**: https://github.com/ruvnet/ruview (MIT License)
- **ESP-WiFi-CSI**: https://github.com/StevenMHernandez/ESP32-CSI-Tool

**Total Cost for 4 Rooms: ~$60-120** (hardware only!)

## Next Steps

1. **Test with simulation** ✅ (No cost)
2. **Buy 2-3 ESP32 boards** (Test 1 room)
3. **Choose firmware** (RuView or DIY)
4. **Deploy & test** (1 room)
5. **Scale** (All camera-free zones)

## Documentation

- [Full Hardware Setup](WIFI_SENSING_HARDWARE_SETUP.md)
- [Week 3 Deployment](WEEK3_DEPLOYMENT.md)
- [Week 3 Complete](WEEK3_COMPLETE.md)

---

**WiFi Sensing: ✅ RUNNING**  
**Simulation Testing: ✅ AVAILABLE NOW**  
**Hardware Ready: Buy ESP32 + Flash Firmware**
