"""
SAC Model Generator

Generates SAP Analytics Cloud semantic models from CIM (Canonical Intermediate Model).

Output: SAC model JSON compatible with SAC REST API
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


def generate_sac_model(cim: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """
    Generate SAC model from CIM.

    Args:
        cim: Canonical Intermediate Model (parsed JSON)
        output_dir: Output directory for SAC artifacts

    Returns:
        Generation report with status and artifacts created
    """
    sac_dir = output_dir / "sac"
    sac_dir.mkdir(parents=True, exist_ok=True)

    # Extract CIM components
    universe_id = cim.get("universe_id", "unknown")
    universe_name = cim.get("universe_name", universe_id)
    data_foundation = cim.get("data_foundation", {})
    business_layer = cim.get("business_layer", {})

    # Build SAC model structure
    sac_model = {
        "modelId": _sanitize_id(universe_id),
        "modelName": universe_name,
        "modelType": "Dataset",
        "version": "1.0",
        "created": datetime.utcnow().isoformat() + "Z",
        "source": f"Migrated from BOBJ universe: {universe_name}",

        # Data sources (tables)
        "dataSources": _generate_data_sources(data_foundation),

        # Dimensions
        "dimensions": _generate_dimensions(business_layer),

        # Measures
        "measures": _generate_measures(business_layer),

        # Relationships (joins)
        "relationships": _generate_relationships(data_foundation),

        # Metadata
        "metadata": {
            "sourceSystem": "BusinessObjects",
            "sourceFormat": cim.get("source_format", "unknown"),
            "migrationTimestamp": datetime.utcnow().isoformat() + "Z",
            "cimVersion": cim.get("metadata", {}).get("cim_version", "0.1"),
        }
    }

    # Write SAC model JSON
    model_file = sac_dir / "sac_model.json"
    with open(model_file, 'w', encoding='utf-8') as f:
        json.dump(sac_model, f, indent=2, ensure_ascii=False)

    # Generate additional SAC artifacts
    artifacts_created = [str(model_file)]

    # Generate dimension hierarchy file (if hierarchies present)
    hierarchies = _generate_hierarchies(business_layer)
    if hierarchies:
        hierarchy_file = sac_dir / "hierarchies.json"
        with open(hierarchy_file, 'w', encoding='utf-8') as f:
            json.dump(hierarchies, f, indent=2)
        artifacts_created.append(str(hierarchy_file))

    # Generate calculated members (if present)
    calculated_members = _generate_calculated_members(business_layer)
    if calculated_members:
        calc_file = sac_dir / "calculated_members.json"
        with open(calc_file, 'w', encoding='utf-8') as f:
            json.dump(calculated_members, f, indent=2)
        artifacts_created.append(str(calc_file))

    return {
        "status": "success",
        "universe_id": universe_id,
        "artifacts": artifacts_created,
        "dimensions_count": len(sac_model["dimensions"]),
        "measures_count": len(sac_model["measures"]),
        "relationships_count": len(sac_model["relationships"]),
    }


def _sanitize_id(name: str) -> str:
    """Sanitize name for use as SAC model ID."""
    # Remove special characters, replace spaces with underscores
    sanitized = "".join(c if c.isalnum() or c == '_' else '_' for c in name)
    return sanitized.lower()


def _generate_data_sources(data_foundation: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate SAC data source definitions from CIM tables."""
    tables = data_foundation.get("tables", [])
    data_sources = []

    for table in tables:
        # Handle both dict and object formats
        if isinstance(table, dict):
            table_name = table.get("name", "")
            table_alias = table.get("alias", table_name)
        else:
            table_name = getattr(table, "name", "")
            table_alias = getattr(table, "alias", table_name)

        if not table_name:
            continue

        data_source = {
            "sourceId": _sanitize_id(table_name),
            "sourceName": table_name,
            "sourceAlias": table_alias,
            "sourceType": "Table",
            "schema": data_foundation.get("connection", {}).get("schema", ""),
        }

        data_sources.append(data_source)

    return data_sources


