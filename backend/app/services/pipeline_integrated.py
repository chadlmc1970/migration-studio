"""
Enterprise Production Pipeline - Integrated Pipeline Execution
Handles all three pipeline stages in-process for deployment reliability
"""
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

# Add engines to path
ENGINES_PATH = Path(__file__).parent.parent / "engines"
sys.path.insert(0, str(ENGINES_PATH))

from app.database import get_db
from app.models.database import Universe, Event
from app.services import runs
from app.services.artifact_storage import ArtifactStorage

PIPELINE_ROOT = Path.home() / "pipeline"
LOCK_FILE = PIPELINE_ROOT / ".pipeline.lock"


def _release_lock():
    """Release pipeline lock file"""
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
    except Exception:
        pass


def _log_event(db: Session, level: str, message: str, universe_id: str = None):
    """Log event to database"""
    try:
        event = Event(
            level=level,
            message=message,
            universe_id=universe_id,
            metadata={}
        )
        db.add(event)
        db.commit()
    except Exception as e:
        print(f"Failed to log event: {e}")


def run_pipeline() -> Dict[str, Any]:
    """
    Execute integrated production pipeline

    Stages:
    1. Parser: Process .unv/.unx files → CIM
    2. Transform: CIM → SAC/Datasphere artifacts
    3. Validation: Generate reports and lineage

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
        PIPELINE_ROOT.mkdir(parents=True, exist_ok=True)
        LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
        if LOCK_FILE.exists():
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

    # Get database session
    db = next(get_db())

    try:
        # STAGE 0: Extract source files and CIM artifacts from database to filesystem
        _log_event(db, "INFO", "Extracting files from database to filesystem")
        import base64
        from app.models.database import Artifact

        # Extract source .unx files if they exist
        source_artifacts = db.query(Artifact).filter(
            Artifact.artifact_type == ArtifactStorage.TYPE_SOURCE_UNX
        ).all()

        if source_artifacts:
            INPUT_DIR = PIPELINE_ROOT / "input"
            INPUT_DIR.mkdir(parents=True, exist_ok=True)

            for artifact in source_artifacts:
                try:
                    binary_content = base64.b64decode(artifact.content)
                    file_path = INPUT_DIR / f"{artifact.universe_id}.unx"
                    with open(file_path, 'wb') as f:
                        f.write(binary_content)
                    _log_event(db, "INFO", f"Extracted {artifact.universe_id}.unx from database", artifact.universe_id)
                except Exception as e:
                    _log_event(db, "ERROR", f"Failed to extract {artifact.universe_id}: {e}", artifact.universe_id)

        # Also extract existing CIM artifacts to filesystem for transform to process
        cim_artifacts = db.query(Artifact).filter(
            Artifact.artifact_type == ArtifactStorage.TYPE_CIM
        ).all()

        if cim_artifacts:
            CIM_DIR = PIPELINE_ROOT / "cim"
            CIM_DIR.mkdir(parents=True, exist_ok=True)

            for artifact in cim_artifacts:
                try:
                    file_path = CIM_DIR / f"{artifact.universe_id}.cim.json"
                    with open(file_path, 'w') as f:
                        f.write(artifact.content)
                    _log_event(db, "INFO", f"Extracted {artifact.universe_id}.cim.json from database", artifact.universe_id)
                except Exception as e:
                    _log_event(db, "ERROR", f"Failed to extract CIM {artifact.universe_id}: {e}", artifact.universe_id)

            _log_event(db, "INFO", f"Extracted {len(cim_artifacts)} CIM artifacts from database")

        # STAGE 1: Parser
        runs.update_stage_status(run_id, "parser", "running")
        _log_event(db, "INFO", f"Starting parser stage for run {run_id}")

        try:
            # Import parser engine
            from bobj2sac.pipeline import process_pipeline as run_parser

            parser_results = run_parser(PIPELINE_ROOT, force=False)

            # Update database with parsed universes
            for processed in parser_results.get("processed", []):
                universe_id = processed["universe"]
                universe = db.query(Universe).filter(Universe.id == universe_id).first()
                if not universe:
                    universe = Universe(
                        id=universe_id,
                        parsed=True,
                        transformed=False,
                        validated=False
                    )
                    db.add(universe)
                else:
                    universe.parsed = True
                    universe.updated_at = datetime.utcnow()

                _log_event(db, "INFO", f"Parsed universe: {universe_id}", universe_id)

                # Save CIM artifact to database
                try:
                    cim_file = PIPELINE_ROOT / "cim" / f"{universe_id}.cim.json"
                    if cim_file.exists():
                        ArtifactStorage.save_file_artifact(
                            db, universe_id, ArtifactStorage.TYPE_CIM, cim_file
                        )
                        _log_event(db, "INFO", f"Saved CIM artifact for {universe_id}", universe_id)
                except Exception as e:
                    _log_event(db, "WARNING", f"Failed to save CIM artifact: {e}", universe_id)

            db.commit()

            results["parser"] = {
                "status": "success",
                "processed": len(parser_results.get("processed", [])),
                "skipped": len(parser_results.get("skipped", [])),
                "failed": len(parser_results.get("failed", [])),
                "details": parser_results
            }
            runs.update_stage_status(run_id, "parser", "success")
            _log_event(db, "INFO", f"Parser stage completed: {len(parser_results.get('processed', []))} processed")

        except Exception as e:
            error_msg = str(e)
            results["parser"] = {"status": "failed", "error": error_msg}
            runs.update_stage_status(run_id, "parser", "failed", error_msg)
            runs.complete_run(run_id, "failed")
            _log_event(db, "ERROR", f"Parser failed: {error_msg}")
            _release_lock()
            db.close()
            return {
                "status": "failed",
                "stage": "parser",
                "run_id": run_id,
                "results": results
            }

        # STAGE 2: Transform
        runs.update_stage_status(run_id, "transform", "running")
        _log_event(db, "INFO", f"Starting transform stage for run {run_id}")

        try:
            # Import transform engine
            from cim_transform.pipeline_runner import PipelineRunner

            # Get all parsed universes from database that haven't been transformed OR lack artifacts
            universes_to_transform = db.query(Universe).filter(Universe.parsed == True).all()

            # For each universe, check if it needs transformation
            universes_needing_transform = []
            cim_dir = PIPELINE_ROOT / "cim"
            cim_dir.mkdir(parents=True, exist_ok=True)

            for universe in universes_to_transform:
                # Check if universe needs transformation or AI enhancement
                needs_transform = (
                    not universe.transformed or
                    not universe.ai_enhanced or  # Reprocess if AI enhancements missing
                    not ArtifactStorage.artifact_exists(db, universe.id, ArtifactStorage.TYPE_SAC_MODEL)
                )

                if needs_transform:
                    # Restore CIM file from database to filesystem (if it exists in DB)
                    cim_content = ArtifactStorage.get_artifact_content(db, universe.id, ArtifactStorage.TYPE_CIM)
                    if cim_content:
                        cim_file = cim_dir / f"{universe.id}.cim.json"
                        with open(cim_file, 'w') as f:
                            f.write(cim_content)
                        _log_event(db, "INFO", f"Restored CIM file for {universe.id} from database", universe.id)

                    # Force transformed flag to False so pipeline will process it
                    universe.transformed = False
                    universes_needing_transform.append(universe.id)

            db.commit()

            if universes_needing_transform:
                _log_event(db, "INFO", f"Universes needing transformation: {', '.join(universes_needing_transform)}")

            # Run transform with force=True if we have universes to transform
            force_transform = len(universes_needing_transform) > 0
            transform_runner = PipelineRunner(PIPELINE_ROOT)
            transform_results = transform_runner.run(force=force_transform)

            # Update database with transformed universes
            for result in transform_results:
                if result.get("status") == "success":
                    universe_id = result.get("universe_id")
                    universe = db.query(Universe).filter(Universe.id == universe_id).first()
                    if universe:
                        universe.transformed = True
                        universe.updated_at = datetime.utcnow()

                        # Save AI enhancements to database if present
                        ai_enhancements = result.get("ai_enhancements")
                        if ai_enhancements:
                            universe.ai_enhanced = True
                            universe.ai_enhancements = ai_enhancements
                            universe.ai_processed_at = datetime.utcnow()

                            # Generate human-readable summary
                            classifications = len(ai_enhancements.get("dimension_classifications", {}))
                            hierarchies = len(ai_enhancements.get("detected_hierarchies", []))
                            formulas = len(ai_enhancements.get("translated_formulas", {}))
                            universe.ai_enhancement_summary = (
                                f"AI classified {classifications} dimensions, "
                                f"detected {hierarchies} hierarchies, "
                                f"translated {formulas} formulas"
                            )

                            _log_event(db, "INFO",
                                      f"AI enhanced {universe_id}: {universe.ai_enhancement_summary}",
                                      universe_id)

                        _log_event(db, "INFO", f"Transformed universe: {universe_id}", universe_id)

                        # Save transform artifacts to database
                        try:
                            targets_dir = PIPELINE_ROOT / "targets" / universe_id

                            # Save SAC model
                            sac_model_file = targets_dir / "sac" / "model.json"
                            if sac_model_file.exists():
                                ArtifactStorage.save_file_artifact(
                                    db, universe_id, ArtifactStorage.TYPE_SAC_MODEL, sac_model_file
                                )

                            # Save Datasphere views
                            datasphere_file = targets_dir / "datasphere" / "views.sql"
                            if datasphere_file.exists():
                                ArtifactStorage.save_file_artifact(
                                    db, universe_id, ArtifactStorage.TYPE_DATASPHERE_VIEWS, datasphere_file
                                )

                            # Save HANA schema
                            hana_file = targets_dir / "hana" / "schema.sql"
                            if hana_file.exists():
                                ArtifactStorage.save_file_artifact(
                                    db, universe_id, ArtifactStorage.TYPE_HANA_SCHEMA, hana_file
                                )

                            _log_event(db, "INFO", f"Saved transform artifacts for {universe_id}", universe_id)
                        except Exception as e:
                            _log_event(db, "WARNING", f"Failed to save transform artifacts: {e}", universe_id)

            db.commit()

            results["transform"] = {
                "status": "success",
                "processed": len([r for r in transform_results if r.get("status") == "success"]),
                "details": transform_results
            }
            runs.update_stage_status(run_id, "transform", "success")
            _log_event(db, "INFO", f"Transform stage completed")

        except Exception as e:
            error_msg = str(e)
            results["transform"] = {"status": "failed", "error": error_msg}
            runs.update_stage_status(run_id, "transform", "failed", error_msg)
            runs.complete_run(run_id, "failed")
            _log_event(db, "ERROR", f"Transform failed: {error_msg}")
            _release_lock()
            db.close()
            return {
                "status": "failed",
                "stage": "transform",
                "run_id": run_id,
                "results": results
            }

        # STAGE 3: Validation
        runs.update_stage_status(run_id, "validation", "running")
        _log_event(db, "INFO", f"Starting validation stage for run {run_id}")

        try:
            # Import validation engine
            from validation_engine.runner import ValidationRunner

            # Create a console mock
            class ConsoleMock:
                def print(self, msg):
                    print(msg)

            validation_runner = ValidationRunner(PIPELINE_ROOT, ConsoleMock())
            validation_runner.run()

            # Update database with validated universes
            validated_count = 0
            for universe in db.query(Universe).filter(Universe.transformed == True, Universe.validated == False).all():
                universe.validated = True
                universe.validated_at = datetime.utcnow()
                universe.updated_at = datetime.utcnow()
                validated_count += 1
                _log_event(db, "INFO", f"Validated universe: {universe.id}", universe.id)

                # Save validation artifacts to database
                try:
                    validation_dir = PIPELINE_ROOT / "validation" / universe.id

                    # Save lineage DOT graph
                    lineage_file = validation_dir / "lineage_graph.dot"
                    if lineage_file.exists():
                        ArtifactStorage.save_file_artifact(
                            db, universe.id, ArtifactStorage.TYPE_LINEAGE_DOT, lineage_file
                        )

                    # Save coverage report
                    coverage_file = validation_dir / "coverage_report.json"
                    if coverage_file.exists():
                        ArtifactStorage.save_file_artifact(
                            db, universe.id, ArtifactStorage.TYPE_COVERAGE_REPORT, coverage_file
                        )

                    # Save semantic diff
                    semantic_file = validation_dir / "semantic_diff.json"
                    if semantic_file.exists():
                        ArtifactStorage.save_file_artifact(
                            db, universe.id, ArtifactStorage.TYPE_SEMANTIC_DIFF, semantic_file
                        )

                    _log_event(db, "INFO", f"Saved validation artifacts for {universe.id}", universe.id)
                except Exception as e:
                    _log_event(db, "WARNING", f"Failed to save validation artifacts: {e}", universe.id)

            db.commit()

            results["validation"] = {
                "status": "success",
                "validated": validated_count
            }
            runs.update_stage_status(run_id, "validation", "success")
            _log_event(db, "INFO", f"Validation stage completed: {validated_count} validated")

        except Exception as e:
            error_msg = str(e)
            results["validation"] = {"status": "failed", "error": error_msg}
            runs.update_stage_status(run_id, "validation", "failed", error_msg)
            runs.complete_run(run_id, "failed")
            _log_event(db, "ERROR", f"Validation failed: {error_msg}")
            _release_lock()
            db.close()
            return {
                "status": "failed",
                "stage": "validation",
                "run_id": run_id,
                "results": results
            }

        # Success - complete run
        runs.complete_run(run_id, "success")
        _log_event(db, "INFO", f"Pipeline run {run_id} completed successfully")
        _release_lock()
        db.close()

        return {
            "status": "success",
            "run_id": run_id,
            "results": results
        }

    except Exception as e:
        # Catch-all for unexpected errors
        _log_event(db, "ERROR", f"Pipeline fatal error: {str(e)}")
        _release_lock()
        db.close()
        return {
            "status": "failed",
            "message": f"Pipeline failed: {str(e)}",
            "run_id": run_id,
            "results": results
        }
