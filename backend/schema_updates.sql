-- BOBJ Migration Studio - Database Schema Updates
-- Add support for new file types and target formats
-- Date: 2026-03-04

-- ============================================================================
-- 1. ADD COLUMNS TO UNIVERSES TABLE
-- ============================================================================

-- Add source format tracking
ALTER TABLE universes ADD COLUMN IF NOT EXISTS source_format VARCHAR(10);
COMMENT ON COLUMN universes.source_format IS 'File format: unx, unv, wid, rpt, rep, car';

-- Add source subtype
ALTER TABLE universes ADD COLUMN IF NOT EXISTS source_subtype VARCHAR(50);
COMMENT ON COLUMN universes.source_subtype IS 'Detailed type: webi_document, crystal_report, etc.';

-- Add target formats (JSONB array)
ALTER TABLE universes ADD COLUMN IF NOT EXISTS target_formats JSONB DEFAULT '{}';
COMMENT ON COLUMN universes.target_formats IS 'Target outputs: {"sac": true, "hana": true, "datasphere": false}';

-- Add parser/generator versions
ALTER TABLE universes ADD COLUMN IF NOT EXISTS parser_version VARCHAR(20);
ALTER TABLE universes ADD COLUMN IF NOT EXISTS generator_version VARCHAR(20);

-- ============================================================================
-- 2. CREATE ARTIFACTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS artifacts (
    id SERIAL PRIMARY KEY,
    universe_id VARCHAR(255) NOT NULL REFERENCES universes(id) ON DELETE CASCADE,
    artifact_type VARCHAR(50) NOT NULL,
    file_path TEXT NOT NULL,
    size_bytes INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

COMMENT ON TABLE artifacts IS 'Tracks generated artifacts (SAC models, HANA schemas, etc.)';
COMMENT ON COLUMN artifacts.artifact_type IS 'Type: sac_model, sac_story, hana_schema, hana_calcview, datasphere_views, datasphere_model, lineage_graph';

CREATE INDEX IF NOT EXISTS idx_artifacts_universe_id ON artifacts(universe_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_type ON artifacts(artifact_type);

-- ============================================================================
-- 3. CREATE PARSERS TABLE (Metadata about available parsers)
-- ============================================================================

CREATE TABLE IF NOT EXISTS parsers (
    id SERIAL PRIMARY KEY,
    parser_name VARCHAR(50) UNIQUE NOT NULL,
    file_extension VARCHAR(10) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    version VARCHAR(20),
    metadata JSONB DEFAULT '{}'
);

COMMENT ON TABLE parsers IS 'Available input parsers and their capabilities';

-- Insert parser metadata
INSERT INTO parsers (parser_name, file_extension, description, status, version) VALUES
    ('UNX Parser', 'unx', 'Universe Designer (UNX - ZIP-based)', 'active', '1.0'),
    ('UNV Parser', 'unv', 'Universe Designer (UNV - binary)', 'placeholder', '0.5'),
    ('WebI Parser', 'wid', 'WebIntelligence documents', 'active', '1.0'),
    ('Crystal Parser', 'rpt', 'Crystal Reports', 'placeholder', '0.1'),
    ('WebI Rep Parser', 'rep', 'WebIntelligence reports (old format)', 'placeholder', '0.1'),
    ('BIAR Parser', 'car', 'BusinessObjects BIAR archives', 'active', '1.0')
ON CONFLICT (parser_name) DO NOTHING;

-- ============================================================================
-- 4. CREATE GENERATORS TABLE (Metadata about available generators)
-- ============================================================================

CREATE TABLE IF NOT EXISTS generators (
    id SERIAL PRIMARY KEY,
    generator_name VARCHAR(50) UNIQUE NOT NULL,
    target_format VARCHAR(20) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    version VARCHAR(20),
    metadata JSONB DEFAULT '{}'
);

COMMENT ON TABLE generators IS 'Available output generators and their capabilities';

-- Insert generator metadata
INSERT INTO generators (generator_name, target_format, description, status, version) VALUES
    ('SAC Model Generator', 'sac', 'SAP Analytics Cloud models', 'active', '1.0'),
    ('SAC Story Generator', 'sac_story', 'SAP Analytics Cloud stories', 'planned', '0.1'),
    ('HANA Schema Generator', 'hana', 'SAP HANA Cloud schemas', 'active', '1.0'),
    ('HANA CalcView Generator', 'hana_calcview', 'SAP HANA calculation views', 'active', '1.0'),
    ('Datasphere Generator', 'datasphere', 'SAP Datasphere views', 'active', '1.0')
ON CONFLICT (generator_name) DO NOTHING;

-- ============================================================================
-- 5. UPDATE VALIDATION_REPORTS TABLE (if exists)
-- ============================================================================

-- Add validation details for new validators
ALTER TABLE validation_reports ADD COLUMN IF NOT EXISTS sac_validation JSONB;
ALTER TABLE validation_reports ADD COLUMN IF NOT EXISTS hana_validation JSONB;
ALTER TABLE validation_reports ADD COLUMN IF NOT EXISTS datasphere_validation JSONB;

COMMENT ON COLUMN validation_reports.sac_validation IS 'SAC model validation results';
COMMENT ON COLUMN validation_reports.hana_validation IS 'HANA schema validation results';
COMMENT ON COLUMN validation_reports.datasphere_validation IS 'Datasphere views validation results';

-- ============================================================================
-- 6. CREATE PARSER_LOGS TABLE (Optional - for detailed parser tracking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS parser_logs (
    id SERIAL PRIMARY KEY,
    universe_id VARCHAR(255) NOT NULL REFERENCES universes(id) ON DELETE CASCADE,
    parser_name VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_seconds FLOAT,
    files_processed INTEGER DEFAULT 0,
    warnings_count INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    log_data JSONB DEFAULT '{}'
);

COMMENT ON TABLE parser_logs IS 'Detailed parser execution logs';

CREATE INDEX IF NOT EXISTS idx_parser_logs_universe ON parser_logs(universe_id);
CREATE INDEX IF NOT EXISTS idx_parser_logs_parser ON parser_logs(parser_name);

-- ============================================================================
-- 7. SAMPLE QUERIES
-- ============================================================================

-- Get all universes with their formats and target configs
-- SELECT
--     id,
--     source_format,
--     source_subtype,
--     target_formats,
--     parsed,
--     transformed,
--     validated
-- FROM universes;

-- Get all artifacts for a universe
-- SELECT
--     artifact_type,
--     file_path,
--     size_bytes,
--     created_at
-- FROM artifacts
-- WHERE universe_id = 'your_universe_id'
-- ORDER BY created_at DESC;

-- Get parser/generator statistics
-- SELECT
--     parser_name,
--     status,
--     version,
--     COUNT(pl.id) as executions
-- FROM parsers p
-- LEFT JOIN parser_logs pl ON p.parser_name = pl.parser_name
-- GROUP BY parser_name, status, version;

-- ============================================================================
-- 8. CLEANUP (if needed)
-- ============================================================================

-- Drop old/unused columns (uncomment if you want to remove)
-- ALTER TABLE universes DROP COLUMN IF EXISTS old_column_name;
