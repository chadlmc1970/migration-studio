"""
HANA Schema Generator

Generates SAP HANA Cloud schemas and calculation views from CIM.

Outputs:
- hana/schema.sql: DDL for tables, views, primary keys
- hana/calculation_views/*.hdbcalculationview: Calculation views (XML format)
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


def generate_hana_schema(cim: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """
    Generate HANA schema from CIM.

    Args:
        cim: Canonical Intermediate Model (parsed JSON)
        output_dir: Output directory for HANA artifacts

    Returns:
        Generation report with status and artifacts created
    """
    hana_dir = output_dir / "hana"
    hana_dir.mkdir(parents=True, exist_ok=True)

    universe_id = cim.get("universe_id", "unknown")
    data_foundation = cim.get("data_foundation", {})
    business_layer = cim.get("business_layer", {})

    artifacts_created = []

    # Generate main schema DDL
    schema_sql = _generate_schema_ddl(data_foundation, business_layer)
    schema_file = hana_dir / "schema.sql"
    with open(schema_file, 'w', encoding='utf-8') as f:
        f.write(schema_sql)
    artifacts_created.append(str(schema_file))

    # Generate calculation views for measures/aggregations
    calc_views_dir = hana_dir / "calculation_views"
    calc_views_dir.mkdir(exist_ok=True)

    calc_views = _generate_calculation_views(business_layer, data_foundation, calc_views_dir)
    artifacts_created.extend(calc_views)

    return {
        "status": "success",
        "universe_id": universe_id,
        "artifacts": artifacts_created,
        "tables_count": len(data_foundation.get("tables", [])),
        "calc_views_count": len(calc_views),
    }


def _generate_schema_ddl(data_foundation: Dict[str, Any], business_layer: Dict[str, Any]) -> str:
    """Generate HANA DDL for tables and views."""
    tables = data_foundation.get("tables", [])
    joins = data_foundation.get("joins", [])

    ddl = []
    ddl.append("-- HANA Schema Generated from BOBJ Universe")
    ddl.append(f"-- Generated: {datetime.utcnow().isoformat()}Z")
    ddl.append("")

    # Generate CREATE TABLE statements
    for table in tables:
        if isinstance(table, dict):
            table_name = table.get("name", "")
        else:
            table_name = getattr(table, "name", "")

        if not table_name:
            continue

        ddl.append(f"-- Table: {table_name}")
        ddl.append(f"CREATE COLUMN TABLE \"{table_name}\" (")

        # Generate columns from dimensions and measures
        columns = _get_table_columns(table_name, business_layer)

        if columns:
            column_defs = []
            for col in columns:
                column_defs.append(f"    \"{col['name']}\" {col['type']}")
            ddl.append(",\n".join(column_defs))
        else:
            # Placeholder columns if no metadata available
            ddl.append("    \"ID\" INTEGER,")
            ddl.append("    \"VALUE\" NVARCHAR(255)")

        ddl.append(");")
        ddl.append("")

    # Generate views for joins
    if joins:
        ddl.append("-- Views for joined data")
        ddl.append("")

        for i, join in enumerate(joins):
            view_name = f"V_JOIN_{i+1}"
            ddl.append(_generate_join_view(join, view_name))
            ddl.append("")

    return "\n".join(ddl)


def _get_table_columns(table_name: str, business_layer: Dict[str, Any]) -> List[Dict[str, str]]:
    """Get columns for a table from dimensions and measures."""
    columns = []

    # Get dimensions for this table
    dimensions = business_layer.get("dimensions", [])
    for dim in dimensions:
        if isinstance(dim, dict):
            source_table = dim.get("source_table", "")
            col_name = dim.get("source_column", dim.get("name", ""))
            data_type = dim.get("data_type", "string")
        else:
            source_table = getattr(dim, "source_table", "")
            col_name = getattr(dim, "source_column", getattr(dim, "name", ""))
            data_type = getattr(dim, "data_type", "string")

        if source_table == table_name and col_name:
            columns.append({
                "name": col_name,
                "type": _map_hana_data_type(data_type)
            })

    # Get measures for this table
    measures = business_layer.get("measures", [])
    for measure in measures:
        if isinstance(measure, dict):
            source_table = measure.get("source_table", "")
            col_name = measure.get("source_column", measure.get("name", ""))
            data_type = measure.get("data_type", "number")
        else:
            source_table = getattr(measure, "source_table", "")
            col_name = getattr(measure, "source_column", getattr(measure, "name", ""))
            data_type = getattr(measure, "data_type", "number")

        if source_table == table_name and col_name:
            columns.append({
                "name": col_name,
                "type": _map_hana_data_type(data_type)
            })

    return columns


def _generate_join_view(join: Any, view_name: str) -> str:
    """Generate SQL view for a join."""
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

    join_keyword = _map_join_type_sql(join_type)

    sql = f"""CREATE VIEW \"{view_name}\" AS
