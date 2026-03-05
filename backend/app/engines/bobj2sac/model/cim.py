"""Canonical Intermediate Model (CIM) for universe representation."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SourceFile(BaseModel):
    """Represents a source file from the universe archive."""

    relative_path: str
    size_bytes: int
    sha256: str


class DataFoundation(BaseModel):
    """Placeholder for data foundation artifacts (tables, joins, etc.)."""

    tables: list[str] = Field(default_factory=list, description="Discovered table names")
    joins: list[dict[str, Any]] = Field(default_factory=list, description="Join definitions")
    raw_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Raw unparsed metadata"
    )


class BusinessLayer(BaseModel):
    """Placeholder for business layer objects."""

    dimensions: list[dict[str, Any]] = Field(default_factory=list, description="Dimension objects with name, table, column")
    measures: list[dict[str, Any]] = Field(default_factory=list, description="Measure objects with name, table, column")
    filters: list[str] = Field(default_factory=list, description="Filter names")
    raw_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Raw unparsed metadata"
    )


class CanonicalModel(BaseModel):
    """Canonical Intermediate Model for a BOBJ universe."""

    universe_id: str = Field(description="Unique identifier for the universe")
    universe_name: str = Field(description="Display name of the universe")
    source_format: str = Field(description="Source format: unx or unv")
    extraction_timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="When this model was created",
    )
    source_files: list[SourceFile] = Field(
        default_factory=list, description="Manifest of source files"
    )
    data_foundation: DataFoundation = Field(
        default_factory=DataFoundation, description="Data foundation artifacts"
    )
    business_layer: BusinessLayer = Field(
        default_factory=BusinessLayer, description="Business layer objects"
    )
    object_counts: dict[str, int] = Field(
        default_factory=dict, description="Summary counts of various objects"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    def update_counts(self) -> None:
        """Update object_counts from parsed structures."""
        self.object_counts = {
            "source_files": len(self.source_files),
            "tables": len(self.data_foundation.tables),
            "joins": len(self.data_foundation.joins),
            "dimensions": len(self.business_layer.dimensions),
            "measures": len(self.business_layer.measures),
            "filters": len(self.business_layer.filters),
        }
