# Enterprise Artifact Storage - Deployment Guide

## What Changed

**Problem**: Render's ephemeral filesystem loses all generated artifacts (SAC models, SQL schemas, validation reports) on every deployment or restart.

**Solution**: Store all artifacts directly in Neon PostgreSQL database for persistent, enterprise-grade storage.

## Architecture

```
Pipeline Stages:
├── Parser    → Save CIM to database
├── Transform → Save SAC/Datasphere/HANA artifacts to database
└── Validation → Save coverage/lineage/semantic_diff to database

API Endpoints:
└── Serve artifacts from database (no filesystem required)
```

## Files Modified

### 1. Database Schema
- **`backend/app/models/database.py`**
  - `Artifact.content` - TEXT column for storing artifact content
  - `Artifact.content_type` - MIME type (application/json, text/sql, text/plain)
  - `Artifact.version` - Version tracking

### 2. Artifact Storage Service
- **`backend/app/services/artifact_storage.py`** (NEW)
  - `ArtifactStorage.save_artifact()` - Save artifact to database
  - `ArtifactStorage.get_artifact()` - Retrieve artifact from database
  - `ArtifactStorage.list_artifacts()` - List all artifacts for universe
  - Supports JSON and file-based artifacts

### 3. Pipeline Integration
- **`backend/app/services/pipeline_integrated.py`**
  - Parser: Save CIM artifacts
  - Transform: Save SAC/Datasphere/HANA artifacts
  - Validation: Save coverage/lineage/semantic_diff artifacts

### 4. API Routes
- **`backend/app/api/routes.py`**
  - `/universes/{id}/sac` - Serve SAC model from database
  - `/universes/{id}/download` - Serve artifacts from database
  - `/universes/{id}/reports` - Get reports from database

### 5. Database Migration
- **`backend/migrations/002_add_artifact_content.sql`**
  - Add `content`, `content_type`, `version` columns
  - Rename `file_path` to `file_path_old` (for rollback)
  - Add indexes for performance

## Deployment Steps

### Step 1: Code Deployment ✅ DONE
```bash
git add backend/app/models/database.py backend/app/services/artifact_storage.py \
        backend/app/api/routes.py backend/app/services/pipeline_integrated.py \
        backend/migrations/
git commit -m "Enterprise artifact storage in PostgreSQL"
git push origin main
```

**Status**: Deployed to GitHub. Render auto-deploying now.

### Step 2: Database Migration ⏳ PENDING
```bash
cd ~/migration_studio/backend
export DATABASE_URL='postgresql://neon_user:password@ep-dark-hill-aiwdm4cf-pooler.c-4.us-east-1.aws.neon.tech/neondb'
./apply_migration.sh
```

**What it does**:
- Adds new columns to `artifacts` table
- Preserves old `file_path` column as `file_path_old` (for rollback)
- Creates indexes for performance

### Step 3: Wait for Render Deployment ⏳ PENDING
Check deployment status at: https://dashboard.render.com

### Step 4: Trigger Pipeline Run ⏳ PENDING
```bash
curl -X POST https://migration-studio-api.onrender.com/api/run-pipeline
```

**What it does**:
- Processes all universes
- Saves all artifacts to database
- Validates everything

### Step 5: Test Artifact Access ⏳ PENDING
```bash
# List universes
curl https://migration-studio-api.onrender.com/api/universes

# Get SAC model
curl https://migration-studio-api.onrender.com/api/universes/BOEXI40-Audit-Sybase/sac

# Download artifact
curl "https://migration-studio-api.onrender.com/api/universes/BOEXI40-Audit-Sybase/download?artifact=sac/model.json"
```

**Expected**: All artifacts return 200 OK with content from database.

## Benefits

✅ **Persistent Storage** - Artifacts survive deployments/restarts
✅ **Enterprise Reliability** - Neon PostgreSQL with backups
✅ **No File Management** - No filesystem cleanup needed
✅ **Versioning Ready** - Version column for future enhancements
✅ **Audit Trail** - created_at timestamps on all artifacts
✅ **Scalable** - Database handles growth automatically

## Rollback Plan

If migration fails, revert database changes:
```sql
ALTER TABLE artifacts RENAME COLUMN file_path_old TO file_path;
ALTER TABLE artifacts DROP COLUMN IF EXISTS content;
ALTER TABLE artifacts DROP COLUMN IF EXISTS content_type;
ALTER TABLE artifacts DROP COLUMN IF EXISTS version;
```

Then revert code:
```bash
git revert HEAD
git push origin main
```

## Next Steps

1. ✅ **Code deployed** - Waiting for Render
2. ⏳ **Run migration** - Apply schema changes to Neon
3. ⏳ **Trigger pipeline** - Populate artifacts in database
4. ⏳ **Test endpoints** - Verify artifact downloads work
5. ⏳ **Monitor Render logs** - Check for any errors

## Notes

- Old filesystem-based code still works locally (for development)
- Production (Render) now uses database exclusively
- Frontend requires no changes (same API endpoints)
- Migration is backward-compatible (keeps old file_path column)

## Support

If issues arise:
- Check Render logs: https://dashboard.render.com
- Check Neon console: https://console.neon.tech
- Verify migration applied: `psql $DATABASE_URL -c "\d artifacts"`