SELECT
    L.*,
    R.*
FROM \"{left_table}\" AS L
{join_keyword} \"{right_table}\" AS R
    ON L.\"{left_column}\" = R.\"{right_column}\";"""

    return sql


def _generate_calculation_views(business_layer: Dict[str, Any], data_foundation: Dict[str, Any], output_dir: Path) -> List[str]:
    """Generate HANA calculation views for measures."""
    measures = business_layer.get("measures", [])
    calc_views = []

    for measure in measures:
        if isinstance(measure, dict):
            measure_name = measure.get("name", "")
            aggregation = measure.get("aggregation", "sum")
        else:
            measure_name = getattr(measure, "name", "")
            aggregation = getattr(measure, "aggregation", "sum")

        if not measure_name:
            continue

        # Generate calculation view XML
        calc_view_xml = _generate_calc_view_xml(measure, data_foundation)

        sanitized_name = "".join(c if c.isalnum() or c == '_' else '_' for c in measure_name)
        calc_view_file = output_dir / f"CV_{sanitized_name}.hdbcalculationview"

        with open(calc_view_file, 'w', encoding='utf-8') as f:
            f.write(calc_view_xml)

        calc_views.append(str(calc_view_file))

    return calc_views


def _generate_calc_view_xml(measure: Any, data_foundation: Dict[str, Any]) -> str:
    """Generate HANA calculation view XML (simplified)."""
    if isinstance(measure, dict):
        measure_name = measure.get("name", "")
        aggregation = measure.get("aggregation", "sum")
        source_table = measure.get("source_table", "")
        source_column = measure.get("source_column", "")
    else:
        measure_name = getattr(measure, "name", "")
        aggregation = getattr(measure, "aggregation", "sum")
        source_table = getattr(measure, "source_table", "")
        source_column = getattr(measure, "source_column", "")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Calculation:scenario xmlns:Calculation="http://www.sap.com/ndb/BiModelCalculation.ecore">
  <calculationViews>
    <calculationView xsi:type="Calculation:AggregationView" id="Aggregation_1">
      <viewAttributes>
        <viewAttribute id="{measure_name}" aggregationType="{aggregation.upper()}">
          <resourceUri>{source_table}</resourceUri>
        </viewAttribute>
      </viewAttributes>
      <input node="#{source_table}">
        <mapping xsi:type="Calculation:AttributeMapping" target="{measure_name}" source="{source_column}"/>
      </input>
    </calculationView>
  </calculationViews>
  <logicalModel id="{measure_name}_LogicalModel">
    <attributes>
      <attribute id="{measure_name}" order="1" displayAttribute="false" attributeHierarchyActive="false">
        <keyMapping columnObjectName="Aggregation_1" columnName="{measure_name}"/>
      </attribute>
    </attributes>
  </logicalModel>
</Calculation:scenario>
"""
    return xml


def _map_hana_data_type(data_type: str) -> str:
    """Map CIM data type to HANA data type."""
    type_map = {
        "string": "NVARCHAR(255)",
        "text": "NVARCHAR(5000)",
        "number": "DECIMAL(15,2)",
        "integer": "INTEGER",
        "decimal": "DECIMAL(15,2)",
        "date": "DATE",
        "datetime": "TIMESTAMP",
        "timestamp": "TIMESTAMP",
        "boolean": "BOOLEAN",
    }
    return type_map.get(data_type.lower(), "NVARCHAR(255)")


def _map_join_type_sql(join_type: str) -> str:
    """Map CIM join type to SQL join keyword."""
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
