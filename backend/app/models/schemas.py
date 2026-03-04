from typing import Dict, List, Optional, Any
from pydantic import BaseModel


class PipelineState(BaseModel):
    universes: Dict[str, dict] = {}


class UploadResponse(BaseModel):
    status: str
    filename: str
    path: str


class StageResult(BaseModel):
    status: str
    output: str
    error: str


class PipelineRunResponse(BaseModel):
    status: str
    run_id: str
    message: Optional[str] = None
    stage: Optional[str] = None
    results: Dict[str, StageResult]


class UniverseReports(BaseModel):
    coverage_report: Optional[Dict[str, Any]]
    semantic_diff: Optional[Dict[str, Any]]
    lineage_graph: Optional[Dict[str, Any]]


class StageStatus(BaseModel):
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


class RunRecord(BaseModel):
    run_id: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    stages: Dict[str, StageStatus]
    universes_processed: List[str] = []


class KPIMetrics(BaseModel):
    total_universes: int
    parsed: int
    transformed: int
    validated: int
    needs_attention: int


class Event(BaseModel):
    timestamp: str
    level: str
    message: str
    universe_id: Optional[str] = None


class AvailableArtifacts(BaseModel):
    sac_model: bool
    datasphere_views: bool
    hana_schema: bool
    lineage_dot: bool


class UniverseReportsWithArtifacts(BaseModel):
    universe_id: str
    coverage_report: Optional[Dict[str, Any]]
    semantic_diff: Optional[Dict[str, Any]]
    lineage_graph: Optional[str]
    available_artifacts: AvailableArtifacts
