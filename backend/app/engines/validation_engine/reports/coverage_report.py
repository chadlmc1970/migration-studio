"""
Coverage Report Generator - generates coverage reports
"""
from typing import Dict, Any


class CoverageReportGenerator:
    """Generates coverage reports"""

    def generate(self, coverage_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a coverage report.

        Args:
            coverage_results: Results from CoverageValidator

        Returns:
            Formatted coverage report
        """
        report = {
            "summary": {
                "table_coverage": coverage_results.get("table_coverage", 0.0),
                "dimension_coverage": coverage_results.get("dimension_coverage", 0.0),
                "measure_coverage": coverage_results.get("measure_coverage", 0.0),
                "join_coverage": coverage_results.get("join_coverage", 0.0),
                "overall_coverage": self._compute_overall_coverage(coverage_results)
            },
            "details": coverage_results.get("details", {}),
            "status": self._compute_status(coverage_results)
        }

        return report

    def _compute_overall_coverage(self, results: Dict[str, Any]) -> float:
        """Compute weighted overall coverage"""
        table_cov = results.get("table_coverage", 0.0)
        dim_cov = results.get("dimension_coverage", 0.0)
        measure_cov = results.get("measure_coverage", 0.0)
        join_cov = results.get("join_coverage", 0.0)

        # Weighted average (dimensions and measures weighted higher)
        weights = {
            "table": 0.2,
            "dimension": 0.3,
            "measure": 0.3,
            "join": 0.2
        }

        overall = (
            table_cov * weights["table"] +
            dim_cov * weights["dimension"] +
            measure_cov * weights["measure"] +
            join_cov * weights["join"]
        )

        return round(overall, 4)

    def _compute_status(self, results: Dict[str, Any]) -> str:
        """Compute overall status"""
        overall = self._compute_overall_coverage(results)

        if overall >= 0.95:
            return "EXCELLENT"
        elif overall >= 0.80:
            return "GOOD"
        elif overall >= 0.60:
            return "FAIR"
        else:
            return "POOR"
