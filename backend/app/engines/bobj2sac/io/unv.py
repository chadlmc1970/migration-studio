"""UNV (binary) universe extractor with JSON and SAP SDK support."""

from pathlib import Path
import shutil
import json

from ..model.cim import CanonicalModel, SourceFile, Table, Join, Dimension, Measure
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

            # Convert SDK output to CanonicalModel
            _populate_cim_from_sdk(cim, cim_data, logger)

            logger.log(f"✓ Extracted: {len(cim.tables)} tables, {len(cim.dimensions)} dimensions, {len(cim.measures)} measures")

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
        for table_name in json_data.get("tables", []):
            if isinstance(table_name, str):
                cim.add_table(Table(
                    name=table_name,
                    table_type="table"
                ))
            elif isinstance(table_name, dict):
                cim.add_table(Table(
                    name=table_name.get("name", "Unknown"),
                    table_type=table_name.get("type", "table"),
                    sql=table_name.get("sql")
                ))

        # Extract joins
        for join_data in json_data.get("joins", []):
            cim.add_join(Join(
                name=join_data.get("name", ""),
                left_table=join_data.get("left_table", ""),
                right_table=join_data.get("right_table", ""),
                join_type=join_data.get("type", "inner"),
                condition=join_data.get("condition", ""),
                cardinality=join_data.get("cardinality")
            ))

        # Extract dimensions
        for dim_data in json_data.get("dimensions", []):
            cim.add_dimension(Dimension(
                name=dim_data.get("name", ""),
                table=dim_data.get("table"),
                column=dim_data.get("column"),
                description=dim_data.get("description", ""),
                qualification=dim_data.get("qualification", "dimension")
            ))

        # Extract measures
        for measure_data in json_data.get("measures", []):
            cim.add_measure(Measure(
                name=measure_data.get("name", ""),
                table=measure_data.get("table"),
                column=measure_data.get("column"),
                aggregation=measure_data.get("aggregation", "SUM"),
                formula=measure_data.get("formula"),
                description=measure_data.get("description", "")
            ))

        # Store filters and other metadata
        if "filters" in json_data:
            cim.metadata["filters"] = json_data["filters"]
        if "contexts" in json_data:
            cim.metadata["contexts"] = json_data["contexts"]
        if "prompts" in json_data:
            cim.metadata["prompts"] = json_data["prompts"]

        cim.update_counts()

        logger.log(f"✅ JSON extraction complete:")
        logger.log(f"   - {len(cim.tables)} tables")
        logger.log(f"   - {len(cim.joins)} joins")
        logger.log(f"   - {len(cim.dimensions)} dimensions")
        logger.log(f"   - {len(cim.measures)} measures")
        if "filters" in json_data:
            logger.log(f"   - {len(json_data['filters'])} filters")

        return cim

    except Exception as e:
        logger.error(f"Failed to parse JSON: {e}")
        logger.warn("Falling back to binary extraction")
        # Fall through to binary extraction
        return extract_from_binary(unv_path, output_dir, logger)


def extract_from_binary(input_path: Path, output_dir: Path, logger: ConversionLogger) -> CanonicalModel:
    """
    Extract from binary .unv file using SDK (original method).

    This is the SLOW PATH - requires SDK and may hit encryption issues.
    """
    logger.log("Attempting binary extraction with SDK...")

    """Populate CanonicalModel from SDK-extracted data"""

    # Add tables
    for table_data in cim_data.get('tables', []):
        table = Table(
            name=table_data['name'],
            table_type=table_data.get('type', 'table')
        )
        table.metadata['sql'] = table_data.get('sql')
        table.metadata['description'] = table_data.get('description')
        cim.tables.append(table)

    # Add joins
    for join_data in cim_data.get('joins', []):
        join = Join(
            left_table=join_data['left_table'],
            right_table=join_data['right_table'],
            join_type=join_data.get('type', 'inner'),
            condition=join_data['condition']
        )
        join.metadata['cardinality'] = join_data.get('cardinality')
        cim.joins.append(join)

    # Add dimensions
    for dim_data in cim_data.get('dimensions', []):
        dim = Dimension(
            name=dim_data['name'],
            source_table=dim_data.get('table'),
            source_column=dim_data.get('column'),
            description=dim_data.get('description', '')
        )
        dim.metadata['type'] = dim_data.get('type')
        dim.metadata['qualification'] = dim_data.get('qualification')
        cim.dimensions.append(dim)

    # Add measures
    for measure_data in cim_data.get('measures', []):
        measure = Measure(
            name=measure_data['name'],
            source_table=measure_data.get('table'),
            source_column=measure_data.get('column'),
            aggregation=measure_data.get('aggregation', 'SUM'),
            description=measure_data.get('description', '')
        )
        measure.metadata['formula'] = measure_data.get('formula')
        cim.measures.append(measure)


def _create_placeholder_cim(cim: CanonicalModel, logger: ConversionLogger):
    """Create placeholder CIM when SDK is not available"""

    cim.metadata["note"] = (
        "UNV binary format requires SAP BusinessObjects SDK. "
        "Placeholder data created - install SDK for full extraction."
    )

    logger.warn("Install SAP BOBJ SDK for full UNV parsing")
    logger.warn("Copy SDK JARs to: backend/app/engines/bobj2sac/sdk/BOBJ_SDK/")
