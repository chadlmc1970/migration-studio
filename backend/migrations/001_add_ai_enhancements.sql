-- Migration: Add AI enhancements columns to universes table
-- Description: Adds JSONB column for structured AI enhancement data and timestamp
-- Date: 2026-03-05
-- Author: Claude (Migration Studio)

-- Add ai_enhancements JSONB column for structured data
ALTER TABLE universes
ADD COLUMN IF NOT EXISTS ai_enhancements JSONB;

-- Add timestamp for when AI processing completed
ALTER TABLE universes
ADD COLUMN IF NOT EXISTS ai_processed_at TIMESTAMP WITH TIME ZONE;

-- Create index for querying AI enhancement data
CREATE INDEX IF NOT EXISTS idx_universes_ai_enhanced
ON universes(ai_enhanced)
WHERE ai_enhanced = true;

-- Create GIN index for JSONB queries (enables fast JSON queries)
CREATE INDEX IF NOT EXISTS idx_universes_ai_enhancements
ON universes USING GIN (ai_enhancements);

-- Add comment for documentation
COMMENT ON COLUMN universes.ai_enhancements IS 'Structured AI enhancement data including dimension classifications, hierarchies, and formula translations';
COMMENT ON COLUMN universes.ai_processed_at IS 'Timestamp when AI semantic enhancement processing completed';
