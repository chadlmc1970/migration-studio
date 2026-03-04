from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from pathlib import Path
import json
import shutil
from datetime import datetime
from app.services.pipeline import run_pipeline
from app.services import runs
from app.database import get_db
from app.models.database import Universe, Event, Run, ValidationReport, Artifact

router = APIRouter(prefix="/api")

PIPELINE_ROOT = Path.home() / "pipeline"
INPUT_DIR = PIPELINE_ROOT / "input"
VALIDATION_DIR = PIPELINE_ROOT / "validation"
TARGETS_DIR = PIPELINE_ROOT / "targets"


@router.get("/health")
async def api_health():
    return {"status": "healthy", "message": "API routes ready"}


@router.get("/state")
async def get_state(db: Session = Depends(get_db)):
    """Get pipeline state from database"""
    universes_db = db.query(Universe).all()

    universes_dict = {}
    for u in universes_db:
        universes_dict[u.id] = {
            "parsed": u.parsed,
            "transformed": u.transformed,
            "validated": u.validated,
            "validated_at": u.validated_at.isoformat() if u.validated_at else None
        }

    return {"universes": universes_dict}


@router.get("/universes")
async def list_universes(db: Session = Depends(get_db)):
    """List all universes from database"""
    universes_db = db.query(Universe).order_by(Universe.created_at.desc()).all()

    return [{
        "id": u.id,
        "parsed": u.parsed,
        "transformed": u.transformed,
        "validated": u.validated,
        "validated_at": u.validated_at.isoformat() if u.validated_at else None
    } for u in universes_db]


@router.get("/kpis")
async def get_kpis(db: Session = Depends(get_db)):
    """Get KPI metrics from database"""
    total = db.query(Universe).count()
    parsed = db.query(Universe).filter(Universe.parsed == True).count()
    transformed = db.query(Universe).filter(Universe.transformed == True).count()
    validated = db.query(Universe).filter(Universe.validated == True).count()

    # Calculate needs_attention from validation reports
    needs_attention = 0
    validated_universes = db.query(Universe).filter(Universe.validated == True).all()

    for universe in validated_universes:
        validation_path = VALIDATION_DIR / universe.id / "coverage_report.json"
        if validation_path.exists():
            try:
                with open(validation_path) as f:
                    report = json.load(f)
                    coverage = report.get("coverage_percentage", 100)
                    if coverage < 80:
                        needs_attention += 1
            except Exception:
                pass

    return {
        "total_universes": total,
        "parsed": parsed,
        "transformed": transformed,
        "validated": validated,
        "needs_attention": needs_attention
    }


@router.get("/events")
async def get_events(limit: int = 50, db: Session = Depends(get_db)):
    """Get events from database"""
    events_db = db.query(Event).order_by(Event.timestamp.desc()).limit(limit).all()

    return [{
        "timestamp": e.timestamp.isoformat(),
        "level": e.level,
        "message": e.message,
        "universe_id": e.universe_id
    } for e in events_db]


@router.post("/upload")
async def upload_universe(file: UploadFile = File(...)):
    """Upload .unv or .unx files directly to ~/pipeline/input/"""

    if not (file.filename.endswith('.unv') or file.filename.endswith('.unx')):
        raise HTTPException(
            status_code=400,
            detail="Only .unv and .unx files are allowed"
        )

    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    file_path = INPUT_DIR / file.filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )

    return {
        "status": "success",
        "filename": file.filename,
        "path": str(file_path)
    }


@router.post("/run")
async def run_pipeline_endpoint():
    """Run the full pipeline sequentially: Parser → Transform → Validation"""

    result = run_pipeline()

    if result["status"] == "error":
        active_run_id = None
        active_runs = runs.get_active_runs()
        if active_runs:
            active_run_id = active_runs[0]["run_id"]

        return JSONResponse(
            status_code=409,
            content={
                "status": "rejected",
                "reason": "pipeline already running",
                "active_run_id": active_run_id
            }
        )

    if result["status"] == "failed":
        return JSONResponse(
            status_code=500,
            content=result
        )

    return result


