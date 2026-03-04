'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'

interface Run {
  run_id: string
  status: string
  started_at: string
  completed_at?: string
  duration_seconds?: number
  universes_processed?: string[]
}

export default function RunsPage() {
  const [running, setRunning] = useState(false)
  const [logs, setLogs] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const [runs, setRuns] = useState<Run[]>([])
  const [loadingRuns, setLoadingRuns] = useState(true)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  // Fetch runs history
  useEffect(() => {
    loadRuns()
  }, [])

  async function loadRuns() {
    try {
      setLoadingRuns(true)
      const data = await api.getRuns(50)
      setRuns(data)
    } catch (err) {
      console.error('Failed to load runs:', err)
    } finally {
      setLoadingRuns(false)
    }
  }

  async function handleRunMigration() {
    try {
      setRunning(true)
      setError(null)
      setLogs('Starting migration pipeline...\n')

      const result = await api.runPipeline()

      setLogs((prev) => prev + `\nRun ID: ${result.run_id}\n`)
      setLogs((prev) => prev + `Status: ${result.status}\n`)
      setLogs((prev) => prev + `\n${result.message}\n`)

      if (result.status === 'completed') {
        setLogs((prev) => prev + '\n✅ Migration completed successfully!')
        loadRuns() // Refresh runs list
      } else if (result.status === 'failed') {
        setLogs((prev) => prev + '\n❌ Migration failed')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run migration')
      setLogs((prev) => prev + `\n❌ Error: ${err instanceof Error ? err.message : 'Unknown error'}`)
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
      loadRuns() // Refresh runs list
    } catch (err) {
      alert(`Failed to delete run: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setDeletingId(null)
    }
  }

  function formatDuration(seconds?: number) {
    if (!seconds) return 'N/A'
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`
  }

  function formatDate(isoString: string) {
    return new Date(isoString).toLocaleString()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Run Migration</h1>
          <p className="mt-1 text-sm text-slate-600">
            Execute the full pipeline: Parser → Transform → Validation
          </p>
        </div>
        <button
          onClick={handleRunMigration}
          disabled={running}
          className="inline-flex items-center gap-2 rounded-md bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {running ? (
            <>
              <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Running...
            </>
          ) : (
            <>
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Run Migration
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Log Output */}
      {logs && (
        <div className="rounded-lg border border-slate-200 bg-slate-900 p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-100">Pipeline Output</h3>
            <button
              onClick={() => setLogs('')}
              className="text-xs text-slate-400 hover:text-slate-200"
            >
              Clear
            </button>
          </div>
          <pre className="text-sm text-slate-100 font-mono whitespace-pre-wrap h-96 overflow-y-auto">
            {logs}
          </pre>
        </div>
      )}

      {/* Runs History */}
      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Run History</h3>

        {loadingRuns ? (
          <div className="text-center py-8 text-slate-500">Loading runs...</div>
        ) : runs.length === 0 ? (
          <div className="text-center py-8 text-slate-500">No runs yet. Click "Run Migration" to start your first pipeline execution.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead>
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Run ID</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Started</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Duration</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Universes</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {runs.map((run) => (
                  <tr key={run.run_id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-sm font-mono text-slate-900">{run.run_id}</td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        run.status === 'success' ? 'bg-green-100 text-green-800' :
                        run.status === 'running' ? 'bg-blue-100 text-blue-800' :
                        run.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-slate-100 text-slate-800'
                      }`}>
                        {run.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-600">{formatDate(run.started_at)}</td>
                    <td className="px-4 py-3 text-sm text-slate-600">{formatDuration(run.duration_seconds)}</td>
                    <td className="px-4 py-3 text-sm text-slate-600">{run.universes_processed?.length || 0}</td>
                    <td className="px-4 py-3 text-right text-sm">
                      <button
                        onClick={() => handleDeleteRun(run.run_id)}
                        disabled={deletingId === run.run_id}
                        className="text-red-600 hover:text-red-800 disabled:opacity-50"
                        title="Delete run and associated files"
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

      {/* Info Box */}
      <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
        <h4 className="text-sm font-semibold text-blue-900">Pipeline Execution Order</h4>
        <ol className="mt-2 space-y-1 text-sm text-blue-800">
          <li>1. <strong>Parser</strong> - Convert universe files to CIM</li>
          <li>2. <strong>Transform</strong> - Generate SAC, Datasphere, HANA artifacts</li>
          <li>3. <strong>Validation</strong> - Run quality checks and generate reports</li>
        </ol>
      </div>
    </div>
  )
}
