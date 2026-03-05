-- Migration: Add content column to artifacts table
-- Replaces file_path with direct content storage

-- Add new columns
ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS content TEXT;
ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS content_type VARCHAR(100);
ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;

-- Rename file_path to file_path_old (for rollback if needed)
ALTER TABLE artifacts RENAME COLUMN file_path TO file_path_old;

-- Make content required after migration
-- UPDATE artifacts SET content = '' WHERE content IS NULL;
-- ALTER TABLE artifacts ALTER COLUMN content SET NOT NULL;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_artifacts_universe_type ON artifacts(universe_id, artifact_type);
CREATE INDEX IF NOT EXISTS idx_artifacts_created ON artifacts(created_at DESC);

-- Comments
COMMENT ON COLUMN artifacts.content IS 'Artifact content stored directly (JSON, SQL, DOT, etc)';
COMMENT ON COLUMN artifacts.content_type IS 'MIME type: application/json, text/sql, text/plain';
COMMENT ON COLUMN artifacts.version IS 'Version number for artifact versioning';