@router.get("/universes/{universe_id}/reports")
async def get_universe_reports(universe_id: str, db: Session = Depends(get_db)):
    """Return JSON reports and available artifacts from validation and targets directories"""

    # Check if universe exists in database
    universe = db.query(Universe).filter(Universe.id == universe_id).first()
    if not universe:
        raise HTTPException(
            status_code=404,
            detail=f"Universe not found: {universe_id}"
        )

    validation_path = VALIDATION_DIR / universe_id

    # Create validation directory if it doesn't exist
    if not validation_path.exists():
        validation_path.mkdir(parents=True, exist_ok=True)

    # Read coverage_report.json
    coverage_report = None
    coverage_file = validation_path / "coverage_report.json"
    if coverage_file.exists():
        try:
            with open(coverage_file) as f:
                coverage_report = json.load(f)
        except Exception as e:
            coverage_report = {"error": str(e)}

    # Read semantic_diff.json
    semantic_diff = None
    semantic_diff_file = validation_path / "semantic_diff.json"
    if semantic_diff_file.exists():
        try:
            with open(semantic_diff_file) as f:
                semantic_diff = json.load(f)
        except Exception as e:
            semantic_diff = {"error": str(e)}

    # Read lineage graph
    lineage_graph = None
    lineage_graph_file = validation_path / "lineage_graph.json"
    if lineage_graph_file.exists():
        try:
            with open(lineage_graph_file) as f:
                lineage_graph = json.dumps(json.load(f))
        except Exception as e:
            lineage_graph = None

    if not lineage_graph:
        lineage_dot_file = validation_path / "lineage_graph.dot"
        if lineage_dot_file.exists():
            try:
                with open(lineage_dot_file) as f:
                    lineage_graph = f.read()
            except Exception:
                pass

    # Check available artifacts
    targets_path = TARGETS_DIR / universe_id

    available_artifacts = {
        "sac_model": False,
        "datasphere_views": False,
        "hana_schema": False,
        "lineage_dot": False
    }

    if targets_path.exists():
        available_artifacts["sac_model"] = (targets_path / "sac" / "model.json").exists()
        available_artifacts["datasphere_views"] = (targets_path / "datasphere" / "views.sql").exists()
        available_artifacts["hana_schema"] = (targets_path / "hana" / "schema.sql").exists()

    available_artifacts["lineage_dot"] = (validation_path / "lineage_graph.dot").exists()

    return {
        "universe_id": universe_id,
        "coverage_report": coverage_report,
        "semantic_diff": semantic_diff,
        "lineage_graph": lineage_graph,
        "available_artifacts": available_artifacts
    }


@router.get("/universes/{universe_id}/download")
async def download_universe_artifact(universe_id: str, artifact: str):
    """Serve artifact files from ~/pipeline/targets/{universe_id}/ or validation"""

    # Special case: lineage_graph.dot comes from validation directory
    if artifact == "lineage_graph.dot":
        validation_path = VALIDATION_DIR / universe_id
        artifact_file = validation_path / artifact

        if not artifact_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Artifact not found: {artifact}"
            )

        return FileResponse(
            path=str(artifact_file),
            media_type="text/plain",
            filename=artifact_file.name
        )

    # Other artifacts come from targets directory
    targets_path = TARGETS_DIR / universe_id

    if not targets_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Targets directory not found for universe: {universe_id}"
        )

    artifact_file = targets_path / artifact

    if not artifact_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Artifact not found: {artifact}"
        )

    if not artifact_file.is_file():
        raise HTTPException(
            status_code=400,
            detail=f"Path is not a file: {artifact}"
        )

    # Determine media type
    if artifact.endswith('.json'):
        media_type = "application/json"
    elif artifact.endswith('.sql'):
        media_type = "text/plain"
    else:
        media_type = "application/octet-stream"

    return FileResponse(
        path=str(artifact_file),
        media_type=media_type,
        filename=artifact_file.name
    )


@router.get("/runs")
async def list_pipeline_runs(limit: int = 50):
    """List recent pipeline runs"""
    run_list = runs.list_runs(limit=limit)
    return run_list


@router.get("/runs/active")
async def get_active_pipeline_runs():
    """Get currently running pipeline executions"""
    active = runs.get_active_runs()
    return active


@router.get("/runs/{run_id}")
async def get_pipeline_run(run_id: str):
    """Get detailed information about a specific pipeline run"""
    run_record = runs.get_run_record(run_id)

    if not run_record:
        raise HTTPException(
            status_code=404,
            detail=f"Run not found: {run_id}"
        )

    return run_record


@router.get("/runs/{run_id}/logs")
async def get_run_logs(run_id: str):
    """Get engine logs for a specific pipeline run"""
    run_record = runs.get_run_record(run_id)

    if not run_record:
        raise HTTPException(
            status_code=404,
            detail=f"Run not found: {run_id}"
        )

    logs = runs.get_run_logs(run_id)

    return {
        "run_id": run_id,
        "logs": logs
    }


@router.post("/universes/{universe_id}/reprocess")
async def reprocess_universe(universe_id: str, db: Session = Depends(get_db)):
    """Reset universe state and reprocess through pipeline"""
    
    universe = db.query(Universe).filter(Universe.id == universe_id).first()
    if not universe:
        raise HTTPException(status_code=404, detail=f"Universe not found: {universe_id}")
    
    # Reset universe state
    universe.parsed = False
    universe.transformed = False
    universe.validated = False
    universe.validated_at = None
    db.commit()
    
    # Delete generated files to force regeneration
    import shutil
    cim_file = Path.home() / "pipeline" / "cim" / f"{universe_id}.cim.json"
    targets_dir = Path.home() / "pipeline" / "targets" / universe_id
    validation_dir = Path.home() / "pipeline" / "validation" / universe_id
    
    if cim_file.exists():
        cim_file.unlink()
    if targets_dir.exists():
        shutil.rmtree(targets_dir)
    if validation_dir.exists():
        shutil.rmtree(validation_dir)
    
    return {"status": "success", "message": f"Universe {universe_id} reset. Run pipeline to reprocess."}
