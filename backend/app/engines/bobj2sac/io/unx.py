"""UNX (zip-based) universe extractor."""

import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

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
    Discover universe structure from extracted XML files.
    Parses BOBJ universe XML to extract tables, joins, dimensions, and measures.
    """
    logger.log("Parsing universe XML structure...")

    # Find all XML files
    xml_files = list(raw_dir.rglob("*.xml"))
    if not xml_files:
        logger.warn("No XML files found in universe archive")
        return

    logger.log(f"Found {len(xml_files)} XML file(s)")

    # Parse each XML file
    for xml_file in xml_files:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Remove namespace if present
            if '}' in root.tag:
                ns = root.tag.split('}')[0] + '}'
            else:
                ns = ''

            logger.log(f"Parsing {xml_file.name}...")

            # Extract DataFoundation - Tables
            data_foundation = root.find(f'.//{ns}DataFoundation') or root.find('.//DataFoundation')
            if data_foundation:
                tables_node = data_foundation.find(f'.//{ns}Tables') or data_foundation.find('.//Tables')
                if tables_node:
                    for table in tables_node.findall(f'.//{ns}Table') or tables_node.findall('.//Table'):
                        table_name = table.get('name') or table.get('alias', 'Unknown')
                        if table_name and table_name not in cim.data_foundation.tables:
                            cim.data_foundation.tables.append(table_name)
                            logger.log(f"  Found table: {table_name}")

                # Extract Joins
                joins_node = data_foundation.find(f'.//{ns}Joins') or data_foundation.find('.//Joins')
                if joins_node:
                    for join in joins_node.findall(f'.//{ns}Join') or joins_node.findall('.//Join'):
                        join_name = join.get('name', 'Unknown')
                        left_table = None
                        right_table = None
                        condition = None

                        left_node = join.find(f'.//{ns}LeftTable') or join.find('.//LeftTable')
                        if left_node is not None and left_node.text:
                            left_table = left_node.text

                        right_node = join.find(f'.//{ns}RightTable') or join.find('.//RightTable')
                        if right_node is not None and right_node.text:
                            right_table = right_node.text

                        cond_node = join.find(f'.//{ns}Condition') or join.find('.//Condition')
                        if cond_node is not None and cond_node.text:
                            condition = cond_node.text

                        if left_table and right_table:
                            join_info = {
                                "name": join_name,
                                "left_table": left_table,
                                "right_table": right_table,
                                "condition": condition or f"{left_table} = {right_table}"
                            }
                            cim.data_foundation.joins.append(join_info)
                            logger.log(f"  Found join: {join_name} ({left_table} -> {right_table})")

            # Extract BusinessLayer - Dimensions and Measures
            business_layer = root.find(f'.//{ns}BusinessLayer') or root.find('.//BusinessLayer')

            # DEBUG: Log what we're finding
            logger.log(f"  Root tag: {root.tag}")
            logger.log(f"  Namespace: '{ns}' (len={len(ns)})")
            logger.log(f"  BusinessLayer found: {business_layer is not None}")

            if business_layer:
                # Try multiple ways to find dimensions
                dims1 = business_layer.findall(f'.//{ns}Dimension')
                dims2 = business_layer.findall('.//Dimension')
                dims3 = root.findall('.//*[@class="Dimension"]')
                dims4 = root.findall('.//*[local-name()="Dimension"]')

                logger.log(f"  Dimension search: ns={len(dims1 or [])}, no-ns={len(dims2 or [])}, class={len(dims3 or [])}, local-name={len(dims4 or [])}")

                # Use whichever found dimensions
                dimensions_list = dims1 or dims2 or dims3 or dims4 or []

                # Extract Dimensions
                for dimension in dimensions_list:
                    dim_name = dimension.get('name', 'Unknown')

                    # Extract expression to get table.column
                    expr_node = dimension.find(f'.//{ns}Expression') or dimension.find('.//Expression')
                    table_node = dimension.find(f'.//{ns}Table') or dimension.find('.//Table')

                    table_name = None
                    column_name = None

                    # Try to get table from <Table> element
                    if table_node is not None and table_node.text:
                        table_name = table_node.text.strip()

                    # Try to parse expression for table.column
                    if expr_node is not None and expr_node.text:
                        expr = expr_node.text.strip()
                        # Handle expressions like "TABLE.COLUMN" or calculations
                        if '.' in expr and not any(op in expr for op in ['(', '+', '-', '*', '/', 'CASE']):
                            parts = expr.split('.', 1)
                            if not table_name:
                                table_name = parts[0].strip()
                            column_name = parts[1].strip()
                        else:
                            # For calculated dimensions, use expression as column
                            column_name = expr[:50]  # Truncate long expressions

                    if dim_name:
                        dim_obj = {
                            "name": dim_name,
                            "table": table_name or "Unknown",
                            "column": column_name or dim_name
                        }
                        cim.business_layer.dimensions.append(dim_obj)
                        logger.log(f"  Found dimension: {dim_name} ({table_name}.{column_name})")

                # Extract Measures
                for measure in business_layer.findall(f'.//{ns}Measure') or business_layer.findall('.//Measure'):
                    measure_name = measure.get('name', 'Unknown')

                    # Extract expression to get table.column
                    expr_node = measure.find(f'.//{ns}Expression') or measure.find('.//Expression')
                    table_node = measure.find(f'.//{ns}Table') or measure.find('.//Table')

                    table_name = None
                    column_name = None

                    # Try to get table from <Table> element
                    if table_node is not None and table_node.text:
                        table_name = table_node.text.strip()

                    # Try to parse expression for table.column
                    if expr_node is not None and expr_node.text:
                        expr = expr_node.text.strip()
                        # Handle expressions like "TABLE.COLUMN" or calculations
                        if '.' in expr and not any(op in expr for op in ['CASE', 'SUM', 'AVG', 'COUNT', 'MIN', 'MAX']):
                            parts = expr.split('.', 1)
                            if not table_name:
                                table_name = parts[0].strip()
                            # Remove any trailing parentheses or operators
                            col = parts[1].strip()
                            if ' ' in col:
                                col = col.split()[0]
                            column_name = col
                        else:
                            # For calculated measures, use first table.column reference
                            if '.' in expr:
                                import re
                                match = re.search(r'(\w+)\.(\w+)', expr)
                                if match:
                                    if not table_name:
                                        table_name = match.group(1)
                                    column_name = match.group(2)

                    if measure_name:
                        measure_obj = {
                            "name": measure_name,
                            "table": table_name or "Unknown",
                            "column": column_name or measure_name
                        }
                        cim.business_layer.measures.append(measure_obj)
                        logger.log(f"  Found measure: {measure_name} ({table_name}.{column_name})")

                # Extract Filters
                for filter_node in business_layer.findall(f'.//{ns}Filter') or business_layer.findall('.//Filter'):
                    filter_name = filter_node.get('name', 'Unknown')
                    if filter_name and filter_name not in cim.business_layer.filters:
                        cim.business_layer.filters.append(filter_name)
                        logger.log(f"  Found filter: {filter_name}")

        except ET.ParseError as e:
            logger.error(f"XML parse error in {xml_file.name}: {e}")
        except Exception as e:
            logger.error(f"Error processing {xml_file.name}: {e}")

    # Log summary
    logger.log(f"Parsing complete:")
    logger.log(f"  Tables: {len(cim.data_foundation.tables)}")
    logger.log(f"  Joins: {len(cim.data_foundation.joins)}")
    logger.log(f"  Dimensions: {len(cim.business_layer.dimensions)}")
    logger.log(f"  Measures: {len(cim.business_layer.measures)}")
    logger.log(f"  Filters: {len(cim.business_layer.filters)}")
