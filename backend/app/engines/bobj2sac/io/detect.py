"""Universe file format detection."""

from pathlib import Path


def detect_format(input_path: Path) -> str:
    """Detect universe format from file extension."""
    suffix = input_path.suffix.lower()
    if suffix == ".unx":
        return "unx"
    elif suffix == ".unv":
        return "unv"
    else:
        raise ValueError(f"Unknown universe format: {suffix}")
