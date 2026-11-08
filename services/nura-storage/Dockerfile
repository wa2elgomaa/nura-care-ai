FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json ./
RUN npm install

# Copy source
COPY . .

# Build
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy package files and install production dependencies
COPY package.json ./
RUN npm install --production

# Copy built application
COPY --from=builder /app/dist ./dist

# Create storage directory
RUN mkdir -p /data/storage && chmod 777 /data/storage

# Expose port
EXPOSE 3012

# Start
CMD ["node", "dist/main"]
