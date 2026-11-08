-- Migration 006: Enhanced Alerts with Person Identity (Fixed)
-- Week 1: Add person identification and context to alerts
-- Created: 2026-11-08

-- Columns already added by previous migration, ensure they exist
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='alerts' AND column_name='persons_involved') THEN
    ALTER TABLE alerts ADD COLUMN persons_involved JSONB DEFAULT '[]'::jsonb;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='alerts' AND column_name='context') THEN
    ALTER TABLE alerts ADD COLUMN context JSONB DEFAULT '{}'::jsonb;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='alerts' AND column_name='evidence') THEN
    ALTER TABLE alerts ADD COLUMN evidence JSONB DEFAULT '{}'::jsonb;
  END IF;
END $$;

-- Create indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_alerts_persons ON alerts USING GIN (persons_involved);
CREATE INDEX IF NOT EXISTS idx_alerts_context ON alerts USING GIN (context);
CREATE INDEX IF NOT EXISTS idx_alerts_evidence ON alerts USING GIN (evidence);

-- Person face images storage (using 'id' column from alerts table)
CREATE TABLE IF NOT EXISTS alert_person_images (
  image_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
  person_id VARCHAR(255),
  image_filename VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alert_person_images_alert ON alert_person_images(alert_id);
CREATE INDEX IF NOT EXISTS idx_alert_person_images_person ON alert_person_images(person_id);

-- Comments
COMMENT ON COLUMN alerts.persons_involved IS 'JSONB array: [{person_id, name, role, confidence, image_url, bbox, is_primary_subject}]';
COMMENT ON COLUMN alerts.context IS 'JSONB: {detection_method, detector_scores, vlm_analysis, environment}';
COMMENT ON COLUMN alerts.evidence IS 'JSONB: {snapshot_url, clip_url, clip_duration_seconds, etc}';

SELECT 'Migration 006 complete' AS status;
