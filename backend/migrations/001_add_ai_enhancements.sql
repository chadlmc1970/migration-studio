-- Migration: Add AI enhancements columns to universes table
-- Description: Adds all AI-related columns (flag, summary, data, timestamp)
-- Date: 2026-03-05
-- Author: Claude (Migration Studio)

-- Add ai_enhanced boolean flag
ALTER TABLE universes
ADD COLUMN IF NOT EXISTS ai_enhanced BOOLEAN DEFAULT FALSE;

-- Add ai_enhancement_summary text field
ALTER TABLE universes
ADD COLUMN IF NOT EXISTS ai_enhancement_summary TEXT;

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

-- Add comments for documentation
COMMENT ON COLUMN universes.ai_enhanced IS 'Boolean flag indicating if AI processing was successful';
COMMENT ON COLUMN universes.ai_enhancement_summary IS 'Human-readable summary of AI enhancements applied';
COMMENT ON COLUMN universes.ai_enhancements IS 'Structured AI enhancement data including dimension classifications, hierarchies, and formula translations';
COMMENT ON COLUMN universes.ai_processed_at IS 'Timestamp when AI semantic enhancement processing completed';
