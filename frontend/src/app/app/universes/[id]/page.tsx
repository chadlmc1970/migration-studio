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
        <div className="rounded-2xl bg-white border border-slate-200 p-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-slate-900">Available Downloads</h3>
            <p className="text-sm text-slate-600 mt-1">Download generated migration artifacts</p>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {reports?.available_artifacts.sac_model && (
              <DownloadCard
                universeId={params.id}
                artifact="sac/model.json"
                label="SAC Model"
                description="Analytics Cloud model definition"
                icon="sac"
              />
            )}
            {reports?.available_artifacts.datasphere_views && (
              <DownloadCard
                universeId={params.id}
                artifact="datasphere/views.sql"
                label="Datasphere Views"
                description="SQL view definitions"
                icon="datasphere"
              />
            )}
            {reports?.available_artifacts.hana_schema && (
              <DownloadCard
                universeId={params.id}
                artifact="hana/schema.sql"
                label="HANA Schema"
                description="Database schema DDL"
                icon="hana"
              />
            )}
            {reports?.available_artifacts.lineage_dot && (
              <DownloadCard
                universeId={params.id}
                artifact="lineage_graph.dot"
                label="Lineage Graph"
                description="Data lineage visualization"
                icon="lineage"
              />
            )}
          </div>

          {!reports?.available_artifacts.sac_model &&
           !reports?.available_artifacts.datasphere_views &&
           !reports?.available_artifacts.hana_schema &&
           !reports?.available_artifacts.lineage_dot && (
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3 3m0 0l-3-3m3 3V10" />
              </svg>
              <p className="mt-4 text-sm font-medium text-slate-900">No artifacts available</p>
              <p className="mt-1 text-sm text-slate-500">Run the pipeline to generate downloadable files</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function DownloadCard({
  universeId,
  artifact,
  label,
  description,
  icon,
}: {
  universeId: string
  artifact: string
  label: string
  description: string
  icon: 'sac' | 'datasphere' | 'hana' | 'lineage'
}) {
  const downloadUrl = api.getDownloadUrl(universeId, artifact)

  const iconColors = {
    sac: 'bg-blue-100 text-blue-600',
    datasphere: 'bg-purple-100 text-purple-600',
    hana: 'bg-green-100 text-green-600',
    lineage: 'bg-orange-100 text-orange-600',
  }

  const icons = {
    sac: (
      <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    datasphere: (
      <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
      </svg>
    ),
    hana: (
      <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
      </svg>
    ),
    lineage: (
      <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
  }

  return (
    <a
      href={downloadUrl}
      download
      className="group relative flex items-start gap-4 rounded-xl border-2 border-slate-200 bg-white p-5 transition-all hover:border-indigo-500 hover:shadow-lg"
    >
      <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-lg ${iconColors[icon]}`}>
        {icons[icon]}
      </div>

      <div className="flex-1 min-w-0">
        <h4 className="text-base font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors">
          {label}
        </h4>
        <p className="text-sm text-slate-600 mt-0.5">{description}</p>
        <div className="flex items-center gap-2 mt-2">
          <span className="inline-flex items-center gap-1 text-xs font-medium text-indigo-600">
            <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download
          </span>
        </div>
      </div>

      <div className="shrink-0 text-slate-400 group-hover:text-indigo-500 transition-colors">
        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </a>
  )
}
