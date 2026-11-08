-- Migration 006: Enhanced Alerts with Person Identity
-- Week 1: Add person identification and context to alerts
-- Created: 2026-11-08

-- Update alerts table to support JSONB for persons_involved and context
ALTER TABLE alerts
  ADD COLUMN IF NOT EXISTS persons_involved JSONB DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS context JSONB DEFAULT '{}'::jsonb;

-- Create indexes for JSONB queries
CREATE INDEX IF NOT EXISTS idx_alerts_persons ON alerts USING GIN (persons_involved);
CREATE INDEX IF NOT EXISTS idx_alerts_context ON alerts USING GIN (context);

-- Add evidence storage table for person face images
CREATE TABLE IF NOT EXISTS alert_person_images (
  image_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_id UUID REFERENCES alerts(alert_id) ON DELETE CASCADE,
  person_id VARCHAR(255),
  image_data BYTEA NOT NULL,
  image_filename VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alert_person_images_alert ON alert_person_images(alert_id);
CREATE INDEX IF NOT EXISTS idx_alert_person_images_person ON alert_person_images(person_id);

-- Add evidence field update (if alerts table already has evidence column)
-- Update existing alerts to have proper evidence structure
DO $$
BEGIN
  -- Check if evidence column exists and is not JSONB
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'alerts' AND column_name = 'evidence'
    AND data_type != 'jsonb'
  ) THEN
    -- Convert to JSONB if needed
    ALTER TABLE alerts ALTER COLUMN evidence TYPE JSONB USING evidence::JSONB;
  ELSIF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'alerts' AND column_name = 'evidence'
  ) THEN
    -- Add evidence column if it doesn't exist
    ALTER TABLE alerts ADD COLUMN evidence JSONB DEFAULT '{}'::jsonb;
  END IF;
END $$;

-- Create index for evidence queries
CREATE INDEX IF NOT EXISTS idx_alerts_evidence ON alerts USING GIN (evidence);

-- Comments for documentation
COMMENT ON COLUMN alerts.persons_involved IS 'JSONB array of persons involved in the alert with their details (person_id, name, role, confidence, image_url, bbox, is_primary_subject)';
COMMENT ON COLUMN alerts.context IS 'JSONB object containing detection context (detection_method, detector_scores, vlm_analysis, environment data)';
COMMENT ON COLUMN alerts.evidence IS 'JSONB object containing evidence URLs (snapshot_url, clip_url, etc.)';
COMMENT ON TABLE alert_person_images IS 'Stores face images extracted from frames for persons involved in alerts';

-- Migration complete
-- This migration is idempotent and can be run multiple times safely
