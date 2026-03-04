#!/usr/bin/env python3
"""
Validation Engine CLI
"""
import typer
from pathlib import Path
from rich.console import Console
from runner import ValidationRunner

app = typer.Typer(help="Validation and Lineage Engine for SAP Migration")
console = Console()


@app.command()
def run(
    pipeline_root: Path = typer.Option(
        Path.home() / "pipeline",
        "--pipeline-root",
        "-p",
        help="Root directory of the pipeline filesystem"
    ),
    universe_id: str = typer.Option(
        None,
        "--universe",
        "-u",
        help="Specific universe to validate (optional, validates all if not provided)"
    ),
    generate_mocks: bool = typer.Option(
        False,
        "--generate-mocks",
        "-m",
        help="Generate mock data if CIM/targets are missing"
    )
):
    """
    Run validation on CIM files and generated targets.

    Scans /pipeline/cim for universes, loads generated targets,
    runs validation checks, builds lineage graphs, and writes reports.
    """
    console.print(f"[bold blue]Validation Engine Starting[/bold blue]")
    console.print(f"Pipeline root: {pipeline_root}")

    runner = ValidationRunner(pipeline_root, console)

    try:
        runner.run(universe_id=universe_id, generate_mocks=generate_mocks)
        console.print("[bold green]✓ Validation completed successfully[/bold green]")
    except Exception as e:
        console.print(f"[bold red]✗ Validation failed: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def list_universes(
    pipeline_root: Path = typer.Option(
        Path.home() / "pipeline",
        "--pipeline-root",
        "-p",
        help="Root directory of the pipeline filesystem"
    )
):
    """
    List all available universes in the CIM directory.
    """
    cim_dir = pipeline_root / "cim"

    if not cim_dir.exists():
        console.print(f"[yellow]CIM directory not found: {cim_dir}[/yellow]")
        return

    cim_files = list(cim_dir.glob("*.cim.json"))

    if not cim_files:
        console.print("[yellow]No CIM files found[/yellow]")
        return

    console.print(f"[bold]Found {len(cim_files)} universe(s):[/bold]")
    for cim_file in cim_files:
        universe_id = cim_file.stem.replace(".cim", "")
        console.print(f"  • {universe_id}")


if __name__ == "__main__":
    app()
