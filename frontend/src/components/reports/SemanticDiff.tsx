import type { SemanticDiff } from '@/lib/types'

interface SemanticDiffProps {
  diff: SemanticDiff
}

export default function SemanticDiffComponent({ diff }: SemanticDiffProps) {
  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <h3 className="text-lg font-semibold text-slate-900">Semantic Validation</h3>
        <div className="mt-4 space-y-4">
          <div className="flex items-center justify-between rounded-md bg-slate-50 p-4">
            <span className="text-sm font-medium text-slate-600">Total Dimensions</span>
            <span className="text-lg font-semibold text-slate-900">{diff.summary.total_dimensions}</span>
          </div>
          <div className="flex items-center justify-between rounded-md bg-slate-50 p-4">
            <span className="text-sm font-medium text-slate-600">Missing Dimensions</span>
            <span className={`text-lg font-semibold ${
              diff.summary.missing_dimensions_count === 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {diff.summary.missing_dimensions_count}
            </span>
          </div>
          <div className="flex items-center justify-between rounded-md bg-slate-50 p-4">
            <span className="text-sm font-medium text-slate-600">Total Measures</span>
            <span className="text-lg font-semibold text-slate-900">{diff.summary.total_measures}</span>
          </div>
          <div className="flex items-center justify-between rounded-md bg-slate-50 p-4">
            <span className="text-sm font-medium text-slate-600">Missing Measures</span>
            <span className={`text-lg font-semibold ${
              diff.summary.missing_measures_count === 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {diff.summary.missing_measures_count}
            </span>
          </div>
          <div className="flex items-center justify-between rounded-md bg-slate-50 p-4">
            <span className="text-sm font-medium text-slate-600">Aggregation Mismatches</span>
            <span className={`text-lg font-semibold ${
              diff.summary.aggregation_mismatches_count === 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {diff.summary.aggregation_mismatches_count}
            </span>
          </div>
          <div className="mt-4 rounded-md border-2 p-4 text-center ${
            diff.status === 'PASS' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
          }">
            <span className={`text-lg font-bold ${
              diff.status === 'PASS' ? 'text-green-700' : 'text-red-700'
            }`}>
              {diff.status}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
