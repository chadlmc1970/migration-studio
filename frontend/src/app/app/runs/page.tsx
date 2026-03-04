'use client'

import { useState, useEffect, useRef } from 'react'
import { api } from '@/lib/api'
import type { RunRecord, UniverseInfo } from '@/lib/types'

export default function RunsPage() {
  const [running, setRunning] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [runs, setRuns] = useState<RunRecord[]>([])
  const [universes, setUniverses] = useState<UniverseInfo[]>([])
  const [loadingRuns, setLoadingRuns] = useState(true)
  const [loadingUniverses, setLoadingUniverses] = useState(true)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    loadRuns()
    loadUniverses()
  }, [])

  async function loadRuns() {
    try {
      setLoadingRuns(true)
      const data = await api.getRuns(10)
      setRuns(data)
    } catch (err) {
      console.error('Failed to load runs:', err)
    } finally {
      setLoadingRuns(false)
    }
  }

  async function loadUniverses() {
    try {
      setLoadingUniverses(true)
      const data = await api.getUniverses()
      setUniverses(data)
    } catch (err) {
      console.error('Failed to load universes:', err)
    } finally {
      setLoadingUniverses(false)
    }
  }

  async function handleFileUpload(files: FileList | null) {
    if (!files || files.length === 0) return

    setUploading(true)
    setError(null)

    try {
      for (const file of Array.from(files)) {
        if (!file.name.endsWith('.unv') && !file.name.endsWith('.unx')) {
          throw new Error(`Invalid file type: ${file.name}. Only .unv and .unx files are allowed.`)
        }
        await api.uploadUniverse(file)
      }
      loadUniverses() // Refresh list
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  async function handleRunMigration() {
    if (universes.length === 0) {
      setError('No universe files to process. Please upload .unv or .unx files first.')
      return
    }

    try {
      setRunning(true)
      setError(null)
      await api.runPipeline()
      // Refresh both lists after run completes
      setTimeout(() => {
        loadRuns()
        loadUniverses()
      }, 2000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run migration')
    } finally {
      setRunning(false)
    }
  }

  async function handleDeleteRun(runId: string) {
    if (!confirm('Delete this run and all associated universe files/outputs?')) {
      return
    }

    try {
      setDeletingId(runId)
      await api.deleteRun(runId)
      loadRuns()
      loadUniverses()
    } catch (err) {
      alert(`Failed to delete run: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setDeletingId(null)
    }
  }

  function handleDragOver(e: React.DragEvent) {
    e.preventDefault()
    setDragOver(true)
  }

  function handleDragLeave(e: React.DragEvent) {
    e.preventDefault()
    setDragOver(false)
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    setDragOver(false)
    handleFileUpload(e.dataTransfer.files)
  }

  function formatDuration(seconds?: number) {
    if (!seconds) return 'N/A'
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`
  }

  function formatDate(isoString: string) {
    const date = new Date(isoString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`
    return date.toLocaleDateString()
  }

  const pendingUniverses = universes.filter(u => !u.parsed)
  const processingUniverses = universes.filter(u => u.parsed && !u.validated)

  return (
    <div className="space-y-6">
      {/* Header with CTA */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Pipeline Control</h1>
          <p className="mt-2 text-slate-600">
            Upload universe files and run the migration pipeline
          </p>
        </div>
        <button
          onClick={handleRunMigration}
          disabled={running || universes.length === 0}
          className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-3 text-base font-semibold text-white shadow-lg hover:shadow-xl hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
          {running ? (
            <>
              <svg className="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </>
          ) : (
            <>
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Run Pipeline
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-4">
          <div className="flex items-center gap-2">
            <svg className="h-5 w-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-sm font-medium text-red-800">{error}</p>
          </div>
        </div>
      )}

      {/* Upload + Status Grid */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Upload Zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`relative group ${dragOver ? 'scale-[1.02]' : ''} transition-transform`}
        >
          <div className={`rounded-2xl border-2 border-dashed p-8 text-center transition-all ${
            dragOver
              ? 'border-indigo-500 bg-indigo-50'
              : 'border-slate-300 bg-white hover:border-indigo-400 hover:bg-slate-50'
          }`}>
            <input
              ref={fileInputRef}
              type="file"
              accept=".unv,.unx"
              multiple
              onChange={(e) => handleFileUpload(e.target.files)}
              className="hidden"
            />

            {uploading ? (
              <div className="space-y-3">
                <svg className="h-12 w-12 mx-auto text-indigo-500 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p className="text-sm font-medium text-slate-700">Uploading files...</p>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="mx-auto w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center">
                  <svg className="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <div>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="text-sm font-semibold text-indigo-600 hover:text-indigo-500"
                  >
                    Click to upload
                  </button>
                  <span className="text-sm text-slate-600"> or drag and drop</span>
                </div>
                <p className="text-xs text-slate-500">.unv or .unx files</p>
              </div>
            )}
          </div>
        </div>

        {/* Pipeline Status */}
        <div className="rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 p-6 text-white">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Current Status
          </h3>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-white/10 flex items-center justify-center">
                  <svg className="h-5 w-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium">Pending Files</p>
                  <p className="text-xs text-slate-400">Ready to process</p>
                </div>
              </div>
              <span className="text-2xl font-bold">{pendingUniverses.length}</span>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-white/10 flex items-center justify-center">
                  <svg className="h-5 w-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium">Processing</p>
                  <p className="text-xs text-slate-400">In pipeline</p>
                </div>
              </div>
              <span className="text-2xl font-bold">{processingUniverses.length}</span>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-white/10 flex items-center justify-center">
                  <svg className="h-5 w-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium">Total Runs</p>
                  <p className="text-xs text-slate-400">All time</p>
                </div>
              </div>
              <span className="text-2xl font-bold">{runs.length}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Runs */}
      <div className="rounded-2xl bg-white border border-slate-200 overflow-hidden">
        <div className="p-6 border-b border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900">Recent Runs</h3>
          <p className="text-sm text-slate-600 mt-1">Pipeline execution history</p>
        </div>

        {loadingRuns ? (
          <div className="p-8 text-center text-slate-500">Loading...</div>
        ) : runs.length === 0 ? (
          <div className="p-12 text-center">
            <div className="mx-auto w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center mb-4">
              <svg className="h-8 w-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <p className="text-slate-600 font-medium">No pipeline runs yet</p>
            <p className="text-sm text-slate-500 mt-1">Upload universe files and run your first migration</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Run ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Started</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Duration</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Files</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {runs.map((run) => (
                  <tr key={run.run_id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4 text-sm font-mono text-slate-600">{run.run_id}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                        run.status === 'success' ? 'bg-green-100 text-green-700' :
                        run.status === 'running' ? 'bg-blue-100 text-blue-700' :
                        run.status === 'failed' ? 'bg-red-100 text-red-700' :
                        'bg-slate-100 text-slate-700'
                      }`}>
                        {run.status === 'running' && (
                          <svg className="h-3 w-3 animate-spin" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                        )}
                        {run.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-600">{formatDate(run.started_at)}</td>
                    <td className="px-6 py-4 text-sm text-slate-600">{formatDuration(run.duration_seconds)}</td>
                    <td className="px-6 py-4 text-sm text-slate-600">{run.universes_processed?.length || 0}</td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleDeleteRun(run.run_id)}
                        disabled={deletingId === run.run_id}
                        className="text-slate-400 hover:text-red-600 disabled:opacity-50 transition-colors"
                        title="Delete run and files"
                      >
                        {deletingId === run.run_id ? (
                          <svg className="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                        ) : (
                          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
