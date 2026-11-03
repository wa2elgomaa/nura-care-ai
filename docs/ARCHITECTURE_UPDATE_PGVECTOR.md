# Architecture Update: pgvector Instead of Qdrant

**Date**: 2026-11-03  
**Reason**: Railway deployment compatibility

## Problem

- Qdrant is only used for RAG embeddings (rule knowledge base)
- Railway doesn't offer managed Qdrant
- Self-hosting Qdrant on Railway adds complexity and cost
- RAG data is **edge-only** anyway (policies never leave school servers)

## Solution: Use pgvector

**pgvector** is a PostgreSQL extension for vector similarity search - perfect for our use case.

### Why pgvector?

✅ **Already have Postgres** on edge and cloud  
✅ **Railway supports Postgres natively** with pgvector extension  
✅ **Simpler architecture** - one database instead of two  
✅ **Good enough performance** for our scale (100s of rules, not millions of vectors)  
✅ **ACID transactions** - can atomically update rules + embeddings  
✅ **Mature and stable** - used by Supabase, Neon, etc.  

### What Changes

#### Before (with Qdrant)
```
nura-rag service
  ↓
Qdrant (vector database)
  ↓
Find similar rules
```

#### After (with pgvector)
```
nura-rag service
  ↓
Postgres + pgvector extension
  ↓
Find similar rules
```

### Performance Comparison

| Feature | Qdrant | pgvector |
|---------|--------|----------|
| **Vector search speed** | Faster (specialized) | Fast enough (<10ms for 1000 vectors) |
| **Deployment** | Separate container | Extension in Postgres |
| **Railway support** | None | Native |
| **ACID transactions** | No | Yes |
| **Our scale** | Overkill (millions) | Perfect (100s-1000s) |

### RAG Use Case Scale

- **Total rules**: ~100-500 per site (school policies + government regulations)
- **Query frequency**: Only when violation detected (~1-10/minute peak)
- **Embedding size**: 384-768 dimensions (sentence-transformers)
- **Latency target**: <100ms for rule matching (not latency-critical)

**pgvector handles this easily** - it's designed for exactly this scale.

---

## Implementation Changes

### 1. Update Postgres Init Script

**File**: `edge/postgres/init.sql`

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create rules table with embeddings
CREATE TABLE rules (
    id SERIAL PRIMARY KEY,
    rule_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    clause TEXT NOT NULL,
    source VARCHAR(255) NOT NULL,  -- e.g., "STATE-REG-45.1.2"
    severity VARCHAR(20) NOT NULL, -- critical, high, medium, low
    category VARCHAR(50) NOT NULL, -- supervision, capacity, behavior, etc.
    embedding vector(384),         -- pgvector column (384 = all-MiniLM-L6-v2 dim)
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index for vector similarity search
CREATE INDEX ON rules USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Example: Find similar rules
-- SELECT rule_id, title, 1 - (embedding <=> '[0.1, 0.2, ...]') AS similarity
-- FROM rules
-- ORDER BY embedding <=> '[0.1, 0.2, ...]'
-- LIMIT 5;
```

### 2. Update compose.yaml

**Remove**:
```yaml
qdrant:
  image: qdrant/qdrant:v1.12.4
  volumes:
    - qdrant_data:/qdrant/storage

volumes:
  qdrant_data:
```

**Keep Postgres** (already has what we need with pgvector):
```yaml
postgres:
  image: postgres:16-alpine
  # pgvector available in Postgres 16+
```

### 3. Update nura-rag Service

**Before** (with Qdrant):
```typescript
import { QdrantClient } from '@qdrant/qdrant-js';

const qdrant = new QdrantClient({ url: 'http://qdrant:6333' });
const results = await qdrant.search('rules', {
  vector: embedding,
  limit: 5
});
```

**After** (with pgvector):
```typescript
import { Pool } from 'pg';

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

const results = await pool.query(`
  SELECT 
    rule_id, 
    title, 
    description, 
    clause, 
    source, 
    severity,
    1 - (embedding <=> $1) AS similarity
  FROM rules
  WHERE 1 - (embedding <=> $1) > 0.7  -- similarity threshold
  ORDER BY embedding <=> $1
  LIMIT 5
`, [embedding]);
```

### 4. Update Environment Variables

**Remove**:
```bash
QDRANT_URL=http://qdrant:6333
```

**Already have**:
```bash
DATABASE_URL=postgresql://nura:password@postgres:5432/nura
```

---

## Migration Plan

### Step 1: Update Postgres Init
- Add pgvector extension
- Create rules table with vector column
- Create ivfflat index

### Step 2: Remove Qdrant
- Remove from compose.yaml
- Remove from documentation
- Remove from service dependencies

### Step 3: Update nura-rag Service
- Replace Qdrant client with pg client
- Update queries to use pgvector syntax
- Test vector search performance

### Step 4: Load Rules
- Create rule ingestion script
- Generate embeddings with sentence-transformers
- Insert into Postgres with pgvector

---

## Railway Deployment

### Cloud Postgres (Railway)

**pgvector support**: ✅ Available in Railway Postgres

```sql
-- Enable on Railway Postgres
CREATE EXTENSION IF NOT EXISTS vector;
```

**No additional cost** - pgvector is free extension included with Postgres.

### Edge Postgres (Docker)

**Already works** - Postgres 16+ includes pgvector support:

```yaml
postgres:
  image: postgres:16-alpine
  # pgvector available, no special image needed
```

---

## Performance Validation

### Benchmark pgvector

```sql
-- Insert 1000 test rules with embeddings
-- Query time with ivfflat index:
EXPLAIN ANALYZE
SELECT rule_id, title, 1 - (embedding <=> $1) AS similarity
FROM rules
ORDER BY embedding <=> $1
LIMIT 5;

-- Expected: <10ms for 1000 vectors
-- Expected: <50ms for 10,000 vectors
```

**Our scale (100-500 rules)**: pgvector will be <5ms, well within targets.

---

## Benefits of This Change

✅ **Simpler architecture** - one less service to manage  
✅ **Railway compatible** - native Postgres support  
✅ **ACID transactions** - update rules + embeddings atomically  
✅ **Better for edge** - already running Postgres anyway  
✅ **Cost savings** - no separate vector DB to host  
✅ **Good enough performance** - <10ms for our scale  

---

## What Stays the Same

- VLM service (no changes)
- Rules engine (no changes)
- Embedding generation (still use sentence-transformers)
- RAG logic (only storage layer changes)

---

## Decision

**✅ Use pgvector instead of Qdrant**

**Rationale**: 
- RAG data is edge-only (privacy requirement)
- Railway doesn't support Qdrant
- pgvector is perfect for our scale
- Simpler architecture = easier to maintain

---

**Status**: Architecture updated, ready to implement in nura-rag service

**Next**: Build nura-rag service with pgvector from the start
