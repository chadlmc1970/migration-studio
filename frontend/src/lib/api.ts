// Centralized API client - all backend calls go through here

import type {
  PipelineState,
  EventEntry,
  UniverseInfo,
  KPIStats,
  UniverseReports,
  RunResponse,
  RunRecord,
} from './types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`)
  }

  return response.json()
}

export const api = {
  // Get pipeline state
  getState: () => fetchAPI<PipelineState>('/state'),

  // Get recent events
  getEvents: (limit: number = 100) =>
    fetchAPI<EventEntry[]>(`/events?limit=${limit}`),

  // Get dashboard KPIs
  getKPIs: () => fetchAPI<KPIStats>('/kpis'),

  // Get all universes
  getUniverses: () => fetchAPI<UniverseInfo[]>('/universes'),

  // Get universe reports
  getUniverseReports: (universeId: string) =>
    fetchAPI<UniverseReports>(`/universes/${universeId}/reports`),

  // Upload universe file
  uploadUniverse: async (file: File): Promise<{ success: boolean; message: string }> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`)
    }

    return response.json()
  },

  // Run migration pipeline
  runPipeline: () => fetchAPI<RunResponse>('/run', { method: 'POST' }),

  // Get all runs
  getRuns: (limit: number = 50) => fetchAPI<RunRecord[]>(`/runs?limit=${limit}`),

  // Delete a run and its associated files
  deleteRun: (runId: string) =>
    fetchAPI<{ status: string; message: string }>(`/runs/${runId}`, {
      method: 'DELETE',
    }),

  // Get download URL for artifact
  getDownloadUrl: (universeId: string, artifact: string) =>
    `${API_BASE}/universes/${universeId}/download?artifact=${artifact}`,
}
