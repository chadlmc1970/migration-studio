"""
SAC Model Validator

Validates SAC model JSON for:
- Schema compliance
- Reference integrity
- Dimension/measure completeness
- Relationship validity
"""

import json
from typing import Dict, Any, List
from pathlib import Path


class SACValidator:
    """Validates SAC model artifacts"""

    def validate(self, sac_model_path: Path) -> Dict[str, Any]:
        """
        Validate SAC model JSON file.

        Returns:
            {
                "status": "pass" | "fail" | "warning",
                "errors": [],
                "warnings": [],
                "checks": {
                    "schema_valid": bool,
                    "dimensions_valid": bool,
                    "measures_valid": bool,
                    "relationships_valid": bool,
                    "data_sources_valid": bool
                }
            }
        """
        result = {
            "status": "pass",
            "errors": [],
            "warnings": [],
            "checks": {}
        }

        # Check if file exists
        if not sac_model_path.exists():
            result["status"] = "fail"
            result["errors"].append(f"SAC model file not found: {sac_model_path}")
            return result

        # Load SAC model
        try:
            with open(sac_model_path, 'r', encoding='utf-8') as f:
                model = json.load(f)
        except json.JSONDecodeError as e:
            result["status"] = "fail"
            result["errors"].append(f"Invalid JSON: {e}")
            return result
        except Exception as e:
            result["status"] = "fail"
            result["errors"].append(f"Failed to load SAC model: {e}")
            return result

        # Run validation checks
        result["checks"]["schema_valid"] = self._validate_schema(model, result)
        result["checks"]["data_sources_valid"] = self._validate_data_sources(model, result)
        result["checks"]["dimensions_valid"] = self._validate_dimensions(model, result)
        result["checks"]["measures_valid"] = self._validate_measures(model, result)
        result["checks"]["relationships_valid"] = self._validate_relationships(model, result)

        # Set overall status
        if result["errors"]:
            result["status"] = "fail"
        elif result["warnings"]:
            result["status"] = "warning"

        return result

    def _validate_schema(self, model: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """Validate SAC model schema (required fields)."""
        required_fields = ["modelId", "modelName", "dimensions", "measures"]

        for field in required_fields:
            if field not in model:
                result["errors"].append(f"Missing required field: {field}")
                return False

        # Check types
        if not isinstance(model.get("dimensions"), list):
            result["errors"].append("Field 'dimensions' must be a list")
            return False

        if not isinstance(model.get("measures"), list):
            result["errors"].append("Field 'measures' must be a list")
            return False

        return True

    def _validate_data_sources(self, model: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """Validate data source definitions."""
        data_sources = model.get("dataSources", [])

        if not data_sources:
            result["warnings"].append("No data sources defined")
            return True

        valid = True
        source_ids = set()

        for ds in data_sources:
            # Check required fields
            if "sourceId" not in ds:
                result["errors"].append("Data source missing 'sourceId'")
                valid = False
                continue

            source_id = ds["sourceId"]

            # Check for duplicates
            if source_id in source_ids:
                result["errors"].append(f"Duplicate data source ID: {source_id}")
                valid = False

            source_ids.add(source_id)

            # Check source name
            if "sourceName" not in ds:
                result["warnings"].append(f"Data source {source_id} missing 'sourceName'")

        return valid

    def _validate_dimensions(self, model: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """Validate dimension definitions."""
        dimensions = model.get("dimensions", [])

        if not dimensions:
            result["warnings"].append("No dimensions defined")
            return True

        valid = True
        dim_ids = set()
        data_source_ids = {ds.get("sourceId") for ds in model.get("dataSources", [])}

        for dim in dimensions:
            # Check required fields
            if "dimensionId" not in dim:
                result["errors"].append("Dimension missing 'dimensionId'")
                valid = False
                continue

            dim_id = dim["dimensionId"]

            # Check for duplicates
            if dim_id in dim_ids:
                result["errors"].append(f"Duplicate dimension ID: {dim_id}")
                valid = False

            dim_ids.add(dim_id)

            # Check dimension name
            if "dimensionName" not in dim:
                result["errors"].append(f"Dimension {dim_id} missing 'dimensionName'")
                valid = False

            # Check source table reference
            source_table = dim.get("sourceTable", "")
            if source_table and source_table not in data_source_ids:
                result["errors"].append(
                    f"Dimension {dim_id} references unknown data source: {source_table}"
                )
                valid = False

            # Check data type
            if "dataType" not in dim:
                result["warnings"].append(f"Dimension {dim_id} missing 'dataType'")

        return valid

    def _validate_measures(self, model: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """Validate measure definitions."""
        measures = model.get("measures", [])

        if not measures:
            result["warnings"].append("No measures defined")
            return True

        valid = True
        measure_ids = set()
        data_source_ids = {ds.get("sourceId") for ds in model.get("dataSources", [])}

        for measure in measures:
            # Check required fields
            if "measureId" not in measure:
                result["errors"].append("Measure missing 'measureId'")
                valid = False
                continue

            measure_id = measure["measureId"]

            # Check for duplicates
            if measure_id in measure_ids:
                result["errors"].append(f"Duplicate measure ID: {measure_id}")
                valid = False

            measure_ids.add(measure_id)

            # Check measure name
            if "measureName" not in measure:
                result["errors"].append(f"Measure {measure_id} missing 'measureName'")
                valid = False

            # Check aggregation
            if "aggregation" not in measure:
                result["errors"].append(f"Measure {measure_id} missing 'aggregation'")
                valid = False
            else:
                agg = measure["aggregation"]
                valid_aggs = ["SUM", "COUNT", "AVERAGE", "MIN", "MAX", "DISTINCT_COUNT"]
                if agg not in valid_aggs:
                    result["warnings"].append(
                        f"Measure {measure_id} has unknown aggregation: {agg}"
                    )

            # Check source table reference
            source_table = measure.get("sourceTable", "")
            if source_table and source_table not in data_source_ids:
                result["errors"].append(
                    f"Measure {measure_id} references unknown data source: {source_table}"
                )
                valid = False

            # Check data type
            if "dataType" not in measure:
                result["warnings"].append(f"Measure {measure_id} missing 'dataType'")

        return valid

    def _validate_relationships(self, model: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """Validate relationship definitions."""
        relationships = model.get("relationships", [])

        if not relationships:
            result["warnings"].append("No relationships defined")
            return True

        valid = True
        data_source_ids = {ds.get("sourceId") for ds in model.get("dataSources", [])}

        for rel in relationships:
            # Check required fields
            required = ["relationshipId", "fromTable", "toTable"]
            for field in required:
                if field not in rel:
                    result["errors"].append(f"Relationship missing '{field}'")
                    valid = False

            if not all(f in rel for f in required):
                continue

            rel_id = rel["relationshipId"]

            # Check table references
            from_table = rel["fromTable"]
            to_table = rel["toTable"]

            if from_table not in data_source_ids:
                result["errors"].append(
                    f"Relationship {rel_id} references unknown fromTable: {from_table}"
                )
                valid = False

            if to_table not in data_source_ids:
                result["errors"].append(
                    f"Relationship {rel_id} references unknown toTable: {to_table}"
                )
                valid = False

            # Check join type
            if "joinType" in rel:
                join_type = rel["joinType"]
                valid_joins = ["Inner", "Left Outer", "Right Outer", "Full Outer"]
                if join_type not in valid_joins:
                    result["warnings"].append(
                        f"Relationship {rel_id} has unknown join type: {join_type}"
                    )

        return valid
