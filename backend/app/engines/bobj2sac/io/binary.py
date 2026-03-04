"""Hybrid parser for binary BOEXI universe files.

When UDX export isn't available, this parser extracts what metadata it can
from binary .unx/.blx/.dfx files and allows manual supplementation via JSON.
"""

import zipfile
import json
from pathlib import Path
from typing import Dict, Any

from bobj2sac.model.cim import CanonicalModel, SourceFile
from bobj2sac.util.hashing import sha256_bytes
from bobj2sac.util.logging import ConversionLogger


def extract_binary_universe(input_path: Path, output_dir: Path, logger: ConversionLogger) -> CanonicalModel:
    """
    Extract metadata from binary .unx universe files.

    Strategy:
    1. Extract Properties file for basic metadata
    2. Look for companion .json metadata file (manual supplement)
    3. Create minimal CIM with available info

    Args:
        input_path: Path to .unx file
        output_dir: Output directory
        logger: Conversion logger

    Returns:
        CanonicalModel with extracted metadata
    """
    logger.log(f"Extracting binary universe: {input_path}")

    # Create raw directory
    raw_dir = output_dir / "raw" / "binary_extract"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Read source file
    with open(input_path, "rb") as f:
        data = f.read()

    source_file = SourceFile(
        file_name=input_path.name,
        file_type="unx_binary",
        file_path=str(input_path),
        file_size=len(data),
        file_hash=sha256_bytes(data),
    )

    # Initialize CIM with defaults
    cim = CanonicalModel(
        universe_id=input_path.stem,
        universe_name=input_path.stem,
        source_format="unx_binary",
        source_files=[source_file],
    )

    # Extract .unx archive
    try:
        with zipfile.ZipFile(input_path, "r") as zf:
            logger.log(f"Extracting {len(zf.namelist())} files from archive")
            zf.extractall(raw_dir)

            # Parse Properties file for metadata
            if "Properties" in zf.namelist():
                _parse_properties(raw_dir / "Properties", cim, logger)

    except Exception as e:
        logger.error(f"Failed to extract archive: {e}")

    # Check for companion metadata JSON
    json_path = input_path.with_suffix('.json')
    if json_path.exists():
        logger.log(f"Found companion metadata file: {json_path.name}")
        _load_companion_metadata(json_path, cim, logger)
    else:
        logger.warn(f"No companion metadata found. Create {json_path.name} to supplement universe definition")
        logger.warn("See /tmp/universe_template.json for format")

    cim.update_counts()
    logger.log(f"Binary extraction complete: {len(cim.data_foundation.tables)} tables, "
              f"{len(cim.business_layer.dimensions)} dimensions, "
              f"{len(cim.business_layer.measures)} measures")

    return cim


def _parse_properties(props_path: Path, cim: CanonicalModel, logger: ConversionLogger) -> None:
    """Parse Properties file for basic metadata."""
    try:
        with open(props_path, 'rb') as f:
            data = f.read()

        # Properties file is binary but contains readable strings
        text = data.decode('utf-8', errors='ignore')

        # Extract key metadata
        if 'UNIVERSE_NAME' in text:
            start = text.find('UNIVERSE_NAME')
            snippet = text[start:start+200]
            # Try to extract name
            parts = snippet.split('\x00')
            for part in parts:
                if part and len(part) > 3 and not part.startswith('UNIVERSE'):
                    cim.universe_name = part.strip()
                    logger.log(f"Extracted universe name: {cim.universe_name}")
                    break

        if 'CREATION_TIME' in text:
            start = text.find('CREATION_TIME')
            snippet = text[start:start+100]
            parts = snippet.split('\x00')
            for part in parts:
                if 'T' in part and '-' in part:
                    cim.metadata['creation_time'] = part.strip()
                    logger.log(f"Extracted creation time: {part.strip()}")
                    break

    except Exception as e:
        logger.warn(f"Could not parse Properties file: {e}")


def _load_companion_metadata(json_path: Path, cim: CanonicalModel, logger: ConversionLogger) -> None:
    """Load manually created companion metadata JSON."""
    try:
        with open(json_path, 'r') as f:
            metadata = json.load(f)

        # Update CIM with provided metadata
        if 'universe_name' in metadata:
            cim.universe_name = metadata['universe_name']

        if 'description' in metadata:
            cim.metadata['description'] = metadata['description']

        # Load tables
        if 'tables' in metadata:
            for table in metadata['tables']:
                table_name = table if isinstance(table, str) else table.get('name')
                if table_name and table_name not in cim.data_foundation.tables:
                    cim.data_foundation.tables.append(table_name)
                    logger.log(f"  Loaded table: {table_name}")

        # Load joins
        if 'joins' in metadata:
            cim.data_foundation.joins.extend(metadata['joins'])
            logger.log(f"  Loaded {len(metadata['joins'])} joins")

        # Load dimensions
        if 'dimensions' in metadata:
            for dim in metadata['dimensions']:
                if isinstance(dim, dict):
                    cim.business_layer.dimensions.append(dim)
                else:
                    cim.business_layer.dimensions.append({
                        "name": dim,
                        "table": "Unknown",
                        "column": dim
                    })
            logger.log(f"  Loaded {len(metadata['dimensions'])} dimensions")

        # Load measures
        if 'measures' in metadata:
            for measure in metadata['measures']:
                if isinstance(measure, dict):
                    cim.business_layer.measures.append(measure)
                else:
                    cim.business_layer.measures.append({
                        "name": measure,
                        "table": "Unknown",
                        "column": measure,
                        "aggregation": "SUM"
                    })
            logger.log(f"  Loaded {len(metadata['measures'])} measures")

        # Load filters
        if 'filters' in metadata:
            for flt in metadata['filters']:
                filter_name = flt if isinstance(flt, str) else flt.get('name', 'Unknown')
                if filter_name not in cim.business_layer.filters:
                    cim.business_layer.filters.append(filter_name)
            logger.log(f"  Loaded {len(metadata['filters'])} filters")

        logger.log("Companion metadata loaded successfully")

    except Exception as e:
        logger.error(f"Failed to load companion metadata: {e}")
