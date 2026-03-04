from pathlib import Path

# Pipeline filesystem paths
PIPELINE_ROOT = Path.home() / "pipeline"
INPUT_DIR = PIPELINE_ROOT / "input"
CIM_DIR = PIPELINE_ROOT / "cim"
TARGETS_DIR = PIPELINE_ROOT / "targets"
VALIDATION_DIR = PIPELINE_ROOT / "validation"
RUNS_DIR = PIPELINE_ROOT / "runs"
LOGS_DIR = PIPELINE_ROOT / "logs"
STATE_FILE = PIPELINE_ROOT / "state" / "pipeline_state.json"
EVENTS_FILE = PIPELINE_ROOT / "events" / "events.log"

# Engine paths
VALIDATION_ENGINE_DIR = Path.home() / "validation_engine"
