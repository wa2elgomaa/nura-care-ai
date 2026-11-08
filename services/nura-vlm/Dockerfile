FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy local packages first (needed by requirements.txt)
COPY ./packages/ ./packages/

# Copy requirements
COPY ./services/nura-vlm/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./services/nura-vlm/src/ ./src/

# Copy model files
COPY ./services/nura-vlm/models/ ./models/

# Non-root user
RUN useradd -m -u 1000 nura && chown -R nura:nura /app
USER nura

EXPOSE 8001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
