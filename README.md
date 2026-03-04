# Universe Migration Studio

Modern SaaS UI for SAP BusinessObjects Universe migration pipeline.

## Overview

Universe Migration Studio orchestrates three existing engines to convert SAP BusinessObjects universes into SAP Analytics Cloud, Datasphere, and HANA artifacts.

- **Frontend**: Next.js with Apple-inspired design
- **Backend**: FastAPI (thin API wrapper)
- **Pipeline**: File-based coordination via `~/pipeline`

## Architecture

### External Engines (Do Not Modify)

1. **Parser Engine**: `~/BOBJ_SAC_Converter`
   - Command: `python -m bobj2sac.cli pipeline --root ~/pipeline`

2. **Transform Engine**: `~/cim_transform`
   - Command: `python -m cim_transform.cli run --pipeline-root ~/pipeline`

3. **Validation Engine**: `~/validation_engine`
   - Command: `cd ~/validation_engine && python cli.py run`

### Pipeline Filesystem

```
~/pipeline/
├── input/          # Upload universe files here
├── cim/            # Parser output
├── targets/        # Transform output (SAC/Datasphere/HANA)
├── validation/     # Validation reports
├── runs/           # Run metadata
├── logs/           # Engine logs
├── state/          # pipeline_state.json
└── events/         # events.log
```

## Local Development

### Prerequisites

- Python 3.9+
- Node.js 18+
- The three engine repositories installed

### Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Run

```bash
# Terminal 1: Backend
cd backend
./run.sh

# Terminal 2: Frontend
cd frontend
npm run dev
```

Visit: http://localhost:3000

## API Endpoints

- `GET /api/state` - Pipeline state
- `GET /api/events` - Recent events
- `GET /api/kpis` - Dashboard statistics
- `GET /api/universes` - List universes
- `GET /api/runs` - List migration runs
- `POST /api/upload` - Upload universe file
- `POST /api/runs` - Execute migration
