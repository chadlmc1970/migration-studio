"""
Semantic Validator - validates semantic preservation of dimensions and measures
"""
from typing import Dict, Any, List, Optional
from loaders.cim_loader import CIM
from loaders.target_loader import Targets


class SemanticValidator:
    """Validates semantic preservation of business logic"""

    def validate(self, cim: CIM, targets: Optional[Targets]) -> Dict[str, Any]:
        """
        Validate that dimensions and measures are preserved.

        Returns:
            {
                "dimensions_checked": int,
                "missing_dimensions": [...],
                "measures_checked": int,
                "missing_measures": [...],
                "aggregation_mismatches": [...]
            }
        """
        if targets is None:
            return {
                "dimensions_checked": len(cim.dimensions),
                "missing_dimensions": [{"id": d.id, "name": d.name} for d in cim.dimensions],
                "measures_checked": len(cim.measures),
                "missing_measures": [{"id": m.id, "name": m.name} for m in cim.measures],
                "aggregation_mismatches": []
            }

        # Validate dimensions
        dimension_results = self._validate_dimensions(cim, targets)

        # Validate measures
        measure_results = self._validate_measures(cim, targets)

        return {
            "dimensions_checked": len(cim.dimensions),
            "missing_dimensions": dimension_results["missing"],
            "measures_checked": len(cim.measures),
            "missing_measures": measure_results["missing"],
            "aggregation_mismatches": measure_results["aggregation_mismatches"]
        }

    def _validate_dimensions(self, cim: CIM, targets: Targets) -> Dict[str, Any]:
        """Validate dimensions"""
        missing = []

        # Build target dimension lookup
        target_dimensions = {}

        if targets.sac_model:
            for dim in targets.sac_model.dimensions:
                dim_id = dim.get("id", "").upper()
                target_dimensions[dim_id] = dim

        # Also check Datasphere columns
        target_columns = set()
        for view in targets.datasphere_views:
            target_columns.update(c.upper() for c in view.columns)

        # Check each CIM dimension
        for dim in cim.dimensions:
            dim_id = dim.id.upper()

            # Check if dimension exists in targets
            if dim_id not in target_dimensions and dim_id not in target_columns:
                missing.append({
                    "id": dim.id,
                    "name": dim.name,
                    "table": dim.table,
                    "column": dim.column
                })

        return {
            "missing": missing
        }

    def _validate_measures(self, cim: CIM, targets: Targets) -> Dict[str, Any]:
        """Validate measures"""
        missing = []
        aggregation_mismatches = []

        # Build target measure lookup
        target_measures = {}

        if targets.sac_model:
            for measure in targets.sac_model.measures:
                measure_id = measure.get("id", "").upper()
                target_measures[measure_id] = measure

        # Also check Datasphere columns (approximation)
        target_columns = set()
        for view in targets.datasphere_views:
            target_columns.update(c.upper() for c in view.columns)

        # Check each CIM measure
        for measure in cim.measures:
            measure_id = measure.id.upper()

            # Check if measure exists
            if measure_id not in target_measures and measure_id not in target_columns:
                missing.append({
                    "id": measure.id,
                    "name": measure.name,
                    "expression": measure.expression,
                    "aggregation": measure.aggregation
                })
            elif measure_id in target_measures:
                # Check aggregation
                target_agg = target_measures[measure_id].get("aggregation", "").upper()
                cim_agg = measure.aggregation.upper()

                if target_agg and cim_agg and target_agg != cim_agg:
                    aggregation_mismatches.append({
                        "id": measure.id,
                        "name": measure.name,
                        "expected_aggregation": cim_agg,
                        "actual_aggregation": target_agg
                    })

        return {
            "missing": missing,
            "aggregation_mismatches": aggregation_mismatches
        }
