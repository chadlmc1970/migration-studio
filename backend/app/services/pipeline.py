"""
Pipeline Service - Delegates to integrated pipeline implementation
"""
from typing import Dict, Any
from app.services.pipeline_integrated import run_pipeline as _run_pipeline_integrated


def run_pipeline() -> Dict[str, Any]:
    """
    Execute full pipeline with run tracking and concurrency control

    Returns:
        Dict with status, run_id, and stage results
    """
    return _run_pipeline_integrated()
