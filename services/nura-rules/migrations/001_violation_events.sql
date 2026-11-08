-- nura-rules Database Schema
-- Violation events table for storing detected violations

-- Violation events table
CREATE TABLE IF NOT EXISTS violation_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(100) UNIQUE NOT NULL,
    rule_id VARCHAR(100) NOT NULL,
    camera_id VARCHAR(100) NOT NULL,
    site_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    context TEXT NOT NULL,
    evidence_clip_path VARCHAR(500),
    rule_source VARCHAR(255),
    similarity_score FLOAT,
    duration_seconds FLOAT,
    status VARCHAR(50) DEFAULT 'open' CHECK (status IN ('open', 'acknowledged', 'resolved', 'dismissed')),
    acknowledged BOOLEAN DEFAULT false,
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by VARCHAR(100),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS violation_events_rule_id_idx ON violation_events(rule_id);
CREATE INDEX IF NOT EXISTS violation_events_camera_id_idx ON violation_events(camera_id);
CREATE INDEX IF NOT EXISTS violation_events_site_id_idx ON violation_events(site_id);
CREATE INDEX IF NOT EXISTS violation_events_severity_idx ON violation_events(severity);
CREATE INDEX IF NOT EXISTS violation_events_timestamp_idx ON violation_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS violation_events_acknowledged_idx ON violation_events(acknowledged);

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS violation_events_site_camera_idx ON violation_events(site_id, camera_id, timestamp DESC);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_violation_events_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_violation_events_updated_at
BEFORE UPDATE ON violation_events
FOR EACH ROW EXECUTE FUNCTION update_violation_events_updated_at();

-- Comments for documentation
COMMENT ON TABLE violation_events IS 'Detected violations from rules engine';
COMMENT ON COLUMN violation_events.event_id IS 'Unique event identifier (EVT-timestamp-random)';
COMMENT ON COLUMN violation_events.similarity_score IS 'RAG similarity score for matched rule (0-1)';
COMMENT ON COLUMN violation_events.duration_seconds IS 'Duration of violation condition (for threshold-based rules)';
COMMENT ON COLUMN violation_events.evidence_clip_path IS 'Path to video clip evidence';
COMMENT ON COLUMN violation_events.acknowledged IS 'Whether violation has been acknowledged by staff';
