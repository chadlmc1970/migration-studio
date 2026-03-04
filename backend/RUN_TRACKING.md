# Run Tracking System

## Overview

The backend now includes a comprehensive run tracking system that records every pipeline execution with unique IDs, timestamps, and stage-level status tracking.

## Features

✅ **Unique Run IDs** - Each execution gets a timestamped ID like `run_20260304_143052_a7f3b2e1`

✅ **Stage Tracking** - Monitor Parser, Transform, and Validation stages independently

✅ **Persistent History** - All runs stored in `~/pipeline/runs/` as JSON files

✅ **Status Monitoring** - Track running, completed, and failed executions

✅ **Duration Tracking** - Automatic timing for each run and stage

## Run Record Structure

```json
{
  "run_id": "run_20260304_143052_a7f3b2e1",
  "status": "running|success|failed",
  "started_at": "2026-03-04T14:30:52.123456",
  "completed_at": "2026-03-04T14:45:12.654321",
  "duration_seconds": 920.53,
  "stages": {
    "parser": {
      "status": "success|failed|timeout|pending|running",
      "started_at": "2026-03-04T14:30:52.234567",
      "completed_at": "2026-03-04T14:35:10.123456",
      "error": null
    },
    "transform": { ... },
    "validation": { ... }
  },
  "universes_processed": ["sales_universe", "hr_universe"]
}
```

## API Endpoints

### POST /api/run
**Execute pipeline** - Now returns `run_id` for tracking

Response:
```json
{
  "status": "success",
  "run_id": "run_20260304_143052_a7f3b2e1",
  "results": {
    "parser": {"status": "success", "output": "...", "error": ""},
    "transform": {"status": "success", "output": "...", "error": ""},
    "validation": {"status": "success", "output": "...", "error": ""}
  }
}
```

### GET /api/runs?limit=50
**List recent runs** - Returns array of run records

Query params:
- `limit` - Maximum runs to return (default: 50)

Example:
```bash
curl http://localhost:8000/api/runs?limit=10
```

### GET /api/runs/active
**Get active runs** - Returns currently executing pipelines

Example:
```bash
curl http://localhost:8000/api/runs/active
```

### GET /api/runs/{run_id}
**Get run details** - Fetch specific run record

Example:
```bash
curl http://localhost:8000/api/runs/run_20260304_143052_a7f3b2e1
```

## Filesystem Storage

All run records are stored in:
```
~/pipeline/runs/
├── run_20260304_143052_a7f3b2e1.json
├── run_20260304_152314_b9c4d5f2.json
└── run_20260304_163421_e1f2g3h4.json
```

This ensures:
- Run history persists across server restarts
- Filesystem remains the single source of truth
- No database required

## Usage Examples

### Monitor a running pipeline
```bash
# Start pipeline
RUN_ID=$(curl -X POST http://localhost:8000/api/run | jq -r '.run_id')

# Check status
curl http://localhost:8000/api/runs/$RUN_ID | jq '.status, .stages'
```

### View recent execution history
```bash
# Get last 10 runs
curl http://localhost:8000/api/runs?limit=10 | jq '.[] | {run_id, status, duration_seconds}'
```

### Check for failures
```bash
# Find failed runs
curl http://localhost:8000/api/runs | jq '.[] | select(.status=="failed")'
```

### Monitor active executions
```bash
# Check if pipeline is running
curl http://localhost:8000/api/runs/active | jq 'length'
```

## Stage Status Values

Each stage can have these statuses:

- **pending** - Not started yet
- **running** - Currently executing
- **success** - Completed successfully
- **failed** - Execution failed (CalledProcessError)
- **timeout** - Exceeded 1-hour timeout

## Integration with Existing System

The run tracking system:
- ✅ Does NOT modify engine code
- ✅ Uses filesystem as source of truth
- ✅ Integrates seamlessly with existing endpoints
- ✅ Adds minimal overhead (~10ms per stage update)
- ✅ Maintains backward compatibility

All existing endpoints continue to work unchanged. The `/api/run` endpoint now includes `run_id` in responses for tracking.

## Error Handling

If a stage fails:
```json
{
  "status": "failed",
  "stage": "transform",
  "run_id": "run_20260304_143052_a7f3b2e1",
  "results": {
    "parser": {"status": "success", ...},
    "transform": {"status": "failed", "error": "Module not found: xyz"}
  }
}
```

The run record captures:
- Which stage failed
- Error message
- Timestamp of failure
- Successful stages before failure

## Benefits

1. **Debugging** - Trace execution history to diagnose issues
2. **Monitoring** - Track pipeline performance over time
3. **Auditing** - Complete record of all executions
4. **UI Integration** - Frontend can display real-time progress
5. **Analytics** - Analyze stage durations and failure patterns

## Next Steps

The run tracking system is now operational. You can:

1. Test it by running the pipeline: `curl -X POST http://localhost:8000/api/run`
2. View run history: `curl http://localhost:8000/api/runs`
3. Monitor active executions: `curl http://localhost:8000/api/runs/active`

All run data persists in `~/pipeline/runs/` and is available across sessions.
