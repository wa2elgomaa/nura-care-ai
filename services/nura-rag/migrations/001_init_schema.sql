-- nura-rag Database Schema
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Rules table with pgvector embeddings
CREATE TABLE IF NOT EXISTS rules (
    id SERIAL PRIMARY KEY,
    rule_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    clause TEXT NOT NULL,
    source VARCHAR(255) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    category VARCHAR(50) NOT NULL,
    enabled BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding vector(384),  -- all-MiniLM-L6-v2 dimensions
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for vector similarity search
CREATE INDEX IF NOT EXISTS rules_embedding_idx ON rules
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Index for category filtering
CREATE INDEX IF NOT EXISTS rules_category_idx ON rules(category);

-- Index for enabled rules
CREATE INDEX IF NOT EXISTS rules_enabled_idx ON rules(enabled);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_rules_updated_at BEFORE UPDATE ON rules
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
