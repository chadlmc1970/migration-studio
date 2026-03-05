"""UNV (binary) universe extractor with JSON and SAP SDK support."""

from pathlib import Path
import shutil
import json

from ..model.cim import CanonicalModel, SourceFile
from ..util.hashing import sha256_file
from ..util.logging import ConversionLogger

# Import SDK bridge
try:
    from ..sdk_bridge import BOBJSDKBridge, UNVParser
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False


def extract_unv(input_path: Path, output_dir: Path, logger: ConversionLogger) -> CanonicalModel:
    """
    Extract .unv/.unx universe metadata.

    Extraction priority:
    1. Companion JSON file (if exists) - INSTANT, ACCURATE ✅
    2. SAP SDK binary extraction - COMPLEX, MAY FAIL
    3. Placeholder mode - FALLBACK

    Args:
        input_path: Path to .unv/.unx file
        output_dir: Output directory
        logger: Conversion logger

    Returns:
        CanonicalModel with extracted metadata
    """
    logger.log(f"Processing UNV file: {input_path}")

    # Check for companion JSON metadata file first!
    json_path = input_path.with_suffix('.json')
    if json_path.exists():
        logger.log(f"✓ Found companion JSON metadata: {json_path.name}")
        return extract_from_json(json_path, input_path, output_dir, logger)

    # Create raw directory
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Copy original file to raw
    raw_copy = raw_dir / input_path.name
    shutil.copy2(input_path, raw_copy)

    # Record source file
    file_size = input_path.stat().st_size
    source_file = SourceFile(
        relative_path=input_path.name,
        size_bytes=file_size,
        sha256=sha256_file(input_path),
    )

    # Build canonical model
    universe_name = input_path.stem
    cim = CanonicalModel(
        universe_id=universe_name,
        universe_name=universe_name,
        source_format="unv",
        source_files=[source_file],
    )

    # Try SDK-based extraction
    if SDK_AVAILABLE:
        try:
            logger.log("Using SAP BusinessObjects SDK for UNV parsing")
            parser = UNVParser()
            cim_data = parser.parse_universe(input_path)

            # Update CIM with SDK data
            cim.data_foundation.tables = [t['name'] for t in cim_data.get('tables', [])]
            cim.data_foundation.joins = cim_data.get('joins', [])
            cim.business_layer.dimensions = [d['name'] for d in cim_data.get('dimensions', [])]
            cim.business_layer.measures = [m['name'] for m in cim_data.get('measures', [])]

            # Store full details in metadata
            cim.metadata['dimension_details'] = cim_data.get('dimensions', [])
            cim.metadata['measure_details'] = cim_data.get('measures', [])

            logger.log(f"✓ Extracted: {len(cim.data_foundation.tables)} tables, {len(cim.business_layer.dimensions)} dimensions, {len(cim.business_layer.measures)} measures")

            # Log advanced features
            if cim_data.get('contexts'):
                logger.log(f"  - {len(cim_data['contexts'])} contexts extracted")
                cim.metadata['contexts'] = cim_data['contexts']

            if cim_data.get('prompts'):
                logger.log(f"  - {len(cim_data['prompts'])} prompts/LOVs extracted")
                cim.metadata['prompts'] = cim_data['prompts']

            if cim_data.get('connection'):
                logger.log(f"  - Connection info extracted")
                cim.metadata['connection'] = cim_data['connection']

        except NotImplementedError:
            logger.warn("SDK parser not fully implemented - using placeholder")
            _create_placeholder_cim(cim, logger)

        except Exception as e:
            logger.warn(f"SDK parsing failed: {e} - using placeholder")
            _create_placeholder_cim(cim, logger)
    else:
        logger.warn("SAP SDK not available - creating placeholder model")
        _create_placeholder_cim(cim, logger)

    cim.update_counts()
    return cim


