// Shared TypeScript types for the application

export interface UniverseStatus {
  parsed: boolean
  transformed: boolean
  validated: boolean
  validated_at?: string
}

export interface PipelineState {
  universes: Record<string, UniverseStatus>
}

export interface EventEntry {
  timestamp: string
  level: string
  message: string
  universe_id?: string
}

export interface UniverseInfo {
  id: string
  parsed: boolean
  transformed: boolean
  validated: boolean
  validated_at?: string
  coverage?: number
  last_updated?: string
}

export interface KPIStats {
  total_universes: number
  parsed: number
  transformed: number
  validated: number
  needs_attention: number
}

export interface CoverageReport {
  summary: {
    table_coverage: number
    dimension_coverage: number
    measure_coverage: number
    join_coverage: number
    overall_coverage: number
  }
  status: string
}

export interface SemanticDiff {
  summary: {
    total_dimensions: number
    missing_dimensions_count: number
    total_measures: number
    missing_measures_count: number
    aggregation_mismatches_count: number
  }
  status: string
}

export interface UniverseReports {
  universe_id: string
  coverage_report?: CoverageReport
  semantic_diff?: SemanticDiff
  lineage_graph?: any
  available_artifacts: {
    sac_model: boolean
    datasphere_views: boolean
    hana_schema: boolean
    lineage_dot: boolean
  }
}

export interface RunResponse {
  run_id: string
  status: string
  message: string
}
