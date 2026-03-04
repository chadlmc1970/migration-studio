"""CLI interface for bobj2sac converter."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from bobj2sac.convert import convert_universe
from bobj2sac.pipeline import process_pipeline

app = typer.Typer(help="BOBJ Universe to SAC/Datasphere migration engine")
console = Console()


@app.command()
def convert(
    input_path: Path = typer.Argument(..., help="Path to .unv or .unx universe file"),
    out: Path = typer.Option(..., "--out", help="Output directory for converted artifacts"),
) -> None:
    """Convert a BOBJ universe to canonical intermediate model."""
    console.print(f"[bold blue]BOBJ to SAC Converter[/bold blue]")
    console.print(f"Input: {input_path}")
    console.print(f"Output: {out}")
    console.print()

    try:
        with console.status("[bold green]Converting universe..."):
            cim, logger = convert_universe(input_path, out)

        # Display summary
        console.print("[bold green]✓ Conversion complete[/bold green]")
        console.print()

        # Summary table
        table = Table(title="Conversion Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", justify="right", style="magenta")

        for key, value in cim.object_counts.items():
            table.add_row(key.replace("_", " ").title(), str(value))

        console.print(table)

        # Report summary
        report = logger.to_report()
        summary = report["summary"]

        if summary["error_count"] > 0:
            console.print(f"[bold red]✗ Errors: {summary['error_count']}[/bold red]")
        if summary["warning_count"] > 0:
            console.print(f"[bold yellow]⚠ Warnings: {summary['warning_count']}[/bold yellow]")

        # Output paths
        console.print()
        console.print("[bold]Output artifacts:[/bold]")
        universe_name = input_path.stem
        output_base = out / universe_name
        console.print(f"  • Raw files: {output_base / 'raw'}")
        console.print(f"  • CIM: {output_base / 'cim.json'}")
        console.print(f"  • Report: {output_base / 'report.json'}")

    except Exception as e:
        console.print(f"[bold red]✗ Error: {e}[/bold red]")
        raise typer.Exit(code=1)


@app.command()
def pipeline(
    pipeline_root: Path = typer.Option(
        Path("/pipeline"),
        "--root",
        help="Pipeline root directory",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing CIM files",
    ),
) -> None:
    """Process all universes in pipeline mode (multi-engine system)."""
    console.print(f"[bold blue]Pipeline Mode - Universe Parser Engine[/bold blue]")
    console.print(f"Pipeline root: {pipeline_root}")
    console.print()

    try:
        with console.status("[bold green]Processing pipeline..."):
            results = process_pipeline(pipeline_root, force)

        # Display summary
        console.print("[bold green]✓ Pipeline processing complete[/bold green]")
        console.print()

        # Summary table
        table = Table(title="Pipeline Summary")
        table.add_column("Status", style="cyan")
        table.add_column("Count", justify="right", style="magenta")

        table.add_row("Total universes", str(results["total"]))
        table.add_row("Processed", str(len(results["processed"])))
        table.add_row("Skipped", str(len(results["skipped"])))
        table.add_row("Failed", str(len(results["failed"])))

        console.print(table)

        # Details
        if results["processed"]:
            console.print("\n[bold]Processed:[/bold]")
            for item in results["processed"]:
                console.print(f"  • {item['universe']}")
                console.print(f"    CIM: {item['cim']}")
                console.print(f"    Report: {item['report']}")

        if results["skipped"]:
            console.print("\n[bold yellow]Skipped:[/bold yellow]")
            for item in results["skipped"]:
                console.print(f"  • {item['universe']}: {item['reason']}")

        if results["failed"]:
            console.print("\n[bold red]Failed:[/bold red]")
            for item in results["failed"]:
                console.print(f"  • {item['universe']}: {item['error']}")

        if "message" in results:
            console.print(f"\n[yellow]{results['message']}[/yellow]")

    except Exception as e:
        console.print(f"[bold red]✗ Error: {e}[/bold red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
