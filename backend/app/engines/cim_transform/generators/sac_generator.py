"""SAC Model Generator"""
import json
from pathlib import Path
from ..loaders.cim_loader import CIMModel


def generate_sac_model(cim: CIMModel, output_dir: Path) -> dict:
    """Generate SAC semantic model JSON"""

    dimensions = []
    for dim in cim.dimensions:
        dimensions.append({
            "id": dim.name.replace(" ", "_").lower(),
            "name": dim.name,
            "sourceTable": dim.table,
            "sourceColumn": dim.column,
            "description": dim.description or ""
        })

    measures = []
    for measure in cim.measures:
        measures.append({
            "id": measure.name.replace(" ", "_").lower(),
            "name": measure.name,
            "sourceTable": measure.table,
            "sourceColumn": measure.column,
            "aggregation": measure.aggregation,
            "description": measure.description or ""
        })

    relationships = []
    for join in cim.joins:
        relationships.append({
            "leftTable": join.left_table,
            "rightTable": join.right_table,
            "type": join.type,
            "condition": join.condition
        })

    model = {
        "modelName": cim.universe.name,
        "modelId": cim.universe.id,
        "schemaVersion": "1.0",
        "dimensions": dimensions,
        "measures": measures,
        "relationships": relationships,
        "tables": [table.name for table in cim.tables]
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "model.json"

    with open(output_file, 'w') as f:
        json.dump(model, f, indent=2)

    return model
