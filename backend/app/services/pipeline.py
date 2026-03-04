from pathlib import Path
import subprocess
from typing import Dict, Any
from app.services import runs

PIPELINE_ROOT = Path.home() / "pipeline"
LOCK_FILE = PIPELINE_ROOT / ".pipeline.lock"

PARSER_DIR = Path.home() / "BOBJ_SAC_Converter"
TRANSFORM_DIR = Path.home() / "cim_transform"
VALIDATION_DIR = Path.home() / "validation_engine"

PARSER_PYTHON = PARSER_DIR / "venv/bin/python"
TRANSFORM_PYTHON = TRANSFORM_DIR / "venv/bin/python"
VALIDATION_PYTHON = VALIDATION_DIR / "venv/bin/python"


def _release_lock():
    """Release pipeline lock file"""
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
    except Exception:
        pass


def run_pipeline() -> Dict[str, Any]:
    """
    Execute full pipeline with run tracking and concurrency control

    Returns:
        Dict with status, run_id, and stage results
    """
    # Check for active runs
    active_runs = runs.get_active_runs()
    if active_runs:
        return {
            "status": "error",
            "message": f"Pipeline is already running (run_id: {active_runs[0]['run_id']})",
            "run_id": None,
            "results": {}
        }

    # Create lock file
    try:
        LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
        if LOCK_FILE.exists():
            # Stale lock - remove it
            LOCK_FILE.unlink()
        LOCK_FILE.touch()
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to acquire pipeline lock: {str(e)}",
            "run_id": None,
            "results": {}
        }

    # Create run record
    run_id = runs.generate_run_id()
    runs.create_run_record(run_id)

    results = {}

    # Step 1: Parser
    runs.update_stage_status(run_id, "parser", "running")
    try:
        r = subprocess.run(
            [str(PARSER_PYTHON), "bobj2sac/cli.py", "pipeline", "--root", str(PIPELINE_ROOT)],
            cwd=PARSER_DIR,
            capture_output=True,
            text=True,
            check=True,
            timeout=3600
        )
        results["parser"] = {"status": "success", "output": r.stdout, "error": ""}
        runs.update_stage_status(run_id, "parser", "success")

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or str(e)
        results["parser"] = {"status": "failed", "output": e.stdout, "error": error_msg}
        runs.update_stage_status(run_id, "parser", "failed", error_msg)
        runs.complete_run(run_id, "failed")
        _release_lock()
        return {
            "status": "failed",
            "stage": "parser",
            "run_id": run_id,
            "results": results
        }

    except subprocess.TimeoutExpired:
        error_msg = "Parser exceeded 1 hour timeout"
        results["parser"] = {"status": "timeout", "output": "", "error": error_msg}
        runs.update_stage_status(run_id, "parser", "timeout", error_msg)
        runs.complete_run(run_id, "failed")
        _release_lock()
        return {
            "status": "failed",
            "stage": "parser",
            "run_id": run_id,
            "results": results
        }

    # Step 2: Transform
    runs.update_stage_status(run_id, "transform", "running")
    try:
        r = subprocess.run(
            [str(TRANSFORM_PYTHON), "-m", "cim_transform.cli", "run", "--pipeline-root", str(PIPELINE_ROOT)],
            cwd=TRANSFORM_DIR,
            capture_output=True,
            text=True,
            check=True,
            timeout=3600
        )
        results["transform"] = {"status": "success", "output": r.stdout, "error": ""}
        runs.update_stage_status(run_id, "transform", "success")

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or str(e)
        results["transform"] = {"status": "failed", "output": e.stdout, "error": error_msg}
        runs.update_stage_status(run_id, "transform", "failed", error_msg)
        runs.complete_run(run_id, "failed")
        _release_lock()
        return {
            "status": "failed",
            "stage": "transform",
            "run_id": run_id,
            "results": results
        }

    except subprocess.TimeoutExpired:
        error_msg = "Transform exceeded 1 hour timeout"
        results["transform"] = {"status": "timeout", "output": "", "error": error_msg}
        runs.update_stage_status(run_id, "transform", "timeout", error_msg)
        runs.complete_run(run_id, "failed")
        _release_lock()
        return {
            "status": "failed",
            "stage": "transform",
            "run_id": run_id,
            "results": results
        }

    # Step 3: Validation
    runs.update_stage_status(run_id, "validation", "running")
    try:
        r = subprocess.run(
            [str(VALIDATION_PYTHON), "cli.py", "run"],
            cwd=VALIDATION_DIR,
            capture_output=True,
            text=True,
            check=True,
            timeout=3600
        )
        results["validation"] = {"status": "success", "output": r.stdout, "error": ""}
        runs.update_stage_status(run_id, "validation", "success")

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or str(e)
        results["validation"] = {"status": "failed", "output": e.stdout, "error": error_msg}
        runs.update_stage_status(run_id, "validation", "failed", error_msg)
        runs.complete_run(run_id, "failed")
        _release_lock()
        return {
            "status": "failed",
            "stage": "validation",
            "run_id": run_id,
            "results": results
        }

    except subprocess.TimeoutExpired:
        error_msg = "Validation exceeded 1 hour timeout"
        results["validation"] = {"status": "timeout", "output": "", "error": error_msg}
        runs.update_stage_status(run_id, "validation", "timeout", error_msg)
        runs.complete_run(run_id, "failed")
        _release_lock()
        return {
            "status": "failed",
            "stage": "validation",
            "run_id": run_id,
            "results": results
        }

    # Success - complete run
    runs.complete_run(run_id, "success")

    _release_lock()

    return {
        "status": "success",
        "run_id": run_id,
        "results": results
    }
