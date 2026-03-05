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
        <div className="space-y-6">
          {/* Basic Info Card */}
          <div className="rounded-xl border border-slate-200 bg-white p-6">
            <h3 className="text-lg font-semibold text-slate-900">Universe Information</h3>
            <div className="mt-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Universe ID</span>
                <span className="font-mono text-sm font-medium text-slate-900">{reports?.universe_id}</span>
              </div>
              {reports?.ai_enhanced && (
                <div className="flex items-center gap-2 pt-2 mt-2 border-t border-slate-100">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-gradient-to-r from-purple-100 to-indigo-100 text-sm font-medium text-purple-700">
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    AI Enhanced
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* AI Enhancements Card */}
          {reports?.ai_enhanced && reports?.ai_enhancements && reports.ai_enhancements.length > 0 && (
            <div className="rounded-xl border-2 border-indigo-200 bg-gradient-to-br from-white to-indigo-50 p-6">
              <div className="flex items-start gap-3 mb-5">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-purple-500 to-indigo-600 text-white">
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-slate-900">AI-Powered Enhancements</h3>
                  <p className="text-sm text-slate-600 mt-1">
                    Claude analyzed and improved your BusinessObjects extraction
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                {reports.ai_enhancements.map((enhancement, idx) => (
                  <div
                    key={idx}
                    className="group relative rounded-lg border border-slate-200 bg-white p-4 hover:border-indigo-300 hover:shadow-md transition-all"
                  >
                    <div className="flex items-start gap-3">
                      <div className={`mt-0.5 h-2 w-2 rounded-full shrink-0 ${
                        enhancement.impact === 'high' ? 'bg-green-500' :
                        enhancement.impact === 'medium' ? 'bg-yellow-500' :
                        'bg-blue-500'
                      }`}></div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="text-sm font-semibold text-slate-900">{enhancement.category}</h4>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${
                            enhancement.impact === 'high' ? 'bg-green-100 text-green-700' :
                            enhancement.impact === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-blue-100 text-blue-700'
                          }`}>
                            {enhancement.impact} impact
                          </span>
                        </div>
                        <p className="text-sm text-slate-600">{enhancement.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-5 pt-5 border-t border-indigo-200">
                <p className="text-xs text-slate-500 flex items-center gap-1.5">
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  These enhancements are automatically applied to all generated artifacts
                </p>
              </div>
            </div>
          )}

          {/* No AI Enhancements */}
          {!reports?.ai_enhanced && (
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-8 text-center">
              <svg className="mx-auto h-12 w-12 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <p className="mt-4 text-sm font-medium text-slate-900">No AI enhancements yet</p>
              <p className="mt-1 text-sm text-slate-500">Run the pipeline to apply AI-powered improvements</p>
            </div>
          )}
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
