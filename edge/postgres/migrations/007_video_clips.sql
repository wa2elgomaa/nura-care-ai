-- Migration 007: Video Evidence Clips
-- Week 2: Add video clip processing and retention
-- Created: 2026-11-08

-- Clip processing queue
CREATE TABLE IF NOT EXISTS clip_processing_queue (
  queue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
  camera_id VARCHAR(255) NOT NULL,
  incident_timestamp TIMESTAMP NOT NULL,
  before_seconds INTEGER DEFAULT 10,
  after_seconds INTEGER DEFAULT 20,
  status VARCHAR(50) DEFAULT 'pending',  -- pending, processing, completed, failed
  retry_count INTEGER DEFAULT 0,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP,

  CONSTRAINT valid_status CHECK (status IN ('pending', 'processing', 'completed', 'failed'))
);

CREATE INDEX IF NOT EXISTS idx_queue_status ON clip_processing_queue(status, created_at);
CREATE INDEX IF NOT EXISTS idx_queue_alert ON clip_processing_queue(alert_id);

-- Clip retention tracking
CREATE TABLE IF NOT EXISTS clip_retention (
  clip_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
  file_path VARCHAR(500) NOT NULL,
  file_size_bytes BIGINT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL,
  deleted_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_clip_expires ON clip_retention(expires_at) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_clip_alert ON clip_retention(alert_id);

-- Comments
COMMENT ON TABLE clip_processing_queue IS 'Queue for background clip processing from Frigate';
COMMENT ON TABLE clip_retention IS 'Track video clip files for retention/cleanup';
COMMENT ON COLUMN clip_processing_queue.before_seconds IS 'Seconds before incident to include in clip (default 10)';
COMMENT ON COLUMN clip_processing_queue.after_seconds IS 'Seconds after incident to include in clip (default 20)';
COMMENT ON COLUMN clip_retention.expires_at IS 'When clip should be deleted (default 30 days from creation)';

SELECT 'Migration 007 complete' AS status;
