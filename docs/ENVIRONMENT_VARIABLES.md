# Environment Variables Reference

**Complete reference for all services** - All configuration is .env driven, no hard-coded values!

---

## Table of Contents

1. [Shared Variables](#shared-variables) - Used by multiple services
2. [nura-stream-processor](#nura-stream-processor) - Camera processing & analytics
3. [nura-vlm](#nura-vlm) - Vision-Language Model service
4. [nura-alerts](#nura-alerts) - Alerting service
5. [nura-storage](#nura-storage) - Centralized storage
6. [nura-wifi-sensing](#nura-wifi-sensing) - WiFi occupancy detection
7. [Quick Start .env Template](#quick-start-env-template)

---

## Shared Variables

These variables are used by multiple services:

### PostgreSQL (All Services)
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=nura_db
POSTGRES_USER=nura
POSTGRES_PASSWORD=YourSecurePassword!  # ⚠️ CHANGE THIS!
```

### NATS (Most Services)
```env
NATS_URL=nats://nats:4222
```

---

## nura-stream-processor

**Purpose**: Camera detection processing, person identification, activity classification, analytics data collection

**Config File**: `services/nura-stream-processor/src/config/config.service.ts`

### Required
```env
# NATS
NATS_URL=nats://nats:4222

# PostgreSQL (for analytics storage)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=nura_db
POSTGRES_USER=nura
POSTGRES_PASSWORD=YourSecurePassword!

# VLM Service
VLM_SERVICE_URL=http://host.docker.internal:8001

# Frigate
FRIGATE_URL=http://localhost:5000
```

### Optional
```env
# Redis (for real-time location cache)
REDIS_HOST=localhost
REDIS_PORT=6379

# Processing Features (default: true)
ACTIVITY_CLASSIFIER_ENABLED=true
FACE_RECOGNITION_ENABLED=true
UNKNOWN_PERSON_TRACKING_ENABLED=true

# Performance Tuning
DB_POOL_SIZE=10
AI_REQUEST_TIMEOUT=120000  # milliseconds
```

---

## nura-vlm

**Purpose**: Vision-Language Model service - face recognition, person search, analytics, guardian/visitor APIs

**Config File**: `services/nura-vlm/src/config.py` (Pydantic)

### Required
```env
# Server
PORT=8001
HOST=0.0.0.0
DEBUG=false

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2-vision
OLLAMA_TIMEOUT=120  # seconds

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=nura_db
POSTGRES_USER=nura
POSTGRES_PASSWORD=YourSecurePassword!

# Storage Service
STORAGE_SERVICE_URL=http://localhost:3001
```

### Optional - Model Paths
```env
YOLO_MODEL_PATH=models/yolo11n.pt
EMBEDDING_MODEL=Salesforce/blip-image-captioning-base
FACE_RECOGNITION_MODEL=buffalo_l
```

### Optional - Face Recognition
```env
FACE_RECOGNITION_THRESHOLD=0.6  # 0.0-1.0
FACE_DETECTION_SIZE=(640, 640)
FACE_EMBEDDING_DIM=512
```

### Optional - Person Search
```env
FUZZY_SEARCH_THRESHOLD=0.3  # 0.0-1.0
VECTOR_SEARCH_LIMIT=10
```

### Optional - Visitor/Guardian
```env
VISITOR_DEFAULT_DURATION_HOURS=8
GUARDIAN_ENROLLMENT_ENABLED=true
```

### Optional - Analytics
```env
ANALYTICS_CACHE_TTL=3600  # seconds
DAILY_REPORT_CACHE_ENABLED=true
```

### Optional - Performance
```env
MAX_WORKERS=4
REQUEST_TIMEOUT=300  # seconds
DB_POOL_SIZE=10
```

### Optional - Image Processing
```env
MAX_IMAGE_SIZE_MB=10
IMAGE_QUALITY=85  # 1-100
ALLOWED_IMAGE_FORMATS=jpg,jpeg,png,webp
```

### Optional - Detection
```env
PERSON_CONFIDENCE_THRESHOLD=0.5  # 0.0-1.0
NMS_IOU_THRESHOLD=0.45  # 0.0-1.0
MAX_DETECTIONS=50
```

### Optional - Features
```env
VIOLATION_DETECTION_ENABLED=true
STRANGER_DETECTION_ENABLED=true
STORAGE_API_KEY=  # Optional auth for storage service
```

---

## nura-alerts

**Purpose**: Alert distribution (Slack, Email, SMS, Push Notifications)

**Config File**: `services/nura-alerts/src/config/config.service.ts`

### Required
```env
# NATS
NATS_URL=nats://nats:4222

# PostgreSQL (for alert tracking)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=nura_db
POSTGRES_USER=nura
POSTGRES_PASSWORD=YourSecurePassword!

# Frigate (for snapshot retrieval)
FRIGATE_URL=http://localhost:5000
```

### Optional - Alert Channels
```env
# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email
EMAIL_ENABLED=false
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=alerts@nura.care
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# SMS
SMS_ENABLED=false
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_FROM_NUMBER=+1234567890

# Push Notifications
PUSH_NOTIFICATION_ENABLED=false
PUSH_NOTIFICATION_PROVIDER=fcm
FCM_SERVER_KEY=your-fcm-server-key
```

### Optional - Alert Behavior
```env
ALERT_COOLDOWN_MINUTES=5  # Normal alerts
HIGH_SEVERITY_COOLDOWN_MINUTES=1  # High priority alerts

# Performance
DB_POOL_SIZE=10
```

---

## nura-storage

**Purpose**: Centralized file storage (local/S3/GCS/Azure)

**Config File**: `services/nura-storage/src/config/config.service.ts`

### Required
```env
# Storage Backend
STORAGE_BACKEND=local  # local|s3|gcs|azure

# API
PORT=3001
STORAGE_API_KEY=  # Optional - if empty, no auth required
CORS_ENABLED=true
```

### Local Backend
```env
LOCAL_STORAGE_PATH=/data/storage
```

### S3 Backend
```env
S3_BUCKET=nura-storage
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
S3_ENDPOINT=  # Optional - for S3-compatible services (MinIO, etc.)
```

### Google Cloud Storage Backend
```env
GCS_BUCKET=nura-storage
GCS_PROJECT_ID=your-project-id
GCS_CREDENTIALS_PATH=/path/to/credentials.json
```

### Azure Blob Storage Backend
```env
AZURE_STORAGE_ACCOUNT=youraccount
AZURE_STORAGE_KEY=your-key
AZURE_CONTAINER=nura-storage
```

### Optional - Upload Configuration
```env
MAX_FILE_SIZE_MB=100
ALLOWED_MIME_TYPES=image/*,video/*,application/pdf
TEMP_UPLOAD_PATH=/tmp/uploads
STORAGE_BASE_PATH=/data/storage
```

---

## nura-wifi-sensing

**Purpose**: WiFi-based occupancy detection via ESP32 devices

**Config File**: `services/nura-wifi-sensing/src/config/config.service.ts`

### Required
```env
# MQTT (for ESP32 devices)
MQTT_BROKER_URL=mqtt://localhost:1883
MQTT_TOPICS=wifi/+/occupancy,wifi/+/presence

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=nura_db
POSTGRES_USER=nura
POSTGRES_PASSWORD=YourSecurePassword!

# NATS
NATS_URL=nats://nats:4222
```

### Optional - MQTT Authentication
```env
MQTT_USERNAME=
MQTT_PASSWORD=
```

### Optional - WiFi Sensing Behavior
```env
OCCUPANCY_THRESHOLD=1  # Number of people to trigger occupancy
DETECTION_CONFIDENCE_MIN=0.7  # 0.0-1.0
ROOM_MAPPING_ENABLED=true
AFTER_HOURS_DETECTION_ENABLED=true
```

### Optional - Facility Hours
```env
FACILITY_OPEN_HOUR=7  # 7am
FACILITY_CLOSE_HOUR=18  # 6pm
```

### Optional - Multi-Occupancy Detection
```env
MULTI_OCCUPANCY_THRESHOLD=2  # Alert when 2+ people detected
MULTI_OCCUPANCY_ALERT_ENABLED=true
```

### Optional - Performance
```env
DB_POOL_SIZE=10
EVENT_BATCH_SIZE=100  # Batch inserts for performance
EVENT_BATCH_INTERVAL_MS=5000  # Flush every 5 seconds
```

---

## Quick Start .env Template

**Copy this to your `.env` file and customize**:

```env
# ==================== Shared Configuration ====================

# PostgreSQL (All Services)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=nura_db
POSTGRES_USER=nura
POSTGRES_PASSWORD=YourSecurePassword!  # ⚠️ CHANGE THIS!

# NATS (Most Services)
NATS_URL=nats://nats:4222

# ==================== nura-stream-processor ====================
VLM_SERVICE_URL=http://host.docker.internal:8001
FRIGATE_URL=http://localhost:5000
REDIS_HOST=localhost
REDIS_PORT=6379

# Processing Features
ACTIVITY_CLASSIFIER_ENABLED=true
FACE_RECOGNITION_ENABLED=true
UNKNOWN_PERSON_TRACKING_ENABLED=true

# Performance
DB_POOL_SIZE=10
AI_REQUEST_TIMEOUT=120000

# ==================== nura-vlm ====================
PORT=8001
HOST=0.0.0.0
DEBUG=false

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2-vision
OLLAMA_TIMEOUT=120

# Storage Service
STORAGE_SERVICE_URL=http://localhost:3001
STORAGE_API_KEY=

# Model Configuration
YOLO_MODEL_PATH=models/yolo11n.pt
FACE_RECOGNITION_MODEL=buffalo_l

# Thresholds
FACE_RECOGNITION_THRESHOLD=0.6
PERSON_CONFIDENCE_THRESHOLD=0.5
FUZZY_SEARCH_THRESHOLD=0.3

# Features
VIOLATION_DETECTION_ENABLED=true
STRANGER_DETECTION_ENABLED=true
GUARDIAN_ENROLLMENT_ENABLED=true

# ==================== nura-alerts ====================
FRIGATE_URL=http://localhost:5000

# Slack (Optional)
SLACK_WEBHOOK_URL=

# Alert Behavior
ALERT_COOLDOWN_MINUTES=5
HIGH_SEVERITY_COOLDOWN_MINUTES=1

# ==================== nura-storage ====================
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=/data/storage
STORAGE_API_KEY=
MAX_FILE_SIZE_MB=100

# ==================== nura-wifi-sensing ====================
MQTT_BROKER_URL=mqtt://localhost:1883
MQTT_TOPICS=wifi/+/occupancy,wifi/+/presence
MQTT_USERNAME=
MQTT_PASSWORD=

# Facility Hours
FACILITY_OPEN_HOUR=7
FACILITY_CLOSE_HOUR=18

# Multi-Occupancy
MULTI_OCCUPANCY_THRESHOLD=2
MULTI_OCCUPANCY_ALERT_ENABLED=true
```

---

## Best Practices

### ✅ DO:
1. **Use `.env` files** for all configuration
2. **Keep secrets in `.env.local`** (gitignored)
3. **Change default passwords** before production
4. **Use different passwords** for dev/staging/production
5. **Document required vs optional** variables
6. **Validate configuration** on service startup
7. **Log configuration** (without secrets) for debugging

### ❌ DON'T:
1. **Hard-code any configuration** in source code
2. **Commit `.env` files** with real passwords to git
3. **Use default passwords** in production
4. **Skip configuration validation**
5. **Use `process.env.*` directly** - always use ConfigService
6. **Expose secrets in logs** or error messages

---

## Configuration Validation

Each service validates its configuration on startup:

### TypeScript Services (NestJS)
```typescript
const config = new ConfigService();
const validation = config.validateConfig();

if (!validation.valid) {
  logger.error('Configuration validation failed');
  validation.errors.forEach(err => logger.error(err));
  process.exit(1);
}

config.logConfiguration();  // Logs config without secrets
```

### Python Service (FastAPI)
```python
from src.config import config

# Pydantic validates on instantiation
config.log_configuration()  # Logs config without secrets

# Additional validation
valid, errors = config.validate_all()
if not valid:
    logger.error("Configuration validation failed")
    for error in errors:
        logger.error(error)
    sys.exit(1)
```

---

## Service-Specific Notes

### nura-vlm (runs on HOST, not Docker)
- Models are loaded from host filesystem
- Ollama must be running on host
- Use `host.docker.internal` to access from other containers

### nura-stream-processor (runs in Docker)
- PostgreSQL connection from container
- Use `localhost` for host PostgreSQL or `postgres` for container name
- VLM service accessed via `host.docker.internal:8001`

### nura-storage (backend flexibility)
- Start with `local` backend for development
- Switch to `s3`/`gcs`/`azure` for production
- No code changes needed - just env vars!

### nura-wifi-sensing (ESP32 devices)
- MQTT broker must be accessible from ESP32 devices
- Configure device-specific room mapping in database
- Batch inserts for high-frequency events

---

## Troubleshooting

### "Using default password" warning
```
⚠️  Using default PostgreSQL password - set POSTGRES_PASSWORD in .env
```
**Solution**: Set a secure password in your `.env` file

### "No alert channels configured"
```
⚠️  No alert channels configured - alerts will not be sent
```
**Solution**: Configure at least one alert channel (Slack/Email/SMS)

### "YOLO model not found"
```
⚠️  YOLO model not found at models/yolo11n.pt
```
**Solution**: Download YOLO model or update `YOLO_MODEL_PATH`

### "Invalid threshold value"
```
⚠️  Invalid FACE_RECOGNITION_THRESHOLD: 1.5 (must be 0-1)
```
**Solution**: All threshold values must be between 0.0 and 1.0

---

## Summary

**Total Services**: 5  
**Total Environment Variables**: ~100  
**Configuration Approach**: Centralized ConfigService per service  
**Validation**: Automatic on startup  
**Security**: No hard-coded secrets, all .env driven  

**All services use centralized configuration - easy to track, easy to validate, easy to deploy!** ✅
