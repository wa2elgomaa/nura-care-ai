FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force
COPY --from=builder /app/dist ./dist

# Pre-download the transformer model at build time
ENV TRANSFORMERS_CACHE=/app/.cache/transformers
RUN mkdir -p /app/.cache/transformers && \
    node -e "const {pipeline} = require('@xenova/transformers'); \
    (async () => { \
      console.log('Downloading model...'); \
      await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2'); \
      console.log('Model downloaded successfully'); \
    })().catch(err => { console.error('Download failed:', err); process.exit(1); });"

USER node
EXPOSE 3000

CMD ["node", "dist/main.js"]
