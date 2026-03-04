"""
WebI Document Parser (.wid files)

WebI documents are ZIP archives containing:
- document.xml: Report structure, queries, variables
- style.xml: Formatting and styling
- resources/: Images and other assets

This parser extracts semantic content and maps to CIM format.
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..model.cim import CanonicalModel, SourceFile, Dimension, Measure
from ..util.hashing import sha256_bytes
from ..util.logging import ConversionLogger


def extract_wid(input_path: Path, output_dir: Path, logger: ConversionLogger) -> CanonicalModel:
    """
    Extract .wid WebI document and build canonical model.

    Args:
        input_path: Path to .wid file
        output_dir: Output directory for extraction
        logger: Conversion logger

    Returns:
        CanonicalModel with extracted metadata
    """
    logger.log(f"Extracting WebI document: {input_path}")

    # Create raw extraction directory
    raw_dir = output_dir / "raw" / "wid_contents"
    raw_dir.mkdir(parents=True, exist_ok=True)

    source_files: List[SourceFile] = []

    # Extract ZIP contents
    try:
        with zipfile.ZipFile(input_path, "r") as zf:
            logger.log(f"Found {len(zf.namelist())} files in WebI archive")

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
        logger.error(f"Invalid WebI/zip file: {e}")
        raise

    # Build canonical model
    universe_name = input_path.stem
    cim = CanonicalModel(
        universe_id=universe_name,
        universe_name=universe_name,
        source_format="wid",
        source_files=source_files,
    )

    # Parse WebI structure
    _parse_webi_structure(raw_dir, cim, logger)

    cim.update_counts()
    logger.log(f"WebI extraction complete: {len(source_files)} files")

    return cim


def _parse_webi_structure(raw_dir: Path, cim: CanonicalModel, logger: ConversionLogger) -> None:
    """
    Parse WebI document structure from extracted files.

    Extracts:
    - Data providers (queries)
    - Dimensions and measures
    - Filters and variables
    - Report structure
    """
    document_xml = raw_dir / "document.xml"

    if not document_xml.exists():
        logger.warn("document.xml not found in WebI archive - cannot parse structure")
        return

    try:
        tree = ET.parse(document_xml)
        root = tree.getroot()

        # Parse data providers (queries)
        data_providers = _parse_data_providers(root, logger)
        if data_providers:
            cim.metadata["webi_data_providers"] = data_providers
            logger.log(f"Found {len(data_providers)} data provider(s)")

        # Parse dimensions
        dimensions = _parse_dimensions(root, logger)
        for dim in dimensions:
            cim.business_layer.dimensions.append(dim)
        logger.log(f"Extracted {len(dimensions)} dimension(s)")

        # Parse measures
        measures = _parse_measures(root, logger)
        for measure in measures:
            cim.business_layer.measures.append(measure)
        logger.log(f"Extracted {len(measures)} measure(s)")

        # Parse filters
        filters = _parse_filters(root, logger)
        if filters:
            cim.metadata["webi_filters"] = filters
            logger.log(f"Found {len(filters)} filter(s)")

        # Parse variables
        variables = _parse_variables(root, logger)
        if variables:
            cim.metadata["webi_variables"] = variables
            logger.log(f"Found {len(variables)} variable(s)")

        # Parse report structure
        reports = _parse_report_structure(root, logger)
        if reports:
            cim.metadata["webi_reports"] = reports
            logger.log(f"Found {len(reports)} report tab(s)")

    except ET.ParseError as e:
        logger.error(f"Failed to parse document.xml: {e}")
        cim.metadata["parse_error"] = str(e)
    except Exception as e:
        logger.error(f"Unexpected error parsing WebI structure: {e}")
        cim.metadata["parse_error"] = str(e)


def _parse_data_providers(root: ET.Element, logger: ConversionLogger) -> List[Dict[str, Any]]:
    """Extract data provider (query) information."""
    providers = []

    # WebI XML namespace handling (may vary by version)
    # Try common element paths
    for dp_elem in root.findall(".//DataProvider") or root.findall(".//*[@type='DataProvider']"):
        try:
            provider = {
                "name": dp_elem.get("name", "Unnamed"),
                "query": None,
                "universe": None,
                "objects": []
            }

            # Extract query SQL if available
            query_elem = dp_elem.find(".//Query") or dp_elem.find(".//SQL")
            if query_elem is not None and query_elem.text:
                provider["query"] = query_elem.text.strip()

            # Extract universe reference
            universe_elem = dp_elem.find(".//Universe")
            if universe_elem is not None:
                provider["universe"] = universe_elem.get("name") or universe_elem.text

            # Extract objects used in query
            for obj_elem in dp_elem.findall(".//Object") or dp_elem.findall(".//Column"):
                obj_name = obj_elem.get("name") or obj_elem.text
                if obj_name:
                    provider["objects"].append(obj_name)

            providers.append(provider)

        except Exception as e:
            logger.warn(f"Failed to parse data provider: {e}")
            continue

    return providers


def _parse_dimensions(root: ET.Element, logger: ConversionLogger) -> List[Dimension]:
    """Extract dimension objects from WebI document."""
    dimensions = []

    # Look for dimension definitions
    for dim_elem in root.findall(".//Dimension") or root.findall(".//*[@type='Dimension']"):
        try:
            name = dim_elem.get("name") or dim_elem.findtext(".//Name", "Unnamed")
            description = dim_elem.findtext(".//Description", "")

            # Extract qualification (Dimension, Detail, etc.)
            qualification = dim_elem.get("qualification", "Dimension")

            dimension = Dimension(
                name=name,
                description=description,
                source_table=dim_elem.get("table", ""),
                source_column=dim_elem.get("column", ""),
                data_type=dim_elem.get("dataType", "string"),
                raw_metadata={
                    "qualification": qualification,
                    "format": dim_elem.get("format", ""),
                }
            )

            dimensions.append(dimension)

        except Exception as e:
            logger.warn(f"Failed to parse dimension: {e}")
            continue

    return dimensions


def _parse_measures(root: ET.Element, logger: ConversionLogger) -> List[Measure]:
    """Extract measure objects from WebI document."""
    measures = []

    # Look for measure definitions
    for measure_elem in root.findall(".//Measure") or root.findall(".//*[@type='Measure']"):
        try:
            name = measure_elem.get("name") or measure_elem.findtext(".//Name", "Unnamed")
            description = measure_elem.findtext(".//Description", "")

            # Extract aggregation function
            aggregation = measure_elem.get("aggregation") or measure_elem.findtext(".//Aggregation", "sum")

            measure = Measure(
                name=name,
                description=description,
                source_table=measure_elem.get("table", ""),
                source_column=measure_elem.get("column", ""),
                aggregation=aggregation.lower(),
                data_type=measure_elem.get("dataType", "number"),
                raw_metadata={
                    "format": measure_elem.get("format", ""),
                    "formula": measure_elem.findtext(".//Formula", ""),
                }
            )

            measures.append(measure)

        except Exception as e:
            logger.warn(f"Failed to parse measure: {e}")
            continue

    return measures


def _parse_filters(root: ET.Element, logger: ConversionLogger) -> List[Dict[str, Any]]:
    """Extract filter definitions."""
    filters = []

    for filter_elem in root.findall(".//Filter") or root.findall(".//*[@type='Filter']"):
        try:
            filter_info = {
                "name": filter_elem.get("name", "Unnamed"),
                "expression": filter_elem.findtext(".//Expression", ""),
                "operand": filter_elem.get("operand", ""),
                "operator": filter_elem.get("operator", ""),
                "values": []
            }

            # Extract filter values
            for value_elem in filter_elem.findall(".//Value"):
                if value_elem.text:
                    filter_info["values"].append(value_elem.text)

            filters.append(filter_info)

        except Exception as e:
            logger.warn(f"Failed to parse filter: {e}")
            continue

    return filters


def _parse_variables(root: ET.Element, logger: ConversionLogger) -> List[Dict[str, Any]]:
    """Extract variable definitions."""
    variables = []

    for var_elem in root.findall(".//Variable") or root.findall(".//*[@type='Variable']"):
        try:
            variable = {
                "name": var_elem.get("name", "Unnamed"),
                "type": var_elem.get("type", ""),
                "formula": var_elem.findtext(".//Formula", ""),
                "qualification": var_elem.get("qualification", ""),
            }

            variables.append(variable)

        except Exception as e:
            logger.warn(f"Failed to parse variable: {e}")
            continue

    return variables


def _parse_report_structure(root: ET.Element, logger: ConversionLogger) -> List[Dict[str, Any]]:
    """Extract report structure (tabs, blocks, tables, charts)."""
    reports = []

    for report_elem in root.findall(".//Report") or root.findall(".//*[@type='Report']"):
        try:
            report = {
                "name": report_elem.get("name", "Unnamed"),
                "blocks": []
            }

            # Parse blocks (tables, charts, cells)
            for block_elem in report_elem.findall(".//Block"):
                block = {
                    "type": block_elem.get("type", "table"),
                    "name": block_elem.get("name", ""),
                    "columns": []
                }

                # Extract columns used in block
                for col_elem in block_elem.findall(".//Column"):
                    col_name = col_elem.get("name") or col_elem.text
                    if col_name:
                        block["columns"].append(col_name)

                report["blocks"].append(block)

            reports.append(report)

        except Exception as e:
            logger.warn(f"Failed to parse report structure: {e}")
            continue

    return reports
