-- Week 4: Person Search & Locate
-- Enable extensions and indexes for fast person search
-- Created: 2026-11-08

-- Enable fuzzy text search extension
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create GIN index for fast fuzzy name search
-- This allows SIMILARITY() queries to be very fast
CREATE INDEX IF NOT EXISTS idx_enrolled_persons_name_trgm
ON enrolled_persons USING gin (full_name gin_trgm_ops);

-- Index for display_name as well (some searches might use this)
CREATE INDEX IF NOT EXISTS idx_enrolled_persons_display_name_trgm
ON enrolled_persons USING gin (display_name gin_trgm_ops);

-- Index for person_detections queries (movement history)
-- person_id + detected_at DESC for fast "last seen" queries
CREATE INDEX IF NOT EXISTS idx_person_detections_person_time
ON person_detections (person_id, detected_at DESC);

-- Index for camera_id queries (movements by camera)
CREATE INDEX IF NOT EXISTS idx_person_detections_camera_time
ON person_detections (camera_id, detected_at DESC);

-- Index for fast vector search (if not already created)
-- IVFFlat index for approximate nearest neighbor search
CREATE INDEX IF NOT EXISTS idx_enrolled_persons_face_embedding
ON enrolled_persons USING ivfflat (face_embedding vector_cosine_ops)
WITH (lists = 100);

-- Index for visitors face search
CREATE INDEX IF NOT EXISTS idx_visitors_face_encoding
ON visitors USING ivfflat (face_encoding vector_cosine_ops)
WITH (lists = 50);

-- Analyze tables to update statistics for query planner
ANALYZE enrolled_persons;
ANALYZE person_detections;
ANALYZE visitors;

-- Verify extensions
SELECT extname, extversion
FROM pg_extension
WHERE extname IN ('pg_trgm', 'vector');

-- Test fuzzy search (should return results for partial names)
-- Example: SIMILARITY('john', 'John Doe') > 0.3
SELECT 'Fuzzy search test:',
       SIMILARITY('john', 'John Doe') as john_similarity,
       SIMILARITY('jan', 'Jane Smith') as jane_similarity;
