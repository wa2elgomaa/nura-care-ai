-- Phase 4B: Person Identification Database Schema
-- Migration 001: Person Enrollment & Tracking

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- 1. ENROLLED PERSONS (Face Embeddings Database)
-- ============================================================================

CREATE TABLE enrolled_persons (
    id SERIAL PRIMARY KEY,

    -- Identity
    person_id VARCHAR(50) UNIQUE NOT NULL,  -- e.g., "adam_w", "noah_m"
    full_name VARCHAR(100) NOT NULL,        -- e.g., "Adam Williams"
    display_name VARCHAR(100),              -- e.g., "Adam W."

    -- Biometric Data
    face_embedding vector(512),             -- Face embedding (ArcFace/FaceNet: 512D)
    face_embedding_model VARCHAR(50),       -- e.g., "arcface_r100"

    -- Metadata
    age_years INT,                          -- Child's age
    grade_level VARCHAR(20),                -- e.g., "Pre-K", "Kindergarten"
    classroom VARCHAR(50),                  -- e.g., "Room 3A"
    parent_contact JSONB,                   -- {phone, email, emergency_contact}

    -- Enrollment Info
    enrollment_photo_url TEXT,              -- Original enrollment photo
    enrollment_quality_score FLOAT,         -- Face quality at enrollment (0-1)
    enrolled_by VARCHAR(100),               -- Staff member who enrolled
    enrolled_at TIMESTAMP DEFAULT NOW(),

    -- Privacy & Consent
    parental_consent BOOLEAN DEFAULT FALSE,
    consent_document_url TEXT,
    consent_date TIMESTAMP,

    -- Status
    active BOOLEAN DEFAULT TRUE,
    notes TEXT,

    -- Timestamps
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP                    -- Soft delete for GDPR compliance
);

-- Indexes
CREATE INDEX idx_enrolled_persons_person_id ON enrolled_persons(person_id);
CREATE INDEX idx_enrolled_persons_active ON enrolled_persons(active) WHERE active = TRUE;
CREATE INDEX idx_enrolled_persons_classroom ON enrolled_persons(classroom);

-- Vector similarity index (HNSW for fast approximate nearest neighbor search)
CREATE INDEX idx_enrolled_persons_face_embedding ON enrolled_persons
USING hnsw (face_embedding vector_cosine_ops);

-- ============================================================================
-- 2. PERSON SIGHTINGS (Active Tracking)
-- ============================================================================

