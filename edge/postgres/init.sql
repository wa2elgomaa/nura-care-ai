-- NURA edge database initialization
-- Creates databases and extensions for Keycloak and application data

-- Create Keycloak database
CREATE DATABASE keycloak;

-- Create main application database (already created by POSTGRES_DB env var)
-- CREATE DATABASE nura;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE keycloak TO nura;
GRANT ALL PRIVILEGES ON DATABASE nura TO nura;

-- Connect to nura database and enable extensions
\c nura;

-- Enable pgvector extension for RAG embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable PostGIS for geospatial data (bus tracking, geofencing)
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable TimescaleDB for time-series data (sensor events, analytics)
-- Note: Requires timescaledb Docker image, see compose.yaml
-- CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create rules table with vector embeddings for RAG
CREATE TABLE IF NOT EXISTS rules (
    id SERIAL PRIMARY KEY,
    rule_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    clause TEXT NOT NULL,
    source VARCHAR(255) NOT NULL,  -- e.g., "STATE-REG-45.1.2", "SCHOOL-POLICY-3.1"
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    category VARCHAR(50) NOT NULL, -- supervision, capacity, behavior, restricted_area, etc.
    embedding vector(384),         -- pgvector column (384 = all-MiniLM-L6-v2 dimensions)
    metadata JSONB DEFAULT '{}',
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index for vector similarity search (cosine distance)
CREATE INDEX IF NOT EXISTS rules_embedding_idx
ON rules USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS rules_category_idx ON rules(category);
CREATE INDEX IF NOT EXISTS rules_severity_idx ON rules(severity);
CREATE INDEX IF NOT EXISTS rules_enabled_idx ON rules(enabled);

-- Create events table for violation tracking
CREATE TABLE IF NOT EXISTS violation_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(100) UNIQUE NOT NULL,
    rule_id VARCHAR(50) REFERENCES rules(rule_id),
    camera_id VARCHAR(50),
    site_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    context TEXT,
    evidence_clip_path TEXT,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'acknowledged', 'resolved', 'false_positive')),
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for violation events
CREATE INDEX IF NOT EXISTS violation_events_timestamp_idx ON violation_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS violation_events_status_idx ON violation_events(status);
CREATE INDEX IF NOT EXISTS violation_events_site_idx ON violation_events(site_id);
CREATE INDEX IF NOT EXISTS violation_events_camera_idx ON violation_events(camera_id);

-- Create audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    user_id VARCHAR(100),
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    action VARCHAR(50) NOT NULL,
    details JSONB DEFAULT '{}',
    ip_address INET,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS audit_log_timestamp_idx ON audit_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS audit_log_user_idx ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS audit_log_event_type_idx ON audit_log(event_type);

-- Insert sample rules for testing
INSERT INTO rules (rule_id, title, description, clause, source, severity, category) VALUES
('RULE-001', 'Continuous Adult Supervision Required', 'Children ages 0-5 must be within sight and sound of qualified staff at all times during operating hours', 'Children ages zero through five years must be within sight and sound of qualified child care staff at all times', 'STATE-REG-45.1.2', 'critical', 'supervision'),
('RULE-002', 'Maximum Room Capacity', 'Classrooms must not exceed posted maximum occupancy limits', 'The total number of persons (children and staff) in any room shall not exceed the posted maximum occupancy', 'FIRE-CODE-12.4', 'high', 'capacity'),
('RULE-003', 'Restricted Area Access', 'Children must not access kitchens, storage rooms, or staff-only areas without direct supervision', 'Children shall be prohibited from entering food preparation areas, chemical storage, and administrative offices without immediate staff escort', 'HEALTH-CODE-8.2', 'high', 'restricted_area')
ON CONFLICT (rule_id) DO NOTHING;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
CREATE TRIGGER update_rules_updated_at BEFORE UPDATE ON rules
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE rules IS 'School policies and government regulations with vector embeddings for semantic search';
COMMENT ON TABLE violation_events IS 'Detected safety violations with evidence and resolution tracking';
COMMENT ON TABLE audit_log IS 'Immutable audit trail of all system actions';
COMMENT ON EXTENSION vector IS 'pgvector extension for similarity search (replaces Qdrant)';
COMMENT ON EXTENSION postgis IS 'PostGIS extension for geospatial features (bus tracking, geofencing)';
