#!/bin/bash
# Apply database migration to Neon PostgreSQL production database
# Run this after deploying artifact storage changes

set -e

echo "======================================"
echo "Database Migration - Artifact Storage"
echo "======================================"
echo ""

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL environment variable not set"
    echo ""
    echo "Set it with:"
    echo "  export DATABASE_URL='postgresql://...'"
    exit 1
fi

MIGRATION_FILE="migrations/002_add_artifact_content.sql"

if [ ! -f "$MIGRATION_FILE" ]; then
    echo "❌ Migration file not found: $MIGRATION_FILE"
    exit 1
fi

echo "Migration: $MIGRATION_FILE"
echo "Target: Production (Neon)"
echo ""
echo "This will:"
echo "  - Add 'content' column to artifacts table"
echo "  - Add 'content_type' and 'version' columns"
echo "  - Rename 'file_path' to 'file_path_old'"
echo "  - Create indexes for performance"
echo ""

read -p "Apply migration to production? (yes/no): " response

if [ "$response" != "yes" ]; then
    echo "❌ Migration cancelled"
    exit 0
fi

echo ""
echo "Applying migration..."

# Apply using psql
psql "$DATABASE_URL" -f "$MIGRATION_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration applied successfully!"
    echo ""
    echo "Verifying schema..."
    psql "$DATABASE_URL" -c "\d artifacts"
    echo ""
    echo "======================================"
    echo "✅ Complete"
    echo "======================================"
    echo ""
    echo "Next steps:"
    echo "1. Render will auto-deploy new code (check https://dashboard.render.com)"
    echo "2. Trigger pipeline run to populate artifacts:"
    echo "   curl -X POST https://migration-studio-api.onrender.com/api/run-pipeline"
else
    echo ""
    echo "❌ Migration failed"
    exit 1
fi
