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

# Import SDK bridge
try:
    from ..sdk_bridge import BOBJSDKBridge, UNVParser
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False


def extract_binary_universe(input_path: Path, output_dir: Path, logger: ConversionLogger) -> CanonicalModel:
    """
    Extract metadata from binary .unx universe files.

    Strategy:
    1. Try SAP SDK parser first (if available)
    2. Fall back to Properties file extraction
    3. Look for companion .json metadata file (manual supplement)
    4. Use built-in metadata for known universe types

    Args:
        input_path: Path to .unx file
        output_dir: Output directory
        logger: Conversion logger

    Returns:
        CanonicalModel with extracted metadata
    """
    logger.log(f"Extracting binary universe: {input_path}")

    # Read source file
    with open(input_path, "rb") as f:
        data = f.read()

    source_file = SourceFile(
        relative_path=input_path.name,
        size_bytes=len(data),
        sha256=sha256_bytes(data),
    )

    # Initialize CIM with defaults
    cim = CanonicalModel(
        universe_id=input_path.stem,
        universe_name=input_path.stem,
        source_format="unx_binary",
        source_files=[source_file],
    )

    # Try SDK-based extraction first
    if SDK_AVAILABLE:
        try:
            logger.log("Using SAP BusinessObjects SDK for UNX parsing")
            parser = UNVParser()
            cim_data = parser.parse_universe(input_path)
            _populate_cim_from_sdk(cim, cim_data, logger)

            cim.update_counts()
            logger.log(f"SDK extraction complete: {len(cim.data_foundation.tables)} tables, "
                      f"{len(cim.business_layer.dimensions)} dimensions, "
                      f"{len(cim.business_layer.measures)} measures")
            return cim

        except Exception as e:
            logger.warn(f"SDK parsing failed: {e} - falling back to manual extraction")
    else:
        logger.warn("SAP SDK not available - using fallback extraction methods")

    # Fallback: Extract archive and parse Properties
    raw_dir = output_dir / "raw" / "binary_extract"
    raw_dir.mkdir(parents=True, exist_ok=True)

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
    elif 'BOEXI40-Audit' in input_path.name:
        # Load built-in BOEXI40 Audit metadata
        logger.log("Loading built-in BOEXI40 Audit universe metadata...")
        _load_builtin_audit_metadata(cim, logger)
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


def _load_builtin_audit_metadata(cim: CanonicalModel, logger: ConversionLogger) -> None:
    """Load built-in metadata for BOEXI40 Audit universes."""
    # Standard BOEXI40 Audit universe structure
    tables = [
        "CMS_AUDITEVENT",
        "CMS_INFOOBJECTS",
        "CMS_INFOOBJECTS5",
        "CMS_USERDETAILS"
    ]

    dimensions = [
        {"name": "Event Type", "table": "CMS_AUDITEVENT", "column": "SI_EVENT_TYPE"},
        {"name": "Event Action", "table": "CMS_AUDITEVENT", "column": "SI_ACTION"},
        {"name": "Event Date", "table": "CMS_AUDITEVENT", "column": "SI_TIMESTAMP"},
        {"name": "User Name", "table": "CMS_USERDETAILS", "column": "SI_NAME"},
        {"name": "Object Name", "table": "CMS_INFOOBJECTS", "column": "SI_NAME"},
        {"name": "Object Type", "table": "CMS_INFOOBJECTS", "column": "SI_KIND"}
    ]

    measures = [
        {"name": "Event Count", "table": "CMS_AUDITEVENT", "column": "SI_EVENT_ID", "aggregation": "COUNT"},
        {"name": "Unique Users", "table": "CMS_AUDITEVENT", "column": "SI_USER_ID", "aggregation": "COUNT_DISTINCT"},
        {"name": "Unique Objects", "table": "CMS_AUDITEVENT", "column": "SI_OBJECT_ID", "aggregation": "COUNT_DISTINCT"}
    ]

    joins = [
        {
            "name": "EventToInfoObject",
            "left_table": "CMS_AUDITEVENT",
            "right_table": "CMS_INFOOBJECTS",
            "condition": "CMS_AUDITEVENT.SI_OBJECT_ID = CMS_INFOOBJECTS.SI_ID"
        }
    ]

    # Load into CIM
    cim.data_foundation.tables.extend(tables)
    cim.data_foundation.joins.extend(joins)
    cim.business_layer.dimensions.extend(dimensions)
    cim.business_layer.measures.extend(measures)

    logger.log(f"Loaded built-in BOEXI40 Audit metadata: {len(tables)} tables, {len(dimensions)} dimensions, {len(measures)} measures")


def _populate_cim_from_sdk(cim: CanonicalModel, cim_data: dict, logger: ConversionLogger):
    """Populate CanonicalModel from SDK-extracted data"""

    # Update universe metadata
    if 'universe' in cim_data:
        universe_meta = cim_data['universe']
        cim.universe_name = universe_meta.get('name', cim.universe_name)
        if 'description' in universe_meta:
            cim.metadata['description'] = universe_meta['description']
        if 'version' in universe_meta:
            cim.metadata['version'] = universe_meta['version']

    # Load tables
    if 'tables' in cim_data:
        for table in cim_data['tables']:
            table_name = table.get('name')
            if table_name:
                cim.data_foundation.tables.append(table_name)
                if table.get('sql'):
                    cim.metadata.setdefault('table_sql', {})[table_name] = table['sql']
        logger.log(f"  Loaded {len(cim_data['tables'])} tables from SDK")

    # Load joins
    if 'joins' in cim_data:
        for join in cim_data['joins']:
            cim.data_foundation.joins.append({
                "name": f"{join['left_table']}_to_{join['right_table']}",
                "left_table": join['left_table'],
                "right_table": join['right_table'],
                "condition": join['condition']
            })
        logger.log(f"  Loaded {len(cim_data['joins'])} joins from SDK")

    # Load dimensions
    if 'dimensions' in cim_data:
        for dim in cim_data['dimensions']:
            cim.business_layer.dimensions.append({
                "name": dim['name'],
                "table": dim.get('table', 'Unknown'),
                "column": dim.get('column', dim['name']),
                "description": dim.get('description', '')
            })
        logger.log(f"  Loaded {len(cim_data['dimensions'])} dimensions from SDK")

    # Load measures
    if 'measures' in cim_data:
        for measure in cim_data['measures']:
            cim.business_layer.measures.append({
                "name": measure['name'],
                "table": measure.get('table', 'Unknown'),
                "column": measure.get('column', measure['name']),
                "aggregation": measure.get('aggregation', 'SUM'),
                "formula": measure.get('formula')
            })
        logger.log(f"  Loaded {len(cim_data['measures'])} measures from SDK")

    # Load contexts (BOBJ-specific)
    if 'contexts' in cim_data and cim_data['contexts']:
        cim.metadata['contexts'] = cim_data['contexts']
        logger.log(f"  Loaded {len(cim_data['contexts'])} contexts from SDK")

    # Load prompts/LOVs
    if 'prompts' in cim_data and cim_data['prompts']:
        cim.metadata['prompts'] = cim_data['prompts']
        logger.log(f"  Loaded {len(cim_data['prompts'])} prompts from SDK")

    # Load connection info
    if 'connection' in cim_data and cim_data['connection']:
        cim.metadata['connection'] = cim_data['connection']

    logger.log("SDK data successfully populated into CIM")

