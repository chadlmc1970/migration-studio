"""UNV (binary) universe extractor."""

from pathlib import Path

from bobj2sac.model.cim import CanonicalModel, SourceFile
from bobj2sac.util.hashing import sha256_file
from bobj2sac.util.logging import ConversionLogger


def extract_unv(input_path: Path, output_dir: Path, logger: ConversionLogger) -> CanonicalModel:
    """
    Extract .unv universe (binary format).

    This is a container extractor placeholder.
    Real implementation requires proprietary format knowledge.

    Args:
        input_path: Path to .unv file
        output_dir: Output directory
        logger: Conversion logger

    Returns:
        CanonicalModel with basic metadata
    """
    logger.warn("UNV format parsing not implemented - creating placeholder model")
    logger.log(f"Processing UNV file: {input_path}")

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
    universe_name = input_path.stem
    cim = CanonicalModel(
        universe_id=universe_name,
        universe_name=universe_name,
        source_format="unv",
        source_files=[source_file],
    )

    cim.metadata["note"] = (
        "UNV binary format requires proprietary parser. "
        "TODO: Implement structure extraction or integrate with BO SDK."
    )

    logger.warn("TODO: Implement UNV binary format parser")
    logger.warn("TODO: Extract tables, joins, dimensions, measures from binary structure")

    cim.update_counts()
    return cim
