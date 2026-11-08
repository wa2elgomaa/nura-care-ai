-- Migration 008: WiFi Sensing & Visitor Management
-- Week 3: Dual data sources (Camera + WiFi) + Stranger detection
-- Created: 2026-11-08

-- WiFi sensing events (PRIMARY data source)
CREATE TABLE IF NOT EXISTS wifi_sensing_events (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  room_id VARCHAR(100) NOT NULL,
  room_type VARCHAR(50) NOT NULL,
  occupancy_count INTEGER NOT NULL,
  device_count INTEGER NOT NULL,
  timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
  duration_seconds INTEGER,
  esp32_nodes TEXT[],  -- Array of ESP32 MAC addresses

  CONSTRAINT valid_room_type CHECK (room_type IN ('bathroom', 'kitchen', 'storage', 'mechanical', 'classroom'))
);

CREATE INDEX IF NOT EXISTS idx_wifi_events_room ON wifi_sensing_events(room_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_wifi_events_timestamp ON wifi_sensing_events(timestamp DESC);

-- WiFi room configuration
CREATE TABLE IF NOT EXISTS wifi_rooms (
  room_id VARCHAR(100) PRIMARY KEY,
  room_type VARCHAR(50) NOT NULL,
  room_name VARCHAR(255) NOT NULL,
  esp32_node_ids TEXT[],
  camera_coverage BOOLEAN DEFAULT FALSE,  -- Does room also have cameras?
  multi_occupancy_threshold INTEGER DEFAULT 2,
  multi_occupancy_duration_seconds INTEGER DEFAULT 120,
  operating_hours_start TIME DEFAULT '06:00',
  operating_hours_end TIME DEFAULT '18:00',
  enabled BOOLEAN DEFAULT TRUE
);

-- Visitors table
CREATE TABLE IF NOT EXISTS visitors (
  visitor_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  face_encoding VECTOR(512),
  photo_path VARCHAR(500),  -- Path in storage service
  valid_from TIMESTAMP NOT NULL,
  valid_until TIMESTAMP NOT NULL,
  purpose TEXT,
  approved_by VARCHAR(255),
  checked_out TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_visitors_valid ON visitors(valid_from, valid_until) WHERE checked_out IS NULL;
CREATE INDEX IF NOT EXISTS idx_visitors_name ON visitors(name);

-- Update alerts to track data source
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='alerts' AND column_name='data_source'
  ) THEN
    ALTER TABLE alerts ADD COLUMN data_source VARCHAR(20);
  END IF;
END $$;

-- Add constraint if not exists
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.constraint_column_usage
    WHERE constraint_name='valid_data_source'
  ) THEN
    ALTER TABLE alerts ADD CONSTRAINT valid_data_source
      CHECK (data_source IN ('camera', 'wifi', 'hybrid'));
  END IF;
END $$;

-- Add is_visitor to enrolled_persons if not exists
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='enrolled_persons' AND column_name='is_visitor'
  ) THEN
    ALTER TABLE enrolled_persons ADD COLUMN is_visitor BOOLEAN DEFAULT FALSE;
  END IF;
END $$;

-- Insert example WiFi rooms
INSERT INTO wifi_rooms (room_id, room_type, room_name, esp32_node_ids, camera_coverage) VALUES
  ('bathroom_boys_1f', 'bathroom', 'Boys Bathroom 1F', ARRAY['AA:BB:CC:DD:EE:01'], FALSE),
  ('bathroom_girls_1f', 'bathroom', 'Girls Bathroom 1F', ARRAY['AA:BB:CC:DD:EE:02'], FALSE),
  ('storage_main', 'storage', 'Main Storage Room', ARRAY['AA:BB:CC:DD:EE:03'], FALSE),
  ('kitchen', 'kitchen', 'Kitchen', ARRAY['AA:BB:CC:DD:EE:04'], TRUE)
ON CONFLICT (room_id) DO NOTHING;

-- Comments
COMMENT ON TABLE wifi_sensing_events IS 'WiFi sensing occupancy events from ESP32/RuView (PRIMARY data source)';
COMMENT ON TABLE wifi_rooms IS 'WiFi sensing room configuration';
COMMENT ON TABLE visitors IS 'Temporary visitor whitelist for stranger detection';
COMMENT ON COLUMN alerts.data_source IS 'Data source: camera, wifi, or hybrid (both)';

SELECT 'Migration 008 complete' AS status;
