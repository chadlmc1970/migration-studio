"""
Validation Runner - orchestrates all validation and lineage generation
"""
from pathlib import Path
from datetime import datetime
import json
from typing import Optional
from rich.console import Console

from loaders.cim_loader import CIMLoader
from loaders.target_loader import TargetLoader
from validators.coverage_validator import CoverageValidator
from validators.join_validator import JoinValidator
from validators.semantic_validator import SemanticValidator
from lineage.lineage_builder import LineageBuilder
from lineage.graph_export import GraphExporter
from reports.diff_report import DiffReportGenerator
from reports.coverage_report import CoverageReportGenerator
from pipeline_state import PipelineStateManager


class ValidationRunner:
    """Orchestrates validation and lineage generation"""

    def __init__(self, pipeline_root: Path, console: Console):
        self.pipeline_root = Path(pipeline_root)
        self.console = console

        # Initialize directories
        self.cim_dir = self.pipeline_root / "cim"
        self.targets_dir = self.pipeline_root / "targets"
        self.validation_dir = self.pipeline_root / "validation"
        self.logs_dir = self.pipeline_root / "logs" / "validation"

        # Create directories if they don't exist
        self.validation_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Initialize pipeline state manager
        self.state_manager = PipelineStateManager(self.pipeline_root)

        # Initialize components
        self.cim_loader = CIMLoader()
        self.target_loader = TargetLoader()
        self.coverage_validator = CoverageValidator()
        self.join_validator = JoinValidator()
        self.semantic_validator = SemanticValidator()
        self.lineage_builder = LineageBuilder()
        self.graph_exporter = GraphExporter()
        self.diff_generator = DiffReportGenerator()
        self.coverage_generator = CoverageReportGenerator()

    def run(self, universe_id: Optional[str] = None, generate_mocks: bool = False):
        """Run validation for all or specific universe"""

        # Check if CIM directory exists
        if not self.cim_dir.exists():
            self.console.print(f"[yellow]Warning: CIM directory not found: {self.cim_dir}[/yellow]")
            if generate_mocks:
                self._generate_mock_data()
            else:
                self.console.print("[yellow]Use --generate-mocks to create example data[/yellow]")
                return

        # Get list of universes to process
        if universe_id:
            universes = [universe_id]
        else:
            # Use pipeline state to determine which universes need validation
            universes = self.state_manager.get_universes_to_validate()

            if not universes:
                # Fallback: scan for all CIM files
                cim_files = list(self.cim_dir.glob("*.cim.json"))
                if not cim_files:
                    self.console.print("[yellow]No CIM files found and no universes marked for validation[/yellow]")
                    if generate_mocks:
                        self._generate_mock_data()
                        cim_files = list(self.cim_dir.glob("*.cim.json"))
                    else:
                        return
                universes = [f.stem.replace(".cim", "") for f in cim_files]
                self.console.print(f"[dim]Note: Using fallback mode (scanning CIM directory)[/dim]")
            else:
                self.console.print(f"[dim]Pipeline state: {len(universes)} universe(s) ready for validation[/dim]")

        # Process each universe
        for univ_id in universes:
            self.console.print(f"\n[bold cyan]Processing universe: {univ_id}[/bold cyan]")
            success = self._validate_universe(univ_id)

            # Update pipeline state
            if success:
                self.state_manager.mark_validated(univ_id, success=True)
                self.console.print(f"[dim]✓ Pipeline state updated: validated=true[/dim]")

    def _validate_universe(self, universe_id: str) -> bool:
        """
        Validate a single universe

        Returns:
            bool: True if validation succeeded, False otherwise
        """

        start_time = datetime.now()

        try:
            # 1. Load CIM
            self.console.print(f"  Loading CIM...")
            cim_path = self.cim_dir / f"{universe_id}.cim.json"

            if not cim_path.exists():
                self.console.print(f"[yellow]  Warning: CIM file not found: {cim_path}[/yellow]")
                return False

            cim = self.cim_loader.load(cim_path)
        except Exception as e:
            self.console.print(f"[red]  Error loading CIM: {e}[/red]")
            return False

        # 2. Load targets
        self.console.print(f"  Loading targets...")
        targets_path = self.targets_dir / universe_id

        if not targets_path.exists():
            self.console.print(f"[yellow]  Warning: Targets not found: {targets_path}[/yellow]")
            self.console.print(f"[yellow]  Continuing validation with CIM only...[/yellow]")
            targets = None
        else:
            targets = self.target_loader.load(targets_path)

        # 3. Run validators
        self.console.print(f"  Running semantic validation...")
        semantic_results = self.semantic_validator.validate(cim, targets)

        self.console.print(f"  Running coverage validation...")
        coverage_results = self.coverage_validator.validate(cim, targets)

        self.console.print(f"  Running join validation...")
        join_results = self.join_validator.validate(cim, targets)

        # 4. Build lineage graph
        self.console.print(f"  Building lineage graph...")
        lineage_graph = self.lineage_builder.build(cim, targets)

        # 5. Generate reports
        self.console.print(f"  Generating reports...")

        output_dir = self.validation_dir / universe_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # Semantic diff report
        diff_report = self.diff_generator.generate(semantic_results)
        diff_path = output_dir / "semantic_diff.json"
        with open(diff_path, "w") as f:
            json.dump(diff_report, f, indent=2)
        self.console.print(f"    → {diff_path}")

        # Coverage report
        coverage_report = self.coverage_generator.generate(coverage_results)
        coverage_path = output_dir / "coverage_report.json"
        with open(coverage_path, "w") as f:
            json.dump(coverage_report, f, indent=2)
        self.console.print(f"    → {coverage_path}")

        # Lineage graph (JSON)
        lineage_path = output_dir / "lineage_graph.json"
        self.graph_exporter.export_json(lineage_graph, lineage_path)
        self.console.print(f"    → {lineage_path}")

        # Lineage graph (DOT - optional)
        dot_path = output_dir / "lineage_graph.dot"
        self.graph_exporter.export_dot(lineage_graph, dot_path)
        self.console.print(f"    → {dot_path}")

        # 6. Write validation log
        elapsed = (datetime.now() - start_time).total_seconds()

        log_report = {
            "universe": universe_id,
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": elapsed,
            "dimensions_checked": semantic_results.get("dimensions_checked", 0),
            "dimensions_missing": len(semantic_results.get("missing_dimensions", [])),
            "measures_checked": semantic_results.get("measures_checked", 0),
            "measures_missing": len(semantic_results.get("missing_measures", [])),
            "joins_checked": join_results.get("joins_checked", 0),
            "joins_missing": len(join_results.get("missing_joins", [])),
            "coverage": coverage_results.get("coverage", {}),
            "status": "completed"
        }

        log_path = self.logs_dir / f"{universe_id}_validation_report.json"
        with open(log_path, "w") as f:
            json.dump(log_report, f, indent=2)

        self.console.print(f"  [green]✓ Validation log: {log_path}[/green]")

        # Print summary
        self._print_summary(log_report)

        return True

    def _print_summary(self, log_report: dict):
        """Print validation summary"""
        self.console.print(f"\n[bold]Summary:[/bold]")
        self.console.print(f"  Dimensions: {log_report['dimensions_checked']} checked, {log_report['dimensions_missing']} missing")
        self.console.print(f"  Measures: {log_report['measures_checked']} checked, {log_report['measures_missing']} missing")
        self.console.print(f"  Joins: {log_report['joins_checked']} checked, {log_report['joins_missing']} missing")

        coverage = log_report.get("coverage", {})
        if coverage:
            self.console.print(f"  Coverage:")
            for key, value in coverage.items():
                percentage = value * 100 if isinstance(value, float) else 0
                self.console.print(f"    {key}: {percentage:.1f}%")

    def _generate_mock_data(self):
        """Generate mock CIM and target data for testing"""
        self.console.print("[yellow]Generating mock data...[/yellow]")

        # Create mock CIM
        mock_cim = {
            "metadata": {
                "universe_id": "sales_universe",
                "universe_name": "Sales Universe",
                "version": "1.0",
                "extracted_at": datetime.now().isoformat()
            },
            "tables": [
                {
                    "id": "ORDERS",
                    "name": "ORDERS",
                    "schema": "SALES",
                    "columns": [
                        {"name": "ORDER_ID", "type": "INTEGER"},
                        {"name": "CUSTOMER_ID", "type": "INTEGER"},
                        {"name": "ORDER_DATE", "type": "DATE"},
                        {"name": "AMOUNT", "type": "DECIMAL"}
                    ]
                },
                {
                    "id": "CUSTOMERS",
                    "name": "CUSTOMERS",
                    "schema": "SALES",
                    "columns": [
                        {"name": "CUSTOMER_ID", "type": "INTEGER"},
                        {"name": "CUSTOMER_NAME", "type": "VARCHAR"},
                        {"name": "REGION", "type": "VARCHAR"}
                    ]
                }
            ],
            "dimensions": [
                {
                    "id": "ORDER_ID",
                    "name": "Order ID",
                    "table": "ORDERS",
                    "column": "ORDER_ID",
                    "type": "dimension"
                },
                {
                    "id": "CUSTOMER_NAME",
                    "name": "Customer Name",
                    "table": "CUSTOMERS",
                    "column": "CUSTOMER_NAME",
                    "type": "dimension"
                },
                {
                    "id": "ORDER_DATE",
                    "name": "Order Date",
                    "table": "ORDERS",
                    "column": "ORDER_DATE",
                    "type": "dimension"
                },
                {
                    "id": "REGION",
                    "name": "Region",
                    "table": "CUSTOMERS",
                    "column": "REGION",
                    "type": "dimension"
                }
            ],
            "measures": [
                {
                    "id": "REVENUE",
                    "name": "Revenue",
                    "expression": "SUM(ORDERS.AMOUNT)",
                    "aggregation": "SUM",
                    "type": "measure"
                },
                {
                    "id": "ORDER_COUNT",
                    "name": "Order Count",
                    "expression": "COUNT(ORDERS.ORDER_ID)",
                    "aggregation": "COUNT",
                    "type": "measure"
                }
            ],
            "joins": [
                {
                    "id": "ORDERS_CUSTOMERS",
                    "left_table": "ORDERS",
                    "right_table": "CUSTOMERS",
                    "left_column": "CUSTOMER_ID",
                    "right_column": "CUSTOMER_ID",
                    "join_type": "INNER",
                    "cardinality": "N:1"
                }
            ]
        }

        cim_path = self.cim_dir / "sales_universe.cim.json"
        self.cim_dir.mkdir(parents=True, exist_ok=True)
        with open(cim_path, "w") as f:
            json.dump(mock_cim, f, indent=2)
        self.console.print(f"  Created: {cim_path}")

        # Create mock targets
        targets_dir = self.targets_dir / "sales_universe"
        targets_dir.mkdir(parents=True, exist_ok=True)

        # Mock SAC model
        sac_dir = targets_dir / "sac"
        sac_dir.mkdir(exist_ok=True)
        mock_sac = {
            "modelId": "sales_universe",
            "dimensions": [
                {"id": "ORDER_ID", "name": "Order ID"},
                {"id": "CUSTOMER_NAME", "name": "Customer Name"},
                {"id": "ORDER_DATE", "name": "Order Date"},
                {"id": "REGION", "name": "Region"}
            ],
            "measures": [
                {"id": "REVENUE", "name": "Revenue", "aggregation": "SUM"},
                {"id": "ORDER_COUNT", "name": "Order Count", "aggregation": "COUNT"}
            ]
        }
        with open(sac_dir / "model.json", "w") as f:
            json.dump(mock_sac, f, indent=2)

        # Mock Datasphere SQL
        datasphere_dir = targets_dir / "datasphere"
        datasphere_dir.mkdir(exist_ok=True)
        mock_sql = """
CREATE VIEW SALES_UNIVERSE_VIEW AS
SELECT
    o.ORDER_ID,
    c.CUSTOMER_NAME,
    o.ORDER_DATE,
    c.REGION,
    SUM(o.AMOUNT) as REVENUE,
    COUNT(o.ORDER_ID) as ORDER_COUNT
FROM SALES.ORDERS o
INNER JOIN SALES.CUSTOMERS c
    ON o.CUSTOMER_ID = c.CUSTOMER_ID
GROUP BY o.ORDER_ID, c.CUSTOMER_NAME, o.ORDER_DATE, c.REGION;
"""
        with open(datasphere_dir / "views.sql", "w") as f:
            f.write(mock_sql)

        self.console.print(f"  Created: {targets_dir}")
        self.console.print("[green]Mock data generation complete[/green]")
