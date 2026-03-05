import os
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

# AI Enhancement Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
AI_ENABLED = bool(ANTHROPIC_API_KEY)
AI_MODEL = os.getenv("AI_MODEL", "claude-opus-4-6")  # Latest Claude Opus model
AI_CACHE_TTL = int(os.getenv("AI_CACHE_TTL", "900"))  # 15 minutes
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "4096"))
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.0"))  # Deterministic by default
