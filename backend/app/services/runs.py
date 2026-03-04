"""
Run tracking service - manages pipeline execution history

Each pipeline execution gets a unique run_id and persistent record.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid


PIPELINE_ROOT = Path.home() / "pipeline"
RUNS_DIR = PIPELINE_ROOT / "runs"


def generate_run_id() -> str:
    """Generate unique run ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"run_{timestamp}_{short_uuid}"


def create_run_record(run_id: str) -> Dict[str, Any]:
    """
    Create initial run record

    Returns:
        Run record dictionary
    """
    RUNS_DIR.mkdir(parents=True, exist_ok=True)

    record = {
        "run_id": run_id,
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "duration_seconds": None,
        "stages": {
            "parser": {"status": "pending", "started_at": None, "completed_at": None, "error": None},
            "transform": {"status": "pending", "started_at": None, "completed_at": None, "error": None},
            "validation": {"status": "pending", "started_at": None, "completed_at": None, "error": None}
        },
        "universes_processed": []
    }

    _save_run_record(run_id, record)
    return record


def update_stage_status(
    run_id: str,
    stage: str,
    status: str,
    error: Optional[str] = None
) -> None:
    """
    Update stage status in run record

    Args:
        run_id: Run identifier
        stage: Stage name (parser, transform, validation)
        status: Stage status (running, success, failed, timeout)
        error: Error message if failed
    """
    record = get_run_record(run_id)
    if not record:
        return

    now = datetime.now().isoformat()

    if status == "running":
        record["stages"][stage]["status"] = "running"
        record["stages"][stage]["started_at"] = now
    else:
        record["stages"][stage]["status"] = status
        record["stages"][stage]["completed_at"] = now
        if error:
            record["stages"][stage]["error"] = error

    _save_run_record(run_id, record)


def complete_run(
    run_id: str,
    status: str,
    universes: Optional[List[str]] = None
) -> None:
    """
    Mark run as completed

    Args:
        run_id: Run identifier
        status: Final status (success, failed)
        universes: List of universe IDs processed
    """
    record = get_run_record(run_id)
    if not record:
        return

    completed_at = datetime.now()
    started_at = datetime.fromisoformat(record["started_at"])
    duration = (completed_at - started_at).total_seconds()

    record["status"] = status
    record["completed_at"] = completed_at.isoformat()
    record["duration_seconds"] = round(duration, 2)

    if universes:
        record["universes_processed"] = universes

    _save_run_record(run_id, record)


def get_run_record(run_id: str) -> Optional[Dict[str, Any]]:
    """
    Get run record by ID

    Args:
        run_id: Run identifier

    Returns:
        Run record or None if not found
    """
    run_file = RUNS_DIR / f"{run_id}.json"

    if not run_file.exists():
        return None

    try:
        with open(run_file) as f:
            return json.load(f)
    except Exception:
        return None


def list_runs(limit: int = 50) -> List[Dict[str, Any]]:
    """
    List recent runs

    Args:
        limit: Maximum number of runs to return

    Returns:
        List of run records, sorted by start time (newest first)
    """
    if not RUNS_DIR.exists():
        return []

    run_files = sorted(
        RUNS_DIR.glob("run_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    runs = []
    for run_file in run_files[:limit]:
        try:
            with open(run_file) as f:
                runs.append(json.load(f))
        except Exception:
            continue

    return runs


def get_active_runs() -> List[Dict[str, Any]]:
    """
    Get currently running pipeline executions

    Returns:
        List of active run records
    """
    all_runs = list_runs(limit=100)
    return [r for r in all_runs if r["status"] == "running"]


def _save_run_record(run_id: str, record: Dict[str, Any]) -> None:
    """Save run record to filesystem"""
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    run_file = RUNS_DIR / f"{run_id}.json"

    with open(run_file, "w") as f:
        json.dump(record, f, indent=2)


def get_run_logs(run_id: str) -> Dict[str, Optional[str]]:
    """
    Get engine logs for a specific run

    Args:
        run_id: Run identifier (e.g., run_20260304_143052_a7f3b2e1)

    Returns:
        Dict with logs for each stage (parser, transform, validation)
    """
    logs_dir = PIPELINE_ROOT / "logs"

    result = {
        "parser": None,
        "transform": None,
        "validation": None
    }

    # Extract timestamp from run_id (format: run_YYYYMMDD_HHMMSS_uuid)
    parts = run_id.split("_")
    if len(parts) < 3:
        return result

    timestamp = f"{parts[1]}_{parts[2]}"  # YYYYMMDD_HHMMSS

    # Check each engine's log directory
    for stage in ["parser", "transform", "validation"]:
        stage_logs_dir = logs_dir / stage

        if not stage_logs_dir.exists():
            continue

        # Try exact match first: {run_id}.log
        exact_match = stage_logs_dir / f"{run_id}.log"
        if exact_match.exists():
            try:
                with open(exact_match) as f:
                    result[stage] = f.read()
                continue
            except Exception:
                pass

        # Try timestamp match: {timestamp}.log
        timestamp_match = stage_logs_dir / f"{timestamp}.log"
        if timestamp_match.exists():
            try:
                with open(timestamp_match) as f:
                    result[stage] = f.read()
                continue
            except Exception:
                pass

        # Fallback: find most recent log file matching timestamp pattern
        try:
            matching_files = list(stage_logs_dir.glob(f"{timestamp}*.log"))
            if matching_files:
                # Sort by modification time, get most recent
                latest = max(matching_files, key=lambda p: p.stat().st_mtime)
                with open(latest) as f:
                    result[stage] = f.read()
        except Exception:
            pass

    return result
