import type { CoverageReport } from '@/lib/types'

interface CoverageReportProps {
  report: CoverageReport
}

export default function CoverageReportComponent({ report }: CoverageReportProps) {
  const metrics = [
    { label: 'Table Coverage', value: report.summary.table_coverage },
    { label: 'Dimension Coverage', value: report.summary.dimension_coverage },
    { label: 'Measure Coverage', value: report.summary.measure_coverage },
    { label: 'Join Coverage', value: report.summary.join_coverage },
  ]

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <h3 className="text-lg font-semibold text-slate-900">Coverage Summary</h3>
        <div className="mt-4 grid grid-cols-2 gap-4">
          {metrics.map((metric) => (
            <div key={metric.label} className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-slate-600">{metric.label}</span>
                <span className="text-sm font-semibold text-slate-900">
                  {Math.round(metric.value * 100)}%
                </span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-100">
                <div
                  className="h-2 rounded-full bg-green-500"
                  style={{ width: `${metric.value * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
        <div className="mt-6 rounded-md bg-slate-50 p-4">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-slate-600">Overall Coverage:</span>
            <span className="text-lg font-bold text-slate-900">
              {Math.round(report.summary.overall_coverage * 100)}%
            </span>
            <span className={`ml-2 rounded-full px-2 py-1 text-xs font-medium ${
              report.status === 'EXCELLENT' ? 'bg-green-100 text-green-700' :
              report.status === 'GOOD' ? 'bg-blue-100 text-blue-700' :
              'bg-yellow-100 text-yellow-700'
            }`}>
              {report.status}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
