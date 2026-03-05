from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse, Response
from sqlalchemy.orm import Session
from pathlib import Path
import json
import shutil
from datetime import datetime
from app.services.pipeline import run_pipeline
from app.services import runs
from app.services.artifact_storage import ArtifactStorage
from app.services.storage_controls import StorageControls
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


@router.post("/upload/metadata")
async def upload_metadata(file: UploadFile = File(...)):
    """Upload companion .json metadata file for binary universes"""

    if not file.filename.endswith('.json'):
        raise HTTPException(
            status_code=400,
            detail="Only .json files are allowed"
        )

    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    file_path = INPUT_DIR / file.filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save metadata file: {str(e)}"
        )

    return {
        "status": "success",
        "filename": file.filename,
        "path": str(file_path),
        "message": "Companion metadata uploaded. Re-run pipeline to apply."
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

    # Get reports from database
    coverage_report = ArtifactStorage.get_artifact_json(
        db, universe_id, ArtifactStorage.TYPE_COVERAGE_REPORT
    )

    semantic_diff = ArtifactStorage.get_artifact_json(
        db, universe_id, ArtifactStorage.TYPE_SEMANTIC_DIFF
    )

    # Get lineage graph
    lineage_graph = ArtifactStorage.get_artifact_content(
        db, universe_id, ArtifactStorage.TYPE_LINEAGE_DOT
    )

    # Check available artifacts based on database
    artifacts = ArtifactStorage.list_artifacts(db, universe_id)
    available_artifacts = {
        "sac_model": any(a.artifact_type == ArtifactStorage.TYPE_SAC_MODEL for a in artifacts),
        "datasphere_views": any(a.artifact_type == ArtifactStorage.TYPE_DATASPHERE_VIEWS for a in artifacts),
        "hana_schema": any(a.artifact_type == ArtifactStorage.TYPE_HANA_SCHEMA for a in artifacts),
        "lineage_dot": any(a.artifact_type == ArtifactStorage.TYPE_LINEAGE_DOT for a in artifacts),
    }

    return {
        "universe_id": universe_id,
        "coverage_report": coverage_report,
        "semantic_diff": semantic_diff,
        "lineage_graph": lineage_graph,
        "available_artifacts": available_artifacts
    }


@router.get("/universes/{universe_id}/sac")
async def get_sac_model(universe_id: str, db: Session = Depends(get_db)):
    """Get SAC model JSON for a universe from database"""
    sac_model = ArtifactStorage.get_artifact_json(
        db, universe_id, ArtifactStorage.TYPE_SAC_MODEL
    )

    if not sac_model:
        raise HTTPException(
            status_code=404,
            detail=f"SAC model not found for universe: {universe_id}"
        )

    return sac_model


@router.get("/universes/{universe_id}/download")
async def download_universe_artifact(universe_id: str, artifact: str, db: Session = Depends(get_db)):
    """Serve artifact files from database"""

    # Map artifact path to artifact type
    artifact_type_map = {
        "lineage_graph.dot": ArtifactStorage.TYPE_LINEAGE_DOT,
        "sac/model.json": ArtifactStorage.TYPE_SAC_MODEL,
        "datasphere/views.sql": ArtifactStorage.TYPE_DATASPHERE_VIEWS,
        "hana/schema.sql": ArtifactStorage.TYPE_HANA_SCHEMA,
        "cim.json": ArtifactStorage.TYPE_CIM,
        "coverage_report.json": ArtifactStorage.TYPE_COVERAGE_REPORT,
        "semantic_diff.json": ArtifactStorage.TYPE_SEMANTIC_DIFF,
    }

    artifact_type = artifact_type_map.get(artifact)
    if not artifact_type:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown artifact type: {artifact}"
        )

    artifact_obj = ArtifactStorage.get_artifact(db, universe_id, artifact_type)

    if not artifact_obj:
        raise HTTPException(
            status_code=404,
            detail=f"Artifact not found: {artifact}"
        )

    # Determine filename
    filename = artifact.split("/")[-1]  # Extract filename from path

    # Return artifact content as response
    return Response(
        content=artifact_obj.content,
        media_type=artifact_obj.content_type or "text/plain",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
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


@router.delete("/runs/{run_id}")
async def delete_run(run_id: str, db: Session = Depends(get_db)):
    """Delete a run and optionally its universe files and outputs"""
    run_record = runs.get_run_record(run_id)

    if not run_record:
        raise HTTPException(
            status_code=404,
            detail=f"Run not found: {run_id}"
        )

    # Get universes processed in this run from metadata
    metadata = run_record.get("metadata", {})
    universes_processed = metadata.get("universes", [])

    deleted_items = {
        "run_record": run_id,
        "universe_files": [],
        "output_directories": []
    }

    # Delete universe source files (.unv/.unx) from input directory
    for universe_id in universes_processed:
        for ext in ['.unv', '.unx']:
            file_path = INPUT_DIR / f"{universe_id}{ext}"
            if file_path.exists():
                try:
                    file_path.unlink()
                    deleted_items["universe_files"].append(str(file_path))
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

        # Delete output directories (targets and validation)
        target_dir = TARGETS_DIR / universe_id
        if target_dir.exists():
            try:
                shutil.rmtree(target_dir)
                deleted_items["output_directories"].append(str(target_dir))
            except Exception as e:
                print(f"Failed to delete {target_dir}: {e}")

        validation_dir = VALIDATION_DIR / universe_id
        if validation_dir.exists():
            try:
                shutil.rmtree(validation_dir)
                deleted_items["output_directories"].append(str(validation_dir))
            except Exception as e:
                print(f"Failed to delete {validation_dir}: {e}")

        # Delete from database
        universe = db.query(Universe).filter(Universe.id == universe_id).first()
        if universe:
            db.delete(universe)

    # Delete run record from filesystem
    runs.delete_run(run_id)

    # Commit database changes
    db.commit()

    return {
        "status": "deleted",
        "message": f"Run {run_id} and associated files deleted successfully",
        "deleted": deleted_items
    }


@router.delete("/universes/{universe_id}")
async def delete_universe(universe_id: str, db: Session = Depends(get_db)):
    """Delete a universe and all its associated files"""

    deleted_items = {
        "universe_id": universe_id,
        "universe_files": [],
        "output_directories": []
    }

    # Delete universe source files (.unv/.unx) from input directory
    for ext in ['.unv', '.unx']:
        file_path = INPUT_DIR / f"{universe_id}{ext}"
        if file_path.exists():
            try:
                file_path.unlink()
                deleted_items["universe_files"].append(str(file_path))
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")

    # Delete CIM file
    cim_file = Path.home() / "pipeline" / "cim" / f"{universe_id}.cim.json"
    if cim_file.exists():
        try:
            cim_file.unlink()
            deleted_items["universe_files"].append(str(cim_file))
        except Exception as e:
            print(f"Failed to delete {cim_file}: {e}")

    # Delete output directories (targets and validation)
    target_dir = TARGETS_DIR / universe_id
    if target_dir.exists():
        try:
            shutil.rmtree(target_dir)
            deleted_items["output_directories"].append(str(target_dir))
        except Exception as e:
            print(f"Failed to delete {target_dir}: {e}")

    validation_dir = VALIDATION_DIR / universe_id
    if validation_dir.exists():
        try:
            shutil.rmtree(validation_dir)
            deleted_items["output_directories"].append(str(validation_dir))
        except Exception as e:
            print(f"Failed to delete {validation_dir}: {e}")

    # Delete from database
    universe = db.query(Universe).filter(Universe.id == universe_id).first()
    if universe:
        db.delete(universe)
        db.commit()

    return {
        "status": "deleted",
        "message": f"Universe {universe_id} and all associated files deleted successfully",
        "deleted": deleted_items
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


# ===== STORAGE CONTROL ENDPOINTS =====

@router.get("/storage/stats")
async def get_storage_stats(db: Session = Depends(get_db)):
    """Get database storage statistics and usage metrics"""
    return StorageControls.get_storage_stats(db)


@router.get("/storage/largest")
async def get_largest_artifacts(limit: int = 10, db: Session = Depends(get_db)):
    """Get the largest artifacts for analysis"""
    return StorageControls.get_largest_artifacts(db, limit)


@router.post("/storage/cleanup")
async def run_storage_cleanup(db: Session = Depends(get_db)):
    """Run full storage cleanup (events, runs, old artifact versions, orphaned universes)"""
    results = StorageControls.full_cleanup(db)

    # Get updated stats after cleanup
    stats = StorageControls.get_storage_stats(db)

    return {
        "cleanup_results": results,
        "storage_stats": stats
    }


@router.post("/storage/cleanup/events")
async def cleanup_old_events(days: int = 30, db: Session = Depends(get_db)):
    """Delete events older than specified days"""
    deleted = StorageControls.cleanup_old_events(db, days)
    return {"status": "success", "deleted_count": deleted, "retention_days": days}


@router.post("/storage/cleanup/runs")
async def cleanup_old_runs(days: int = 90, db: Session = Depends(get_db)):
    """Delete run records older than specified days"""
    deleted = StorageControls.cleanup_old_runs(db, days)
    return {"status": "success", "deleted_count": deleted, "retention_days": days}


@router.post("/storage/cleanup/artifacts")
async def cleanup_old_artifact_versions(keep_versions: int = 3, db: Session = Depends(get_db)):
    """Keep only the latest N versions of each artifact"""
    deleted = StorageControls.cleanup_old_artifact_versions(db, keep_versions)
    return {"status": "success", "deleted_count": deleted, "versions_kept": keep_versions}
