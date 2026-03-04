"""UDX (Universe Design eXchange) format parser.

UDX is SAP's XML-based export format for BusinessObjects universes.
This is the recommended format for migration as it's human-readable and complete.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

from bobj2sac.model.cim import CanonicalModel, SourceFile
from bobj2sac.util.hashing import sha256_bytes
from bobj2sac.util.logging import ConversionLogger


def extract_udx(input_path: Path, output_dir: Path, logger: ConversionLogger) -> CanonicalModel:
    """
    Parse .udx universe file and build canonical model.

    Args:
        input_path: Path to .udx file
        output_dir: Output directory for extraction
        logger: Conversion logger

    Returns:
        CanonicalModel with extracted metadata
    """
    logger.log(f"Parsing UDX file: {input_path}")

    # Create raw directory
    raw_dir = output_dir / "raw" / "udx_contents"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Read and record source file
    with open(input_path, "rb") as f:
        data = f.read()

    source_file = SourceFile(
        file_name=input_path.name,
        file_type="udx",
        file_path=str(input_path),
        file_size=len(data),
        file_hash=sha256_bytes(data),
    )

    # Initialize CIM
    cim = CanonicalModel(
        universe_id=input_path.stem,
        universe_name=input_path.stem,
        source_format="udx",
        source_files=[source_file],
    )

    # Parse UDX XML
    try:
        tree = ET.parse(input_path)
        root = tree.getroot()

        # UDX files use namespaces
        ns = _extract_namespace(root)

        logger.log(f"UDX root tag: {root.tag}")

        # Extract universe info
        _parse_universe_info(root, ns, cim, logger)

        # Extract data foundation
        _parse_data_foundation(root, ns, cim, logger)

        # Extract business layer
        _parse_business_layer(root, ns, cim, logger)

        cim.update_counts()
        logger.log(f"UDX parsing complete: {len(cim.data_foundation.tables)} tables, "
                  f"{len(cim.business_layer.dimensions)} dimensions, "
                  f"{len(cim.business_layer.measures)} measures")

    except Exception as e:
        logger.error(f"Failed to parse UDX: {e}")
        raise

    return cim


def _extract_namespace(root: ET.Element) -> str:
    """Extract XML namespace from root element."""
    if '}' in root.tag:
        return root.tag.split('}')[0] + '}'
    return ''


def _parse_universe_info(root: ET.Element, ns: str, cim: CanonicalModel, logger: ConversionLogger) -> None:
    """Parse universe metadata from UDX."""
    # Look for universe name/description
    name_elem = root.find(f'.//{ns}UniverseName') or root.find('.//UniverseName')
    if name_elem is not None and name_elem.text:
        cim.universe_name = name_elem.text
        logger.log(f"Universe name: {cim.universe_name}")

    desc_elem = root.find(f'.//{ns}Description') or root.find('.//Description')
    if desc_elem is not None and desc_elem.text:
        cim.metadata['description'] = desc_elem.text


def _parse_data_foundation(root: ET.Element, ns: str, cim: CanonicalModel, logger: ConversionLogger) -> None:
    """Parse data foundation (tables and joins) from UDX."""

    # Find DataFoundation or PhysicalLayer section
    df = root.find(f'.//{ns}DataFoundation') or root.find('.//DataFoundation')
    if not df:
        df = root.find(f'.//{ns}PhysicalLayer') or root.find('.//PhysicalLayer')

    if not df:
        logger.warn("No DataFoundation section found in UDX")
        return

    logger.log("Parsing data foundation...")

    # Parse tables
    for table_elem in df.findall(f'.//{ns}Table') or df.findall('.//Table'):
        table_name = table_elem.get('name') or table_elem.get('alias')
        if table_name and table_name not in cim.data_foundation.tables:
            cim.data_foundation.tables.append(table_name)
            logger.log(f"  Found table: {table_name}")

    # Parse joins
    for join_elem in df.findall(f'.//{ns}Join') or df.findall('.//Join'):
        join_name = join_elem.get('name', 'Unknown')

        left_table_elem = join_elem.find(f'.//{ns}SourceTable') or join_elem.find('.//SourceTable')
        right_table_elem = join_elem.find(f'.//{ns}TargetTable') or join_elem.find('.//TargetTable')

        left_table = left_table_elem.text if left_table_elem is not None and left_table_elem.text else None
        right_table = right_table_elem.text if right_table_elem is not None and right_table_elem.text else None

        if left_table and right_table:
            join_info = {
                "name": join_name,
                "left_table": left_table,
                "right_table": right_table,
                "condition": f"{left_table} = {right_table}"
            }
            cim.data_foundation.joins.append(join_info)
            logger.log(f"  Found join: {join_name}")


def _parse_business_layer(root: ET.Element, ns: str, cim: CanonicalModel, logger: ConversionLogger) -> None:
    """Parse business layer (dimensions, measures, filters) from UDX."""

    bl = root.find(f'.//{ns}BusinessLayer') or root.find('.//BusinessLayer')
    if not bl:
        logger.warn("No BusinessLayer section found in UDX")
        return

    logger.log("Parsing business layer...")

    # Parse dimensions
    for dim_elem in bl.findall(f'.//{ns}Dimension') or bl.findall('.//Dimension'):
        dim_name = dim_elem.get('name', 'Unknown')

        # Get expression to extract table.column
        expr_elem = dim_elem.find(f'.//{ns}Expression') or dim_elem.find('.//Expression')
        table_elem = dim_elem.find(f'.//{ns}TableName') or dim_elem.find('.//TableName')

        table_name = table_elem.text.strip() if table_elem is not None and table_elem.text else "Unknown"
        column_name = dim_name

        # Try to parse expression for table.column
        if expr_elem is not None and expr_elem.text:
            expr = expr_elem.text.strip()
            if '.' in expr:
                parts = expr.split('.', 1)
                if not table_elem:
                    table_name = parts[0].strip()
                column_name = parts[1].strip()

        dim_obj = {
            "name": dim_name,
            "table": table_name,
            "column": column_name
        }
        cim.business_layer.dimensions.append(dim_obj)
        logger.log(f"  Found dimension: {dim_name}")

    # Parse measures
    for measure_elem in bl.findall(f'.//{ns}Measure') or bl.findall('.//Measure'):
        measure_name = measure_elem.get('name', 'Unknown')

        expr_elem = measure_elem.find(f'.//{ns}Expression') or measure_elem.find('.//Expression')
        table_elem = measure_elem.find(f'.//{ns}TableName') or measure_elem.find('.//TableName')
        agg_elem = measure_elem.find(f'.//{ns}AggregateFunction') or measure_elem.find('.//AggregateFunction')

        table_name = table_elem.text.strip() if table_elem is not None and table_elem.text else "Unknown"
        column_name = measure_name
        aggregation = agg_elem.text.strip() if agg_elem is not None and agg_elem.text else "SUM"

        if expr_elem is not None and expr_elem.text:
            expr = expr_elem.text.strip()
            if '.' in expr and '(' not in expr:
                parts = expr.split('.', 1)
                if not table_elem:
                    table_name = parts[0].strip()
                column_name = parts[1].strip()

        measure_obj = {
            "name": measure_name,
            "table": table_name,
            "column": column_name,
            "aggregation": aggregation
        }
        cim.business_layer.measures.append(measure_obj)
        logger.log(f"  Found measure: {measure_name} ({aggregation})")

    # Parse filters
    for filter_elem in bl.findall(f'.//{ns}Filter') or bl.findall('.//Filter'):
        filter_name = filter_elem.get('name', 'Unknown')
        if filter_name not in cim.business_layer.filters:
            cim.business_layer.filters.append(filter_name)
            logger.log(f"  Found filter: {filter_name}")
