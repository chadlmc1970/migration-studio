"""Pipeline orchestration for multi-engine migration system."""

import json
from pathlib import Path
from typing import Any

from bobj2sac.convert import convert_universe
from bobj2sac.state import PipelineState
from bobj2sac.util.logging import ConversionLogger


def process_pipeline(
    pipeline_root: Path = Path("/pipeline"),
    force: bool = False,
) -> dict[str, Any]:
    """
    Process all universes in pipeline input directory.

    Args:
        pipeline_root: Root pipeline directory
        force: If True, overwrite existing CIM files

    Returns:
        Summary of pipeline run
    """
    input_dir = pipeline_root / "input"
    cim_dir = pipeline_root / "cim"
    logs_dir = pipeline_root / "logs" / "parser"
    raw_dir = pipeline_root / "raw"

    # Ensure directories exist
    cim_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Initialize pipeline state
    pipeline_state = PipelineState(pipeline_root)

    # Track processing results
    results = {
        "processed": [],
        "skipped": [],
        "failed": [],
        "total": 0,
    }

    # Scan for universe files (including subdirectories)
    universe_files = list(input_dir.glob("**/*.unx")) + list(input_dir.glob("**/*.unv"))

    if not universe_files:
        return {
            **results,
            "message": f"No universe files found in {input_dir}",
        }

    for universe_file in universe_files:
        results["total"] += 1
        universe_id = universe_file.stem

        # Check if CIM already exists
        cim_path = cim_dir / f"{universe_id}.cim.json"
        if cim_path.exists() and not force:
            results["skipped"].append({
                "universe": universe_id,
                "reason": "CIM already exists",
                "path": str(cim_path),
            })
            continue

        try:
            # Convert universe to temporary location
            temp_output = raw_dir / universe_id
            cim, logger = convert_universe(universe_file, temp_output)

            # Build pipeline CIM (schema v0.1 format)
            pipeline_cim = _build_pipeline_cim(cim)

            # Write CIM to pipeline location
            with open(cim_path, "w") as f:
                json.dump(pipeline_cim, f, indent=2)

            # Write parser report
            parser_report = _build_parser_report(cim, logger)
            report_path = logs_dir / f"{universe_id}_report.json"
            with open(report_path, "w") as f:
                json.dump(parser_report, f, indent=2)

            # Update pipeline state: mark as parsed
            pipeline_state.mark_parsed(universe_id)

            results["processed"].append({
                "universe": universe_id,
                "cim": str(cim_path),
                "report": str(report_path),
                "raw": str(temp_output),
            })

        except Exception as e:
            results["failed"].append({
                "universe": universe_id,
                "error": str(e),
            })

    return results


def _build_pipeline_cim(cim: Any) -> dict[str, Any]:
    """
    Transform internal CIM to pipeline CIM format (schema v0.1).

    Args:
        cim: Internal CanonicalModel instance

    Returns:
        Pipeline-compatible CIM dictionary
    """
    return {
        "schema_version": "0.1",
        "universe": {
            "name": cim.universe_name,
            "id": cim.universe_id,
            "source_format": cim.source_format,
            "extraction_timestamp": cim.extraction_timestamp,
        },
        "tables": [
            {"name": table} for table in cim.data_foundation.tables
        ],
        "joins": cim.data_foundation.joins,
        "dimensions": [
            dim if isinstance(dim, dict) else {"name": dim, "table": "Unknown", "column": dim}
            for dim in cim.business_layer.dimensions
        ],
        "measures": [
            measure if isinstance(measure, dict) else {"name": measure, "table": "Unknown", "column": measure}
            for measure in cim.business_layer.measures
        ],
        "filters": [
            {"name": flt} for flt in cim.business_layer.filters
        ],
        "source_files": [sf.model_dump() for sf in cim.source_files],
        "metadata": {
            "data_foundation": cim.data_foundation.raw_metadata,
            "business_layer": cim.business_layer.raw_metadata,
            **cim.metadata,
        },
    }


def _build_parser_report(cim: Any, logger: ConversionLogger) -> dict[str, Any]:
    """
    Build parser report for pipeline inspection.

    Args:
        cim: CanonicalModel instance
        logger: ConversionLogger

    Returns:
        Parser report dictionary
    """
    # Identify unparsed sections
    unparsed_sections = []
    if not cim.data_foundation.tables and cim.data_foundation.raw_metadata:
        unparsed_sections.append("data_foundation_tables")
    if not cim.data_foundation.joins and cim.data_foundation.raw_metadata:
        unparsed_sections.append("data_foundation_joins")
    if not cim.business_layer.dimensions and cim.business_layer.raw_metadata:
        unparsed_sections.append("business_layer_dimensions")
    if not cim.business_layer.measures and cim.business_layer.raw_metadata:
        unparsed_sections.append("business_layer_measures")

    return {
        "universe": cim.universe_id,
        "tables_detected": len(cim.data_foundation.tables),
        "joins_detected": len(cim.data_foundation.joins),
        "dimensions_detected": len(cim.business_layer.dimensions),
        "measures_detected": len(cim.business_layer.measures),
        "filters_detected": len(cim.business_layer.filters),
        "warnings": logger.warnings,
        "errors": logger.errors,
        "unparsed_sections": unparsed_sections,
        "source_files_count": len(cim.source_files),
    }
