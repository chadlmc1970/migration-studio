"""Transformation Report Logger"""
import json
from pathlib import Path
from datetime import datetime
from ..loaders.cim_loader import CIMModel
from ..graph.semantic_graph import SemanticGraph


class TransformReport:
    """Generate transformation reports"""

    def __init__(self, cim: CIMModel):
        self.cim = cim
        self.warnings = []
        self.errors = []

    def add_warning(self, message: str):
        """Add a warning to the report"""
        self.warnings.append(message)

    def add_error(self, message: str):
        """Add an error to the report"""
        self.errors.append(message)

    def validate_cim(self):
        """Validate CIM structure and log warnings"""
        if not self.cim.tables:
            self.add_warning("No tables defined in CIM")

        if not self.cim.dimensions and not self.cim.measures:
            self.add_warning("No dimensions or measures defined")

        # Check if all dimension/measure tables exist
        table_names = {t.name for t in self.cim.tables}

        for dim in self.cim.dimensions:
            if dim.table not in table_names:
                self.add_warning(f"Dimension '{dim.name}' references undefined table '{dim.table}'")

        for measure in self.cim.measures:
            if measure.table not in table_names:
                self.add_warning(f"Measure '{measure.name}' references undefined table '{measure.table}'")

        # Check join connectivity
        if len(self.cim.tables) > 1:
            graph = SemanticGraph(self.cim)
            if not graph.is_connected():
                self.add_warning("Not all tables are connected via joins")

    def generate_report(self, output_path: Path) -> dict:
        """Generate and save transformation report"""
        self.validate_cim()

        report = {
            "universe": self.cim.universe.id,
            "universe_name": self.cim.universe.name,
            "timestamp": datetime.utcnow().isoformat(),
            "schema_version": self.cim.schema_version,
            "tables": len(self.cim.tables),
            "joins": len(self.cim.joins),
            "dimensions": len(self.cim.dimensions),
            "measures": len(self.cim.measures),
            "warnings": self.warnings,
            "errors": self.errors,
            "status": "error" if self.errors else "warning" if self.warnings else "success"
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        return report
