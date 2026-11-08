-- nura-face Database Schema
-- Face embeddings with pgvector for similarity search

-- Enable pgvector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- Face embeddings table
CREATE TABLE IF NOT EXISTS face_embeddings (
    id SERIAL PRIMARY KEY,
    person_id VARCHAR(100) NOT NULL,
    person_name VARCHAR(255) NOT NULL,
    person_type VARCHAR(50) NOT NULL CHECK (person_type IN ('student', 'staff', 'parent', 'visitor', 'unknown')),
    embedding vector(512) NOT NULL,  -- InsightFace buffalo_l embedding dimension
    photo_path VARCHAR(500),
    site_id VARCHAR(100) NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast lookup
CREATE INDEX IF NOT EXISTS face_embeddings_person_id_idx ON face_embeddings(person_id);
CREATE INDEX IF NOT EXISTS face_embeddings_person_type_idx ON face_embeddings(person_type);
CREATE INDEX IF NOT EXISTS face_embeddings_site_id_idx ON face_embeddings(site_id);

-- Vector similarity search index (cosine distance)
CREATE INDEX IF NOT EXISTS face_embeddings_embedding_idx ON face_embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Composite index for person lookup
CREATE INDEX IF NOT EXISTS face_embeddings_person_site_idx ON face_embeddings(person_id, site_id);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_face_embeddings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_face_embeddings_updated_at
BEFORE UPDATE ON face_embeddings
FOR EACH ROW EXECUTE FUNCTION update_face_embeddings_updated_at();

-- Comments for documentation
COMMENT ON TABLE face_embeddings IS 'Face recognition embeddings for person identification';
COMMENT ON COLUMN face_embeddings.embedding IS 'Face embedding vector (512-dim from InsightFace buffalo_l)';
COMMENT ON COLUMN face_embeddings.confidence IS 'Enrollment quality score (0-1)';
COMMENT ON COLUMN face_embeddings.metadata IS 'Additional metadata (enrollment source, quality metrics, etc.)';
