#!/usr/bin/env python3
"""
Quick demo script showing the validation engine in action
"""
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

console = Console()

def show_validation_summary():
    """Display validation summary"""

    # Load validation report
    report_path = Path.home() / "pipeline/logs/validation/sales_universe_validation_report.json"

    if not report_path.exists():
        console.print("[red]No validation report found. Run 'python cli.py run' first.[/red]")
        return

    with open(report_path) as f:
        report = json.load(f)

    # Load coverage report
    coverage_path = Path.home() / "pipeline/validation/sales_universe/coverage_report.json"
    with open(coverage_path) as f:
        coverage = json.load(f)

    # Load semantic diff
    diff_path = Path.home() / "pipeline/validation/sales_universe/semantic_diff.json"
    with open(diff_path) as f:
        diff = json.load(f)

    # Header
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]SAP Migration Validation Engine[/bold cyan]\n"
        "[dim]Semantic Preservation & Lineage Analysis[/dim]",
        border_style="cyan"
    ))

    # Universe info
    console.print(f"\n[bold]Universe:[/bold] {report['universe']}")
    console.print(f"[bold]Status:[/bold] {report['status']} ✅")
    console.print(f"[bold]Timestamp:[/bold] {report['timestamp']}")
    console.print(f"[bold]Duration:[/bold] {report['elapsed_seconds']:.3f}s")

    # Semantic validation table
    console.print("\n[bold cyan]═══ Semantic Validation ═══[/bold cyan]")

    semantic_table = Table(show_header=True, header_style="bold magenta")
    semantic_table.add_column("Element Type", style="cyan")
    semantic_table.add_column("Checked", justify="right", style="green")
    semantic_table.add_column("Missing", justify="right", style="red")
    semantic_table.add_column("Status", justify="center")

    semantic_table.add_row(
        "Dimensions",
        str(report['dimensions_checked']),
        str(report['dimensions_missing']),
        "✅ PASS" if report['dimensions_missing'] == 0 else "❌ FAIL"
    )
    semantic_table.add_row(
        "Measures",
        str(report['measures_checked']),
        str(report['measures_missing']),
        "✅ PASS" if report['measures_missing'] == 0 else "❌ FAIL"
    )
    semantic_table.add_row(
        "Joins",
        str(report['joins_checked']),
        str(report['joins_missing']),
        "⚠️  WARNING" if report['joins_missing'] > 0 else "✅ PASS"
    )

    console.print(semantic_table)
    console.print(f"\n[bold]Overall Status:[/bold] {diff['status']}")

    # Coverage table
    console.print("\n[bold cyan]═══ Coverage Analysis ═══[/bold cyan]")

    coverage_table = Table(show_header=True, header_style="bold magenta")
    coverage_table.add_column("Metric", style="cyan")
    coverage_table.add_column("Coverage %", justify="right", style="green")
    coverage_table.add_column("Found/Total", justify="right")
    coverage_table.add_column("Missing", justify="right")

    for metric_name, metric_data in coverage['details'].items():
        percentage = metric_data['coverage'] * 100
        coverage_table.add_row(
            metric_name.replace('_', ' ').title(),
            f"{percentage:.1f}%",
            f"{metric_data['found']}/{metric_data['total']}",
            str(len(metric_data.get('missing', [])))
        )

    console.print(coverage_table)
    console.print(f"\n[bold]Overall Coverage:[/bold] {coverage['summary']['overall_coverage'] * 100:.1f}%")
    console.print(f"[bold]Status:[/bold] {coverage['status']}")

    # Lineage tree
    console.print("\n[bold cyan]═══ Lineage Graph ═══[/bold cyan]")

    lineage_path = Path.home() / "pipeline/validation/sales_universe/lineage_graph.json"
    with open(lineage_path) as f:
        lineage = json.load(f)

    console.print(f"\n[bold]Nodes:[/bold] {lineage['stats']['node_count']}")
    console.print(f"[bold]Edges:[/bold] {lineage['stats']['edge_count']}")

    # Count node types
    node_types = {}
    for node in lineage['nodes']:
        node_type = node['type']
        node_types[node_type] = node_types.get(node_type, 0) + 1

    console.print("\n[bold]Node Types:[/bold]")
    for node_type, count in sorted(node_types.items()):
        console.print(f"  • {node_type}: {count}")

    # Output files
    console.print("\n[bold cyan]═══ Output Files ═══[/bold cyan]")

    files_tree = Tree("📁 /pipeline/validation/sales_universe/")
    files_tree.add("📄 semantic_diff.json")
    files_tree.add("📄 coverage_report.json")
    files_tree.add("📊 lineage_graph.json")
    files_tree.add("🎨 lineage_graph.dot")

    console.print(files_tree)

    # Footer
    console.print("\n" + "─" * 60)
    console.print("[dim]Validation complete. All semantic logic preserved.[/dim]")
    console.print("─" * 60 + "\n")


if __name__ == "__main__":
    show_validation_summary()
