"""
Coverage Validator - validates transformation coverage
"""
from typing import Dict, Any, Optional
from loaders.cim_loader import CIM
from loaders.target_loader import Targets


class CoverageValidator:
    """Validates coverage of CIM elements in generated targets"""

    def validate(self, cim: CIM, targets: Optional[Targets]) -> Dict[str, Any]:
        """
        Compute coverage metrics for dimensions, measures, joins, and tables.

        Returns:
            {
                "table_coverage": 0.0-1.0,
                "dimension_coverage": 0.0-1.0,
                "measure_coverage": 0.0-1.0,
                "join_coverage": 0.0-1.0,
                "details": {...}
            }
        """
        if targets is None:
            return {
                "table_coverage": 0.0,
                "dimension_coverage": 0.0,
                "measure_coverage": 0.0,
                "join_coverage": 0.0,
                "details": {
                    "error": "No targets available"
                }
            }

        # Compute individual coverages
        table_coverage = self._compute_table_coverage(cim, targets)
        dimension_coverage = self._compute_dimension_coverage(cim, targets)
        measure_coverage = self._compute_measure_coverage(cim, targets)
        join_coverage = self._compute_join_coverage(cim, targets)

        return {
            "table_coverage": table_coverage["coverage"],
            "dimension_coverage": dimension_coverage["coverage"],
            "measure_coverage": measure_coverage["coverage"],
            "join_coverage": join_coverage["coverage"],
            "details": {
                "tables": table_coverage,
                "dimensions": dimension_coverage,
                "measures": measure_coverage,
                "joins": join_coverage
            }
        }

    def _compute_table_coverage(self, cim: CIM, targets: Targets) -> Dict[str, Any]:
        """Compute table coverage"""
        cim_tables = {t.name.upper() for t in cim.tables}

        if not cim_tables:
            return {"coverage": 1.0, "total": 0, "found": 0, "missing": []}

        # Collect all tables from targets
        target_tables = set()

        # From Datasphere views
        for view in targets.datasphere_views:
            target_tables.update(t.upper() for t in view.tables)

        # From HANA schema
        if targets.hana_schema:
            target_tables.update(t.upper() for t in targets.hana_schema.tables)

        # Compute coverage
        found_tables = cim_tables & target_tables
        missing_tables = cim_tables - target_tables

        coverage = len(found_tables) / len(cim_tables) if cim_tables else 1.0

        return {
            "coverage": coverage,
            "total": len(cim_tables),
            "found": len(found_tables),
            "missing": sorted(list(missing_tables))
        }

    def _compute_dimension_coverage(self, cim: CIM, targets: Targets) -> Dict[str, Any]:
        """Compute dimension coverage"""
        cim_dimensions = {d.id.upper() for d in cim.dimensions}

        if not cim_dimensions:
            return {"coverage": 1.0, "total": 0, "found": 0, "missing": []}

        # Collect dimensions from SAC model
        target_dimensions = set()

        if targets.sac_model:
            target_dimensions.update(d.get("id", "").upper() for d in targets.sac_model.dimensions)

        # Also check column names in Datasphere views
        for view in targets.datasphere_views:
            target_dimensions.update(c.upper() for c in view.columns)

        # Compute coverage
        found_dimensions = cim_dimensions & target_dimensions
        missing_dimensions = cim_dimensions - target_dimensions

        coverage = len(found_dimensions) / len(cim_dimensions) if cim_dimensions else 1.0

        return {
            "coverage": coverage,
            "total": len(cim_dimensions),
            "found": len(found_dimensions),
            "missing": sorted(list(missing_dimensions))
        }

    def _compute_measure_coverage(self, cim: CIM, targets: Targets) -> Dict[str, Any]:
        """Compute measure coverage"""
        cim_measures = {m.id.upper() for m in cim.measures}

        if not cim_measures:
            return {"coverage": 1.0, "total": 0, "found": 0, "missing": []}

        # Collect measures from SAC model
        target_measures = set()

        if targets.sac_model:
            target_measures.update(m.get("id", "").upper() for m in targets.sac_model.measures)

        # Also check column names in Datasphere views
        for view in targets.datasphere_views:
            target_measures.update(c.upper() for c in view.columns)

        # Compute coverage
        found_measures = cim_measures & target_measures
        missing_measures = cim_measures - target_measures

        coverage = len(found_measures) / len(cim_measures) if cim_measures else 1.0

        return {
            "coverage": coverage,
            "total": len(cim_measures),
            "found": len(found_measures),
            "missing": sorted(list(missing_measures))
        }

    def _compute_join_coverage(self, cim: CIM, targets: Targets) -> Dict[str, Any]:
        """Compute join coverage"""
        cim_joins = {
            f"{j.left_table.upper()}_{j.right_table.upper()}"
            for j in cim.joins
        }

        if not cim_joins:
            return {"coverage": 1.0, "total": 0, "found": 0, "missing": []}

        # Collect joins from Datasphere views
        target_joins = set()

        for view in targets.datasphere_views:
            for join in view.joins:
                right_table = join.get("right_table", "").upper()
                # Approximate: we don't have left table easily, so check if right table is in view
                if right_table:
                    for table in view.tables:
                        if table.upper() != right_table:
                            target_joins.add(f"{table.upper()}_{right_table}")

        # Compute coverage
        found_joins = cim_joins & target_joins
        missing_joins = cim_joins - target_joins

        # More lenient: if we found any joins and CIM has joins, give partial credit
        if not target_joins and cim_joins:
            coverage = 0.0
        elif not cim_joins:
            coverage = 1.0
        else:
            coverage = len(found_joins) / len(cim_joins)

        return {
            "coverage": coverage,
            "total": len(cim_joins),
            "found": len(found_joins),
            "missing": sorted(list(missing_joins))
        }
