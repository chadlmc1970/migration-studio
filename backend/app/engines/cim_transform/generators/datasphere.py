"""
Datasphere View Generator

Generates SAP Datasphere SQL views from CIM.

Datasphere uses SQL views and graphical models to represent data.
This generator creates SQL view definitions compatible with Datasphere.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


def generate_datasphere_views(cim: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """
    Generate Datasphere views from CIM.

    Args:
        cim: Canonical Intermediate Model (parsed JSON)
        output_dir: Output directory for Datasphere artifacts

    Returns:
        Generation report with status and artifacts created
    """
    datasphere_dir = output_dir / "datasphere"
    datasphere_dir.mkdir(parents=True, exist_ok=True)

    universe_id = cim.get("universe_id", "unknown")
    data_foundation = cim.get("data_foundation", {})
    business_layer = cim.get("business_layer", {})

    artifacts_created = []

    # Generate SQL views
    views_sql = _generate_views_sql(data_foundation, business_layer)
    views_file = datasphere_dir / "views.sql"
    with open(views_file, 'w', encoding='utf-8') as f:
        f.write(views_sql)
    artifacts_created.append(str(views_file))

    # Generate Datasphere model JSON (CSN format - Core Schema Notation)
    model_json = _generate_datasphere_model(cim, data_foundation, business_layer)
    model_file = datasphere_dir / "model.json"
    with open(model_file, 'w', encoding='utf-8') as f:
        json.dump(model_json, f, indent=2)
    artifacts_created.append(str(model_file))

    return {
        "status": "success",
        "universe_id": universe_id,
        "artifacts": artifacts_created,
        "views_count": len(data_foundation.get("tables", [])) + len(business_layer.get("dimensions", [])),
    }


def _generate_views_sql(data_foundation: Dict[str, Any], business_layer: Dict[str, Any]) -> str:
    """Generate SQL view definitions for Datasphere."""
    tables = data_foundation.get("tables", [])
    joins = data_foundation.get("joins", [])
    dimensions = business_layer.get("dimensions", [])
    measures = business_layer.get("measures", [])

    sql = []
    sql.append("-- Datasphere SQL Views Generated from BOBJ Universe")
    sql.append(f"-- Generated: {datetime.utcnow().isoformat()}Z")
    sql.append("")

    # Generate base table views
    for table in tables:
        if isinstance(table, dict):
            table_name = table.get("name", "")
        else:
            table_name = getattr(table, "name", "")

        if not table_name:
            continue

        sql.append(f"-- Base View: {table_name}")
        sql.append(f"CREATE VIEW \"V_{table_name}\" AS")

        # Get columns for this table
        columns = _get_table_columns(table_name, dimensions, measures)

        if columns:
            select_cols = ",\n    ".join([f"\"{col}\"" for col in columns])
            sql.append(f"SELECT\n    {select_cols}")
        else:
            sql.append("SELECT *")

        sql.append(f"FROM \"{table_name}\";")
        sql.append("")

    # Generate dimension views (with aggregations)
    for dim in dimensions:
        if isinstance(dim, dict):
            dim_name = dim.get("name", "")
            source_table = dim.get("source_table", "")
            source_column = dim.get("source_column", "")
        else:
            dim_name = getattr(dim, "name", "")
            source_table = getattr(dim, "source_table", "")
            source_column = getattr(dim, "source_column", "")

        if not (dim_name and source_table):
            continue

        view_name = f"V_DIM_{_sanitize_name(dim_name)}"
        sql.append(f"-- Dimension View: {dim_name}")
        sql.append(f"CREATE VIEW \"{view_name}\" AS")
        sql.append(f"SELECT DISTINCT")
        sql.append(f"    \"{source_column}\" AS \"{dim_name}\"")
        sql.append(f"FROM \"{source_table}\";")
        sql.append("")

    # Generate analytical views (dimensions + measures with joins)
    if joins and measures:
        sql.append("-- Analytical View (Combined)")
        sql.append("CREATE VIEW \"V_ANALYTICAL\" AS")

        # Build SELECT clause
        select_parts = []

        # Add dimensions
        for dim in dimensions:
            if isinstance(dim, dict):
                dim_name = dim.get("name", "")
                source_table = dim.get("source_table", "")
                source_column = dim.get("source_column", "")
            else:
                dim_name = getattr(dim, "name", "")
                source_table = getattr(dim, "source_table", "")
                source_column = getattr(dim, "source_column", "")

            if dim_name and source_table and source_column:
                table_alias = _get_table_alias(source_table, tables)
                select_parts.append(f"    {table_alias}.\"{source_column}\" AS \"{dim_name}\"")

        # Add measures
        for measure in measures:
            if isinstance(measure, dict):
                measure_name = measure.get("name", "")
                source_table = measure.get("source_table", "")
                source_column = measure.get("source_column", "")
                aggregation = measure.get("aggregation", "sum")
            else:
                measure_name = getattr(measure, "name", "")
                source_table = getattr(measure, "source_table", "")
                source_column = getattr(measure, "source_column", "")
                aggregation = getattr(measure, "aggregation", "sum")

            if measure_name and source_table and source_column:
                table_alias = _get_table_alias(source_table, tables)
                agg_func = aggregation.upper()
                select_parts.append(f"    {agg_func}({table_alias}.\"{source_column}\") AS \"{measure_name}\"")

        sql.append("SELECT")
        sql.append(",\n".join(select_parts))

        # Build FROM clause with joins
        if tables:
            first_table = tables[0]
            if isinstance(first_table, dict):
                first_table_name = first_table.get("name", "")
            else:
                first_table_name = getattr(first_table, "name", "")

            sql.append(f"FROM \"{first_table_name}\" AS T1")

            # Add joins
            for i, join in enumerate(joins):
                if isinstance(join, dict):
                    right_table = join.get("right_table", "")
                    left_column = join.get("left_column", "")
                    right_column = join.get("right_column", "")
                    join_type = join.get("join_type", "inner")
                else:
                    right_table = getattr(join, "right_table", "")
                    left_column = getattr(join, "left_column", "")
                    right_column = getattr(join, "right_column", "")
                    join_type = getattr(join, "join_type", "inner")

                join_keyword = _map_join_type(join_type)
                table_num = i + 2
                sql.append(f"{join_keyword} \"{right_table}\" AS T{table_num}")
                sql.append(f"    ON T1.\"{left_column}\" = T{table_num}.\"{right_column}\"")

        # Add GROUP BY for measures
        if measures and dimensions:
            dim_columns = []
            for dim in dimensions:
                if isinstance(dim, dict):
                    dim_name = dim.get("name", "")
                else:
                    dim_name = getattr(dim, "name", "")
                if dim_name:
                    dim_columns.append(f"\"{dim_name}\"")

            if dim_columns:
                sql.append("GROUP BY " + ", ".join(dim_columns))

        sql.append(";")
        sql.append("")

    return "\n".join(sql)


def _generate_datasphere_model(cim: Dict[str, Any], data_foundation: Dict[str, Any], business_layer: Dict[str, Any]) -> Dict[str, Any]:
    """Generate Datasphere model in CSN (Core Schema Notation) format."""
    universe_id = cim.get("universe_id", "unknown")
    universe_name = cim.get("universe_name", universe_id)

    model = {
        "namespace": f"bobj.{_sanitize_name(universe_id)}",
        "version": "1.0",
        "meta": {
            "creator": "BOBJ Migration Tool",
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "sourceSystem": "BusinessObjects",
            "sourceFormat": cim.get("source_format", "unknown"),
        },
        "definitions": {}
    }

    # Add entity definitions (tables)
    tables = data_foundation.get("tables", [])
    for table in tables:
        if isinstance(table, dict):
            table_name = table.get("name", "")
        else:
            table_name = getattr(table, "name", "")

        if not table_name:
            continue

        entity_key = f"Entity_{table_name}"
        model["definitions"][entity_key] = {
            "kind": "entity",
            "elements": _get_entity_elements(table_name, business_layer)
        }

    # Add view definitions
    dimensions = business_layer.get("dimensions", [])
    measures = business_layer.get("measures", [])

    if dimensions or measures:
        model["definitions"]["AnalyticalView"] = {
            "kind": "view",
            "projection": {
                "from": {"ref": [f"Entity_{tables[0].get('name') if isinstance(tables[0], dict) else getattr(tables[0], 'name', '')}"]},
                "columns": [
                    {"ref": [dim.get("name") if isinstance(dim, dict) else getattr(dim, "name", "")]}
                    for dim in dimensions if (dim.get("name") if isinstance(dim, dict) else getattr(dim, "name", ""))
                ]
            }
        }

    return model


def _get_table_columns(table_name: str, dimensions: List, measures: List) -> List[str]:
    """Get column names for a table."""
    columns = []

    for dim in dimensions:
        if isinstance(dim, dict):
            source_table = dim.get("source_table", "")
            source_column = dim.get("source_column", "")
        else:
            source_table = getattr(dim, "source_table", "")
            source_column = getattr(dim, "source_column", "")

        if source_table == table_name and source_column:
            columns.append(source_column)

    for measure in measures:
        if isinstance(measure, dict):
            source_table = measure.get("source_table", "")
            source_column = measure.get("source_column", "")
        else:
            source_table = getattr(measure, "source_table", "")
            source_column = getattr(measure, "source_column", "")

        if source_table == table_name and source_column:
            columns.append(source_column)

    return columns


def _get_entity_elements(table_name: str, business_layer: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """Get entity element definitions for CSN format."""
    elements = {}

    dimensions = business_layer.get("dimensions", [])
    measures = business_layer.get("measures", [])

    for dim in dimensions:
        if isinstance(dim, dict):
            source_table = dim.get("source_table", "")
            dim_name = dim.get("name", "")
            data_type = dim.get("data_type", "string")
        else:
            source_table = getattr(dim, "source_table", "")
            dim_name = getattr(dim, "name", "")
            data_type = getattr(dim, "data_type", "string")

        if source_table == table_name and dim_name:
            elements[dim_name] = {
                "type": _map_csn_type(data_type)
            }

    for measure in measures:
        if isinstance(measure, dict):
            source_table = measure.get("source_table", "")
            measure_name = measure.get("name", "")
            data_type = measure.get("data_type", "number")
        else:
            source_table = getattr(measure, "source_table", "")
            measure_name = getattr(measure, "name", "")
            data_type = getattr(measure, "data_type", "number")

        if source_table == table_name and measure_name:
            elements[measure_name] = {
                "type": _map_csn_type(data_type)
            }

    return elements


def _get_table_alias(table_name: str, tables: List) -> str:
    """Get SQL alias for a table."""
    for i, table in enumerate(tables):
        if isinstance(table, dict):
            t_name = table.get("name", "")
        else:
            t_name = getattr(table, "name", "")

        if t_name == table_name:
            return f"T{i+1}"

    return "T1"


def _sanitize_name(name: str) -> str:
    """Sanitize name for SQL/CSN identifiers."""
    return "".join(c if c.isalnum() or c == '_' else '_' for c in name).upper()


def _map_join_type(join_type: str) -> str:
    """Map join type to SQL keyword."""
    join_map = {
        "inner": "INNER JOIN",
        "left": "LEFT OUTER JOIN",
        "right": "RIGHT OUTER JOIN",
        "full": "FULL OUTER JOIN",
        "left outer": "LEFT OUTER JOIN",
        "right outer": "RIGHT OUTER JOIN",
        "full outer": "FULL OUTER JOIN",
    }
    return join_map.get(join_type.lower(), "INNER JOIN")


def _map_csn_type(data_type: str) -> str:
    """Map CIM data type to CSN type."""
    type_map = {
        "string": "cds.String",
        "number": "cds.Decimal",
        "integer": "cds.Integer",
        "decimal": "cds.Decimal",
        "date": "cds.Date",
        "datetime": "cds.Timestamp",
        "timestamp": "cds.Timestamp",
        "boolean": "cds.Boolean",
    }
    return type_map.get(data_type.lower(), "cds.String")
