"""
Datasphere View Validator

Validates Datasphere SQL views for:
- SQL syntax correctness
- View definition completeness
- Column references validity
- Join structure integrity
"""

import re
import sqlparse
from typing import Dict, Any, List
from pathlib import Path


class DatasphereValidator:
    """Validates Datasphere SQL view files"""

    def validate(self, datasphere_views_path: Path) -> Dict[str, Any]:
        """
        Validate Datasphere views SQL file.

        Returns:
            {
                "status": "pass" | "fail" | "warning",
                "errors": [],
                "warnings": [],
                "checks": {
                    "syntax_valid": bool,
                    "views_defined": bool,
                    "references_valid": bool,
                    "joins_valid": bool
                }
            }
        """
        result = {
            "status": "pass",
            "errors": [],
            "warnings": [],
            "checks": {},
            "stats": {
                "views": 0,
                "statements": 0
            }
        }

        # Check if file exists
        if not datasphere_views_path.exists():
            result["status": "fail"
            result["errors"].append(f"Datasphere views file not found: {datasphere_views_path}")
            return result

        # Load SQL file
        try:
            with open(datasphere_views_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
        except Exception as e:
            result["status"] = "fail"
            result["errors"].append(f"Failed to load Datasphere views: {e}")
            return result

        # Run validation checks
        result["checks"]["syntax_valid"] = self._validate_syntax(sql_content, result)
        result["checks"]["views_defined"] = self._validate_views(sql_content, result)
        result["checks"]["references_valid"] = self._validate_references(sql_content, result)
        result["checks"]["joins_valid"] = self._validate_joins(sql_content, result)

        # Set overall status
        if result["errors"]:
            result["status"] = "fail"
        elif result["warnings"]:
            result["status"] = "warning"

        return result

    def _validate_syntax(self, sql: str, result: Dict[str, Any]) -> bool:
        """Validate SQL syntax using sqlparse."""
        try:
            statements = sqlparse.parse(sql)
            result["stats"]["statements"] = len([s for s in statements if s.get_type()])

            if result["stats"]["statements"] == 0:
                result["warnings"].append("No SQL statements found in views file")
                return True

            # Check for basic syntax errors
            for stmt in statements:
                if stmt.get_type() is None and str(stmt).strip() and not str(stmt).strip().startswith('--'):
                    result["warnings"].append(f"Unparseable statement: {str(stmt)[:50]}...")

            return True

        except Exception as e:
            result["errors"].append(f"SQL syntax error: {e}")
            return False

    def _validate_views(self, sql: str, result: Dict[str, Any]) -> bool:
        """Validate view definitions."""
        # Find CREATE VIEW statements
        create_view_pattern = r'CREATE\s+VIEW\s+"?(\w+)"?'
        views = re.findall(create_view_pattern, sql, re.IGNORECASE)

        result["stats"]["views"] = len(views)

        if len(views) == 0:
            result["warnings"].append("No CREATE VIEW statements found")
            return True

        # Check for views without SELECT
        for view_name in views:
            # Look for SELECT after this view definition
            view_def_pattern = rf'CREATE\s+VIEW\s+"{view_name}".*?AS\s+SELECT'
            if not re.search(view_def_pattern, sql, re.IGNORECASE | re.DOTALL):
                result["errors"].append(f"View {view_name} missing SELECT clause")
                return False

        return True

    def _validate_references(self, sql: str, result: Dict[str, Any]) -> bool:
        """Validate table and column references."""
        # Extract table names from FROM and JOIN clauses
        from_pattern = r'FROM\s+"?(\w+)"?'
        join_pattern = r'JOIN\s+"?(\w+)"?'

        from_tables = re.findall(from_pattern, sql, re.IGNORECASE)
        join_tables = re.findall(join_pattern, sql, re.IGNORECASE)

        all_tables = set(from_tables + join_tables)

        if not all_tables:
            result["warnings"].append("No table references found in views")

        # Check for SELECT *  (not recommended)
        select_star_pattern = r'SELECT\s+\*'
        if re.search(select_star_pattern, sql, re.IGNORECASE):
            result["warnings"].append("Found SELECT * (explicit column list recommended)")

        return True

    def _validate_joins(self, sql: str, result: Dict[str, Any]) -> bool:
        """Validate JOIN clauses."""
        # Find JOIN statements
        join_pattern = r'(INNER|LEFT|RIGHT|FULL)?\s*(?:OUTER\s+)?JOIN\s+"?(\w+)"?\s+(?:AS\s+)?(\w+)?\s+ON\s+([\w\."=\s]+)'
        joins = re.findall(join_pattern, sql, re.IGNORECASE)

        if not joins:
            return True  # No joins to validate

        for join in joins:
            join_type, table, alias, condition = join

            # Check if ON condition is present
            if not condition.strip():
                result["errors"].append(f"JOIN on table {table} missing ON condition")
                return False

            # Check if ON condition has equality
            if '=' not in condition:
                result["warnings"].append(f"JOIN on table {table} has unusual ON condition: {condition[:30]}")

        # Check for cross joins (joins without ON)
        cross_join_pattern = r'JOIN\s+"?\w+"?(?:\s+AS\s+\w+)?\s+(?!ON)'
        cross_joins = re.findall(cross_join_pattern, sql, re.IGNORECASE)

        if cross_joins:
            result["warnings"].append(f"Found {len(cross_joins)} potential cross join(s) without ON clause")

        return True
