# Service Template Guide

Guide for creating new NURA microservices following project conventions.

## TypeScript Service (NestJS)

### Directory Structure
```
services/nura-service-name/
├── Dockerfile
├── package.json
├── tsconfig.json
├── .dockerignore
├── README.md
├── src/
│   ├── main.ts          # Entry point
│   ├── app.module.ts    # Root module
│   ├── app.controller.ts
│   ├── app.service.ts
│   └── config/
│       └── config.ts    # Environment configuration
└── test/
    └── app.e2e-spec.ts
```

### Minimal package.json
```json
{
  "name": "nura-service-name",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "engines": { "node": ">=22" },
  "scripts": {
    "build": "tsc",
    "start": "node dist/main.js",
    "start:dev": "tsc --watch",
    "test": "tsc && node --test"
  },
  "dependencies": {
    "@nestjs/common": "^10.3.0",
    "@nestjs/core": "^10.3.0",
    "@nestjs/platform-express": "^10.3.0",
    "reflect-metadata": "^0.2.1",
    "rxjs": "^7.8.1"
  },
  "devDependencies": {
    "@types/node": "^22.10.0",
    "typescript": "^5.6.0"
  }
}
```

### Dockerfile (TypeScript)
```dockerfile
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force
COPY --from=builder /app/dist ./dist
USER node
EXPOSE 3000
CMD ["node", "dist/main.js"]
```

### compose.yaml entry
```yaml
  nura-service-name:
    <<: *nura-stub
    build:
      context: ./services/nura-service-name
    image: ${NURA_SERVICE_NAME_IMAGE:-nura/service-name:dev}
    environment:
      <<: *nura-env
      PORT: "3000"
      CUSTOM_VAR: ${CUSTOM_VAR:-default}
    depends_on:
      - postgres
      - nats
```

---

## Python Service (FastAPI)

### Directory Structure
```
services/nura-service-name/
├── Dockerfile
├── requirements.txt
├── .dockerignore
├── README.md
├── src/
│   ├── main.py          # FastAPI app
│   ├── config.py        # Environment configuration
│   ├── models.py        # Pydantic models
│   ├── routes/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
└── tests/
    └── test_main.py
```

### Minimal requirements.txt
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.6.0
pydantic-settings==2.1.0
```

### Dockerfile (Python)
```dockerfile
FROM python:3.11-slim
WORKDIR /app

# System dependencies (if needed)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

RUN useradd -m -u 1000 nura && chown -R nura:nura /app
USER nura

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### main.py template
```python
from fastapi import FastAPI
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    nats_url: str = "nats://nats:4222"
    site_id: str = "dev-site-001"
    log_level: str = "info"

    class Config:
        env_file = ".env"

app = FastAPI(
    title="NURA Service Name",
    version="0.1.0"
)

settings = Settings()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}

@app.get("/")
async def root():
    return {"service": "nura-service-name", "version": "0.1.0"}
```

### compose.yaml entry
```yaml
  nura-service-name:
    <<: *nura-stub
    build:
      context: ./services/nura-service-name
    image: ${NURA_SERVICE_NAME_IMAGE:-nura/service-name:dev}
    environment:
      <<: *nura-env
      CUSTOM_VAR: ${CUSTOM_VAR:-default}
    depends_on:
      - postgres
      - nats
```

---

## Common Patterns

### Environment Variables
All services inherit `*nura-env`:
```yaml
x-nura-env: &nura-env
  DATABASE_URL: postgresql://${POSTGRES_USER:-nura}:${POSTGRES_PASSWORD}@postgres:5432/nura
  NATS_URL: nats://nats:4222
  MQTT_URL: mqtt://mosquitto:1883
  QDRANT_URL: http://qdrant:6333
  OIDC_ISSUER: http://keycloak:8080/realms/nura
  SITE_ID: ${SITE_ID:-dev-site-001}
  LOG_LEVEL: ${LOG_LEVEL:-info}
```

### Health Check Endpoint
Every service MUST expose `GET /health`:
```json
{
  "status": "healthy" | "degraded" | "unhealthy",
  "version": "0.1.0",
  "dependencies": {
    "database": "connected",
    "nats": "connected"
  }
}
```

### NATS Event Publishing (TypeScript)
```typescript
import { connect } from 'nats';

const nc = await connect({ servers: process.env.NATS_URL });
const js = nc.jetstream();

await js.publish('nura.events.alert', JSON.stringify({
  type: 'fall_detected',
  site_id: process.env.SITE_ID,
  timestamp: Date.now(),
  zone: 'room3'
}));
```

### NATS Event Publishing (Python)
```python
import asyncio
from nats.aio.client import Client as NATS
import json

nc = NATS()
await nc.connect(servers=[settings.nats_url])
js = nc.jetstream()

await js.publish('nura.events.alert', json.dumps({
    'type': 'fall_detected',
    'site_id': settings.site_id,
    'timestamp': int(time.time()),
    'zone': 'room3'
}).encode())
```

---

## Testing Checklist

- [ ] Service starts successfully
- [ ] `/health` endpoint responds
- [ ] Environment variables load correctly
- [ ] Connects to required dependencies (DB, NATS, etc.)
- [ ] Docker image builds without errors
- [ ] Logs structured output (JSON preferred)
- [ ] Non-root user in container
- [ ] .dockerignore excludes dev files
- [ ] README documents API endpoints
- [ ] README lists environment variables

---

## Service Naming Conventions

- Repository: `nura-service-name`
- Docker image: `nura/service-name:dev`
- Container name (if needed): `nura-service-name`
- Compose service: `nura-service-name`
- NATS subject prefix: `nura.service-name.*`

---

## Next Steps After Creation

1. Add service to [ARCHITECTURE.md](./ARCHITECTURE.md) Service Catalog
2. Document NATS event contracts in shared types
3. Add Prometheus metrics endpoint (`/metrics`)
4. Write integration tests
5. Add to CI/CD pipeline
6. Update .env.example with new variables
