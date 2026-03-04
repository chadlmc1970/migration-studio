"""UNX (zip-based) universe extractor."""

import zipfile
from pathlib import Path

from bobj2sac.model.cim import CanonicalModel, SourceFile
from bobj2sac.util.hashing import sha256_bytes
from bobj2sac.util.logging import ConversionLogger


def extract_unx(input_path: Path, output_dir: Path, logger: ConversionLogger) -> CanonicalModel:
    """
    Extract .unx universe (zip container) and build canonical model.

    Args:
        input_path: Path to .unx file
        output_dir: Output directory for extraction
        logger: Conversion logger

    Returns:
        CanonicalModel with extracted metadata
    """
    logger.log(f"Extracting UNX file: {input_path}")

    # Create raw extraction directory
    raw_dir = output_dir / "raw" / "unx_contents"
    raw_dir.mkdir(parents=True, exist_ok=True)

    source_files: list[SourceFile] = []

    # Extract zip contents
    try:
        with zipfile.ZipFile(input_path, "r") as zf:
            logger.log(f"Found {len(zf.namelist())} files in archive")

            for name in zf.namelist():
                # Skip directories
                if name.endswith("/"):
                    continue

                # Extract file
                data = zf.read(name)
                extract_path = raw_dir / name
                extract_path.parent.mkdir(parents=True, exist_ok=True)

                with open(extract_path, "wb") as f:
                    f.write(data)

                # Record in manifest
                source_files.append(
                    SourceFile(
                        relative_path=name,
                        size_bytes=len(data),
                        sha256=sha256_bytes(data),
                    )
                )
                logger.log(f"Extracted: {name} ({len(data)} bytes)")

    except zipfile.BadZipFile as e:
        logger.error(f"Invalid UNX/zip file: {e}")
        raise

    # Build canonical model
    universe_name = input_path.stem
    cim = CanonicalModel(
        universe_id=universe_name,
        universe_name=universe_name,
        source_format="unx",
        source_files=source_files,
    )

    # Attempt to discover structure from extracted files
    _discover_structure(raw_dir, cim, logger)

    cim.update_counts()
    logger.log(f"UNX extraction complete: {len(source_files)} files")

    return cim


def _discover_structure(raw_dir: Path, cim: CanonicalModel, logger: ConversionLogger) -> None:
    """
    Discover universe structure from extracted files.

    This is a placeholder for actual UNX parsing logic.
    Real implementation would parse XML/binary files within the archive.
    """
    logger.warn("UNX structure discovery not fully implemented - placeholder mode")

    # Look for common UNX file patterns
    xml_files = list(raw_dir.rglob("*.xml"))
    if xml_files:
        logger.log(f"Found {len(xml_files)} XML files")
        cim.metadata["xml_files"] = [str(f.relative_to(raw_dir)) for f in xml_files]

    # Look for data foundation hints
    for xml_file in xml_files:
        name_lower = xml_file.name.lower()
        if "datafoundation" in name_lower or "connection" in name_lower:
            logger.log(f"Potential data foundation file: {xml_file.name}")
            cim.data_foundation.raw_metadata[xml_file.name] = {
                "path": str(xml_file.relative_to(raw_dir)),
                "note": "TODO: parse this file for table/join definitions",
            }

        if "businesslayer" in name_lower or "dimension" in name_lower:
            logger.log(f"Potential business layer file: {xml_file.name}")
            cim.business_layer.raw_metadata[xml_file.name] = {
                "path": str(xml_file.relative_to(raw_dir)),
                "note": "TODO: parse this file for dimension/measure definitions",
            }

    # Placeholder object counts
    logger.warn("Object counts are placeholders - full parsing not implemented")
