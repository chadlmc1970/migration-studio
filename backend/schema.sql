-- Migration Studio Database Schema for Neon PostgreSQL

-- Universes table - replaces pipeline_state.json
CREATE TABLE universes (
    id VARCHAR(255) PRIMARY KEY,
    parsed BOOLEAN DEFAULT FALSE,
    transformed BOOLEAN DEFAULT FALSE,
    validated BOOLEAN DEFAULT FALSE,
    validated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Events table - replaces events.log
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    level VARCHAR(20) NOT NULL, -- INFO, WARNING, ERROR
    message TEXT NOT NULL,
    universe_id VARCHAR(255),
    metadata JSONB,
    FOREIGN KEY (universe_id) REFERENCES universes(id) ON DELETE CASCADE
);

-- Pipeline runs table - track execution history
CREATE TABLE runs (
    id VARCHAR(50) PRIMARY KEY,
    status VARCHAR(20) NOT NULL, -- pending, running, completed, failed
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    universes_processed INTEGER DEFAULT 0,
    metadata JSONB
);

-- Validation reports table - store coverage and semantic diff
CREATE TABLE validation_reports (
    id SERIAL PRIMARY KEY,
    universe_id VARCHAR(255) NOT NULL,
    coverage_report JSONB,
    semantic_diff JSONB,
    lineage_graph TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (universe_id) REFERENCES universes(id) ON DELETE CASCADE
);

-- Artifacts table - track available downloads
CREATE TABLE artifacts (
    id SERIAL PRIMARY KEY,
    universe_id VARCHAR(255) NOT NULL,
    artifact_type VARCHAR(50) NOT NULL, -- sac_model, datasphere_views, hana_schema, lineage_dot
    file_path TEXT NOT NULL,
    file_size INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (universe_id) REFERENCES universes(id) ON DELETE CASCADE,
    UNIQUE(universe_id, artifact_type)
);

-- Indexes for performance
CREATE INDEX idx_events_timestamp ON events(timestamp DESC);
CREATE INDEX idx_events_universe ON events(universe_id);
CREATE INDEX idx_runs_status ON runs(status);
CREATE INDEX idx_runs_started ON runs(started_at DESC);
CREATE INDEX idx_artifacts_universe ON artifacts(universe_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for universes table
CREATE TRIGGER update_universes_updated_at
    BEFORE UPDATE ON universes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
