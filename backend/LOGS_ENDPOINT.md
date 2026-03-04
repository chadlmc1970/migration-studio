# Engine Logs Endpoint

## New Endpoint: GET /api/runs/{run_id}/logs

Retrieve engine logs for a specific pipeline run.

## Purpose

Allows the frontend UI to display detailed execution logs from each engine stage (Parser, Transform, Validation) for debugging and monitoring purposes.

## Request

```bash
GET /api/runs/{run_id}/logs
```

**Path Parameters:**
- `run_id` (string, required) - The unique run identifier (e.g., `run_20260304_143052_a7f3b2e1`)

## Response

### Success (200 OK)

```json
{
  "run_id": "run_20260304_143052_a7f3b2e1",
  "logs": {
    "parser": "...parser log text...",
    "transform": "...transform log text...",
    "validation": "...validation log text..."
  }
}
```

### Run Not Found (404 Not Found)

```json
{
  "detail": "Run not found: run_20260304_143052_a7f3b2e1"
}
```

## Log Resolution Strategy

The endpoint searches for log files in the following locations:

```
~/pipeline/logs/parser/
~/pipeline/logs/transform/
~/pipeline/logs/validation/
```

For each stage, it attempts to find logs using this priority order:

1. **Exact run_id match**: `{run_id}.log`
   - Example: `run_20260304_143052_a7f3b2e1.log`

2. **Timestamp match**: `{timestamp}.log`
   - Extracted from run_id: `20260304_143052.log`

3. **Wildcard timestamp match**: `{timestamp}*.log`
   - Finds any log file starting with the timestamp
   - Returns the most recently modified file

If no log file is found for a stage, that stage's log value will be `null`.

## Examples

### Get logs for a specific run

```bash
curl http://localhost:8000/api/runs/run_20260304_143052_a7f3b2e1/logs
```

Response:
```json
{
  "run_id": "run_20260304_143052_a7f3b2e1",
  "logs": {
    "parser": "[2026-03-04 14:30:52] Starting parser...\n[2026-03-04 14:32:10] Parsed 3 universes\n",
    "transform": "[2026-03-04 14:35:12] Starting transformation...\n[2026-03-04 14:40:32] Generated SAC models\n",
    "validation": "[2026-03-04 14:42:15] Running validation...\n[2026-03-04 14:45:12] Validation complete\n"
  }
}
```

### No logs available

```bash
curl http://localhost:8000/api/runs/run_20260304_143052_a7f3b2e1/logs
```

Response:
```json
{
  "run_id": "run_20260304_143052_a7f3b2e1",
  "logs": {
    "parser": null,
    "transform": null,
    "validation": null
  }
}
```

### Invalid run_id

```bash
curl http://localhost:8000/api/runs/invalid_run_id/logs
```

Response (404):
```json
{
  "detail": "Run not found: invalid_run_id"
}
```

## Integration with Frontend

The frontend can use this endpoint to:

1. **Display real-time logs** during pipeline execution
2. **Debug failures** by examining error logs
3. **Audit completed runs** to verify processing steps
4. **Monitor progress** for long-running pipelines

Example frontend integration:
```javascript
// Fetch logs for a run
async function getRunLogs(runId) {
  const response = await fetch(`/api/runs/${runId}/logs`);
  const data = await response.json();

  // Display logs in UI
  if (data.logs.parser) {
    console.log('Parser logs:', data.logs.parser);
  }

  return data;
}
```

## Log File Naming Conventions

For engines to integrate with this endpoint, they should write logs to:

```
~/pipeline/logs/{stage}/{run_id}.log
```

Or alternatively:
```
~/pipeline/logs/{stage}/{timestamp}.log
```

Where:
- `{stage}` = `parser`, `transform`, or `validation`
- `{run_id}` = Full run ID (e.g., `run_20260304_143052_a7f3b2e1`)
- `{timestamp}` = Timestamp portion (e.g., `20260304_143052`)

## Implementation Details

**Files Modified:**
- `app/services/runs.py` - Added `get_run_logs()` function
- `app/api/routes.py` - Added `/runs/{run_id}/logs` endpoint

**Design Principles:**
- ✅ Reads from filesystem (no database)
- ✅ Does not modify engine code
- ✅ Returns null for missing logs (graceful degradation)
- ✅ Follows existing API patterns
- ✅ Compatible with any log file naming scheme

**Error Handling:**
- Returns 404 if run_id doesn't exist
- Returns null for individual stage logs if files not found
- Handles file read errors gracefully

## Testing

```bash
# Test with valid run
curl http://localhost:8000/api/runs/run_20260304_073906_d8adaf60/logs | jq

# Test with invalid run (should return 404)
curl http://localhost:8000/api/runs/invalid_id/logs -w "\nStatus: %{http_code}\n"

# View all available runs
curl http://localhost:8000/api/runs | jq '.[] | .run_id'
```

## Endpoint Summary

**Total Backend Endpoints:** 12

1. `GET /api/health`
2. `GET /api/state`
3. `GET /api/universes`
4. `GET /api/events`
5. `POST /api/upload`
6. `POST /api/run`
7. `GET /api/universes/{id}/reports`
8. `GET /api/universes/{id}/download`
9. `GET /api/runs`
10. `GET /api/runs/active`
11. `GET /api/runs/{run_id}`
12. **`GET /api/runs/{run_id}/logs`** ← NEW

All endpoints operational at: **http://localhost:8000**

Documentation: **http://localhost:8000/docs**
