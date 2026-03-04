"""Core conversion orchestration."""

import json
from pathlib import Path

from bobj2sac.io.detect import detect_format
from bobj2sac.io.unv import extract_unv
from bobj2sac.io.unx import extract_unx
from bobj2sac.io.binary import extract_binary_universe
from bobj2sac.model.cim import CanonicalModel
from bobj2sac.util.logging import ConversionLogger


def convert_universe(input_path: Path, output_dir: Path) -> tuple[CanonicalModel, ConversionLogger]:
    """
    Convert a BOBJ universe to canonical intermediate model.

    Args:
        input_path: Path to .unv or .unx file
        output_dir: Output directory for artifacts

    Returns:
        Tuple of (CanonicalModel, ConversionLogger)
    """
    logger = ConversionLogger()

    # Validate input
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Detect format
    try:
        fmt = detect_format(input_path)
        logger.log(f"Detected format: {fmt}")
    except ValueError as e:
        logger.error(str(e))
        raise

    # Create output directory
    universe_name = input_path.stem
    universe_output = output_dir / universe_name
    universe_output.mkdir(parents=True, exist_ok=True)

    # Extract based on format
    if fmt == "unx":
        # Try XML-based extraction first, fall back to binary
        try:
            cim = extract_unx(input_path, universe_output, logger)
            # If no tables/dims/measures found, try binary parser
            if (len(cim.data_foundation.tables) == 0 and
                len(cim.business_layer.dimensions) == 0 and
                len(cim.business_layer.measures) == 0):
                logger.warn("XML parsing found no content, trying binary parser...")
                cim = extract_binary_universe(input_path, universe_output, logger)
        except Exception as e:
            logger.warn(f"XML parsing failed: {e}, trying binary parser...")
            cim = extract_binary_universe(input_path, universe_output, logger)
    elif fmt == "unv":
        cim = extract_unv(input_path, universe_output, logger)
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    # Save CIM
    cim_path = universe_output / "cim.json"
    with open(cim_path, "w") as f:
        json.dump(cim.model_dump(), f, indent=2)
    logger.log(f"Saved canonical model: {cim_path}")

    # Save report
    report_path = universe_output / "report.json"
    logger.save(report_path)
    logger.log(f"Saved conversion report: {report_path}")

    return cim, logger
