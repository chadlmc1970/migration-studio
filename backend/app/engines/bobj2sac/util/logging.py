"""Logging utilities."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class ConversionLogger:
    """Logger for conversion process."""

    def __init__(self) -> None:
        self.warnings: list[dict[str, Any]] = []
        self.errors: list[dict[str, Any]] = []
        self.info: list[dict[str, Any]] = []

    def warn(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log a warning."""
        self.warnings.append({
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "context": context or {},
        })

    def error(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log an error."""
        self.errors.append({
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "context": context or {},
        })

    def log(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log info."""
        self.info.append({
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "context": context or {},
        })

    def to_report(self) -> dict[str, Any]:
        """Generate report dictionary."""
        return {
            "warnings": self.warnings,
            "errors": self.errors,
            "info": self.info,
            "summary": {
                "warning_count": len(self.warnings),
                "error_count": len(self.errors),
                "info_count": len(self.info),
            },
        }

    def save(self, output_path: Path) -> None:
        """Save report to JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(self.to_report(), f, indent=2)
