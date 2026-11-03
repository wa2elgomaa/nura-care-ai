#!/bin/bash
# Generate embeddings for all rules in the database

echo "🔄 Generating embeddings for rules..."

# Get all rules from RAG service
RULES=$(docker run --rm --network nura_core_net curlimages/curl:latest -s http://nura-rag:3002/rules 2>/dev/null)

# Check if we got rules
if [ -z "$RULES" ] || [ "$RULES" = "{}" ]; then
    echo "❌ Failed to fetch rules"
    exit 1
fi

echo "✅ Fetched rules from database"

# For each rule, generate embedding by making a test match query
# This will cause the RAG service to generate and cache embeddings

echo "📊 Rules without embeddings:"
docker compose exec -T postgres psql -U nura -d nura -c "SELECT rule_id, title FROM rules WHERE embedding IS NULL;"

echo ""
echo "🔧 Generating embeddings by querying each rule..."

# Query with supervision-related text
docker run --rm --network nura_core_net curlimages/curl:latest -s -X POST http://nura-rag:3002/match \
  -H "Content-Type: application/json" \
  -d '{"event_context":"children need adult supervision","category":"supervision","top_k":5}' > /dev/null 2>&1

# Query with fall-related text
docker run --rm --network nura_core_net curlimages/curl:latest -s -X POST http://nura-rag:3002/match \
  -H "Content-Type: application/json" \
  -d '{"event_context":"child fell down needs assessment","category":"safety","top_k":5}' > /dev/null 2>&1

# Query with restricted area text
docker run --rm --network nura_core_net curlimages/curl:latest -s -X POST http://nura-rag:3002/match \
  -H "Content-Type: application/json" \
  -d '{"event_context":"child accessing bathroom kitchen storage unsupervised","category":"safety","top_k":5}' > /dev/null 2>&1

echo "✅ Embedding generation queries sent"
echo ""
echo "📊 Current rules status:"
docker compose exec -T postgres psql -U nura -d nura -c "SELECT rule_id, title, embedding IS NOT NULL as has_embedding FROM rules;"