def _generate_dimensions(business_layer: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate SAC dimension definitions from CIM dimensions."""
    cim_dimensions = business_layer.get("dimensions", [])
    dimensions = []

    for dim in cim_dimensions:
        # Handle both dict and object formats
        if isinstance(dim, dict):
            dim_name = dim.get("name", "")
            dim_desc = dim.get("description", "")
            source_table = dim.get("source_table", "")
            source_column = dim.get("source_column", "")
            data_type = dim.get("data_type", "string")
        else:
            dim_name = getattr(dim, "name", "")
            dim_desc = getattr(dim, "description", "")
            source_table = getattr(dim, "source_table", "")
            source_column = getattr(dim, "source_column", "")
            data_type = getattr(dim, "data_type", "string")

        if not dim_name:
            continue

        dimension = {
            "dimensionId": _sanitize_id(dim_name),
            "dimensionName": dim_name,
            "description": dim_desc,
            "dimensionType": _map_dimension_type(data_type),
            "sourceTable": _sanitize_id(source_table) if source_table else "",
            "sourceColumn": source_column,
            "dataType": _map_data_type(data_type),
        }

        dimensions.append(dimension)

    return dimensions


def _generate_measures(business_layer: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate SAC measure definitions from CIM measures."""
    cim_measures = business_layer.get("measures", [])
    measures = []

    for measure in cim_measures:
        # Handle both dict and object formats
        if isinstance(measure, dict):
            measure_name = measure.get("name", "")
            measure_desc = measure.get("description", "")
            source_table = measure.get("source_table", "")
            source_column = measure.get("source_column", "")
            aggregation = measure.get("aggregation", "sum")
            data_type = measure.get("data_type", "number")
        else:
            measure_name = getattr(measure, "name", "")
            measure_desc = getattr(measure, "description", "")
            source_table = getattr(measure, "source_table", "")
            source_column = getattr(measure, "source_column", "")
            aggregation = getattr(measure, "aggregation", "sum")
            data_type = getattr(measure, "data_type", "number")

        if not measure_name:
            continue

        sac_measure = {
            "measureId": _sanitize_id(measure_name),
            "measureName": measure_name,
            "description": measure_desc,
            "aggregation": _map_aggregation(aggregation),
            "sourceTable": _sanitize_id(source_table) if source_table else "",
            "sourceColumn": source_column,
            "dataType": _map_data_type(data_type),
            "format": _get_measure_format(data_type),
        }

        measures.append(sac_measure)

    return measures


def _generate_relationships(data_foundation: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate SAC relationships from CIM joins."""
    cim_joins = data_foundation.get("joins", [])
    relationships = []

    for join in cim_joins:
        # Handle both dict and object formats
        if isinstance(join, dict):
            left_table = join.get("left_table", "")
            right_table = join.get("right_table", "")
            left_column = join.get("left_column", "")
            right_column = join.get("right_column", "")
            join_type = join.get("join_type", "inner")
        else:
            left_table = getattr(join, "left_table", "")
            right_table = getattr(join, "right_table", "")
            left_column = getattr(join, "left_column", "")
            right_column = getattr(join, "right_column", "")
            join_type = getattr(join, "join_type", "inner")

        if not (left_table and right_table):
            continue

        relationship = {
            "relationshipId": f"{_sanitize_id(left_table)}_{_sanitize_id(right_table)}",
            "fromTable": _sanitize_id(left_table),
            "toTable": _sanitize_id(right_table),
            "fromColumn": left_column,
            "toColumn": right_column,
            "joinType": _map_join_type(join_type),
            "cardinality": "OneToMany",  # Default - could be enhanced
        }

        relationships.append(relationship)

    return relationships


def _generate_hierarchies(business_layer: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate SAC hierarchies if present in CIM."""
    # TODO: Extract hierarchy information from CIM
    # Hierarchies may be in metadata or as special dimension types
    return []


def _generate_calculated_members(business_layer: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate SAC calculated members from CIM formulas."""
    # TODO: Extract calculated members/formulas from CIM
    # May be in metadata or as special measure types
    return []


def _map_dimension_type(data_type: str) -> str:
    """Map CIM data type to SAC dimension type."""
    type_map = {
        "string": "Attribute",
        "date": "Time",
        "datetime": "Time",
        "timestamp": "Time",
        "number": "Attribute",
        "integer": "Attribute",
    }
    return type_map.get(data_type.lower(), "Attribute")


def _map_data_type(data_type: str) -> str:
    """Map CIM data type to SAC data type."""
    type_map = {
        "string": "String",
        "number": "Number",
        "integer": "Integer",
        "decimal": "Decimal",
        "date": "Date",
        "datetime": "DateTime",
        "timestamp": "DateTime",
        "boolean": "Boolean",
    }
    return type_map.get(data_type.lower(), "String")


def _map_aggregation(aggregation: str) -> str:
    """Map CIM aggregation to SAC aggregation."""
    agg_map = {
        "sum": "SUM",
        "count": "COUNT",
        "avg": "AVERAGE",
        "average": "AVERAGE",
        "min": "MIN",
        "max": "MAX",
        "distinctcount": "DISTINCT_COUNT",
    }
    return agg_map.get(aggregation.lower(), "SUM")


def _map_join_type(join_type: str) -> str:
    """Map CIM join type to SAC join type."""
    join_map = {
        "inner": "Inner",
        "left": "Left Outer",
        "right": "Right Outer",
        "full": "Full Outer",
        "left outer": "Left Outer",
        "right outer": "Right Outer",
        "full outer": "Full Outer",
    }
    return join_map.get(join_type.lower(), "Inner")


def _get_measure_format(data_type: str) -> str:
    """Get default format for measure based on data type."""
    format_map = {
        "number": "#,##0.00",
        "decimal": "#,##0.00",
        "integer": "#,##0",
        "currency": "$#,##0.00",
        "percent": "0.00%",
    }
    return format_map.get(data_type.lower(), "#,##0.00")
