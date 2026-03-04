# Universe Migration Studio - Backend API

FastAPI backend orchestration layer for the Universe Migration Studio.

## Architecture

The backend is a **thin orchestration layer** that:
- Reads from the filesystem (`~/pipeline`)
- Executes engine CLIs via subprocess
- Exposes REST API endpoints for the frontend

**Important**: The backend does NOT modify engine code or maintain its own database. The filesystem is the single source of truth.

## Endpoints

### Existing Endpoints

- **GET /api/health** - Health check
- **GET /api/state** - Read `~/pipeline/state/pipeline_state.json`
- **GET /api/universes** - List all universes from state file
- **GET /api/events** - Read last N events from `~/pipeline/events/events.log`

### New Endpoints

- **POST /api/upload** - Upload `.unv` or `.unx` files directly to `~/pipeline/input/`
- **POST /api/run** - Run full pipeline sequentially (Parser → Transform → Validation)
- **GET /api/universes/{id}/reports** - Get validation reports for a universe
- **GET /api/universes/{id}/download?artifact={path}** - Download generated artifacts

## Pipeline Execution

The `/api/run` endpoint executes engines sequentially:

### 1. Parser Engine
```bash
python -m bobj2sac.cli pipeline --root ~/pipeline
```

### 2. Transform Engine
```bash
python -m cim_transform.cli run --pipeline-root ~/pipeline
```

### 3. Validation Engine
```bash
cd ~/validation_engine
python cli.py run
```

Each stage:
- Has a 1-hour timeout
- Uses `subprocess.run(check=True)`
- Returns stdout/stderr in the response
- Stops pipeline if any stage fails

## File Upload

**POST /api/upload**

Accepts `.unv` or `.unx` files and saves them directly to:
```
~/pipeline/input/{filename}
```

No subfolders are created.

Example:
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@sales_universe.unv"
```

Response:
```json
{
  "status": "success",
  "filename": "sales_universe.unv",
  "path": "/Users/username/pipeline/input/sales_universe.unv"
}
```

## Reports

**GET /api/universes/{id}/reports**

Returns JSON reports from:
```
~/pipeline/validation/{universe_id}/
```

Files returned:
- `coverage_report.json`
- `semantic_diff.json`
- `lineage_graph.json`

Example:
```bash
curl http://localhost:8000/api/universes/sales_universe/reports
```

Response:
```json
{
  "coverage_report": { ... },
  "semantic_diff": { ... },
  "lineage_graph": { ... }
}
```

## Artifacts Download

**GET /api/universes/{id}/download?artifact={path}**

Serves files from:
```
~/pipeline/targets/{universe_id}/
```

Common artifacts:
- `sac/model.json` - SAC Analytics Cloud model
- `datasphere/views.sql` - Datasphere SQL views
- `hana/schema.sql` - HANA schema definition

Example:
```bash
curl "http://localhost:8000/api/universes/sales_universe/download?artifact=sac/model.json" \
  -o model.json
```

## Running the Server

```bash
cd ~/migration_studio/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Server will be available at: `http://localhost:8000`

API docs (Swagger): `http://localhost:8000/docs`

## Testing

Run endpoint tests:
```bash
python test_endpoints.py
```

Test pipeline execution:
```bash
curl -X POST http://localhost:8000/api/run
```

## Filesystem Coordination

The backend reads from:
```
~/pipeline/
├── input/              # Universe files (.unv, .unx)
├── cim/                # Parser output
├── targets/            # Transform output (downloadable artifacts)
├── validation/         # Validation output (reports)
├── state/
│   └── pipeline_state.json   # Pipeline state
└── events/
    └── events.log            # Event log
```

## Engine Coordination

Engines are executed via CLI and coordinate through the filesystem:

- **Parser (Claude 1)**: `python -m bobj2sac.cli pipeline --root ~/pipeline`
- **Transform (Claude 2)**: `python -m cim_transform.cli run --pipeline-root ~/pipeline`
- **Validation (Claude 3)**: `cd ~/validation_engine && python cli.py run`

The backend **does not modify engine code** - it only:
- Executes their CLIs
- Reads their outputs from the filesystem
- Exposes results via REST API

## Dependencies

- FastAPI
- Uvicorn
- Pydantic
- Python 3.11+

Install:
```bash
pip install fastapi uvicorn pydantic python-multipart
```

## Error Handling

Pipeline execution errors return:
```json
{
  "status": "failed",
  "stage": "parser|transform|validation",
  "results": {
    "parser": {
      "status": "success|failed|timeout|error",
      "output": "stdout",
      "error": "stderr"
    },
    "transform": { ... },
    "validation": { ... }
  }
}
```

## CORS

CORS is enabled for:
- `http://localhost:3000` (Next.js frontend)

Configure in `app/main.py` if needed.
