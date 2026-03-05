"""UNV (binary) universe extractor with SAP SDK support."""

from pathlib import Path
import shutil

from bobj2sac.model.cim import CanonicalModel, SourceFile, Table, Join, Dimension, Measure
from bobj2sac.util.hashing import sha256_file
from bobj2sac.util.logging import ConversionLogger

# Import SDK bridge
try:
    from ..sdk_bridge import BOBJSDKBridge, UNVParser
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False


def extract_unv(input_path: Path, output_dir: Path, logger: ConversionLogger) -> CanonicalModel:
    """
    Extract .unv universe (binary format) using SAP SDK.

    Falls back to placeholder if SDK is not available.

    Args:
        input_path: Path to .unv file
        output_dir: Output directory
        logger: Conversion logger

    Returns:
        CanonicalModel with extracted metadata
    """
    logger.log(f"Processing UNV file: {input_path}")

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


def _populate_cim_from_sdk(cim: CanonicalModel, cim_data: dict, logger: ConversionLogger):
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
