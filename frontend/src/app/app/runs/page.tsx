'use client'

import { useState } from 'react'
import { api } from '@/lib/api'

export default function RunsPage() {
  const [running, setRunning] = useState(false)
  const [logs, setLogs] = useState<string>('')
  const [error, setError] = useState<string | null>(null)

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
      <div className="rounded-lg border border-slate-200 bg-slate-900 p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-slate-100">Pipeline Output</h3>
          {logs && (
            <button
              onClick={() => setLogs('')}
              className="text-xs text-slate-400 hover:text-slate-200"
            >
              Clear
            </button>
          )}
        </div>
        <pre className="text-sm text-slate-100 font-mono whitespace-pre-wrap h-96 overflow-y-auto">
          {logs || 'No output yet. Click "Run Migration" to start the pipeline.'}
        </pre>
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
