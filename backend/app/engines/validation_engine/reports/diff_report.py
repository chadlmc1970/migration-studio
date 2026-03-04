"""
Diff Report Generator - generates semantic diff reports
"""
from typing import Dict, Any


class DiffReportGenerator:
    """Generates semantic difference reports"""

    def generate(self, semantic_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a semantic diff report.

        Args:
            semantic_results: Results from SemanticValidator

        Returns:
            Formatted diff report
        """
        report = {
            "summary": {
                "total_dimensions": semantic_results.get("dimensions_checked", 0),
                "missing_dimensions_count": len(semantic_results.get("missing_dimensions", [])),
                "total_measures": semantic_results.get("measures_checked", 0),
                "missing_measures_count": len(semantic_results.get("missing_measures", [])),
                "aggregation_mismatches_count": len(semantic_results.get("aggregation_mismatches", []))
            },
            "missing_dimensions": semantic_results.get("missing_dimensions", []),
            "missing_measures": semantic_results.get("missing_measures", []),
            "aggregation_mismatches": semantic_results.get("aggregation_mismatches", []),
            "status": self._compute_status(semantic_results)
        }

        return report

    def _compute_status(self, results: Dict[str, Any]) -> str:
        """Compute overall status"""
        missing_dims = len(results.get("missing_dimensions", []))
        missing_measures = len(results.get("missing_measures", []))
        agg_mismatches = len(results.get("aggregation_mismatches", []))

        if missing_dims == 0 and missing_measures == 0 and agg_mismatches == 0:
            return "PASS"
        elif missing_dims > 0 or missing_measures > 0:
            return "FAIL"
        else:
            return "WARNING"
