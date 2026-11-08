-- Alerts table schema
-- Run this migration to create the alerts table

CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    camera VARCHAR(255) NOT NULL,
    violation_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'acknowledged', 'resolved', 'escalated')),
    confidence FLOAT NOT NULL,
    person_id VARCHAR(255),
    detection_count INTEGER DEFAULT 1,
    confidence_avg FLOAT,
    confidence_max FLOAT,
    details TEXT NOT NULL,
    metadata JSONB,
    hash VARCHAR(64),
    first_detected TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_detected TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by VARCHAR(255),
    resolved_at TIMESTAMP WITH TIME ZONE,
    escalation_level INTEGER
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_alerts_camera ON alerts(camera);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_first_detected ON alerts(first_detected);
CREATE INDEX IF NOT EXISTS idx_alerts_hash ON alerts(hash);
CREATE INDEX IF NOT EXISTS idx_alerts_violation_type ON alerts(violation_type);

-- Composite index for deduplication queries
CREATE INDEX IF NOT EXISTS idx_alerts_hash_first_detected ON alerts(hash, first_detected);

-- Comments
COMMENT ON TABLE alerts IS 'Stores safety violation alerts from AI detection pipeline';
COMMENT ON COLUMN alerts.hash IS 'SHA256 hash for deduplication (camera + violation_type + person_id)';
COMMENT ON COLUMN alerts.detection_count IS 'Number of times this violation was detected (aggregated)';
COMMENT ON COLUMN alerts.confidence_avg IS 'Average confidence across all aggregated detections';
COMMENT ON COLUMN alerts.confidence_max IS 'Maximum confidence seen across all aggregated detections';
COMMENT ON COLUMN alerts.metadata IS 'Full violation data from AI pipeline (JSONB)';
COMMENT ON COLUMN alerts.escalation_level IS 'Current escalation level (0=none, 1=supervisor, 2=manager, 3=director)';
