"""
CIM Loader - loads Common Information Model files
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class CIMMetadata(BaseModel):
    universe_id: str
    universe_name: str
    version: str = "1.0"
    extracted_at: str = ""


class CIMTable(BaseModel):
    id: str
    name: str
    table_schema: Optional[str] = Field(default="", alias="schema")
    columns: list = Field(default_factory=list)

    class Config:
        populate_by_name = True


class CIMDimension(BaseModel):
    id: str
    name: str
    table: str
    column: str
    type: str = "dimension"


class CIMMeasure(BaseModel):
    id: str
    name: str
    expression: str
    aggregation: str
    type: str = "measure"


class CIMJoin(BaseModel):
    id: str
    left_table: str
    right_table: str
    left_column: str = ""
    right_column: str = ""
    join_type: str
    cardinality: str = "N:1"


class CIM(BaseModel):
    """Common Information Model representation"""
    metadata: CIMMetadata
    tables: list[CIMTable] = Field(default_factory=list)
    dimensions: list[CIMDimension] = Field(default_factory=list)
    measures: list[CIMMeasure] = Field(default_factory=list)
    joins: list[CIMJoin] = Field(default_factory=list)


class CIMLoader:
    """Loads CIM files from JSON"""

    def load(self, cim_path: Path) -> CIM:
        """Load CIM from file path"""
        with open(cim_path, "r") as f:
            data = json.load(f)

        # Normalize to expected format
        normalized = self._normalize_cim(data)
        return CIM(**normalized)

    def load_from_dict(self, data: Dict[str, Any]) -> CIM:
        """Load CIM from dictionary"""
        normalized = self._normalize_cim(data)
        return CIM(**normalized)

    def _normalize_cim(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize CIM data to expected format.
        Handles multiple CIM schemas.
        """
        # Check if this is legacy format (has schema_version, universe)
        if "schema_version" in data and "universe" in data:
            return self._normalize_legacy_format(data)

        # Otherwise assume standard format
        return data

    def _normalize_legacy_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize legacy CIM format"""
        universe_info = data.get("universe", {})

        # Build metadata
        metadata = {
            "universe_id": universe_info.get("id", "unknown"),
            "universe_name": universe_info.get("name", "Unknown"),
            "version": data.get("schema_version", "0.1"),
            "extracted_at": ""
        }

        # Normalize tables
        tables = []
        for table in data.get("tables", []):
            tables.append({
                "id": table.get("name", ""),
                "name": table.get("name", ""),
                "schema": "",
                "columns": []
            })

        # Normalize dimensions
        dimensions = []
        for dim in data.get("dimensions", []):
            dim_id = self._make_id(dim.get("name", ""))
            dimensions.append({
                "id": dim_id,
                "name": dim.get("name", ""),
                "table": dim.get("table", ""),
                "column": dim.get("column", ""),
                "type": "dimension"
            })

        # Normalize measures
        measures = []
        for measure in data.get("measures", []):
            measure_id = self._make_id(measure.get("name", ""))
            expression = f"{measure.get('aggregation', 'SUM')}({measure.get('table', '')}.{measure.get('column', '')})"
            measures.append({
                "id": measure_id,
                "name": measure.get("name", ""),
                "expression": expression,
                "aggregation": measure.get("aggregation", "SUM"),
                "type": "measure"
            })

        # Normalize joins
        joins = []
        for join in data.get("joins", []):
            join_id = f"{join.get('left_table', '')}_{join.get('right_table', '')}"
            condition = join.get("condition", "")

            # Parse condition to extract columns (simple parsing)
            left_col, right_col = self._parse_join_condition(condition)

            joins.append({
                "id": join_id,
                "left_table": join.get("left_table", ""),
                "right_table": join.get("right_table", ""),
                "left_column": left_col,
                "right_column": right_col,
                "join_type": join.get("type", "INNER").upper(),
                "cardinality": "N:1"
            })

        return {
            "metadata": metadata,
            "tables": tables,
            "dimensions": dimensions,
            "measures": measures,
            "joins": joins
        }

    def _make_id(self, name: str) -> str:
        """Generate ID from name"""
        return name.upper().replace(" ", "_")

    def _parse_join_condition(self, condition: str) -> tuple[str, str]:
        """Parse join condition to extract column names"""
        if "=" in condition:
            parts = condition.split("=")
            if len(parts) == 2:
                left = parts[0].strip()
                right = parts[1].strip()

                # Extract column name (after dot)
                left_col = left.split(".")[-1] if "." in left else left
                right_col = right.split(".")[-1] if "." in right else right

                return left_col, right_col

        return "", ""
