# Storage Controls & Database Maintenance

## Overview

The Migration Studio includes comprehensive storage controls to prevent unbounded growth on Neon PostgreSQL and maintain database health.

## Storage Limits

| Resource | Limit | Reason |
|----------|-------|--------|
| **Individual Artifact** | 10 MB | Prevents single huge artifacts |
| **Total Database Size** | 500 MB | Neon free tier is 512 MB |
| **Artifacts per Universe** | 20 | Prevents runaway versioning |

## Retention Policies

| Data Type | Retention | Versions Kept |
|-----------|-----------|---------------|
| **Events** | 30 days | N/A |
| **Run Records** | 90 days | N/A |
| **Artifact Versions** | Latest only | 3 versions per type |
| **Orphaned Universes** | N/A | Deleted if no artifacts |

## API Endpoints

### Storage Monitoring

```bash
# Get storage statistics
GET /api/storage/stats

Response:
{
  "total_size_mb": 45.3,
  "usage_percent": 9.1,
  "max_size_mb": 500,
  "artifacts": {
    "cim": { "count": 7, "size_mb": 0.02 },
    "sac_model": { "count": 7, "size_mb": 15.2 },
    "hana_schema": { "count": 7, "size_mb": 10.1 }
  },
  "counts": {
    "universes": 7,
    "artifacts": 28,
    "runs": 12,
    "events": 456
  },
  "warnings": []
}

# Get largest artifacts
GET /api/storage/largest?limit=10
```

### Manual Cleanup

```bash
# Full cleanup (all operations)
POST /api/storage/cleanup

# Cleanup old events (default: 30 days)
POST /api/storage/cleanup/events?days=30

# Cleanup old run records (default: 90 days)
POST /api/storage/cleanup/runs?days=90

# Cleanup old artifact versions (default: keep 3)
POST /api/storage/cleanup/artifacts?keep_versions=3
```

## Automated Maintenance

### Nightly Cleanup (GitHub Actions)

A GitHub Actions workflow runs every night at 2 AM UTC:

**File:** `.github/workflows/nightly-maintenance.yml`

**Tasks:**
1. Delete events older than 30 days
2. Delete run records older than 90 days
3. Delete old artifact versions (keep latest 3)
4. Delete orphaned universes (no artifacts)
5. Report storage statistics

**Setup:**
1. Go to GitHub Repository Settings → Secrets
2. Add secret: `NEON_DATABASE_URL` with your Neon connection string
3. Workflow runs automatically every night

### Manual Maintenance Script

You can also run maintenance manually:

```bash
cd backend/scripts
export DATABASE_URL='postgresql://user:pass@host/db'
python nightly_maintenance.py
```

## Storage Warnings

The system monitors storage usage and provides warnings:

| Usage Level | Warning | Action |
|-------------|---------|--------|
| **> 60%** | Monitor closely | Watch for growth trends |
| **> 80%** | Cleanup recommended | Run manual cleanup |
| **> 90%** | Critical | Delete old universes or upgrade Neon plan |

## What Gets Cleaned Up

### Events (30 days)
- Parsing logs
- Transform logs
- Validation logs
- Pipeline run events

**Impact:** Historical logs older than 30 days are deleted. Recent logs preserved.

### Run Records (90 days)
- Pipeline execution history
- Stage status and timing
- Error messages

**Impact:** Old run history is deleted. Recent runs preserved for debugging.

### Artifact Versions (keep 3)
- Each universe can have multiple versions of each artifact type
- Only the latest 3 versions are kept
- Example: If BOEXI40-Audit-Sybase has 5 versions of SAC model, oldest 2 are deleted

**Impact:** Old versions deleted. Latest versions always preserved.

### Orphaned Universes
- Universes with no artifacts (failed uploads)
- Incomplete processing

**Impact:** Failed/incomplete universes are removed automatically.

## Monitoring Storage

### Via API

```bash
# Check current usage
curl https://migration-studio-api.onrender.com/api/storage/stats | jq '.'

# View largest artifacts
curl https://migration-studio-api.onrender.com/api/storage/largest | jq '.'
```

### Via Frontend (Future)

Add a storage dashboard page showing:
- Real-time usage gauge
- Artifact breakdown by type
- Cleanup history
- Manual cleanup buttons

## Emergency Procedures

### If Database Approaches Limit (> 90%)

1. **Run full cleanup:**
   ```bash
   curl -X POST https://migration-studio-api.onrender.com/api/storage/cleanup
   ```

2. **Delete old universes:**
   ```bash
   curl -X DELETE https://migration-studio-api.onrender.com/api/universes/{universe_id}
   ```

3. **Reduce retention periods:**
   ```bash
   # Keep only 7 days of events
   curl -X POST https://migration-studio-api.onrender.com/api/storage/cleanup/events?days=7

   # Keep only 1 artifact version
   curl -X POST https://migration-studio-api.onrender.com/api/storage/cleanup/artifacts?keep_versions=1
   ```

4. **Upgrade Neon plan** (if needed for production use)

## Best Practices

1. **Monitor weekly** - Check storage stats regularly
2. **Run cleanup monthly** - Manual cleanup if automated fails
3. **Delete test data** - Don't keep test universes indefinitely
4. **Limit universe uploads** - Be selective about what to process
5. **Archive old universes** - Download artifacts and delete from system

## Configuration

Storage limits can be adjusted in `backend/app/services/storage_controls.py`:

```python
class StorageControls:
    # Adjust these as needed
    MAX_ARTIFACT_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_TOTAL_DB_SIZE = 500 * 1024 * 1024  # 500 MB
    EVENT_RETENTION_DAYS = 30
    RUN_RETENTION_DAYS = 90
    ARTIFACT_VERSION_LIMIT = 3
```

## Troubleshooting

### "Artifact too large" Error

**Cause:** Artifact exceeds 10 MB limit

**Solutions:**
- Simplify the universe (fewer tables/columns)
- Optimize CIM format (remove redundant data)
- Increase `MAX_ARTIFACT_SIZE` if needed

### "Database storage is XX% full"

**Cause:** Approaching storage limit

**Solutions:**
- Run cleanup: `POST /api/storage/cleanup`
- Delete old universes
- Reduce retention periods
- Upgrade Neon plan

### Nightly maintenance not running

**Cause:** GitHub Actions disabled or secrets not configured

**Solutions:**
- Check GitHub Actions tab for errors
- Verify `NEON_DATABASE_URL` secret is set
- Re-run workflow manually to test
