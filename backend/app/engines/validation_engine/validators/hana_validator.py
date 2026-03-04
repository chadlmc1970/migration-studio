"""
HANA Schema Validator

Validates HANA SQL schemas for:
- SQL syntax correctness
- Table definition completeness
- Data type validity
- Primary key presence
"""

import re
import sqlparse
from typing import Dict, Any, List
from pathlib import Path


class HANAValidator:
    """Validates HANA schema SQL files"""

    def validate(self, hana_schema_path: Path) -> Dict[str, Any]:
        """
        Validate HANA schema SQL file.

        Returns:
            {
                "status": "pass" | "fail" | "warning",
                "errors": [],
                "warnings": [],
                "checks": {
                    "syntax_valid": bool,
                    "tables_defined": bool,
                    "data_types_valid": bool,
                    "primary_keys_present": bool
                }
            }
        """
        result = {
            "status": "pass",
            "errors": [],
            "warnings": [],
            "checks": {},
            "stats": {
                "tables": 0,
                "views": 0,
                "statements": 0
            }
        }

        # Check if file exists
        if not hana_schema_path.exists():
            result["status"] = "fail"
            result["errors"].append(f"HANA schema file not found: {hana_schema_path}")
            return result

        # Load SQL file
        try:
            with open(hana_schema_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
        except Exception as e:
            result["status"] = "fail"
            result["errors"].append(f"Failed to load HANA schema: {e}")
            return result

        # Run validation checks
        result["checks"]["syntax_valid"] = self._validate_syntax(sql_content, result)
        result["checks"]["tables_defined"] = self._validate_tables(sql_content, result)
        result["checks"]["data_types_valid"] = self._validate_data_types(sql_content, result)
        result["checks"]["primary_keys_present"] = self._validate_primary_keys(sql_content, result)

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
                result["warnings"].append("No SQL statements found in schema file")
                return True

            # Check for basic syntax errors
            for stmt in statements:
                if stmt.get_type() is None and str(stmt).strip() and not str(stmt).strip().startswith('--'):
                    result["warnings"].append(f"Unparseable statement: {str(stmt)[:50]}...")

            return True

        except Exception as e:
            result["errors"].append(f"SQL syntax error: {e}")
            return False

    def _validate_tables(self, sql: str, result: Dict[str, Any]) -> bool:
        """Validate table definitions."""
        # Find CREATE TABLE statements
        create_table_pattern = r'CREATE\s+(COLUMN\s+)?TABLE\s+"?(\w+)"?'
        tables = re.findall(create_table_pattern, sql, re.IGNORECASE)

        result["stats"]["tables"] = len(tables)

        if len(tables) == 0:
            result["warnings"].append("No CREATE TABLE statements found")
            return True

        # Check for empty table definitions
        empty_table_pattern = r'CREATE\s+(COLUMN\s+)?TABLE\s+"?(\w+)"?\s*\(\s*\)'
        empty_tables = re.findall(empty_table_pattern, sql, re.IGNORECASE)

        if empty_tables:
            result["errors"].append(f"Found {len(empty_tables)} table(s) with no columns")
            return False

        # Find CREATE VIEW statements
        create_view_pattern = r'CREATE\s+VIEW\s+"?(\w+)"?'
        views = re.findall(create_view_pattern, sql, re.IGNORECASE)
        result["stats"]["views"] = len(views)

        return True

    def _validate_data_types(self, sql: str, result: Dict[str, Any]) -> bool:
        """Validate HANA data types are valid."""
        valid_hana_types = [
            "INTEGER", "BIGINT", "SMALLINT", "TINYINT",
            "DECIMAL", "REAL", "DOUBLE",
            "VARCHAR", "NVARCHAR", "CHAR", "NCHAR",
            "CLOB", "NCLOB", "TEXT",
            "DATE", "TIME", "TIMESTAMP",
            "BOOLEAN",
            "VARBINARY", "BLOB",
            "ST_POINT", "ST_GEOMETRY"
        ]

        # Find column definitions
        column_pattern = r'"?\w+"?\s+(\w+)(?:\([\d,\s]+\))?'
        matches = re.findall(column_pattern, sql, re.IGNORECASE)

        invalid_types = []
        for match in matches:
            data_type = match.upper()
            # Check if it's a valid HANA type (base name)
            base_type = data_type.split('(')[0]
            if base_type not in valid_hana_types and base_type not in ['CREATE', 'TABLE', 'VIEW', 'COLUMN', 'AS', 'SELECT', 'FROM', 'WHERE']:
                if data_type not in invalid_types:
                    invalid_types.append(data_type)

        if invalid_types:
            result["warnings"].append(f"Potentially invalid HANA data types: {', '.join(invalid_types[:5])}")

        return True

    def _validate_primary_keys(self, sql: str, result: Dict[str, Any]) -> bool:
        """Check if tables have primary keys defined."""
        # This is a warning, not an error (primary keys are optional but recommended)

        # Find primary key definitions
        pk_pattern = r'PRIMARY\s+KEY'
        primary_keys = len(re.findall(pk_pattern, sql, re.IGNORECASE))

        tables_count = result["stats"].get("tables", 0)

        if tables_count > 0 and primary_keys == 0:
            result["warnings"].append("No primary keys defined (recommended for performance)")

        if primary_keys > 0 and primary_keys < tables_count:
            result["warnings"].append(f"Only {primary_keys}/{tables_count} tables have primary keys")

        return True
