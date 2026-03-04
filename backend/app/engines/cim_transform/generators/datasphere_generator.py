"""Datasphere SQL Generator"""
from pathlib import Path
from ..loaders.cim_loader import CIMModel


def generate_datasphere_views(cim: CIMModel, output_dir: Path) -> str:
    """Generate Datasphere SQL views"""

    sql_parts = []
    sql_parts.append(f"-- Datasphere Views for {cim.universe.name}")
    sql_parts.append(f"-- Generated from CIM: {cim.universe.id}\n")

    # Individual table views
    for table in cim.tables:
        sql_parts.append(f"CREATE VIEW {table.name}_VIEW AS")
        sql_parts.append(f"SELECT * FROM {table.name};")
        sql_parts.append("")

    # Semantic view with all joins
    if len(cim.tables) > 0 and len(cim.joins) > 0:
        sql_parts.append(f"-- Combined Semantic View")
        sql_parts.append(f"CREATE VIEW {cim.universe.id.upper()}_SEMANTIC_VIEW AS")
        sql_parts.append("SELECT")

        # Add dimensions
        dim_cols = []
        for dim in cim.dimensions:
            dim_cols.append(f"  {dim.table}.{dim.column} AS {dim.name.replace(' ', '_')}")

        # Add measures
        measure_cols = []
        for measure in cim.measures:
            measure_cols.append(f"  {measure.aggregation}({measure.table}.{measure.column}) AS {measure.name.replace(' ', '_')}")

        all_cols = dim_cols + measure_cols
        sql_parts.append(",\n".join(all_cols))

        # FROM clause
        if cim.tables:
            sql_parts.append(f"FROM {cim.tables[0].name}")

        # JOIN clauses
        for join in cim.joins:
            join_type = join.type.upper()
            sql_parts.append(f"{join_type} JOIN {join.right_table}")
            sql_parts.append(f"  ON {join.condition}")

        # GROUP BY dimensions
        if dim_cols:
            group_by = [f"{dim.table}.{dim.column}" for dim in cim.dimensions]
            sql_parts.append(f"GROUP BY {', '.join(group_by)}")

        sql_parts.append(";")

    sql_content = "\n".join(sql_parts)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "views.sql"

    with open(output_file, 'w') as f:
        f.write(sql_content)

    return sql_content
