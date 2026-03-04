"""
Crystal Reports Parser (.rpt files)

Crystal Reports are binary files with proprietary format.
Full parsing requires Crystal Reports SDK or third-party library.

This is a placeholder implementation that extracts basic metadata.
"""

from pathlib import Path

from ..model.cim import CanonicalModel, SourceFile
from ..util.hashing import sha256_file
from ..util.logging import ConversionLogger


def extract_rpt(input_path: Path, output_dir: Path, logger: ConversionLogger) -> CanonicalModel:
    """
    Extract .rpt Crystal Report (placeholder implementation).

    Full implementation requires:
    - Crystal Reports SDK (C#/COM based)
    - Third-party Python libraries (crython, etc.)
    - Crystal Server REST API

    Args:
        input_path: Path to .rpt file
        output_dir: Output directory
        logger: Conversion logger

    Returns:
        CanonicalModel with basic metadata
    """
    logger.warn("Crystal Reports (.rpt) parsing not fully implemented - creating placeholder")
    logger.log(f"Processing Crystal Report: {input_path}")

    # Create raw directory
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Copy original file to raw
    import shutil
    raw_copy = raw_dir / input_path.name
    shutil.copy2(input_path, raw_copy)

    # Record source file
    file_size = input_path.stat().st_size
    source_file = SourceFile(
        relative_path=input_path.name,
        size_bytes=file_size,
        sha256=sha256_file(input_path),
    )

    # Build minimal canonical model
    report_name = input_path.stem
    cim = CanonicalModel(
        universe_id=report_name,
        universe_name=report_name,
        source_format="rpt",
        source_files=[source_file],
    )

    # Add placeholder notes
    cim.metadata["note"] = (
        "Crystal Reports binary format requires proprietary SDK. "
        "TODO: Implement via Crystal SDK, REST API, or third-party library."
    )
    cim.metadata["parser_status"] = "placeholder"
    cim.metadata["implementation_options"] = [
        "SAP Crystal Reports SDK (Windows/.NET)",
        "Crystal Server REST API",
        "Third-party libraries (crython, etc.)",
        "Manual metadata export via Crystal Designer"
    ]

    logger.warn("TODO: Implement Crystal Reports parser")
    logger.warn("TODO: Extract report structure, data sources, formulas, parameters")

    # Attempt basic file signature check
    try:
        with open(input_path, 'rb') as f:
            header = f.read(16)
            cim.metadata["file_signature"] = header.hex()

            # Crystal Reports typically start with specific byte patterns
            if header[:4] == b'\x00\x01\x00\x00' or b'Crystal' in header:
                logger.log("Confirmed Crystal Reports file signature")
                cim.metadata["file_type_confirmed"] = True
            else:
                logger.warn("File signature does not match expected Crystal Reports format")
                cim.metadata["file_type_confirmed"] = False

    except Exception as e:
        logger.warn(f"Failed to read file signature: {e}")

    cim.update_counts()
    return cim
