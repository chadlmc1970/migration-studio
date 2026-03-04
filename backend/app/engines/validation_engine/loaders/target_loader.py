"""
Target Loader - loads generated SAC/Datasphere/HANA artifacts
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import sqlparse


class SACModel(BaseModel):
    """SAC Model representation"""
    modelId: str
    dimensions: list[Dict[str, Any]] = Field(default_factory=list)
    measures: list[Dict[str, Any]] = Field(default_factory=list)


class DatasphereView(BaseModel):
    """Datasphere SQL view"""
    name: str
    sql: str
    tables: list[str] = Field(default_factory=list)
    columns: list[str] = Field(default_factory=list)
    joins: list[Dict[str, Any]] = Field(default_factory=list)


class HANASchema(BaseModel):
    """HANA schema definition"""
    name: str
    sql: str
    tables: list[str] = Field(default_factory=list)


class Targets(BaseModel):
    """Container for all generated targets"""
    sac_model: Optional[SACModel] = None
    datasphere_views: list[DatasphereView] = Field(default_factory=list)
    hana_schema: Optional[HANASchema] = None


class TargetLoader:
    """Loads generated target artifacts"""

    def load(self, targets_path: Path) -> Targets:
        """Load all targets from directory"""
        targets = Targets()

        # Load SAC model
        sac_path = targets_path / "sac" / "model.json"
        if sac_path.exists():
            with open(sac_path, "r") as f:
                sac_data = json.load(f)
                targets.sac_model = SACModel(**sac_data)

        # Load Datasphere views
        datasphere_dir = targets_path / "datasphere"
        if datasphere_dir.exists():
            for sql_file in datasphere_dir.glob("*.sql"):
                view = self._parse_sql_view(sql_file)
                if view:
                    targets.datasphere_views.append(view)

        # Load HANA schema
        hana_path = targets_path / "hana" / "schema.sql"
        if hana_path.exists():
            with open(hana_path, "r") as f:
                sql = f.read()
                targets.hana_schema = HANASchema(
                    name="default",
                    sql=sql,
                    tables=self._extract_tables_from_sql(sql)
                )

        return targets

    def _parse_sql_view(self, sql_file: Path) -> Optional[DatasphereView]:
        """Parse SQL file to extract view information"""
        with open(sql_file, "r") as f:
            sql = f.read()

        if not sql.strip():
            return None

        # Parse SQL
        parsed = sqlparse.parse(sql)
        if not parsed:
            return None

        statement = parsed[0]

        # Extract view name
        view_name = self._extract_view_name(statement)

        # Extract tables
        tables = self._extract_tables_from_sql(sql)

        # Extract columns
        columns = self._extract_columns_from_sql(sql)

        # Extract joins
        joins = self._extract_joins_from_sql(sql)

        return DatasphereView(
            name=view_name or sql_file.stem,
            sql=sql,
            tables=tables,
            columns=columns,
            joins=joins
        )

    def _extract_view_name(self, statement) -> Optional[str]:
        """Extract view name from CREATE VIEW statement"""
        tokens = [t for t in statement.flatten() if not t.is_whitespace]

        for i, token in enumerate(tokens):
            if token.ttype is None and token.value.upper() == "VIEW":
                if i + 1 < len(tokens):
                    next_token = tokens[i + 1]
                    if next_token.ttype is None:
                        return next_token.value
        return None

    def _extract_tables_from_sql(self, sql: str) -> list[str]:
        """Extract table names from SQL"""
        tables = set()
        sql_upper = sql.upper()

        # Simple pattern matching for FROM and JOIN clauses
        keywords = ["FROM", "JOIN"]

        for keyword in keywords:
            parts = sql_upper.split(keyword)
            for part in parts[1:]:  # Skip first part (before first keyword)
                # Get first token after keyword
                tokens = part.strip().split()
                if tokens:
                    table_name = tokens[0].strip("(),;")
                    # Remove alias if present
                    if " " in table_name:
                        table_name = table_name.split()[0]
                    if table_name and not table_name.upper() in ["SELECT", "WHERE", "GROUP", "ORDER"]:
                        tables.add(table_name)

        return sorted(list(tables))

    def _extract_columns_from_sql(self, sql: str) -> list[str]:
        """Extract column names from SELECT clause"""
        columns = []

        parsed = sqlparse.parse(sql)
        if not parsed:
            return columns

        statement = parsed[0]

        # Find SELECT token
        in_select = False
        for token in statement.tokens:
            if token.ttype is sqlparse.tokens.DML and token.value.upper() == "SELECT":
                in_select = True
                continue

            if in_select:
                if token.ttype is sqlparse.tokens.Keyword and token.value.upper() in ["FROM", "WHERE"]:
                    break

                if isinstance(token, sqlparse.sql.IdentifierList):
                    for identifier in token.get_identifiers():
                        col_name = self._extract_column_name(str(identifier))
                        if col_name:
                            columns.append(col_name)
                elif isinstance(token, sqlparse.sql.Identifier):
                    col_name = self._extract_column_name(str(token))
                    if col_name:
                        columns.append(col_name)

        return columns

    def _extract_column_name(self, identifier: str) -> Optional[str]:
        """Extract column name from identifier (handle aliases)"""
        identifier = identifier.strip()

        # Handle "column AS alias"
        if " AS " in identifier.upper():
            parts = identifier.upper().split(" AS ")
            return parts[1].strip()

        # Handle "table.column"
        if "." in identifier:
            parts = identifier.split(".")
            return parts[-1].strip()

        return identifier

    def _extract_joins_from_sql(self, sql: str) -> list[Dict[str, Any]]:
        """Extract join information from SQL"""
        joins = []

        sql_upper = sql.upper()

        # Find JOIN clauses
        join_types = ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN", "JOIN"]

        for join_type in join_types:
            if join_type in sql_upper:
                # Simple extraction (not perfect but works for basic cases)
                parts = sql_upper.split(join_type)
                for i in range(1, len(parts)):
                    part = parts[i]

                    # Extract table
                    tokens = part.strip().split()
                    if not tokens:
                        continue

                    right_table = tokens[0].strip("(),;")

                    # Look for ON clause
                    if " ON " in part:
                        on_clause = part.split(" ON ")[1].split("WHERE")[0].split("GROUP")[0]
                        on_clause = on_clause.strip()

                        joins.append({
                            "type": join_type.strip(),
                            "right_table": right_table,
                            "condition": on_clause
                        })

        return joins
