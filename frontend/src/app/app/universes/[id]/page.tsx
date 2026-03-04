'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import type { UniverseReports } from '@/lib/types'
import CoverageReportComponent from '@/components/reports/CoverageReport'
import SemanticDiffComponent from '@/components/reports/SemanticDiff'

export default function UniverseDetailPage({ params }: { params: { id: string } }) {
  const [reports, setReports] = useState<UniverseReports | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'reports' | 'downloads'>('overview')

  useEffect(() => {
    async function loadReports() {
      try {
        setLoading(true)
        const data = await api.getUniverseReports(params.id)
        setReports(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load reports')
      } finally {
        setLoading(false)
      }
    }
    loadReports()
  }, [params.id])

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-slate-900 mx-auto"></div>
          <p className="mt-4 text-sm text-slate-600">Loading universe details...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 p-6">
        <p className="text-sm text-red-800">{error}</p>
      </div>
    )
  }

  const tabs = [
    { id: 'overview' as const, name: 'Overview' },
    { id: 'reports' as const, name: 'Reports' },
    { id: 'downloads' as const, name: 'Downloads' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{params.id}</h1>
        <p className="mt-1 text-sm text-slate-600">Universe details and validation reports</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium ${
                activeTab === tab.id
                  ? 'border-slate-900 text-slate-900'
                  : 'border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700'
              }`}
            >
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <h3 className="text-lg font-semibold text-slate-900">Overview</h3>
          <p className="mt-2 text-sm text-slate-600">Universe ID: {reports?.universe_id}</p>
        </div>
      )}

      {activeTab === 'reports' && (
        <div className="space-y-6">
          {reports?.coverage_report && (
            <CoverageReportComponent report={reports.coverage_report} />
          )}
          {reports?.semantic_diff && (
            <SemanticDiffComponent diff={reports.semantic_diff} />
          )}
          {!reports?.coverage_report && !reports?.semantic_diff && (
            <div className="rounded-lg border border-slate-200 bg-white p-12 text-center">
              <p className="text-sm text-slate-500">No reports available yet</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'downloads' && (
        <div className="space-y-4">
          {reports?.available_artifacts.sac_model && (
            <DownloadLink universeId={params.id} artifact="sac/model.json" label="SAC Model (JSON)" />
          )}
          {reports?.available_artifacts.datasphere_views && (
            <DownloadLink universeId={params.id} artifact="datasphere/views.sql" label="Datasphere Views (SQL)" />
          )}
          {reports?.available_artifacts.hana_schema && (
            <DownloadLink universeId={params.id} artifact="hana/schema.sql" label="HANA Schema (SQL)" />
          )}
          {reports?.available_artifacts.lineage_dot && (
            <DownloadLink universeId={params.id} artifact="lineage_graph.dot" label="Lineage Graph (DOT)" />
          )}
        </div>
      )}
    </div>
  )
}

function DownloadLink({ universeId, artifact, label }: { universeId: string; artifact: string; label: string }) {
  const downloadUrl = api.getDownloadUrl(universeId, artifact)

  return (
    <a
      href={downloadUrl}
      className="flex items-center justify-between rounded-lg border border-slate-200 bg-white p-4 hover:bg-slate-50"
      download
    >
      <span className="text-sm font-medium text-slate-900">{label}</span>
      <svg className="h-5 w-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
      </svg>
    </a>
  )
}