CREATE TABLE person_sightings (
    id BIGSERIAL PRIMARY KEY,

    -- Identity
    global_id VARCHAR(50),                  -- Identified person_id or NULL if unknown
    camera_id VARCHAR(50) NOT NULL,
    local_track_id INT NOT NULL,            -- ByteTrack ID within camera

    -- Detection
    timestamp TIMESTAMP DEFAULT NOW(),
    bbox JSONB NOT NULL,                    -- [x1, y1, x2, y2]
    frame_number INT,

    -- Identification
    identity_confidence FLOAT,              -- Confidence of identification (0-1)
    identification_method VARCHAR(20),      -- 'face', 'appearance', 'fusion', 'manual'
    face_embedding vector(512),             -- Face embedding if face detected
    appearance_embedding vector(512),       -- Appearance embedding (ReID)

    -- Tracking Context
    velocity JSONB,                         -- [vx, vy] in pixels/frame
    track_age INT,                          -- Frames since first seen

    -- Session
    session_id UUID,                        -- Tracking session (restarts on service restart)

    FOREIGN KEY (global_id) REFERENCES enrolled_persons(person_id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_person_sightings_global_id ON person_sightings(global_id);
CREATE INDEX idx_person_sightings_camera_id ON person_sightings(camera_id);
CREATE INDEX idx_person_sightings_timestamp ON person_sightings(timestamp DESC);
CREATE INDEX idx_person_sightings_session ON person_sightings(session_id);
CREATE INDEX idx_person_sightings_camera_track ON person_sightings(camera_id, local_track_id);

-- Vector indexes for ReID
CREATE INDEX idx_person_sightings_face_embedding ON person_sightings
USING hnsw (face_embedding vector_cosine_ops);

CREATE INDEX idx_person_sightings_appearance_embedding ON person_sightings
USING hnsw (appearance_embedding vector_cosine_ops);

-- ============================================================================
-- 3. PERSON ACTIONS (Behavior Timeline)
-- ============================================================================

CREATE TABLE person_actions (
    id BIGSERIAL PRIMARY KEY,

    -- Identity
    global_id VARCHAR(50) NOT NULL,
    sighting_id BIGINT,                     -- Link to specific sighting

    -- Action
    timestamp TIMESTAMP DEFAULT NOW(),
    action_type VARCHAR(50) NOT NULL,       -- 'violence', 'distress', 'normal', etc.
    confidence FLOAT NOT NULL,
    bbox JSONB,                             -- Person bbox at time of action

    -- Context
    camera_id VARCHAR(50),
    frame_number INT,
    details TEXT,
    metadata JSONB,                         -- Additional action-specific data

    FOREIGN KEY (global_id) REFERENCES enrolled_persons(person_id) ON DELETE CASCADE,
    FOREIGN KEY (sighting_id) REFERENCES person_sightings(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_person_actions_global_id ON person_actions(global_id);
CREATE INDEX idx_person_actions_timestamp ON person_actions(timestamp DESC);
CREATE INDEX idx_person_actions_action_type ON person_actions(action_type);
CREATE INDEX idx_person_actions_camera_id ON person_actions(camera_id);

-- ============================================================================
-- 4. CAMERA TOPOLOGY (Multi-Camera Tracking)
-- ============================================================================

CREATE TABLE camera_topology (
    id SERIAL PRIMARY KEY,

    -- Camera Pair
    camera_a VARCHAR(50) NOT NULL,
    camera_b VARCHAR(50) NOT NULL,

    -- Adjacency
    are_adjacent BOOLEAN DEFAULT TRUE,
    transition_zone JSONB,                  -- Overlap area coordinates

    -- Transition Metrics
    avg_transition_time_sec INT,            -- Typical time to cross
    min_transition_time_sec INT,
    max_transition_time_sec INT,

    -- Direction
    exit_direction_a JSONB,                 -- Direction people exit camera A towards B
    entry_direction_b JSONB,                -- Direction people enter camera B from A

    -- Statistics
    successful_handoffs INT DEFAULT 0,
    failed_handoffs INT DEFAULT 0,

    UNIQUE (camera_a, camera_b)
);

-- Index
CREATE INDEX idx_camera_topology_camera_a ON camera_topology(camera_a);
CREATE INDEX idx_camera_topology_camera_b ON camera_topology(camera_b);

-- ============================================================================
-- 5. CROSS-CAMERA HANDOFFS (Movement Tracking)
-- ============================================================================

CREATE TABLE camera_handoffs (
    id BIGSERIAL PRIMARY KEY,

    -- Person
    global_id VARCHAR(50) NOT NULL,

    -- Handoff
    from_camera VARCHAR(50) NOT NULL,
    to_camera VARCHAR(50) NOT NULL,
    from_sighting_id BIGINT,                -- Last sighting in source camera
    to_sighting_id BIGINT,                  -- First sighting in dest camera

    -- Timing
    exit_timestamp TIMESTAMP,
    entry_timestamp TIMESTAMP,
    transition_duration_sec INT,            -- Calculated duration

    -- Confidence
    handoff_confidence FLOAT,               -- Confidence it's the same person
    matching_method VARCHAR(50),            -- 'appearance', 'temporal', 'topology'

    -- Verification
    verified BOOLEAN DEFAULT FALSE,
    verified_by VARCHAR(100),
    verified_at TIMESTAMP,

    FOREIGN KEY (global_id) REFERENCES enrolled_persons(person_id) ON DELETE CASCADE,
    FOREIGN KEY (from_sighting_id) REFERENCES person_sightings(id) ON DELETE SET NULL,
    FOREIGN KEY (to_sighting_id) REFERENCES person_sightings(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_camera_handoffs_global_id ON camera_handoffs(global_id);
CREATE INDEX idx_camera_handoffs_from_camera ON camera_handoffs(from_camera);
CREATE INDEX idx_camera_handoffs_to_camera ON camera_handoffs(to_camera);
CREATE INDEX idx_camera_handoffs_timestamps ON camera_handoffs(exit_timestamp, entry_timestamp);

-- ============================================================================
-- 6. HELPER FUNCTIONS
-- ============================================================================

-- Function: Find closest face match
CREATE OR REPLACE FUNCTION find_closest_face_match(
    query_embedding vector(512),
    min_confidence FLOAT DEFAULT 0.6
)
RETURNS TABLE (
    person_id VARCHAR(50),
    full_name VARCHAR(100),
    distance FLOAT,
    confidence FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ep.person_id,
        ep.full_name,
        (ep.face_embedding <=> query_embedding) AS distance,
        (1.0 - (ep.face_embedding <=> query_embedding)) AS confidence
    FROM enrolled_persons ep
    WHERE
        ep.active = TRUE
        AND ep.face_embedding IS NOT NULL
        AND (1.0 - (ep.face_embedding <=> query_embedding)) >= min_confidence
    ORDER BY distance ASC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function: Get person's recent location
CREATE OR REPLACE FUNCTION get_person_location(
    p_person_id VARCHAR(50)
)
RETURNS TABLE (
    camera_id VARCHAR(50),
    last_seen TIMESTAMP,
    bbox JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ps.camera_id,
        ps.timestamp,
        ps.bbox
    FROM person_sightings ps
    WHERE ps.global_id = p_person_id
    ORDER BY ps.timestamp DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function: Get person's movement timeline
CREATE OR REPLACE FUNCTION get_person_timeline(
    p_person_id VARCHAR(50),
    p_hours INT DEFAULT 24
)
RETURNS TABLE (
    camera_id VARCHAR(50),
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    num_sightings BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ps.camera_id,
        MIN(ps.timestamp) AS first_seen,
        MAX(ps.timestamp) AS last_seen,
        COUNT(*) AS num_sightings
    FROM person_sightings ps
    WHERE
        ps.global_id = p_person_id
        AND ps.timestamp > NOW() - (p_hours || ' hours')::INTERVAL
    GROUP BY ps.camera_id
    ORDER BY first_seen ASC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 7. TRIGGERS
-- ============================================================================

-- Update timestamp on modification
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_enrolled_persons_modtime
    BEFORE UPDATE ON enrolled_persons
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- ============================================================================
-- 8. SAMPLE DATA (Development/Testing)
-- ============================================================================

-- Insert sample enrolled persons (with placeholder embeddings)
-- Note: In production, these would be real face embeddings from enrollment photos

INSERT INTO enrolled_persons (
    person_id, full_name, display_name, age_years, grade_level,
    classroom, parental_consent, active
) VALUES
    ('adam_w', 'Adam Williams', 'Adam W.', 5, 'Kindergarten', 'Room 3A', TRUE, TRUE),
    ('noah_m', 'Noah Martinez', 'Noah M.', 6, 'First Grade', 'Room 2B', TRUE, TRUE),
    ('sarah_k', 'Sarah Kim', 'Sarah K.', 5, 'Kindergarten', 'Room 3A', TRUE, TRUE),
    ('emma_j', 'Emma Johnson', 'Emma J.', 4, 'Pre-K', 'Room 1C', TRUE, TRUE),
    ('lucas_r', 'Lucas Rodriguez', 'Lucas R.', 6, 'First Grade', 'Room 2B', TRUE, TRUE)
ON CONFLICT (person_id) DO NOTHING;

-- Insert sample camera topology
INSERT INTO camera_topology (
    camera_a, camera_b, are_adjacent, avg_transition_time_sec,
    min_transition_time_sec, max_transition_time_sec
) VALUES
    ('camera_1', 'camera_2', TRUE, 15, 10, 30),  -- Playground → Hallway
    ('camera_2', 'camera_3', TRUE, 20, 15, 40),  -- Hallway → Classroom
    ('camera_1', 'camera_3', FALSE, NULL, NULL, NULL)  -- Not adjacent
ON CONFLICT (camera_a, camera_b) DO NOTHING;

-- ============================================================================
-- NOTES
-- ============================================================================

-- Privacy & GDPR Compliance:
-- 1. Face embeddings are stored (not raw images)
-- 2. Soft delete with deleted_at timestamp
-- 3. Parental consent tracking
-- 4. Person sightings can be purged after retention period

-- Performance:
-- 1. HNSW indexes for fast vector similarity search
-- 2. Compound indexes for common queries
-- 3. Partitioning person_sightings by date (future optimization)

-- Data Retention Policy (implement as needed):
-- - Enrolled persons: Keep until child leaves school
-- - Person sightings: Purge after 90 days
-- - Person actions: Keep for 1 year (incidents may need longer)
-- - Camera handoffs: Purge after 90 days
