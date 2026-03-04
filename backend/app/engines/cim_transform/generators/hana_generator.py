"""HANA Schema Generator"""
from pathlib import Path
from ..loaders.cim_loader import CIMModel


def generate_hana_schema(cim: CIMModel, output_dir: Path) -> str:
    """Generate HANA schema SQL"""

    sql_parts = []
    sql_parts.append(f"-- HANA Schema for {cim.universe.name}")
    sql_parts.append(f"-- Generated from CIM: {cim.universe.id}\n")

    # Generate simple table schemas
    for table in cim.tables:
        sql_parts.append(f"-- Table: {table.name}")
        sql_parts.append(f"CREATE COLUMN TABLE {table.name} (")

        # Collect columns from dimensions and measures
        columns = set()

        for dim in cim.dimensions:
            if dim.table == table.name:
                columns.add((dim.column, "NVARCHAR(255)"))

        for measure in cim.measures:
            if measure.table == table.name:
                col_type = "DECIMAL(15,2)" if measure.aggregation in ["SUM", "AVG"] else "INTEGER"
                columns.add((measure.column, col_type))

        # Add primary key if this is a reference table
        if table.name in ["CUSTOMERS", "PRODUCTS"]:
            columns.add(("ID", "INTEGER PRIMARY KEY"))

        # If no columns detected, add generic ones
        if not columns:
            columns = {
                ("ID", "INTEGER PRIMARY KEY"),
                ("NAME", "NVARCHAR(255)"),
                ("CREATED_AT", "TIMESTAMP")
            }

        col_defs = [f"  {col} {dtype}" for col, dtype in sorted(columns)]
        sql_parts.append(",\n".join(col_defs))
        sql_parts.append(");\n")

    sql_content = "\n".join(sql_parts)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "schema.sql"

    with open(output_file, 'w') as f:
        f.write(sql_content)

    return sql_content
