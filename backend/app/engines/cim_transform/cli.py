"""CLI for CIM Transformation Engine"""
import typer
from pathlib import Path
from .pipeline_runner import PipelineRunner

app = typer.Typer(help="CIM Transformation Engine - Convert CIM to SAC/Datasphere artifacts")


@app.command()
def run(
    pipeline_root: Path = typer.Option(
        Path("/pipeline"),
        "--pipeline-root",
        "-p",
        help="Root directory of the pipeline"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force transformation even if already completed"
    )
):
    """
    Run the transformation engine.

    Scans /pipeline/cim for CIM files and generates SAC/Datasphere artifacts.
    Only processes universes where parsed=true and transformed!=true.
    Use --force to reprocess already transformed universes.
    """
    print("🚀 CIM Transformation Engine")
    print("="*60)

    runner = PipelineRunner(pipeline_root)
    runner.run(force=force)


@app.command()
def version():
    """Show version information"""
    from . import __version__
    print(f"CIM Transformation Engine v{__version__}")


if __name__ == "__main__":
    app()