def extract_from_json(json_path: Path, unv_path: Path, output_dir: Path, logger: ConversionLogger) -> CanonicalModel:
    """
    Extract universe metadata from companion JSON file.

    This is the FAST PATH - no binary decryption needed!

    Args:
        json_path: Path to JSON metadata file
        unv_path: Path to original .unv file (for hashing)
        output_dir: Output directory
        logger: Conversion logger

    Returns:
        CanonicalModel with real metadata from JSON
    """
    logger.log(f"Loading metadata from JSON: {json_path.name}")

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        logger.log("✓ JSON parsed successfully")

        # Create raw directory
        raw_dir = output_dir / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)

        # Copy both files to raw
        for src in [unv_path, json_path]:
            if src.exists():
                shutil.copy2(src, raw_dir / src.name)

        # Record source files
        source_files = []
        if unv_path.exists():
            source_files.append(SourceFile(
                relative_path=unv_path.name,
                size_bytes=unv_path.stat().st_size,
                sha256=sha256_file(unv_path),
            ))
        source_files.append(SourceFile(
            relative_path=json_path.name,
            size_bytes=json_path.stat().st_size,
            sha256=sha256_file(json_path),
        ))

        # Build canonical model from JSON
        universe_id = json_data.get("universe_id", unv_path.stem)
        universe_name = json_data.get("universe_name", universe_id)

        cim = CanonicalModel(
            universe_id=universe_id,
            universe_name=universe_name,
            description=json_data.get("description", ""),
            source_format="unv+json",
            source_files=source_files,
        )

        # Extract tables
        tables = []
        for table_name in json_data.get("tables", []):
            if isinstance(table_name, str):
                tables.append(table_name)
            elif isinstance(table_name, dict):
                tables.append(table_name.get("name", "Unknown"))
        cim.data_foundation.tables = tables

        # Extract joins
        joins = []
        for join_data in json_data.get("joins", []):
            joins.append({
                "name": join_data.get("name", ""),
                "left_table": join_data.get("left_table", ""),
                "right_table": join_data.get("right_table", ""),
                "type": join_data.get("type", "inner"),
                "condition": join_data.get("condition", ""),
                "cardinality": join_data.get("cardinality")
            })
        cim.data_foundation.joins = joins

        # Extract dimensions
        dimensions = []
        for dim_data in json_data.get("dimensions", []):
            dimensions.append(dim_data.get("name", ""))
        cim.business_layer.dimensions = dimensions

        # Extract measures
        measures = []
        for measure_data in json_data.get("measures", []):
            measures.append(measure_data.get("name", ""))
        cim.business_layer.measures = measures

        # Store full details in metadata
        cim.metadata["dimension_details"] = json_data.get("dimensions", [])
        cim.metadata["measure_details"] = json_data.get("measures", [])

        # Store filters and other metadata
        if "filters" in json_data:
            cim.metadata["filters"] = json_data["filters"]
        if "contexts" in json_data:
            cim.metadata["contexts"] = json_data["contexts"]
        if "prompts" in json_data:
            cim.metadata["prompts"] = json_data["prompts"]

        cim.update_counts()

        logger.log(f"✅ JSON extraction complete:")
        logger.log(f"   - {len(cim.data_foundation.tables)} tables")
        logger.log(f"   - {len(cim.data_foundation.joins)} joins")
        logger.log(f"   - {len(cim.business_layer.dimensions)} dimensions")
        logger.log(f"   - {len(cim.business_layer.measures)} measures")
        if "filters" in json_data:
            logger.log(f"   - {len(json_data['filters'])} filters")

        return cim

    except Exception as e:
        logger.error(f"Failed to parse JSON: {e}")
        logger.warn("Falling back to placeholder mode")
        # Fall back to placeholder
        universe_id = unv_path.stem
        cim = CanonicalModel(
            universe_id=universe_id,
            universe_name=universe_id,
            source_format="unv",
        )
        _create_placeholder_cim(cim, logger)
        return cim



def _create_placeholder_cim(cim: CanonicalModel, logger: ConversionLogger):
    """Create placeholder CIM when SDK is not available"""

    cim.metadata["note"] = (
        "UNV binary format requires SAP BusinessObjects SDK. "
        "Placeholder data created - install SDK for full extraction."
    )

    logger.warn("Install SAP BOBJ SDK for full UNV parsing")
    logger.warn("Copy SDK JARs to: backend/app/engines/bobj2sac/sdk/BOBJ_SDK/")
