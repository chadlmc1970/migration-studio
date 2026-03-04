# ARTIFACT FIX - Aligning API with Generated Artifacts

## Issue Found
The transformation engine generates artifacts with these names:
- `sac/model.json` ✅ (generator creates this)
- `hana/schema.sql` ✅
- `datasphere/views.sql` ✅

But the API endpoint was looking for:
- `sac/sac_model.json` ❌ (wrong name)

## Fix Applied
Updated `/backend/app/api/routes.py` line 270:
```python
# Before:
sac_model_path = TARGETS_DIR / universe_id / "sac" / "sac_model.json"

# After:
sac_model_path = TARGETS_DIR / universe_id / "sac" / "model.json"
```

## Artifact Paths for Frontend
The frontend should use these paths for downloads:

| Artifact | Download URL |
|----------|-------------|
| SAC Model | `/api/universes/{id}/download?artifact=sac/model.json` |
| HANA Schema | `/api/universes/{id}/download?artifact=hana/schema.sql` |
| Datasphere Views | `/api/universes/{id}/download?artifact=datasphere/views.sql` |
| Lineage Graph | `/api/universes/{id}/download?artifact=lineage_graph.dot` |

## Verification
Local artifacts confirmed at:
```
/Users/I870089/pipeline/targets/sales_universe/
├── sac/model.json ✅ (1.5KB)
├── hana/schema.sql ✅ (403 bytes)
└── datasphere/views.sql ✅ (688 bytes)
```

## Next Steps
1. Commit this fix
2. Push to production
3. Test artifact downloads on frontend
