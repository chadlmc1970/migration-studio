"""
BIAR Archive Parser (.car files)

BIAR (BusinessObjects Import/Archive) files are ZIP archives containing:
- Multiple BOBJ objects (universes, reports, connections)
- Metadata XML files
- Dependency information

This parser extracts and routes objects to appropriate parsers.
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Tuple

from ..model.cim import CanonicalModel, SourceFile
from ..util.hashing import sha256_bytes
from ..util.logging import ConversionLogger
from .unx import extract_unx
from .unv import extract_unv
from .wid import extract_wid
from .detect import detect_format


def extract_car(input_path: Path, output_dir: Path, logger: ConversionLogger) -> List[CanonicalModel]:
    """
    Extract .car BIAR archive and route contained objects to appropriate parsers.

    Args:
        input_path: Path to .car file
        output_dir: Output directory for extraction
        logger: Conversion logger

    Returns:
        List of CanonicalModels (one per contained object)
    """
    logger.log(f"Extracting BIAR archive: {input_path}")

    # Create raw extraction directory
    raw_dir = output_dir / "raw" / "biar_contents"
    raw_dir.mkdir(parents=True, exist_ok=True)

    source_files: List[SourceFile] = []
    contained_objects: List[Tuple[Path, str]] = []  # (path, format)

    # Extract ZIP contents
    try:
        with zipfile.ZipFile(input_path, "r") as zf:
            logger.log(f"Found {len(zf.namelist())} files in BIAR archive")

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

                # Identify BOBJ objects
                obj_format = _identify_object_type(extract_path, logger)
                if obj_format:
                    contained_objects.append((extract_path, obj_format))
                    logger.log(f"Identified {obj_format} object: {name}")
                else:
                    logger.log(f"Extracted metadata: {name}")

    except zipfile.BadZipFile as e:
        logger.error(f"Invalid BIAR/zip file: {e}")
        raise

    logger.log(f"BIAR extraction complete: {len(contained_objects)} BOBJ object(s) found")

    # Parse contained objects
    models = []
    for obj_path, obj_format in contained_objects:
        try:
            # Create sub-output directory for this object
            obj_name = obj_path.stem
            obj_output_dir = output_dir / obj_name

            logger.log(f"Parsing {obj_format} object: {obj_name}")

            # Route to appropriate parser
            if obj_format == "unx":
                model = extract_unx(obj_path, obj_output_dir, logger)
            elif obj_format == "unv":
                model = extract_unv(obj_path, obj_output_dir, logger)
            elif obj_format == "wid":
                model = extract_wid(obj_path, obj_output_dir, logger)
            else:
                logger.warn(f"No parser available for format: {obj_format}")
                continue

            # Mark as extracted from BIAR
            model.metadata["extracted_from_biar"] = str(input_path.name)
            model.metadata["biar_path"] = obj_path.relative_to(raw_dir).as_posix()

            models.append(model)
            logger.log(f"Successfully parsed {obj_name}")

        except Exception as e:
            logger.error(f"Failed to parse object {obj_path.name}: {e}")
            continue

    if not models:
        logger.warn("No parseable BOBJ objects found in BIAR archive")

        # Create placeholder CIM for the archive itself
        archive_name = input_path.stem
        placeholder = CanonicalModel(
            universe_id=archive_name,
            universe_name=archive_name,
            source_format="car",
            source_files=source_files,
        )
        placeholder.metadata["note"] = "BIAR archive with no parseable objects"
        placeholder.metadata["contained_files"] = len(source_files)
        models.append(placeholder)

    return models


def _identify_object_type(file_path: Path, logger: ConversionLogger) -> str:
    """
    Identify the type of BOBJ object.

    Returns:
        Format string ('unx', 'unv', 'wid', 'rpt', etc.) or empty string if not recognized
    """
    # Check file extension first
    ext = file_path.suffix.lower()
    if ext in ['.unx', '.unv', '.wid', '.rpt', '.rep']:
        return ext[1:]  # Remove the dot

    # Try to detect by content
    try:
        detected = detect_format(file_path)
        if detected and detected != "unknown":
            return detected
    except Exception as e:
        logger.warn(f"Failed to detect format for {file_path.name}: {e}")

    # Check for specific patterns in BIAR metadata
    # BIAR objects often have associated .xml files with type information
    metadata_file = file_path.with_suffix('.xml')
    if metadata_file.exists():
        try:
            tree = ET.parse(metadata_file)
            root = tree.getroot()

            # Look for type indicators
            obj_type = root.get("type") or root.findtext(".//Type")
            if obj_type:
                type_map = {
                    "Universe": "unx" if file_path.suffix == ".unx" else "unv",
                    "Webi": "wid",
                    "CrystalReport": "rpt",
                    "WebIntelligence": "wid",
                }
                return type_map.get(obj_type, "")

        except Exception:
            pass

    return ""


def _parse_biar_manifest(raw_dir: Path, logger: ConversionLogger) -> Dict[str, Any]:
    """
    Parse BIAR manifest file (if present) for archive metadata.

    BIAR archives may contain a manifest.xml with:
    - Object inventory
    - Dependencies
    - Export metadata
    """
    manifest_file = raw_dir / "manifest.xml"
    if not manifest_file.exists():
        # Try alternative names
        for alt_name in ["MANIFEST.XML", "Manifest.xml", "biar_manifest.xml"]:
            alt_file = raw_dir / alt_name
            if alt_file.exists():
                manifest_file = alt_file
                break

    if not manifest_file.exists():
        return {}

    try:
        tree = ET.parse(manifest_file)
        root = tree.getroot()

        manifest = {
            "export_date": root.findtext(".//ExportDate", ""),
            "export_tool": root.findtext(".//Tool", ""),
            "objects": [],
            "dependencies": []
        }

        # Parse object inventory
        for obj_elem in root.findall(".//Object"):
            obj_info = {
                "name": obj_elem.get("name", ""),
                "type": obj_elem.get("type", ""),
                "id": obj_elem.get("id", ""),
                "path": obj_elem.findtext(".//Path", ""),
            }
            manifest["objects"].append(obj_info)

        # Parse dependencies
        for dep_elem in root.findall(".//Dependency"):
            dep_info = {
                "from": dep_elem.get("from", ""),
                "to": dep_elem.get("to", ""),
                "type": dep_elem.get("type", ""),
            }
            manifest["dependencies"].append(dep_info)

        return manifest

    except Exception as e:
        logger.warn(f"Failed to parse BIAR manifest: {e}")
        return {}
